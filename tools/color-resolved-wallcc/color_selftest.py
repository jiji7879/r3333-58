"""Small executable controls for the isolated K58 color-pivot layer."""
import argparse
import itertools
import json
import os
from pathlib import Path
import subprocess

from pysat.solvers import Minisat22

import color_pivot as cp
from color_pivot import (VARIANTS, build, counter, core_digest, local_formula,
                         local_words)
from problem import digest, json_bytes, lookup


def counter_controls():
    tested = 0
    # Every comparator input pair admits precisely the OR/AND output pair.
    for previous, carry in itertools.product((False, True), repeat=2):
        clauses = [[-1, 3], [-2, 3], [1, 2, -3], [1, -4], [2, -4], [-1, -2, 4]]
        values = {1: previous, 2: carry}
        allowed = []
        for hi, lo in itertools.product((False, True), repeat=2):
            assignment = {**values, 3: hi, 4: lo}
            if all(any(assignment[abs(literal)] == (literal > 0) for literal in clause)
                   for clause in clauses):
                allowed.append((hi, lo))
        assert allowed == [(previous or carry, previous and carry)]
    for n in range(1, 9):
        definitions, outputs, last = counter(list(range(1, n + 1)), n)
        with Minisat22(bootstrap_with=definitions) as solver:
            for bits in itertools.product((False, True), repeat=n):
                assumptions = [i + 1 if bit else -(i + 1) for i, bit in enumerate(bits)]
                assert solver.solve(assumptions=assumptions)
                model = set(solver.get_model())
                expected = sum(bits)
                assert all(((literal in model) == (j < expected))
                           for j, literal in enumerate(outputs))
                tested += 1
    return {"status": "PASS", "comparator_assignments": 4, "network_assignments": tested}


def local_word_controls(artifacts):
    core = artifacts["core"]
    row = lookup(core["row"])
    _, case, _ = cp.binding(row["id"])
    # Check the local (untransported) forms, so every physical pivot color and
    # every above-minimum escape count is covered, not just a minimizing word.
    vertices, palette, matrix, atom, physical, definitions, outputs, last, color_targets = local_formula(case)
    from color_pivot import checked_local_semantics
    words = local_words(case, vertices, palette, matrix)
    escape_targets, count = checked_local_semantics(case, vertices, palette, matrix, atom, outputs, color_targets)
    assert count == len(words) == core["binding"]["local_feasible_words"]
    top = 4 * len(vertices)
    for word in words:
        assignment = {}
        for i, color in enumerate(word):
            for candidate in palette:
                assignment[atom(i, candidate)] = candidate == color
        count = sum(color == case["arm_color"] for color in word)
        for j, literal in enumerate(outputs):
            assignment[literal] = j < count
        for clause in escape_targets + color_targets:
            assert any(assignment[abs(literal)] == (literal > 0) for literal in clause), (word, clause)
    return {"status": "PASS", "row": row["id"], "physical_words": len(words),
            "targets_checked_per_word": len(escape_targets + color_targets),
            "above_minimum_alternative": "T_(m+1) checked true on every above-minimum word"}


def negative_control(artifacts, checker, out):
    # Omit the entire target-derivation block while retaining the miter flags.
    # Individual target/case lines can be outside the checker's final core.
    lines = artifacts["proof"].splitlines(keepends=True)
    assert lines[-1].strip() == b"0"
    _, case, _ = cp.binding(artifacts["core"]["row"])
    physical = local_formula(case)[4]
    flag_count = len(artifacts["core"]["escape_clauses"] + artifacts["core"]["color_clauses"])
    stop = len(lines) - flag_count - 1
    assert stop > len(physical)
    omitted = stop - len(physical)
    del lines[len(physical):stop]
    damaged = b"".join(lines)
    path = out / "tampered-proof.drat"
    query = out / "negative-query.cnf"
    path.write_bytes(damaged)
    query.write_bytes(artifacts["query"])
    run = subprocess.run([checker, query, path, "-I", "-f", "-W", "-U"], capture_output=True)
    log = (run.stdout + run.stderr).decode(errors="replace")
    rejected = "s VERIFIED" not in log.splitlines()
    query.unlink()
    return {"status": "PASS" if rejected else "FAIL", "checker_exit": run.returncode,
            "query_sha256": digest(artifacts["query"]), "tampered_proof_sha256": digest(damaged),
            "omitted_derivation_steps": omitted, "expected_rejection": rejected, "log_tail": log[-1600:]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    checker = args.checker.resolve()
    assert checker.is_file() and os.access(checker, os.X_OK)
    assert not args.out.exists(), "selftest output already exists"
    args.out.mkdir(parents=True)
    report = {"counter": counter_controls(), "benchmarks": []}
    first = None
    for path in sorted((cp.CACHE / "benchmarks").glob("*.batch.json")):
        record = json.loads(path.read_bytes())
        artifacts = build(lookup(record["row"]), "first", checker, 120)
        assert artifacts["core"]["benchmark_exact_match"] is not None
        assert artifacts["check"]["status"] == "PASS_RUP_DERIVATION"
        (args.out / f"{record['name']}-receipt.json").write_bytes(json_bytes(artifacts["core"]))
        report["benchmarks"].append({
            "name": record["name"], "row": record["row"], "status": "PASS",
            "receipt_sha256": core_digest(artifacts),
            "query_sha256": artifacts["core"]["derivation_artifacts"]["query_sha256"],
            "proof_sha256": artifacts["core"]["derivation_artifacts"]["proof_sha256"],
            "formula_sha256": {name: artifacts["core"]["formulas"][name]["sha256"] for name in VARIANTS},
            "native_checker": artifacts["check"]["status"],
            "wall_status": "NOT_SOLVED_BY_THIS_TEST",
        })
        if first is None:
            first = artifacts
    report["local_words"] = local_word_controls(first)
    report["tampering"] = negative_control(first, checker, args.out)
    report["status"] = "PASS" if report["tampering"]["status"] == "PASS" else "FAIL"
    (args.out / "selftest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, sort_keys=True))
    assert report["status"] == "PASS"


if __name__ == "__main__":
    if not __debug__:
        raise RuntimeError("Run without -O")
    main()
