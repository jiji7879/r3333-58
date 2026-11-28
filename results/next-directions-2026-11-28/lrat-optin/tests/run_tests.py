#!/usr/bin/env python3
"""Bounded acceptance tests for the fail-closed native-LRAT opt-in.

Everything happens under this member's directory.  The repository tree is only
read: the patch is applied to a throw-away copy of ``tools/color-resolved-wallcc``
and every run directory is a copy of a read-only fixture.

Fixtures (both already closed, copied, never modified in place)
  H8   .scratch/hard-case-mining/source-run   full root, 0 cuts, 49,226 conflicts,
       retained DRAT sha 55a39634..., accepted native-LRAT sha 05f0d7f1...
  R11  .ultramath/smwxwbjk8/m1/plans/15,15,14,13/3d443146...  357 cuts, 4 cubes,
       leaf r11 cube [4262,4645] closed at 1 conflict

Tests are named; a test fails closed if its own expectation is not met exactly.
"""

import json
import os
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent            # .ultramath/<run>/m3/tests
MEMBER = HERE.parent                              # .ultramath/<run>/m3
REPO = MEMBER.parents[2]                          # repository root
WORK = REPO / ".scratch/lrat-optin-integrated-tests"

TOOLS = REPO / "tools/color-resolved-wallcc"
LRAT = REPO / ".ultramath/smx06hpp8/m5/.scratch/tools/lrat-trim-423194927df747528d5b7364806b5b77b2660c12/lrat-trim"
LRAT_SHA = "f1eb1a4486274c35f4accf7bc13b595cfdbcf2d7c9aa6b46fb281f19d0d52895"
SOLVER_SHA = "a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b"
DRATTRIM_SHA = "48891f3f9dfccbbebfc6a21fa9e6daa6b674900a3f65b16a0b0f7f21d8a03bce"

PYSAT_CANDIDATES = (
    REPO / ".scratch/k58/.venv/lib/python3.12/site-packages",
    REPO / ".ultramath/smx06hpp8/m8/.venv/lib/python3.12/site-packages",
)

H8 = REPO / ".scratch/hard-case-mining/source-run"
R11 = (REPO / ".ultramath/smwxwbjk8/m1/plans/15,15,14,13"
       / "3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c")

PINNED = {
    "H8_drat": "55a3963489aad6bab8f2c3069f29045a94d88768f2529c242506f7f23c678eb2",
    "H8_lrat": "05f0d7f11d28e0a784cab3a1a737960fdc8bc5414cc246242d743bb668bd7b34",
    "H8_conflicts": 49226,
    "H8_query": "e8cc97847a6cab9c277933d2dd0d6112c79b061bebb5af221d57df5d6d6a2229",
    "R11_working": "64950cdc66a760e0ce59975b3244701e4c1ae81116b4f804cb35377ceaf4fcde",
    "R11_query_cube": "0390e03d8494256b47f2adee99a02e99fa549dec194e6e3d07e1417388463db2",
    "R11_cuts": 357,
}

RESULTS = []


# ---------------------------------------------------------------- utilities
def sha256(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def environment():
    for candidate in PYSAT_CANDIDATES:
        if candidate.is_dir():
            env = dict(os.environ)
            env["PYTHONPATH"] = str(candidate)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            return env, candidate
    raise SystemExit("no project-local python-sat site-packages found; nothing was installed")


def run(command, cwd, env, timeout=900):
    started = time.monotonic()
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    proc = subprocess.run([str(c) for c in command], cwd=str(cwd), env=env,
                          capture_output=True, text=True, timeout=timeout)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {"command": [str(c) for c in command], "rc": proc.returncode,
            "stdout": proc.stdout, "stderr": proc.stderr,
            "wall_s": round(time.monotonic() - started, 3),
            "cpu_s": round((after.ru_utime - before.ru_utime)
                           + (after.ru_stime - before.ru_stime), 3)}


def timed(command, cwd, env, timeout=900):
    """Same, but through /usr/bin/time -v for a max-RSS figure."""
    out = run(["/usr/bin/time", "-v", "--", *command], cwd, env, timeout)
    rss = None
    for line in out["stderr"].splitlines():
        if "Maximum resident set size" in line:
            rss = int(line.rsplit(":", 1)[1].strip())
    out["max_rss_kib"] = rss
    body = [l for l in out["stderr"].splitlines() if not l.startswith("\t")]
    out["stderr"] = "\n".join(body)
    return out


def check(name, condition, detail):
    RESULTS.append({"test": name, "passed": bool(condition), "detail": detail})
    print(("PASS " if condition else "FAIL ") + name + "  " + json.dumps(detail)[:600], flush=True)
    return bool(condition)


def record(name, detail):
    RESULTS.append({"test": name, "passed": True, "detail": detail, "measurement": True})
    print("MEASURE " + name + "  " + json.dumps(detail)[:900], flush=True)


def refresh(directory):
    if directory.exists():
        shutil.rmtree(directory)
    directory.parent.mkdir(parents=True, exist_ok=True)


def clone_fixture(source, target):
    """Copy a run directory and drop every per-leaf receipt and artifact."""
    refresh(target)
    shutil.copytree(source, target)
    for junk in (target / "leaves", target / ".prepare.lock", target / ".preparing.json"):
        if junk.is_dir():
            shutil.rmtree(junk)
        elif junk.exists():
            junk.unlink()
    return target


def receipt(run, node):
    return json.loads((run / "leaves" / node / "receipt.json").read_bytes())


def plan_of(run):
    return json.loads((run / "plan.json").read_bytes())


# ------------------------------------------------------------------ fixture
def build_sandbox(env):
    """Apply patches/0001-lrat-optin.patch to a copy of the HEAD tool directory."""
    build = WORK / ".scratch/build"
    refresh(build)
    sandbox = build / "tools/color-resolved-wallcc"
    (build / "tools").mkdir(parents=True)
    shutil.copytree(TOOLS, build / "tools/color-resolved-wallcc",
                    ignore=shutil.ignore_patterns("__pycache__", ".scratch"))
    expected = {name: sha256(MEMBER / "patched" / name)
                for name in ("native_leaf.py", "campaign.py", "wallcc.py")}
    expected["lrat_optin.py"] = sha256(MEMBER / "src/lrat_optin.py")
    got = {name: sha256(sandbox / name) for name in expected}
    # Once the option is integrated, a copy of the tested target already has
    # the expected bytes. Do not apply a previously integrated patch a second
    # time, because a fresh baseline is no longer available through `patch`.
    if got == expected:
        return sandbox, {"rc": 0, "stdout": "tested source already integrated", "stderr": ""}, expected, got
    patch = MEMBER / "patches/0001-lrat-optin.patch"
    applied = run(["patch", "-p1", "--batch", "--forward", "-i", patch], build, env)
    sandbox = build / "tools/color-resolved-wallcc"
    got = {name: sha256(sandbox / name) for name in expected}
    return sandbox, applied, expected, got


# -------------------------------------------------------------------- tests
def main():
    env, pysat = environment()
    print(f"python-sat from {pysat}", flush=True)
    started = time.monotonic()
    receipt_out = {"env": {"python": sys.version.split()[0],
                           "python_sat_site_packages": str(pysat),
                           "lrat_trim": str(LRAT), "lrat_trim_sha256": sha256(LRAT),
                           "head": run(["git", "rev-parse", "HEAD"], REPO, env)["stdout"].strip()}}

    sandbox, applied, expected, got = build_sandbox(env)
    check("patch_applies_and_reproduces_developed_source",
          applied["rc"] == 0 and got == expected,
          {"patch_rc": applied["rc"], "patch_stderr": applied["stderr"][-400:],
           "hashes": got, "expected": expected})
    tool = sandbox / "wallcc.py"
    sys.path[:0] = [str(sandbox), str(pysat)]
    import lrat_optin                                            # noqa: E402

    # ---- H8: full root, no cuts, native LRAT ------------------------------
    h8 = clone_fixture(H8, WORK / ".scratch/runs/H8-lrat")
    lrat_run = timed([sys.executable, tool, "resume", h8, "--engine", "native",
                      "--proof", "eager", "--conflicts", "50000", "--seconds", "45",
                      "--check-seconds", "30", "--lrat-trim", LRAT], sandbox, env)
    summary = json.loads(lrat_run["stdout"].strip().splitlines()[-1])
    h8_lrat = receipt(h8, "r")
    check("H8_lrat_leaf_closes_with_pinned_bytes",
          summary["status"] == "COVER_READY" and h8_lrat["status"] == "CHECKED_UNSAT"
          and h8_lrat["artifact_name"] == "leaf.lrat"
          and h8_lrat["artifact_sha256"] == PINNED["H8_lrat"]
          and h8_lrat["lrat_checker_sha256"] == LRAT_SHA
          and h8_lrat["cut_derivation_sha256"] is not None
          and h8_lrat["query_sha256"] == PINNED["H8_query"],
          {"summary": summary, "artifact_sha256": h8_lrat.get("artifact_sha256"),
           "query_sha256": h8_lrat.get("query_sha256"),
           "cpu_s": lrat_run["cpu_s"], "max_rss_kib": lrat_run["max_rss_kib"]})
    check("H8_lrat_search_counters_unchanged",
          h8_lrat["conflicts_used"] == PINNED["H8_conflicts"]
          and h8_lrat["solver"].endswith("+native LRAT"),
          {"conflicts_used": h8_lrat["conflicts_used"],
           "expected_conflicts": PINNED["H8_conflicts"],
           "solver": h8_lrat["solver"]})

    verify = run([sys.executable, tool, "verify", h8, "--check-seconds", "60",
                  "--lrat-trim", LRAT], sandbox, env)
    check("H8_verify_accepts_lrat_receipt",
          verify["rc"] == 0 and json.loads(verify["stdout"])["status"] == "VERIFIED_UNSAT",
          {"rc": verify["rc"], "stdout": verify["stdout"][-500:]})

    before = (h8 / "leaves/r/receipt.json").read_bytes()
    receipt_mtime = (h8 / "leaves/r/receipt.json").stat().st_mtime_ns
    again = run([sys.executable, tool, "resume", h8, "--engine", "native", "--proof", "eager",
                 "--conflicts", "50000", "--seconds", "45", "--check-seconds", "30",
                 "--lrat-trim", LRAT], sandbox, env)
    check("H8_resume_reuses_the_lrat_receipt_without_re_solving",
          again["rc"] == 0 and json.loads(again["stdout"])["status"] == "COVER_READY"
          and (h8 / "leaves/r/receipt.json").read_bytes() == before
          and (h8 / "leaves/r/receipt.json").stat().st_mtime_ns == receipt_mtime
          and again["cpu_s"] < 2.0,
          {"rc": again["rc"], "stdout": again["stdout"][-300:], "cpu_s": again["cpu_s"],
           "receipt_unchanged": (h8 / "leaves/r/receipt.json").read_bytes() == before})

    without = run([sys.executable, tool, "verify", h8, "--check-seconds", "60"], sandbox, env)
    check("verify_refuses_lrat_receipt_without_the_checker",
          without["rc"] == 1 and "pass the same --lrat-trim" in without["stderr"],
          {"rc": without["rc"], "stderr": without["stderr"][-300:]})

    # ---- H8 again with the incumbent DRAT route --------------------------
    h8d = clone_fixture(H8, WORK / ".scratch/runs/H8-drat")
    drat_run = timed([sys.executable, tool, "resume", h8d, "--engine", "native",
                      "--proof", "eager", "--conflicts", "50000", "--seconds", "45",
                      "--check-seconds", "30"], sandbox, env)
    h8_drat = receipt(h8d, "r")
    check("H8_drat_default_unchanged_and_pinned",
          h8_drat["status"] == "CHECKED_UNSAT" and h8_drat["artifact_name"] == "leaf.drat"
          and h8_drat["artifact_sha256"] == PINNED["H8_drat"]
          and h8_drat["conflicts_used"] == PINNED["H8_conflicts"]
          and "lrat_checker_sha256" not in h8_drat,
          {"artifact_sha256": h8_drat.get("artifact_sha256"),
           "conflicts_used": h8_drat.get("conflicts_used"),
           "cpu_s": drat_run["cpu_s"], "max_rss_kib": drat_run["max_rss_kib"]})

    # ---- matched certificate-checking cost, same formula and proof --------
    drat_check = timed([sandbox / "tools/drat-trim", h8d / "parent.cnf",
                        h8d / "leaves/r/leaf.drat", "-i", "-t", "60"], sandbox, env)
    lrat_check = timed([LRAT, h8 / "parent.cnf", h8 / "leaves/r/leaf.lrat"], sandbox, env)
    t0 = time.process_time()
    structure = lrat_optin.binary_lrat_structure(h8 / "leaves/r/leaf.lrat")
    structure_cpu = round(time.process_time() - t0, 3)
    record("matched_H8_certificate_check_cost",
           {"drat_trim": {"rc": drat_check["rc"], "cpu_s": drat_check["cpu_s"],
                          "max_rss_kib": drat_check["max_rss_kib"],
                          "verified": "s VERIFIED" in drat_check["stdout"].splitlines(),
                          "bytes": (h8d / "leaves/r/leaf.drat").stat().st_size},
            "lrat_trim": {"rc": lrat_check["rc"], "cpu_s": lrat_check["cpu_s"],
                          "max_rss_kib": lrat_check["max_rss_kib"],
                          "verified": "s VERIFIED" in lrat_check["stdout"].splitlines(),
                          "bytes": (h8 / "leaves/r/leaf.lrat").stat().st_size},
            "leaf_solver_cpu_s": {"lrat": lrat_run["cpu_s"], "drat": drat_run["cpu_s"]},
            "leaf_solver_max_rss_kib": {"lrat": lrat_run["max_rss_kib"],
                                        "drat": drat_run["max_rss_kib"]},
            "completeness_parse_optional": {
                "enabled_in_audit_only": True, "cpu_s": structure_cpu,
                "additions": structure["additions"], "deletions": structure["deletions"],
                "last_is_empty_add": structure["last_is_empty_add"],
                "bytes": structure["bytes"]}})

    # ---- R11: cube + 357 cuts, the case where the premise matters --------
    r11 = clone_fixture(R11, WORK / ".scratch/runs/R11cut")
    cut_run = timed([sys.executable, tool, "resume", r11, "--engine", "native",
                     "--proof", "eager", "--conflicts", "2000", "--seconds", "20",
                     "--check-seconds", "60", "--jobs", "1", "--lrat-trim", LRAT], sandbox, env)
    cut_summary = json.loads(cut_run["stdout"].strip().splitlines()[-1])
    r11_rec = receipt(r11, "r11")
    check("R11_cube_leaf_closes_with_cut_premise_recorded",
          cut_summary["counts"] == {"CHECKED_UNSAT": 1, "OPEN": 3}
          and r11_rec["status"] == "CHECKED_UNSAT"
          and r11_rec["cube"] == [4262, 4645]
          and r11_rec["artifact_name"] == "leaf.lrat"
          and r11_rec["query_sha256"] == PINNED["R11_query_cube"],
          {"counts": cut_summary["counts"], "receipt": {
              k: r11_rec.get(k) for k in ("status", "cube", "artifact_name",
                                          "artifact_sha256", "query_sha256",
                                          "cut_derivation_sha256", "conflicts_used")},
           "cpu_s": cut_run["cpu_s"]})
    premises = {}
    for node in ("r00", "r01", "r10", "r11"):
        rec = receipt(r11, node)
        premises[node] = (rec["status"], rec.get("artifact_name"))
        if rec["status"] == "OPEN":
            check(f"R11_open_leaf_{node}_carries_no_certificate",
                  not (r11 / "leaves" / node / "leaf.lrat").exists()
                  and not (r11 / "leaves" / node / "leaf.drat").exists()
                  and "artifact_sha256" not in rec,
                  {"receipt_keys": sorted(rec), "status": rec["status"]})
    check("R11_lrat_premise_checked_once_with_357_cuts",
          cut_summary.get("lrat", {}).get("cut_derivation", {}).get("status")
          == "PASS_CUT_DERIVATION"
          and cut_summary["lrat"]["cut_derivation"]["cuts"] == PINNED["R11_cuts"]
          and cut_summary["lrat"]["cut_derivation"]["working_sha256"] == PINNED["R11_working"]
          and premises["r11"][0] == "CHECKED_UNSAT",
          {"cut_derivation": cut_summary.get("lrat", {}).get("cut_derivation"),
           "statuses": premises})

    cut_verify = run([sys.executable, tool, "verify", r11, "--check-seconds", "60",
                      "--lrat-trim", LRAT], sandbox, env)
    cut_verify_json = json.loads(cut_verify["stdout"]) if cut_verify["stdout"].strip() else {}
    check("R11_verify_reaudits_lrat_and_open_leaves",
          cut_verify["rc"] == 2
          and cut_verify_json.get("counts") == {"VERIFIED_UNSAT": 1, "OPEN": 3},
          {"rc": cut_verify["rc"], "stdout": cut_verify["stdout"][-400:],
           "note": "exit 2 is the pre-existing OPEN-verification status"})

    # ---- negative controls ------------------------------------------------
    forged = clone_fixture(R11, WORK / ".scratch/runs/R11-forged-cut")
    working = (forged / "working.cnf").read_bytes()
    lines = working.split(b"\n")
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].startswith(b"c") or lines[i].startswith(b"p") or not lines[i].strip():
            continue
        literals = lines[i].split()[:-1]          # drop the terminating 0
        # Replace the last cut by the negation of its first literal: a unit that
        # compile_cas cannot have produced, because the frozen root already
        # satisfies every emitted cut.
        lines[i] = str(-int(literals[0])).encode() + b" 0"
        break
    (forged / "working.cnf").write_bytes(b"\n".join(lines))
    forged_plan = plan_of(forged)
    forged_plan["working_sha256"] = sha256(forged / "working.cnf")
    (forged / "plan.json").write_bytes((json.dumps(forged_plan, sort_keys=True) + "\n").encode())
    forged_run = run([sys.executable, tool, "resume", forged, "--engine", "native",
                      "--conflicts", "2000", "--seconds", "20", "--check-seconds", "60",
                      "--jobs", "1", "--lrat-trim", LRAT], sandbox, env)
    check("forged_cut_in_working_cnf_is_rejected_before_any_leaf",
          forged_run["rc"] == 1 and "not derived from the parent" in forged_run["stderr"]
          and not (forged / "leaves").exists(),
          {"rc": forged_run["rc"], "stderr": forged_run["stderr"][-400:]})

    empty_cas = clone_fixture(R11, WORK / ".scratch/runs/R11-empty-cas")
    (empty_cas / "cas.drat").write_bytes(b"")
    cas_plan = plan_of(empty_cas)
    cas_plan["cas_proof_sha256"] = sha256(empty_cas / "cas.drat")
    (empty_cas / "plan.json").write_bytes((json.dumps(cas_plan, sort_keys=True) + "\n").encode())
    empty_run = run([sys.executable, tool, "resume", empty_cas, "--engine", "native",
                     "--conflicts", "2000", "--seconds", "20", "--check-seconds", "60",
                     "--jobs", "1", "--lrat-trim", LRAT], sandbox, env)
    check("dropped_cas_prefix_is_rejected",
          empty_run["rc"] == 1 and "not derived from the parent" in empty_run["stderr"],
          {"rc": empty_run["rc"], "stderr": empty_run["stderr"][-400:]})

    # corrupt proof with a laundered receipt hash: the checker itself must refuse
    corrupt = WORK / ".scratch/runs/H8-corrupt-lrat"
    refresh(corrupt)
    shutil.copytree(h8, corrupt)
    proof = corrupt / "leaves/r/leaf.lrat"
    blob = bytearray(proof.read_bytes())
    assert blob
    blob[len(blob) // 2] ^= 0xFF
    proof.write_bytes(bytes(blob))
    rec = receipt(corrupt, "r")
    rec["artifact_sha256"] = sha256(proof)
    (corrupt / "leaves/r/receipt.json").write_bytes(
        (json.dumps(rec, sort_keys=True) + "\n").encode())
    corrupt_run = run([sys.executable, tool, "verify", corrupt, "--check-seconds", "60",
                       "--lrat-trim", LRAT], sandbox, env)
    check("corrupted_lrat_with_matching_receipt_hash_is_rejected",
          corrupt_run["rc"] == 1 and "invalid proof at r" in corrupt_run["stderr"],
          {"rc": corrupt_run["rc"], "stderr": corrupt_run["stderr"][-500:]})

    # truncated proof that parses but has no empty clause: drop its last record
    truncated = WORK / ".scratch/runs/H8-truncated-lrat"
    refresh(truncated)
    shutil.copytree(h8, truncated)
    proof = truncated / "leaves/r/leaf.lrat"
    data = proof.read_bytes()

    def scan(buf):
        offsets, pos = [], 0

        def uint(i):
            value = shift = 0
            while True:
                byte = buf[i]
                i += 1
                value |= (byte & 127) << shift
                if byte < 128:
                    return value, i
                shift += 7

        while pos < len(buf):
            offsets.append(pos)
            tag = buf[pos]
            pos += 1
            if tag == 0x64:
                while True:
                    value, pos = uint(pos)
                    if value == 0:
                        break
            else:
                value, pos = uint(pos)          # clause id
                while True:                     # literals
                    value, pos = uint(pos)
                    if value == 0:
                        break
                while True:                     # hints
                    value, pos = uint(pos)
                    if value == 0:
                        break
        return offsets

    offsets = scan(data)
    proof.write_bytes(data[:offsets[-1]])
    rec = receipt(truncated, "r")
    rec["artifact_sha256"] = sha256(proof)
    (truncated / "leaves/r/receipt.json").write_bytes(
        (json.dumps(rec, sort_keys=True) + "\n").encode())
    truncated_run = run([sys.executable, tool, "verify", truncated, "--check-seconds", "60",
                         "--lrat-trim", LRAT], sandbox, env)
    check("truncated_lrat_without_empty_clause_is_rejected",
          truncated_run["rc"] == 1 and "invalid proof at r" in truncated_run["stderr"],
          {"rc": truncated_run["rc"], "stderr": truncated_run["stderr"][-500:],
           "records": len(offsets)})

    # wrong formula: an LRAT written for working+cube cannot be replayed against
    # the cut-free parent, because the ids of the appended cuts are not there.
    leaf_cnf = REPO / "results/wall-cc-35-2026-11-26/certified-leaf-3d443146-r11/leaf.cnf"
    pipeline_lrat = REPO / "tools/lrat_pipeline/.scratch/runs/R11/b.lrat"
    wrong = run([LRAT, leaf_cnf, r11 / "leaves/r11/leaf.lrat"], sandbox, env)
    check("lrat_rejects_the_leaf_proof_against_the_cut_free_parent",
          wrong["rc"] != 20 and "s VERIFIED" not in wrong["stdout"].splitlines(),
          {"rc": wrong["rc"], "stdout": wrong["stdout"][-300:],
           "note": "leaf.cnf is parent+cube (0 cuts); the leaf proof was written for working+cube"})
    right = run([LRAT, leaf_cnf, pipeline_lrat], sandbox, env)
    check("control_the_leaf_formula_pair_still_verifies_for_its_own_proof",
          right["rc"] == 20 and "s VERIFIED" in right["stdout"].splitlines(),
          {"rc": right["rc"], "proof": str(pipeline_lrat),
           "note": "the earlier pipeline's LRAT for parent+cube, unchanged"})

    # adapter-level binding: a different query hash refuses before the checker runs
    import tempfile
    with tempfile.TemporaryDirectory(dir=WORK / ".scratch") as name:
        passed, log = lrat_optin.replay_lrat(h8, Path(name), [], h8 / "leaves/r/leaf.lrat",
                                             LRAT, 60, "0" * 64)
    check("replay_lrat_refuses_a_query_hash_mismatch",
          passed is False and "not the solver's own input" in log, {"log": log[-200:]})

    # a bounded conflict cap is OPEN, never UNSAT
    capped = clone_fixture(H8, WORK / ".scratch/runs/H8-capped")
    cap_run = run([sys.executable, tool, "resume", capped, "--engine", "native",
                   "--proof", "eager", "--conflicts", "50", "--seconds", "10",
                   "--check-seconds", "30", "--lrat-trim", LRAT], sandbox, env)
    cap_summary = json.loads(cap_run["stdout"].strip().splitlines()[-1])
    cap_rec = receipt(capped, "r")
    check("capped_search_stays_open_and_claims_nothing",
          cap_summary["status"] == "OPEN" and cap_rec["status"] == "OPEN"
          and "artifact_sha256" not in cap_rec
          and not (capped / "leaves/r/leaf.lrat").exists(),
          {"summary_status": cap_summary["status"], "receipt_status": cap_rec["status"],
           "entry": cap_run["rc"]})

    # argument-level fail-closed controls
    bad_path = run([sys.executable, tool, "resume", h8, "--engine", "native",
                    "--lrat-trim", MEMBER / "no-such-lrat-trim"], sandbox, env)
    check("missing_checker_fails_before_any_leaf",
          bad_path["rc"] == 1 and "missing executable LRAT checker" in bad_path["stderr"],
          {"rc": bad_path["rc"], "stderr": bad_path["stderr"][-300:]})
    pinned_wrong = run([sys.executable, tool, "resume", h8, "--engine", "native",
                        "--lrat-trim", LRAT, "--lrat-trim-sha256", "0" * 64], sandbox, env)
    check("pinned_checker_hash_mismatch_fails",
          pinned_wrong["rc"] == 1 and "does not match the pinned review hash" in pinned_wrong["stderr"],
          {"rc": pinned_wrong["rc"], "stderr": pinned_wrong["stderr"][-300:]})
    pysat_arm = run([sys.executable, tool, "resume", h8, "--engine", "pysat",
                     "--lrat-trim", LRAT], sandbox, env)
    check("lrat_with_the_pysat_arm_is_refused",
          pysat_arm["rc"] == 1 and "requires --engine native" in pysat_arm["stderr"],
          {"rc": pysat_arm["rc"], "stderr": pysat_arm["stderr"][-300:]})

    # ------------------------------------------------------------- receipts
    receipt_out.update(
        tests=RESULTS,
        passed=sum(1 for r in RESULTS if r["passed"] and not r.get("measurement")),
        failed=[r["test"] for r in RESULTS if not r["passed"]],
        measurements=[r["test"] for r in RESULTS if r.get("measurement")],
        total_wall_s=round(time.monotonic() - started, 1),
        total_cpu_s=round(sum(r["cpu_s"] for r in (lrat_run, drat_run, cut_run)), 3),
        fixtures={"H8": str(H8), "R11": str(R11)},
        pinned=PINNED, solver_sha256=SOLVER_SHA, drat_trim_sha256=DRATTRIM_SHA)
    out = MEMBER / "receipts/optin-tests.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes((json.dumps(receipt_out, indent=1, sort_keys=True) + "\n").encode())
    print(f"\n{receipt_out['passed']} checks passed, {len(receipt_out['failed'])} failed, "
          f"{receipt_out['total_wall_s']} s wall; receipt {out}", flush=True)
    return 0 if not receipt_out["failed"] else 1


if __name__ == "__main__":
    sys.exit(main())
