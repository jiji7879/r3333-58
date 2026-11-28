#!/usr/bin/env python3
"""Bounded integration controls for a copied, overlaid k58-massive-solver tree."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROW = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
PARENT = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
CUBE = "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8"
RAW = "1bb7a7823b0ceac16d303de15c204b28b11d4354ec17fcf60dba7678754ff9d2"
RAW_CUBE = "fface1b819e26261736cb516be9063e7be2b1be120253875947a4400d4ac912a"
WORKING = "39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38"
CAS = "dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--baseline-run", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--skip-stock-smoke", action="store_true")
    args = ap.parse_args()
    package, baseline, out = args.package.resolve(), args.baseline_run.resolve(), args.out
    if out.exists():
        raise SystemExit(f"output exists: {out}")
    out.mkdir(parents=True)
    logs = out / "logs"
    logs.mkdir()
    cli = package / "k58-mcf.sh"
    stock_cli = package / "k58.sh"
    checks = []

    def run(name, command, expect=0, needle=None):
        result = subprocess.run(list(map(str, command)), stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, check=False)
        (logs / (name + ".log")).write_bytes(result.stdout)
        if result.returncode != expect:
            raise AssertionError(f"{name}: rc {result.returncode}, expected {expect}")
        text = result.stdout.decode(errors="replace")
        if needle is not None and needle not in text:
            raise AssertionError(f"{name}: missing {needle!r}")
        checks.append({"name": name, "returncode": result.returncode, "log": f"logs/{name}.log"})
        return text

    stock_hash_before = sha(stock_cli)
    run("help", [cli, "--help"], needle="Never a stock finalise path")
    run("prepare-missing-output", [cli, "prepare", "--baseline-run", baseline], expect=2,
        needle="prepare requires --out")
    dry_out = out / "dry-run-must-not-exist"
    common = [cli, "prepare", "--baseline-run", baseline,
              "--expect-parent-sha256", PARENT, "--expect-working-sha256", WORKING,
              "--expect-cas-sha256", CAS, "--expect-parent-cube-sha256", CUBE,
              "--expect-augmented-parent-sha256", RAW, "--expect-augmented-cube-sha256", RAW_CUBE,
              "--expect-edges", "45"]
    text = run("prepare-dry-run", [*common, "--out", dry_out, "--dry-run"])
    if dry_out.exists():
        raise AssertionError("prepare dry-run wrote files")
    # The last JSON object is the complete dry-run receipt.
    prepared_dry = json.loads(text)
    if prepared_dry["ordinary_parent_cube_sha256"] != CUBE:
        raise AssertionError("wrong baseline query")
    normal = prepared_dry["normal_form"]
    assert (normal["configurable_edges"], normal["fresh_witnesses"], normal["added_clauses"]) == (45, 2520, 7605)
    assert normal["augmented_parent_sha256"] == RAW
    assert normal["augmented_cube_sha256"] == RAW_CUBE

    prepared = out / "prepared"
    run("prepare", [*common, "--out", prepared])
    receipt = json.loads((prepared / "receipt.json").read_text())
    for name, record in receipt["files"].items():
        assert sha(prepared / name) == record["sha256"], name
    run_dry = out / "run-dry.json"
    text = run("run-dry-run", [cli, "run", "--prepared", prepared, "--conflicts", "1000000", "--dry-run"])
    run_plan = json.loads(text)
    assert run_plan["balanced_conflict_budget"]
    assert [job["conflicts"] for job in run_plan["jobs"]] == [1000000, 1000000]
    assert [job["query_sha256"] for job in run_plan["jobs"]] == [CUBE, RAW_CUBE]
    assert all(job["wall_timeout_seconds"] is None for job in run_plan["jobs"])
    run_dry.write_text(text)

    # Tiny interface cap only: this is not a performance measurement.
    live = out / "open-interface"
    run("open-interface", [cli, "run", "--prepared", prepared, "--conflicts", "1", "--out", live])
    open_summary = json.loads((live / "summary.json").read_text())
    assert open_summary["status_counts"] == {"OPEN": 2}
    for result in live.glob("*/result.json"):
        record = json.loads(result.read_text())
        assert record["proof_artifact"] is None
        assert not list(result.parent.glob("*.drat"))

    run("toy-proof", [cli, "toy-proof", "--out", out / "toy-proof"])
    toy = json.loads((out / "toy-proof/receipt.json").read_text())
    assert toy["status"] == "PASS" and toy["strict_accepted"]
    assert toy["plan_cas_strict_accepted"] and toy["full_byte_read"]
    assert toy["final_empty_clause_required"] and toy["deleted_final_empty_proof_rejected"]
    assert toy["malformed_rejected"]

    # Generator-free schema oracle: independently recalculate every long clause
    # and Tseitin allocation instead of accepting the generator's receipt.
    run("independent-arm3-schema", [sys.executable, Path(__file__).parent / "audit_queries.py",
        "--parent", prepared / "baseline/parent.cnf", "--kind", "arm3",
        "--query", prepared / "queries/raw-arm-cube.cnf",
        "--report", out / "independent-arm3-schema.json"], needle='"result": "PASS"')

    env = dict(os.environ, PYTHONPATH=str(package / "mcf"))
    primitive = subprocess.run([sys.executable, str(package / "mcf/test_controls.py")],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env, check=False)
    (logs / "primitives.log").write_bytes(primitive.stdout)
    assert primitive.returncode == 0 and b"Ran 10 tests" in primitive.stdout and b"OK" in primitive.stdout
    checks.append({"name": "primitives", "returncode": 0, "tests": 10,
                   "semantic_normalisation_runs": 807936})

    bad_baseline = out / "bad-baseline"
    bad_baseline.mkdir()
    for name in ("plan.json", "parent.cnf", "working.cnf", "cas.drat"):
        shutil.copyfile(baseline / name, bad_baseline / name)
    raw = (bad_baseline / "parent.cnf").read_bytes()
    header, body = raw.split(b"\n", 1)
    lines = body.splitlines(keepends=True)
    for index, line in enumerate(lines):
        fields = line.split()
        if fields:
            fields[0] = str(-int(fields[0])).encode()
            lines[index] = b" ".join(fields) + b"\n"
            break
    (bad_baseline / "parent.cnf").write_bytes(header + b"\n" + b"".join(lines))
    rejected = out / "wrong-parent-must-not-exist"
    run("wrong-parent", [cli, "prepare", "--baseline-run", bad_baseline,
                         "--out", rejected, "--dry-run"], expect=2,
        needle="baseline parent hash differs")
    assert not rejected.exists() and not rejected.with_name(rejected.name + ".building").exists()

    # First accepted rule is edge (47,52); physical colour-0 literal is 6409.
    bad_cube = "6409"
    run("wrong-root-sign", [cli, "prepare", "--baseline-run", baseline,
                            "--cube", "1413,1014", "--dry-run"], expect=2,
        needle="retained cube must be -1413,+1014")
    run("wrong-arm", [cli, "prepare", "--baseline-run", baseline,
                      "--arms", "2", "--dry-run"], expect=2,
        needle="exactly the checked arm 3, colour 0")
    run("wrong-colour", [cli, "prepare", "--baseline-run", baseline,
                         "--colour", "3", "--dry-run"], expect=2,
        needle="exactly the checked arm 3, colour 0")
    run("cube-disjoint", [cli, "prepare", "--baseline-run", baseline,
                          "--cube", bad_cube, "--out", out / "bad-cube-out", "--dry-run"],
        expect=2, needle="retained cube must be -1413,+1014")
    assert not (out / "bad-cube-out").exists()
    run("contradictory-cube", [cli, "prepare", "--baseline-run", baseline,
                               "--cube=-1413,1413", "--dry-run"], expect=2,
        needle="complementary literals")
    run("wrong-augmented-pin", [*common, "--expect-augmented-cube-sha256", "0" * 64, "--dry-run"],
        expect=2, needle="augmented parent+cube SHA does not match")
    run("wrong-expected-baseline", [*common, "--expect-parent-cube-sha256", "0" * 64, "--dry-run"],
        expect=2, needle="ordinary parent+cube SHA does not match")

    tampered = out / "tampered-prepared"
    shutil.copytree(prepared, tampered)
    target = tampered / "queries/raw-arm-cube.cnf"
    raw = target.read_bytes()
    header, body = raw.split(b"\n", 1)
    lines = body.splitlines(keepends=True)
    fields = lines[0].split()
    fields[0] = str(-int(fields[0])).encode()
    lines[0] = b" ".join(fields) + b"\n"
    target.write_bytes(header + b"\n" + b"".join(lines))
    run("tampered-query-no-fallback", [cli, "run", "--prepared", tampered,
                                       "--conflicts", "1", "--dry-run"], expect=2,
        needle="prepared file hash/size mismatch")

    def mutate_long_clause(tree, rehash_normal_form):
        """Duplicate a long-MCF literal, preserving clause counts and cube bytes."""
        receipt_path = tree / "receipt.json"
        normal_path = tree / "normal-form.json"
        receipt = json.loads(receipt_path.read_text())
        normal = json.loads(normal_path.read_text())
        raw_parent = tree / "queries/raw-arm-parent.cnf"
        header, body = raw_parent.read_bytes().split(b"\n", 1)
        lines = body.splitlines(keepends=True)
        # Parent 184335 clauses; each edge has 56 Tseitin triples then its long clause.
        index = 184335 + 168
        fields = lines[index].split()
        assert len(fields) == 58 and fields[-1] == b"0" and fields[0] == b"6409"
        fields[-2] = fields[-3]
        changed = b" ".join(fields) + b"\n"
        assert len(changed) == len(lines[index]) and changed != lines[index]
        lines[index] = changed
        raw_bytes = header + b"\n" + b"".join(lines)
        raw_parent.write_bytes(raw_bytes)
        cube_header = header.replace(b"22053 191940", b"22053 191942")
        assert cube_header != header
        cube_bytes = cube_header + b"\n" + b"".join(lines) + b"-1413 0\n1014 0\n"
        (tree / "queries/raw-arm-cube.cnf").write_bytes(cube_bytes)
        for name, data in (("queries/raw-arm-parent.cnf", raw_bytes),
                           ("queries/raw-arm-cube.cnf", cube_bytes)):
            receipt["files"][name]["sha256"] = sha(tree / name)
        if rehash_normal_form:
            normal["augmented_parent_sha256"] = sha(raw_parent)
            normal["augmented_cube_sha256"] = sha(tree / "queries/raw-arm-cube.cnf")
            receipt["normal_form"]["augmented_parent_sha256"] = normal["augmented_parent_sha256"]
            receipt["normal_form"]["augmented_cube_sha256"] = normal["augmented_cube_sha256"]
            payload = json.dumps(normal, sort_keys=True).encode()
            receipt["normal_form_sha256_payload"] = hashlib.sha256(payload).hexdigest()
        normal_path.write_text(json.dumps(normal, indent=2, sort_keys=True) + "\n")
        receipt_path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")

    rehashed = out / "consistently-rehashed-prepared"
    shutil.copytree(prepared, rehashed)
    mutate_long_clause(rehashed, True)
    run("rehashed-semantic-tamper-rejected", [cli, "run", "--prepared", rehashed,
        "--conflicts", "1", "--dry-run"], expect=2,
        needle="normal-form rules/counts differ from pristine regenerated gadgets")

    query_only = out / "query-only-prepared"
    shutil.copytree(prepared, query_only)
    mutate_long_clause(query_only, False)
    run("query-only-rehash-rejected", [cli, "run", "--prepared", query_only,
        "--conflicts", "1", "--dry-run"], expect=2,
        needle="prepared artifact differs from pristine regeneration")

    if not args.skip_stock_smoke:
        run("stock-wallcc-smoke", [stock_cli, "wallcc-smoke"], needle="20/20 checks passed")
    run("stock-help", [stock_cli, "--help"], expect=2)
    stock_help = (logs / "stock-help.log").read_text().lower()
    assert "mcf" not in stock_help and "maximal" not in stock_help
    assert sha(stock_cli) == stock_hash_before
    checks.append({"name": "stock-unchanged-and-no-mcf-fallback", "k58_sha256": stock_hash_before})

    summary = {
        "status": "PASS", "checks": checks,
        "exact_hashes": {"parent": PARENT, "parent_cube": CUBE,
                         "raw_arm_parent": RAW, "raw_arm_cube": RAW_CUBE,
                         "working": WORKING, "cas": CAS},
        "live_solver_scope": "one-conflict OPEN interface only; no performance result, UNSAT result, or physical closure",
        "proof_scope": "three-pigeon/two-hole toy plus derived-cut CAS toy only; target remains OPEN",
        "stock_finalise_admission": False, "physical_closure": False,
    }
    (out / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
