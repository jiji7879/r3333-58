#!/usr/bin/env python3
"""Strict exit-code / proof protocol adapter for the K58 SAT pipeline.

Authority model (the point of this file)
---------------------------------------
* An UNSAT verdict is never taken from an exit code.  It is taken from a
  replayed proof: drat-trim must exit 0 *and* print the exact line
  ``s VERIFIED``.  The exit code is recorded only as a consistency check, and
  a disagreement is reported as REFUSED, never silently downgraded.
* A SAT verdict is not taken from an exit code either: the model printed on
  the ``v`` lines must satisfy every clause of the CNF we handed to the
  solver, as parsed by this file's own reader.
* UNKNOWN from an internal limit (kissat --time/--conflicts, cadical -t/-c,
  all exit 0) and INTERRUPTED from a signal (negative wait status) are
  distinct verdicts and are never promoted to SAT/UNSAT.
* A proof file that this run did not create is not evidence, even when it
  verifies: drat-trim on a formula already closed by unit propagation prints
  ``s VERIFIED`` for an *empty* proof (selftest T08).
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
from pathlib import Path

VERIFIED_LINE = "s VERIFIED"


# --------------------------------------------------------------------------
# binary discovery: portable defaults, overridable by environment
# --------------------------------------------------------------------------
def _first_existing(candidates):
    for cand in candidates:
        if cand and Path(cand).is_file() and os.access(cand, os.X_OK):
            return Path(cand)
    return None


def discover():
    env = os.environ
    here = Path(__file__).resolve()
    roots = [here.parent, *here.parents[1:6]]
    kissat = _first_existing(
        [env.get("K58_KISSAT"), *(str(r / ".scratch/satcheck/bin/kissat") for r in roots),
         shutil.which("kissat")])
    drat = _first_existing(
        [env.get("K58_DRAT_TRIM"), *(str(r / ".scratch/satcheck/bin/drat-trim") for r in roots),
         shutil.which("drat-trim")])
    cadical = _first_existing([env.get("K58_CADICAL"), shutil.which("cadical"),
                              "/opt/lean/bin/cadical"])
    return {"kissat": kissat, "cadical": cadical, "drat-trim": drat}


# --------------------------------------------------------------------------
# CNF reading / model checking (adapter-side ground truth)
# --------------------------------------------------------------------------
class CnfError(ValueError):
    pass


def read_cnf(path):
    """Parse DIMACS.  Returns (nvars, clauses, header_declared_count)."""
    nvars = None
    declared = None
    clauses = []
    cur = []
    with open(path, "r", errors="replace") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line[0] == "c":
                continue
            if line[0] == "p":
                parts = line.split()
                if len(parts) < 4 or parts[1] != "cnf":
                    raise CnfError(f"bad header: {line!r}")
                nvars, declared = int(parts[2]), int(parts[3])
                continue
            if nvars is None:
                raise CnfError("clause before header")
            for tok in line.split():
                lit = int(tok)
                if lit == 0:
                    clauses.append(tuple(cur))
                    cur = []
                else:
                    cur.append(lit)
    if nvars is None:
        raise CnfError("no header")
    if cur:
        raise CnfError("unterminated clause")
    return nvars, clauses, declared


def check_model(clauses, model):
    for clause in clauses:
        if not any((lit > 0) == model.get(abs(lit), False) for lit in clause):
            return False, clause
    return True, None


def parse_model(text):
    model = {}
    for line in text.splitlines():
        if not line.startswith("v"):
            continue
        for tok in line[1:].split():
            lit = int(tok)
            if lit != 0:
                model[abs(lit)] = lit > 0
    return model


def unit_conflict(clauses):
    """True iff plain unit propagation on the clause set derives a conflict.

    Literals are deduplicated first: a clause written (2,2) is the unit clause
    (2).  Without that, this function and bcp.py's counter implementation
    disagreed on 2 of 200 random instances (both of them duplicate-literal
    cases); with it they agree on all 200, see bcp.py --selftest.
    """
    assign = {}
    while True:
        progressed = False
        reduced = []
        for clause in clauses:
            if any(abs(l) in assign and assign[abs(l)] == (l > 0) for l in clause):
                continue                      # satisfied
            rest = tuple(dict.fromkeys(l for l in clause if abs(l) not in assign))
            if not rest:
                return True                   # falsified clause: conflict
            if len(rest) == 1:
                lit = rest[0]
                assign[abs(lit)] = lit > 0
                progressed = True
            reduced.append(rest)
        clauses = reduced
        if not progressed:
            return False


# --------------------------------------------------------------------------
# process running
# --------------------------------------------------------------------------
def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def _snapshot(path):
    try:
        st = os.stat(path)
    except FileNotFoundError:
        return None
    return {"ino": st.st_ino, "size": st.st_size, "mtime_ns": st.st_mtime_ns}


def run_process(cmd, stdout_path, wall_budget, kill_after=None):
    """Run cmd; return (wait_status_as_int, wall, cpu, hit_hard_guard)."""
    started = time.monotonic()
    hard_limit = wall_budget * 3 + 30 if kill_after is None else kill_after
    with open(stdout_path, "wb") as out:
        child = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT,
                                 start_new_session=True)
        hit = False
        deadline = started + hard_limit
        while True:
            pid, status, usage = os.wait4(child.pid, os.WNOHANG)
            if pid != 0:
                break
            if time.monotonic() > deadline:
                hit = True
                try:
                    os.killpg(child.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                pid, status, usage = os.wait4(child.pid, 0)
                break
            time.sleep(0.005)
        child.returncode = os.waitstatus_to_exitcode(status)
    wall = time.monotonic() - started
    cpu = None if usage is None else usage.ru_utime + usage.ru_stime
    return child.returncode, wall, cpu, hit


ENGINE_ARGS = {
    "kissat": lambda b: ["-q", f"--time={int(b)}"],
    "cadical": lambda b: ["-q", "-t", str(int(b))],
}


def classify(rc):
    if rc == 10:
        return "SAT"
    if rc == 20:
        return "UNSAT"
    if rc == 0:
        return "UNKNOWN"
    if rc < 0:
        return f"INTERRUPTED({-rc})"
    return f"ERROR({rc})"


def certify_unsat(cnf, proof, drat_trim, timeout=600, extra=()):
    if drat_trim is None:
        return {"verified": False, "reason": "no drat-trim binary"}
    if not Path(proof).exists():
        return {"verified": False, "reason": "proof file missing"}
    log = Path(str(proof) + ".check.log")
    rc, wall, cpu, hit = run_process(
        [str(drat_trim), str(cnf), str(proof), "-c", *extra], log, timeout,
        kill_after=timeout)
    # Read WITHOUT universal-newline translation.  drat-trim separates progress
    # lines with a lone CR, so the verdict arrives as "\rs VERIFIED\n": a raw
    # reader that splits on "\n" sees "\rs VERIFIED" and rejects a valid proof.
    # Path.read_text() happens to hide this by translating the CR; we do not.
    with open(log, "r", errors="replace", newline="") as fh:
        text = fh.read()
    lines = text.splitlines()
    return {
        "verified": rc == 0 and VERIFIED_LINE in lines,
        "drat_rc": rc,
        "drat_wall": round(wall, 3),
        "drat_cpu": None if cpu is None else round(cpu, 3),
        "drat_log": str(log),
        "verified_seen_splitlines": VERIFIED_LINE in lines,
        # False whenever the verdict follows a bare CR: this is the flag that
        # tells you a "\n"-splitting checker would have rejected the proof.
        "verified_seen_split_nl_raw": VERIFIED_LINE in text.split("\n"),
        "hard_timeout": hit,
        "tail": " | ".join(lines[-3:]),
    }


_VERSION_CACHE = {}


def binary_version(binary):
    key = str(binary)
    if key not in _VERSION_CACHE:
        ver = None
        try:
            out = subprocess.run([key, "--version"], capture_output=True, text=True,
                                 timeout=10)
            for line in (out.stdout + out.stderr).splitlines():
                if re.fullmatch(r"\d+(\.\d+)*", line.strip()):
                    ver = line.strip()
                    break
        except Exception:
            pass
        _VERSION_CACHE[key] = ver
    return _VERSION_CACHE[key]


# --------------------------------------------------------------------------
# the adapter
# --------------------------------------------------------------------------
def run_engine(engine, cnf, proof=None, seconds=60, binaries=None, extra_args=()):
    """Run one engine on one CNF; return a strict receipt.

    receipt['verdict'] in {SAT, UNSAT, UNKNOWN, INTERRUPTED, ERROR, REFUSED}
    receipt['authority'] in {model-check, drat-replay,
                             proof-replay-after-nonzero-exit, none}
    """
    binaries = binaries or discover()
    binary = binaries.get(engine)
    if binary is None:
        raise SystemExit(f"engine {engine!r} not found")
    cnf = Path(cnf)
    nvars, clauses, declared = read_cnf(cnf)
    pre_proof = _snapshot(proof) if proof else None
    log_path = Path(str(proof) + ".solve.log") if proof else cnf.with_suffix(".solve.log")
    argv = [str(binary), *ENGINE_ARGS[engine](seconds), *extra_args, str(cnf)]
    if proof:
        argv.append(str(proof))
    rc, wall, cpu, hit = run_process(argv, log_path, seconds, kill_after=seconds * 3 + 30)
    status = classify(rc)
    rec = {
        "engine": engine,
        "binary": str(binary),
        "binary_version": binary_version(binary),
        "cnf": str(cnf),
        "cnf_sha256": sha256(cnf),
        "nvars": nvars,
        "clauses": len(clauses),
        "header_declared_clauses": declared,
        "header_count_ok": declared == len(clauses),
        "already_unit_closed": unit_conflict([tuple(c) for c in clauses]),
        "budget_seconds": seconds,
        "argv": argv,
        "exit_status": rc,
        "engine_status": status,
        "wall_seconds": round(wall, 3),
        "cpu_seconds": None if cpu is None else round(cpu, 3),
        "hard_guard_fired": hit,
        "log": str(log_path),
    }
    proof_used = False
    if proof:
        post = _snapshot(proof)
        rec["proof"] = str(proof)
        rec["proof_preexisting"] = pre_proof is not None
        rec["proof_bytes"] = post["size"] if post else 0
        fresh = post is not None and (
            pre_proof is None
            or (post["ino"], post["size"], post["mtime_ns"])
            != (pre_proof["ino"], pre_proof["size"], pre_proof["mtime_ns"]))
        rec["proof_fresh"] = fresh
        if post is not None and fresh:
            rec["proof_sha256"] = sha256(proof)
        proof_used = bool(fresh and post and post["size"])

    text = Path(log_path).read_text(errors="replace")

    if status == "SAT":
        model = parse_model(text)
        ok, bad = check_model(clauses, model)
        rec["verdict"] = "SAT" if ok else "REFUSED"
        rec["authority"] = "model-check" if ok else "none"
        rec["model_size"] = len(model)
        if not ok:
            rec["refusal"] = f"engine said SAT but model falsifies {bad!r}"
        return rec

    if proof_used:
        cert = certify_unsat(cnf, proof, binaries.get("drat-trim"),
                             timeout=max(30, 4 * seconds))
        rec["certification"] = cert
        if cert["verified"]:
            rec["verdict"] = "UNSAT"
            rec["authority"] = ("drat-replay" if status == "UNSAT"
                                else "proof-replay-after-nonzero-exit")
            if status != "UNSAT":
                rec["protocol_note"] = (
                    f"exit status says {status} but the proof replays; "
                    "the proof is the authority")
            if rec["already_unit_closed"]:
                rec["protocol_note"] = (
                    "formula closed by unit propagation alone: drat-trim verifies "
                    "any proof here, so this receipt does not attribute the refutation")
            return rec

    if status == "UNSAT":
        rec["verdict"] = "REFUSED"
        rec["refusal"] = "engine exited 20 but no fresh proof verified"
    elif status == "UNKNOWN":
        rec["verdict"] = "UNKNOWN"
    elif status.startswith("INTERRUPTED"):
        rec["verdict"] = "INTERRUPTED"
    else:
        rec["verdict"] = "ERROR"
    rec["authority"] = "none"
    return rec


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="engine protocol adapter")
    sub = ap.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("run", help="run an engine and certify the receipt")
    rp.add_argument("cnf")
    rp.add_argument("--engine", default="kissat")
    rp.add_argument("--proof")
    rp.add_argument("--seconds", type=int, default=60)
    rp.add_argument("--extra", nargs="*", default=[])
    cp = sub.add_parser("certify", help="replay a proof, no solver")
    cp.add_argument("cnf")
    cp.add_argument("proof")
    cp.add_argument("--timeout", type=float, default=600)
    cp.add_argument("--extra", nargs="*", default=[])
    args = ap.parse_args()
    if args.cmd == "run":
        out = run_engine(args.engine, args.cnf, args.proof, args.seconds,
                         extra_args=tuple(args.extra))
    else:
        out = certify_unsat(args.cnf, args.proof, discover()["drat-trim"],
                            timeout=args.timeout, extra=tuple(args.extra))
        try:  # the vacuity flag belongs with any certificate
            import bcp

            out["vacuity"] = bcp.bcp(args.cnf)
        except Exception as exc:  # pragma: no cover
            out["vacuity"] = {"error": repr(exc)}
    print(json.dumps(out, indent=2))
