#!/usr/bin/env python3
"""leafcert -- per-leaf certificate harness for cube-and-conquer (C&C) runs.

Purpose
-------
The pipeline solves a DIMACS base formula B together with a *cube* C (a list of
literals) by rebuilding the leaf formula as B + the unit clauses of C.  A C&C
claim "B is UNSAT" is only certifiable when

  (1) every leaf CNF B+C_i has an ordinary DRAT refutation that replays, and
  (2) the cube set {C_i} is an exhaustive disjunction (every model of B
      satisfies at least one C_i).

This tool does both, byte-exactly and with independent replay:

  freeze  B + C -> leaf CNF (base bytes are copied unchanged, only the DIMACS
          clause count in the header grows and the cube units are appended).
          Rejects cubes that would collide with the encoding (literal out of
          1..nv range, contradictory cube, duplicate cube, non-'p cnf' base,
          'p inccnf' base).
  cover   checks exhaustiveness *independently of any split tree*: the formula
          AND_i (not C_i) must be UNSAT; decided with the same solver binary.
  run     one leaf: engine + conflict/time budget, proof logging, explicit exit
          code handling (10=SAT, 20=UNSAT, 0=UNKNOWN, anything else=error),
          then drat-trim -c replay.  A SAT or UNKNOWN leaf is never certified.
  certify a cube list end to end, with aggregate verdict and receipts.
  replay  independent replay from a receipt (rebuild CNF from base+cube, check
          hashes, re-run drat-trim in a fresh process).

Deliberate non-feature: this tool does NOT certify anything from an
incremental-assumption run.  `inccnf_probe.py` measures why.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_KISSAT = str(HERE / "bin" / "kissat")
DEFAULT_CADICAL = shutil.which("cadical") or ""
DEFAULT_DRATTRIM = str(HERE / "bin" / "drat-trim")

RC_VERDICT = {10: "SAT", 20: "UNSAT", 0: "UNKNOWN", 1: "ERROR"}


class LeafError(RuntimeError):
    pass


# ---------------------------------------------------------------- utilities
def sha256(path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dimacs_header(path):
    """Return (nv, nc, header_bytes) of a 'p cnf' DIMACS file."""
    with open(path, "rb") as f:
        first = f.readline()
        off = len(first)
        head = first.decode("ascii", "strict").split()
        if head[:2] != ["p", "cnf"] or len(head) != 4:
            raise LeafError(
                f"{path}: first line is {first[:80]!r}, expected 'p cnf <vars> <clauses>'; "
                "a 'p inccnf' base is refused on purpose (it is not a formula)")
        try:
            return int(head[2]), int(head[3]), off
        except ValueError:
            raise LeafError(f"{path}: non-numeric DIMACS header {first[:80]!r}")


def check_cube(cube, nv):
    """Selector/variable-collision and polarity checks on one cube."""
    if not isinstance(cube, (list, tuple)) or len(cube) == 0:
        raise LeafError(f"cube must be a non-empty list of literals, got {cube!r}")
    seen = {}
    for lit in cube:
        if not isinstance(lit, int) or lit == 0:
            raise LeafError(f"cube literal {lit!r} is not a non-zero int")
        if abs(lit) > nv:
            raise LeafError(
                f"cube literal {lit} collides with the encoding: |lit| > nv={nv}. "
                "Freezing would silently enlarge the variable space; refused.")
        if lit in seen:
            raise LeafError(f"cube repeats literal {lit}")
        if -lit in seen:
            raise LeafError(f"cube is contradictory: contains {lit} and {-lit}")
        seen[lit] = True
    return list(cube)


# ------------------------------------------------------------------- freeze
def freeze(base, cube, out, expect_sha256=None):
    """Write leaf CNF = base body unchanged + cube units appended.

    Invariants checked here (cheap, and they are the ones that matter):
      * base is 'p cnf'
      * every cube literal is inside 1..nv and the cube is consistent
      * the written byte stream equals base's bytes from offset header_end,
        with only the header line replaced (clause count += len(cube))
      * header variable count is unchanged
    """
    base, out = Path(base), Path(out)
    if expect_sha256 is not None:
        got = sha256(base)
        if got != expect_sha256:
            raise LeafError(f"{base}: sha256 {got} != expected {expect_sha256}")
    nv, nc, off = dimacs_header(base)
    cube = check_cube(cube, nv)
    out.parent.mkdir(parents=True, exist_ok=True)
    with base.open("rb") as f, out.open("wb") as g:
        f.seek(off)
        g.write(f"p cnf {nv} {nc + len(cube)}\n".encode())
        shutil.copyfileobj(f, g, length=8 << 20)
        for lit in cube:
            g.write(f"{lit} 0\n".encode())
    # prefix check: the body we copied must be the base body byte for byte
    with base.open("rb") as f:
        f.seek(off)
        base_body = f.read()
    with out.open("rb") as f:
        f.seek(len(f"p cnf {nv} {nc + len(cube)}\n"))
        leaf_body = f.read(len(base_body))
        tail = f.read()
    if leaf_body != base_body:
        raise LeafError(f"{out}: copied body differs from {base} body")
    if tail != b"".join(f"{lit} 0\n".encode() for lit in cube):
        raise LeafError(f"{out}: appended units are not exactly the cube")
    return {"base": str(base), "base_sha256": sha256(base), "leaf": str(out),
            "leaf_sha256": sha256(out), "variables": nv,
            "base_clauses": nc, "cube": cube}


# ------------------------------------------------------------------ engines
def _cpu_children():
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return r.ru_utime + r.ru_stime


def run_kissat(cnf, proof, conflicts, seconds, extra=()):
    cmd = [DEFAULT_KISSAT, f"--conflicts={conflicts}", f"--time={seconds}", *extra,
           str(cnf), str(proof)]
    return _run_solver(cmd, cnf, proof, parser=_kissat_stats)


def run_cadical(cnf, proof, conflicts, seconds, extra=()):
    cmd = [DEFAULT_CADICAL, "--stats", "--binary=false", "-c", str(conflicts),
           "-t", str(seconds), *extra, str(cnf), str(proof)]
    return _run_solver(cmd, cnf, proof, parser=_cadical_stats)


def _kissat_stats(text):
    out = {}
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("c conflicts:"):
            out["conflicts"] = int(s.split()[2])
        elif s.startswith("c decisions:"):
            out["decisions"] = int(s.split()[2])
        elif s.startswith("c propagations:"):
            out["propagations"] = int(s.split()[2])
        elif s.startswith("c process-time:"):
            tok = s.split()[2].rstrip("s")
            try:
                out["process_time"] = float(tok)
            except ValueError:
                pass
        elif s.startswith("c maximum-resident-set-size:"):
            out["max_rss_bytes"] = int(s.split()[2])
    return out


def _cadical_stats(text):
    # 'c conflicts:     2     36363.64    per second' (needs --stats; -q is fine)
    out = {}
    for line in text.splitlines():
        f = line.split()
        if len(f) >= 3 and f[0] == "c" and f[1] in (
                "conflicts:", "decisions:", "propagations:", "restarts:"):
            try:
                out[f[1].rstrip(":")] = int(f[2])
            except ValueError:
                pass
    return out


def _run_solver(cmd, cnf, proof, parser):
    if Path(proof).exists():
        Path(proof).unlink()
    t0, c0 = time.monotonic(), _cpu_children()
    res = subprocess.run(cmd, capture_output=True, text=True)
    wall, dcpu = time.monotonic() - t0, _cpu_children() - c0
    verdict = RC_VERDICT.get(res.returncode, f"ERROR({res.returncode})")
    rec = {"cmd": cmd, "rc": res.returncode, "verdict": verdict,
           "wall_seconds": round(wall, 3), "child_cpu_seconds": round(dcpu, 3),
           "stdout_tail": "\n".join(res.stdout.splitlines()[-6:]),
           "stderr_tail": "\n".join(res.stderr.splitlines()[-6:])}
    rec.update(parser(res.stdout))
    if Path(proof).exists():
        rec["proof"] = str(proof)
        rec["proof_bytes"] = Path(proof).stat().st_size
        rec["proof_sha256"] = sha256(proof)
    else:
        rec["proof"] = None
        rec["proof_bytes"] = 0
    if verdict == "SAT":
        model = []
        for line in res.stdout.splitlines():
            if line.startswith("v "):
                model.extend(int(x) for x in line.split()[1:] if x != "0")
        rec["model_literals"] = len(model)
    if verdict not in ("SAT", "UNSAT", "UNKNOWN"):
        raise LeafError(f"solver failed: {rec['cmd']}: rc={res.returncode}\n{res.stderr[-2000:]}")
    return rec


def verify_drat(cnf, proof, timeout=3600):
    t0, c0 = time.monotonic(), _cpu_children()
    res = subprocess.run([DEFAULT_DRATTRIM, str(cnf), str(proof), "-c"],
                         capture_output=True, text=True, timeout=timeout)
    wall, dcpu = time.monotonic() - t0, _cpu_children() - c0
    ok = res.returncode == 0 and "s VERIFIED" in res.stdout
    return {"verified": ok, "drat_trim_rc": res.returncode,
            "drat_trim_wall_seconds": round(wall, 3),
            "drat_trim_cpu_seconds": round(dcpu, 3),
            "drat_trim_tail": "\n".join(res.stdout.strip().splitlines()[-5:]),
            "cnf_sha256": sha256(cnf), "proof_sha256": sha256(proof)}


# ------------------------------------------------------------------ coverage
def coverage(cubes, nv, workdir, conflicts=200000, seconds=60):
    """Decide whether the cubes are an exhaustive disjunction on 1..nv.

    The negation of the disjunction is AND_i (not C_i), a CNF whose clauses are
    the negated cubes; UNSAT of it means every total assignment satisfies some
    cube.  This is independent of how the cubes were produced (split tree or
    not), and it also catches a leaf list that lost a branch.
    """
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    seen, clauses = set(), []
    for i, cube in enumerate(cubes):
        cube = check_cube(cube, nv)
        key = tuple(sorted(cube))
        if key in seen:
            raise LeafError(f"duplicate cube at index {i}: {cube}")
        seen.add(key)
        clauses.append(" ".join(str(-l) for l in cube) + " 0")
    blocking = workdir / "blocking.cnf"
    blocking.write_text(f"p cnf {nv} {len(clauses)}\n" + "\n".join(clauses) + "\n")
    rec = run_kissat(blocking, workdir / "blocking.drat", conflicts, seconds)
    exhaustive = rec["verdict"] == "UNSAT"
    if rec["verdict"] == "UNSAT":
        vr = verify_drat(blocking, workdir / "blocking.drat")
        exhaustive = vr["verified"]
        rec["drat"] = vr
    return {"cubes": len(cubes), "blocking_cnf": str(blocking),
            "blocking_sha256": sha256(blocking), "exhaustive": exhaustive,
            "solver": rec}


# ------------------------------------------------------------------ certify
def certify(base, cubes, outdir, engine="kissat", conflicts=100000, seconds=120,
            ids=None, expect_base_sha256=None, replay_proofs=True):
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    nv, nc, _ = dimacs_header(base)
    ids = ids or [f"leaf{i:03d}" for i in range(len(cubes))]
    if len(ids) != len(cubes):
        raise LeafError("ids and cubes differ in length")
    records, t0 = [], time.monotonic()
    runner = {"kissat": run_kissat, "cadical": run_cadical}[engine]
    for leaf_id, cube in zip(ids, cubes):
        cnf = outdir / f"{leaf_id}.cnf"
        fr = freeze(base, cube, cnf, expect_sha256=expect_base_sha256 if not records else None)
        # only the first call re-hashes the base; later ones are cheap prefix work
        proof = outdir / f"{leaf_id}.drat"
        sol = runner(cnf, proof, conflicts, seconds)
        rec = {"leaf": leaf_id, "cube": cube, "cnf": str(cnf),
               "cnf_sha256": fr["leaf_sha256"], **fr, "solve": sol}
        if sol["verdict"] == "UNSAT":
            rec["drat"] = verify_drat(cnf, proof) if replay_proofs else {"verified": None}
            rec["status"] = "UNSAT_VERIFIED" if rec["drat"]["verified"] else "UNSAT_PROOF_FAILED"
        elif sol["verdict"] == "SAT":
            rec["status"] = "SAT"
        else:
            rec["status"] = "UNKNOWN"
        records.append(rec)
        print(json.dumps({"leaf": leaf_id, "status": rec["status"],
                          "wall": sol["wall_seconds"], "conflicts": sol.get("conflicts")}),
              flush=True)
    cov = coverage(cubes, nv, outdir / "coverage")
    counts = {}
    for r in records:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    closed = counts.get("UNSAT_VERIFIED", 0) == len(cubes)
    report = {
        "base": str(base), "base_sha256": sha256(base), "variables": nv,
        "engine": engine, "budget": {"conflicts": conflicts, "seconds": seconds},
        "leaves": len(cubes), "status_counts": counts,
        "coverage_exhaustive": cov["exhaustive"],
        "coverage": cov,
        "conclusion": ("BASE UNSAT: all leaves DRAT-verified and the cube "
                       "disjunction is exhaustive" if closed and cov["exhaustive"]
                       else "NO CLOSURE: leaves not all verified"
                            if not closed else
                            "NO CLOSURE: cube disjunction not shown exhaustive"),
        "total_wall_seconds": round(time.monotonic() - t0, 3),
        "records": records,
    }
    (outdir / "certificate.json").write_text(json.dumps(report, indent=1) + "\n")
    return report


# ------------------------------------------------------------------- replay
def replay(certificate_json, workdir):
    """Independent replay: rebuild every leaf from base+cube, check hashes,
    re-run drat-trim in a fresh process, and re-check coverage."""
    cert = json.loads(Path(certificate_json).read_text())
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    base = cert["base"]
    ok = True
    results = []
    for rec in cert["records"]:
        cnf = workdir / f"{rec['leaf']}.cnf"
        fr = freeze(base, rec["cube"], cnf)
        same = fr["leaf_sha256"] == rec["cnf_sha256"]
        proof = rec["solve"].get("proof")
        row = {"leaf": rec["leaf"], "rebuild_sha_matches": same,
               "recorded_status": rec["status"]}
        if proof is None or not Path(proof).exists():
            row["error"] = "recorded proof missing; cannot replay"
            ok = False
        elif rec["status"] == "UNSAT_VERIFIED":
            same_proof = sha256(proof) == rec["solve"]["proof_sha256"]
            vr = verify_drat(cnf, proof)
            row.update({"proof_sha_matches": same_proof, "drat": vr})
            if not (same and same_proof and vr["verified"]):
                ok = False
        results.append(row)
    cov = coverage([r["cube"] for r in cert["records"]], cert["variables"],
                   workdir / "coverage")
    ok = ok and cov["exhaustive"]
    out = {"certificate": str(certificate_json), "replay_ok": ok,
           "coverage_exhaustive": cov["exhaustive"], "results": results}
    (workdir / "replay.json").write_text(json.dumps(out, indent=1) + "\n")
    return out


# --------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("freeze")
    f.add_argument("base"); f.add_argument("cube"); f.add_argument("out")
    f.add_argument("--expect-base-sha256")

    c = sub.add_parser("cover")
    c.add_argument("base"); c.add_argument("cubes")
    c.add_argument("workdir"); c.add_argument("--conflicts", type=int, default=200000)
    c.add_argument("--seconds", type=int, default=60)

    r = sub.add_parser("run")
    r.add_argument("cnf"); r.add_argument("outdir")
    r.add_argument("--engine", default="kissat", choices=["kissat", "cadical"])
    r.add_argument("--conflicts", type=int, default=100000)
    r.add_argument("--seconds", type=int, default=120)

    ce = sub.add_parser("certify")
    ce.add_argument("base"); ce.add_argument("cubes"); ce.add_argument("outdir")
    ce.add_argument("--engine", default="kissat", choices=["kissat", "cadical"])
    ce.add_argument("--conflicts", type=int, default=100000)
    ce.add_argument("--seconds", type=int, default=120)
    ce.add_argument("--expect-base-sha256")

    rp = sub.add_parser("replay")
    rp.add_argument("certificate"); rp.add_argument("workdir")

    a = ap.parse_args(argv)
    if a.cmd == "freeze":
        cube = [int(x) for x in a.cube.split(",") if x.strip()]
        print(json.dumps(freeze(a.base, cube, a.out, a.expect_base_sha256), indent=1))
    elif a.cmd == "cover":
        nv = dimacs_header(a.base)[0]
        cubes = json.loads(Path(a.cubes).read_text())
        if isinstance(cubes, dict):
            cubes = cubes["cubes"]
        print(json.dumps(coverage(cubes, nv, a.workdir, a.conflicts, a.seconds), indent=1))
    elif a.cmd == "run":
        outdir = Path(a.outdir); outdir.mkdir(parents=True, exist_ok=True)
        proof = outdir / (Path(a.cnf).stem + ".drat")
        runner = run_kissat if a.engine == "kissat" else run_cadical
        sol = runner(a.cnf, proof, a.conflicts, a.seconds)
        if sol["verdict"] == "UNSAT":
            sol["drat"] = verify_drat(a.cnf, proof)
        print(json.dumps(sol, indent=1))
    elif a.cmd == "certify":
        nv = dimacs_header(a.base)[0]
        cubes = json.loads(Path(a.cubes).read_text())
        ids = None
        if isinstance(cubes, dict):
            ids = cubes.get("ids"); cubes = cubes["cubes"]
        print(json.dumps(certify(a.base, cubes, a.outdir, a.engine, a.conflicts,
                                 a.seconds, ids, a.expect_base_sha256), indent=1))
    elif a.cmd == "replay":
        print(json.dumps(replay(a.certificate, a.workdir), indent=1))


if __name__ == "__main__":
    main()
