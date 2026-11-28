#!/usr/bin/env python3
"""Fresh stock-Kissat searches on the exact five-leaf frontier.

No incremental/assumption status is used. Cubes are explicit CNF unit clauses.
UNSAT requires a complete native proof, deletion-stripped additions-only
normalization, and two strict original-parent+cube drat-trim replays.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import shutil
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "inputs"


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_cubes(path):
    cubes = []
    data = path.read_bytes()
    for lineno, line in enumerate(data.decode("ascii").splitlines(), 1):
        fields = line.split()
        if not fields or fields[0] != "a" or fields[-1] != "0":
            raise ValueError(f"cube line {lineno}: malformed")
        cube = [int(x) for x in fields[1:-1]]
        if not cube or len({abs(x) for x in cube}) != len(cube) or 0 in cube:
            raise ValueError(f"cube line {lineno}: invalid literals")
        cubes.append(cube)
    return cubes


def write_query(base, cube, out):
    with base.open("rb") as src:
        header = src.readline().split()
        if header[:2] != [b"p", b"cnf"]:
            raise ValueError("bad base header")
        nv, nc = int(header[2]), int(header[3])
        with out.open("wb") as dst:
            dst.write(f"p cnf {nv} {nc + len(cube)}\n".encode())
            shutil.copyfileobj(src, dst, 1 << 20)
            for lit in cube:
                dst.write(f"{lit} 0\n".encode())


def normalize_additions(paths, output):
    """Consume every byte of binary CAS+leaf proofs; retain only additions."""
    tag = None
    record = bytearray()
    additions = deletions = 0
    final_empty = False
    total_in = total_out = 0
    with output.open("wb") as dst:
        for path in paths:
            with path.open("rb") as src:
                for chunk in iter(lambda: src.read(1 << 20), b""):
                    total_in += len(chunk)
                    for byte in chunk:
                        if tag is None:
                            if byte not in (ord("a"), ord("d")):
                                raise ValueError(f"invalid binary proof tag {byte}")
                            tag = byte
                            record = bytearray([byte])
                        else:
                            record.append(byte)
                            if byte == 0:
                                if tag == ord("a"):
                                    dst.write(record)
                                    total_out += len(record)
                                    additions += 1
                                    final_empty = record == b"a\0"
                                else:
                                    deletions += 1
                                tag = None
                                record = bytearray()
    if tag is not None or not final_empty:
        raise ValueError("truncated proof or no final added empty clause")
    return {"input_bytes_accounted": total_in, "output_bytes": total_out,
            "additions_preserved": additions, "deletions_removed": deletions,
            "final_added_empty_clause": final_empty}


def strict_check(checker, query, proof, logpath, seconds):
    cmd = [str(checker.resolve()), str(query.resolve()), str(proof.resolve()),
           "-i", "-U", "-t", str(seconds)]
    try:
        run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=seconds + 15)
        rc = run.returncode
        raw = run.stdout
        launcher_timeout = False
    except subprocess.TimeoutExpired as exc:
        rc = 124
        raw = (exc.stdout or b"") + b"\nCHECKER LAUNCHER TIMEOUT\n"
        launcher_timeout = True
    log = raw.replace(b"\r", b"\n")
    logpath.write_bytes(log)
    text = log.decode(errors="replace")
    lines = text.splitlines()
    reads = [int(x) for x in re.findall(r"finished parsing, read (\d+) bytes from proof file", text)]
    whole_bytes = reads == [proof.stat().st_size]
    clean = not any("WARNING" in x or "ERROR" in x or "NOT VERIFIED" in x for x in lines)
    passed = (rc == 0 and lines.count("s VERIFIED") == 1 and clean and whole_bytes
              and not launcher_timeout)
    return {"passed": passed, "returncode": rc, "clean": clean,
            "exact_verified_lines": lines.count("s VERIFIED"),
            "proof_read_byte_counts": reads,
            "strict_whole_proof_bytes": whole_bytes,
            "launcher_timeout": launcher_timeout,
            "checker_sha256": sha(checker), "log": logpath.name,
            "command": cmd}


def checked_model(logtext, query):
    values = []
    for line in logtext.splitlines():
        if line.startswith("v "):
            values.extend(int(x) for x in line[2:].split())
        elif line.startswith("s "):
            values = []
    lits = {x for x in values if x}
    if not lits:
        return False, None
    clauses = []
    current = []
    for line in query.read_text().splitlines():
        if not line or line[0] in "cp":
            continue
        for field in line.split():
            lit = int(field)
            if lit:
                current.append(lit)
            else:
                clauses.append(current)
                current = []
    okay = not current and all(any(x in lits for x in clause) for clause in clauses)
    model_bytes = (" ".join(str(x) for x in sorted(lits, key=lambda x: abs(x))) + " 0\n").encode()
    return okay, hashlib.sha256(model_bytes).hexdigest() if okay else None


def terminate_group(proc):
    if proc.poll() is not None:
        return
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=5)
    except (ProcessLookupError, subprocess.TimeoutExpired):
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        proc.wait()


def search_one(index, cube, out, args):
    leaf = out / f"leaf-{index}"
    leaf.mkdir()
    working_query = leaf / "working-query.cnf"
    original_query = leaf / "query.cnf"
    proof = leaf / "leaf.drat"
    solver_log = leaf / "solver.log"
    write_query(IN / "working.cnf", cube, working_query)
    write_query(IN / "parent.cnf", cube, original_query)
    cmd = [str(args.solver.resolve()), f"--time={args.seconds}",
           f"--conflicts={args.conflicts}", "--seed=0", "--flushproof=true",
           str(working_query.resolve()), str(proof.resolve())]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic()
    resource_stop = None
    with solver_log.open("wb") as log:
        proc = subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT,
                                start_new_session=True)
        while proc.poll() is None:
            if proof.exists() and proof.stat().st_size >= args.max_proof_bytes:
                resource_stop = "proof-byte-cap"
                terminate_group(proc)
                break
            if time.monotonic() - started >= args.seconds + 15:
                resource_stop = "launcher-timeout"
                terminate_group(proc)
                break
            time.sleep(0.5)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    elapsed = time.monotonic() - started
    rawlog = solver_log.read_bytes().replace(b"\r", b"\n")
    text = rawlog.decode(errors="replace")
    statuses = [x for x in text.splitlines() if x in
                ("s SATISFIABLE", "s UNSATISFIABLE", "s UNKNOWN")]
    conflicts = [int(x.replace(",", "")) for x in re.findall(r"^c conflicts:\s+([0-9,]+)", text, re.M)]
    rec = {"index": index, "cube": cube, "solver": "Kissat 4.0.4 (k58-massive-solver)",
           "solver_sha256": sha(args.solver), "command": cmd,
           "solver_returncode": proc.returncode, "solver_status_lines": statuses,
           "solver_conflicts_last": conflicts[-1] if conflicts else None,
           "elapsed_s": elapsed,
           "cpu_s": (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime),
           "budget": {"seconds": args.seconds, "conflicts": args.conflicts,
                      "launcher_seconds": args.seconds + 15, "proof": "eager binary"},
           "parent_sha256": sha(IN / "parent.cnf"), "working_sha256": sha(IN / "working.cnf"),
           "cas_sha256": sha(IN / "cas.drat"),
           "query_sha256": sha(original_query), "working_query_sha256": sha(working_query),
           "resource_stop": resource_stop}
    if resource_stop is None and proc.returncode == 20 and statuses == ["s UNSATISFIABLE"]:
        if not proof.is_file() or proof.stat().st_size > args.max_proof_bytes:
            rec["status"] = "CHECK_FAILED_MISSING_OR_OVERSIZE_PROOF"
        else:
            rec["raw_proof_sha256"] = sha(proof)
            rec["raw_proof_bytes"] = proof.stat().st_size
            normalized = leaf / "joined.additions-only.drat"
            rec["normalization"] = normalize_additions([IN / "cas.drat", proof], normalized)
            rec["normalized_proof_sha256"] = sha(normalized)
            checks = []
            for name, checker in (("primary", args.checker), ("second", args.second_checker)):
                result = strict_check(checker, original_query, normalized,
                                      leaf / f"strict-replay-{name}.log", args.check_seconds)
                checks.append(result)
                if not result["passed"]:
                    break
            rec["checks"] = checks
            rec["status"] = "CHECKED_UNSAT" if len(checks) == 2 and all(x["passed"] for x in checks) else "CHECK_FAILED"
    elif resource_stop is None and proc.returncode == 10 and statuses == ["s SATISFIABLE"]:
        okay, model_hash = checked_model(text, original_query)
        rec["status"] = "CNF_SAT_MODEL_CHECKED" if okay else "CNF_SAT_MODEL_UNVERIFIED"
        rec["model_sha256"] = model_hash
    else:
        rec["status"] = "OPEN"
    if proof.exists() and rec["status"] in ("OPEN", "CNF_SAT_MODEL_CHECKED", "CNF_SAT_MODEL_UNVERIFIED"):
        rec["discarded_noncertificate_proof_bytes"] = proof.stat().st_size
        rec["discarded_noncertificate_proof_sha256"] = sha(proof)
        proof.unlink()
    return rec


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seconds", type=int, default=120)
    p.add_argument("--conflicts", type=int, default=4000000)
    p.add_argument("--check-seconds", type=int, default=300)
    p.add_argument("--max-proof-bytes", type=int, default=1000000000)
    p.add_argument("--solver", type=Path, default=ROOT / "bin/kissat-massive")
    p.add_argument("--checker", type=Path, default=ROOT / "bin/drat-trim-own")
    p.add_argument("--second-checker", type=Path, default=ROOT / "bin/drat-trim-massive")
    p.add_argument("--only", type=int, action="append")
    args = p.parse_args()
    out = ROOT / "run" / "kissat-frontier"
    out.mkdir(exist_ok=False)
    cubes = read_cubes(IN / "frontier.cubes")
    selected = list(enumerate(cubes)) if args.only is None else [(i, cubes[i]) for i in args.only]
    receipts = []
    for index, cube in selected:
        rec = search_one(index, cube, out, args)
        receipts.append(rec)
        (out / "receipts.json").write_text(json.dumps(receipts, indent=2, sort_keys=True) + "\n")
        print(json.dumps(rec, sort_keys=True), flush=True)
    print(json.dumps({"leaves_attempted": len(receipts),
                      "checked_unsat": sum(x["status"] == "CHECKED_UNSAT" for x in receipts),
                      "open": sum(x["status"] == "OPEN" for x in receipts)}, sort_keys=True))


if __name__ == "__main__":
    main()
