"""Fresh destination-side refutation attempt for an appended clause C, with a
measurement path validated on a tiny control.

For a wire clause C (a consequence of the K15 square/matching theorem on this
parent), build  base(C) = exact retained request  +  the negation of C  (one unit
per literal), run the repository's native CaDiCaL 2.1.2 on it under a wall cap,
and replay any proof with the repository's drat-trim without -w.

Measurement contract (corrected): CPU is the *child* CPU from
resource.getrusage(RUSAGE_CHILDREN) deltas, wall is time.monotonic(). Driver-side
time.process_time() around subprocess.run measures this Python process, not the
solver, and is never recorded as solver CPU. A tiny fresh UNSAT control is run
through the same path first, so a zero or nonsense child-CPU reading is visible.

Solver exit 20 = refuted (then the checker must print exactly one 's VERIFIED');
exit 0 = unknown at the cap, which is OPEN, not a refutation. Histories: the two
retained 120 s-capped attempts (verify-clauses-with-invalid-cpu-field.json) carry
a parent-process CPU field that is void, and their real CPU cannot be recovered.
"""
import hashlib, json, resource, subprocess, time
from pathlib import Path
REPO = Path("/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo")
HERE = REPO / ".ultramath/smx0er1f6/m2"
CADICAL = REPO / "tools/color-resolved-wallcc/bin/cadical-2.1.2"
DRAT = REPO / "tools/color-resolved-wallcc/bin/drat-trim"
BASE = HERE / "parent-cube.cnf"
CAP_SECONDS = 20

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run_child(cmd):
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    wall = time.monotonic()
    res = subprocess.run(cmd, capture_output=True, text=True, check=False)
    wall = time.monotonic() - wall
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr,
            "wall_seconds": wall,
            "child_user_cpu_seconds": after.ru_utime - before.ru_utime,
            "child_system_cpu_seconds": after.ru_stime - before.ru_stime,
            "child_cpu_seconds": (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime),
            "children_maxrss_kib": after.ru_maxrss}

out = []
# --- control: tiny fresh UNSAT CNF, solver exit must be 20 and drat-trim must verify
ctrl = HERE / "control-unsat.cnf"; ctrl_proof = HERE / "control-unsat.drat"
ctrl.write_bytes(b"p cnf 2 4\n1 2 0\n1 -2 0\n-1 2 0\n-1 -2 0\n")
sol = run_child([str(CADICAL), "-q", str(ctrl), str(ctrl_proof)])
chk = run_child([str(DRAT), str(ctrl), str(ctrl_proof)])
lines = [x for x in chk["stdout"].splitlines() if x.strip() == "s VERIFIED"]
ctrl_rec = {"control": True, "cnf_sha256": sha(ctrl), "solver_returncode": sol["returncode"],
            "solver_wall_seconds": sol["wall_seconds"], "solver_child_cpu_seconds": sol["child_cpu_seconds"],
            "proof_bytes": ctrl_proof.stat().st_size,
            "checker_returncode": chk["returncode"], "checker_child_cpu_seconds": chk["child_cpu_seconds"],
            "s_verified_lines": len(lines)}
ctrl_rec["ok"] = (sol["returncode"] == 20 and chk["returncode"] == 0 and len(lines) == 1
                  and sol["child_cpu_seconds"] > 0 and sol["wall_seconds"] > 0)
out.append(ctrl_rec)
print(json.dumps({k: ctrl_rec[k] for k in ("control", "solver_returncode", "solver_wall_seconds",
      "solver_child_cpu_seconds", "checker_returncode", "s_verified_lines", "ok")}, sort_keys=True), flush=True)
assert ctrl_rec["ok"], ctrl_rec
ctrl_proof.unlink(missing_ok=True)

up = json.loads((HERE / "up.json").read_text())
nontrivial = [d for d in up["detail"] if not d["up_refuted"]]
picks = [nontrivial[0], nontrivial[len(nontrivial) // 2]]
base = BASE.read_bytes(); first, rest = base.split(b"\n", 1)
assert first == b"p cnf 19533 184337"
for i, d in enumerate(picks, 1):
    c = d["clause"]
    q = HERE / f"query-{i}.cnf"; proof = HERE / f"query-{i}.drat"
    q.write_bytes(b"p cnf 19533 %d\n" % (184337 + len(c)) + rest + b"".join(b"%d 0\n" % (-l) for l in c))
    sol = run_child([str(CADICAL), "-q", "-t", str(CAP_SECONDS), str(q), str(proof)])
    chk = run_child([str(DRAT), str(q), str(proof)]) if proof.exists() else None
    lines = [x for x in chk["stdout"].splitlines() if x.strip() == "s VERIFIED"] if chk else []
    rec = {"index": i, "clause": c, "up_refuted_at_base": d["up_refuted"], "query_sha256": sha(q),
           "wall_cap_seconds": CAP_SECONDS, "solver_returncode": sol["returncode"],
           "solver_wall_seconds": sol["wall_seconds"],
           "solver_child_user_cpu_seconds": sol["child_user_cpu_seconds"],
           "solver_child_system_cpu_seconds": sol["child_system_cpu_seconds"],
           "solver_child_cpu_seconds": sol["child_cpu_seconds"],
           "children_maxrss_kib": sol["children_maxrss_kib"],
           "proof_bytes": proof.stat().st_size if proof.exists() else 0,
           "proof_sha256": sha(proof) if proof.exists() else None,
           "checker_returncode": chk["returncode"] if chk else None,
           "checker_child_cpu_seconds": chk["child_cpu_seconds"] if chk else None,
           "s_verified_lines": len(lines)}
    rec["refuted"] = (sol["returncode"] == 20 and rec["checker_returncode"] == 0 and len(lines) == 1)
    rec["status"] = "UNSAT_verified" if rec["refuted"] else "OPEN_unknown_at_cap"
    out.append(rec)
    print(json.dumps({k: rec[k] for k in ("index", "solver_returncode", "solver_wall_seconds",
          "solver_child_cpu_seconds", "status", "s_verified_lines")}, sort_keys=True), flush=True)
    proof.unlink(missing_ok=True); q.unlink(missing_ok=True)
doc = {"measurement": "child CPU = resource.getrusage(RUSAGE_CHILDREN) delta; wall = time.monotonic()",
       "note": "The retained 120 s-capped records in verify-clauses-with-invalid-cpu-field.json "
               "stored driver time.process_time() as solver_cpu_seconds; that field is void and no "
               "accurate historic CPU can be recovered from those records. These reruns use a "
               f"{CAP_SECONDS} s wall cap and correct child accounting.",
       "control_validated": ctrl_rec["ok"], "records": out}
(HERE / "verify-clauses.json").write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
