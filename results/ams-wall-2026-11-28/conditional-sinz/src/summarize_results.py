#!/usr/bin/env python3
"""Independently recompute A/B ratios and determinism controls from raw receipts."""
import hashlib
import json
import math
from pathlib import Path

M = Path(__file__).resolve().parent.parent
R = M / "results"
EXPECTED = {
    "parent": "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae",
    "naive": "bac8c106d698a0734ca8dbec535b0ccc212d8329f5cd79b49e25f6071420d05b",
    "naive-split": "02fc6b42b7edb93aa7647b5bbcc384a1a1328b64e6d1a1afba96657fdbe00f5d",
    "boundary": "fa8be04c4d10d38f803a0db34109732ee551ea1c85d4e834d369d5a73bd25cdc",
}
KEYS = ("conflicts", "decisions", "propagations", "restarts")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def path_for(policy):
    return M / "inputs" / "parent.cnf" if policy == "parent" else R / f"wall-two5-{policy}.cnf"


def ratio(a, b):
    return a / b


def comparison(records, seed, a, b):
    """Return b/a for metrics at one seed; a and b are policy names."""
    by = {r["policy"]: r for r in records if r["seed"] == seed}
    x, y = by[a], by[b]
    for r in (x, y):
        assert r["status"] == "OPEN" and not r["proof_logging"]
        assert r["query_sha256"] == EXPECTED[r["policy"]] == sha(path_for(r["policy"]))
    out = {"control": a, "variant": b, "seed": seed,
           "status": {a: x["status"], b: y["status"]},
           "search_cpu_seconds": {a: x["search_process_cpu_seconds"], b: y["search_process_cpu_seconds"]},
           "stats": {a: x["stats"], b: y["stats"]},
           "cpu_ratio_variant_over_control": ratio(y["search_process_cpu_seconds"], x["search_process_cpu_seconds"])}
    out["normalized_cpu_per_1e6_conflicts"] = {
        name: r["search_process_cpu_seconds"] * 1000000 / r["stats"]["conflicts"]
        for name, r in ((a, x), (b, y))}
    out["normalized_cpu_ratio"] = (out["normalized_cpu_per_1e6_conflicts"][b] /
                                     out["normalized_cpu_per_1e6_conflicts"][a])
    out["stat_ratios_variant_over_control"] = {key: ratio(y["stats"][key], x["stats"][key]) for key in KEYS}
    return out


def main():
    s1 = json.loads((R / "benchmark-1m" / "summary.json").read_text())
    s2 = json.loads((R / "benchmark-order-1m" / "summary.json").read_text())
    assert len(s1) == len(s2) == 6
    for records in (s1, s2):
        assert len({r["sequence"] for r in records}) == 6
        for r in records:
            assert r["returncode"] == 0 and r["status"] == "OPEN"
            assert r["conflict_budget"] == 1000000
            assert 1000000 <= r["stats"]["conflicts"] <= 1000005
            assert not r["proof_logging"]
            assert r["query_sha256"] == EXPECTED[r["policy"]] == sha(path_for(r["policy"]))
    stage1 = {"boundary_vs_naive": [comparison(s1, seed, "naive", "boundary") for seed in (0, 1)],
              "boundary_vs_parent_context": [comparison(s1, seed, "parent", "boundary") for seed in (0, 1)],
              "naive_vs_parent_context": [comparison(s1, seed, "parent", "naive") for seed in (0, 1)]}
    stage2 = {"guard_only_boundary_vs_naive_split": [comparison(s2, seed, "naive-split", "boundary") for seed in (0, 1)],
              "order_only_naive_vs_naive_split": [comparison(s2, seed, "naive-split", "naive") for seed in (0, 1)]}
    for pairs in list(stage1.values()) + list(stage2.values()):
        for x in pairs:
            x["cpu_ratio_percent_change"] = 100 * (x["cpu_ratio_variant_over_control"] - 1)
    determinism = {}
    for seed in (0, 1):
        a1 = {r["policy"]: r for r in s1 if r["seed"] == seed}
        a2 = {r["policy"]: r for r in s2 if r["seed"] == seed}
        determinism[str(seed)] = {
            "naive_repeated_operation_counts_identical": all(a1["naive"]["stats"][k] == a2["naive"]["stats"][k] for k in KEYS),
            "boundary_repeated_operation_counts_identical": all(a1["boundary"]["stats"][k] == a2["boundary"]["stats"][k] for k in KEYS),
            "naive_vs_naive_split_operation_counts_identical": all(a2["naive"]["stats"][k] == a2["naive-split"]["stats"][k] for k in KEYS),
        }
        assert all(determinism[str(seed)].values())
    guard_ratios = [x["cpu_ratio_variant_over_control"] for x in stage2["guard_only_boundary_vs_naive_split"]]
    guard_normalized = [x["normalized_cpu_ratio"] for x in stage2["guard_only_boundary_vs_naive_split"]]
    result = {
        "row": "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06",
        "parent_sha256": EXPECTED["parent"],
        "query_sha256": EXPECTED,
        "working_sha256_unused_in_this_encoding_test": "39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38",
        "rUP_CAS_prefix_sha256_unused_no_proof_generated": "dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3",
        "number_of_solver_calls": 12,
        "all_statuses": "OPEN",
        "conflict_cap_overshoot_explanation": "CaDiCaL195 reports 1000000, 1000001 or 1000005 after the same requested 1000000-conflict budget; ratios use requested-cap pairing and normalized values are also recorded.",
        "stage1": stage1,
        "stage2": stage2,
        "guard_only_geometric_mean_cpu_ratio": math.prod(guard_ratios) ** 0.5,
        "guard_only_geometric_mean_normalized_cpu_ratio": math.prod(guard_normalized) ** 0.5,
        "favourable_bounded_throughput_preregistered": all(x < 1 for x in guard_ratios) and math.prod(guard_ratios) ** 0.5 <= 0.95,
        "determinism_controls": determinism,
        "scope": "CNF performance only. No leaf/parent proof was produced or checked. No physical colouring, semantic row, profile, or Ramsey conclusion.",
        "negative_conclusion_scope": "At two seeds and one million requested conflicts on this exact parent, removing recurrence guards reduced decisions but increased CPU in both controlled pairs and did not produce a verdict. This is bounded evidence against unconditional recurrence activation here, not a universal theorem or a standalone timeout claim.",
    }
    assert not result["favourable_bounded_throughput_preregistered"]
    (R / "analysis.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    checked1 = {"note": "Requested-cap pairing; internal summary's exact-conflict equality test was too strict for CaDiCaL's 1/5-conflict overshoot.",
                "boundary_over_naive_cpu_ratio_by_seed": {str(seed): stage1["boundary_vs_naive"][seed]["cpu_ratio_variant_over_control"] for seed in (0, 1)},
                "all_open": True, "superseded_by": "results/analysis.json"}
    (R / "benchmark-1m" / "analysis-checked.json").write_text(json.dumps(checked1, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"guard_only_cpu_ratios": guard_ratios,
                      "guard_only_normalized_cpu_ratios": guard_normalized,
                      "guard_only_geomean": result["guard_only_geometric_mean_cpu_ratio"],
                      "determinism_controls": determinism,
                      "all_statuses": "OPEN"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
