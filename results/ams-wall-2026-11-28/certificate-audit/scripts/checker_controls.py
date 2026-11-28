#!/usr/bin/env python3
"""Positive/negative controls for strict certificate acceptance."""
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runner", ROOT / "scripts/run_frontier_kissat.py")
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


def main():
    c = ROOT / "inputs/controls"
    out = ROOT / "checks/controls"
    out.mkdir(parents=True, exist_ok=True)
    posq, negq, proof = c / "k6-query.cnf", c / "k5-query.cnf", c / "k6-proof.drat"
    checks = []

    def check(label, query, proof_path):
        for name, binary in (("primary", ROOT / "bin/drat-trim-own"),
                             ("second", ROOT / "bin/drat-trim-massive")):
            result = r.strict_check(binary, query, proof_path,
                                    out / f"{label}-{name}.log", 30)
            result.update(label=label, query_sha256=r.sha(query),
                          proof_sha256=r.sha(proof_path), proof_file_bytes=proof_path.stat().st_size)
            checks.append(result)
            print(label, name, result["passed"], result["returncode"],
                  result["exact_verified_lines"], result["proof_read_byte_counts"])

    check("positive", posq, proof)
    check("wrong-query", negq, proof)
    truncated = out / "k6-truncated.drat"
    truncated.write_bytes(proof.read_bytes()[:-1])
    check("truncated", posq, truncated)
    normalized = out / "k6-renormalized.drat"
    metadata = r.normalize_additions([proof], normalized)
    assert normalized.read_bytes() == proof.read_bytes()
    try:
        r.normalize_additions([ROOT / "inputs/cas.drat"],
                              out / "cas-invalid-as-refutation.drat")
    except ValueError as exc:
        derivation_rejected = str(exc)
    else:
        raise AssertionError("CAS derivation was incorrectly accepted as a refutation")
    report = {
        "positive_passes": all(x["passed"] for x in checks if x["label"] == "positive"),
        "negative_controls_reject": all(not x["passed"] for x in checks if x["label"] != "positive"),
        "truncation_false_verified_status_rejected": all(
            not x["passed"] and x["returncode"] == 0 and x["exact_verified_lines"] == 1
            and not x["strict_whole_proof_bytes"]
            for x in checks if x["label"] == "truncated"),
        "renormalization_byte_identical": True,
        "renormalization": metadata,
        "cas_derivation_as_refutation_rejected": derivation_rejected,
        "query_sha256": {"k6": r.sha(posq), "k5": r.sha(negq)},
        "proof_sha256": r.sha(proof),
        "results": checks,
    }
    (out / "summary.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    assert report["positive_passes"] and report["negative_controls_reject"]
    assert report["truncation_false_verified_status_rejected"]
    print("PASS controls; CAS-only rejection:", derivation_rejected)


if __name__ == "__main__":
    main()
