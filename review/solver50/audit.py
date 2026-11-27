#!/usr/bin/env python3
"""Independent, read-only receipt audit for the K58 150k representative file.

This script does not invoke a SAT solver, regenerate a formula, or check a proof.
It checks tabular identity, consolidated-vs-block receipts, overlap, conflicts,
and the existing 3-second receipts.  Its output is data evidence, not a local
proof audit or a whole-row verdict.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
B = HERE / "bundle" / "K58_wall_50k"
R50 = B / "round50"
OUT = B / "results"


def rows(path: Path):
    with gzip.open(path, "rt", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def raw_gzip(path: Path) -> bytes:
    with gzip.open(path, "rb") as f:
        return f.read()


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def q(values, p):
    """Nearest-rank quantile, with the exact convention recorded in output."""
    if not values:
        return None
    a = sorted(values)
    return a[max(0, math.ceil(p * len(a)) - 1)]


def dist(values):
    return {
        "n": len(values),
        "sum": sum(values),
        "min": min(values),
        "median": statistics.median(values),
        "p95": q(values, 0.95),
        "max": max(values),
        "mean": statistics.fmean(values),
    }


def identity(r):
    return (r["row_id"], r["w"], r["z"])


def normalized_receipt(r):
    z = dict(r)
    for k in ("rank", "block", "cap", "conflicts"):
        z[k] = int(z[k])
    return z


def main():
    report = {"scope": "receipts only; no proof replay and no new solving"}
    reps_path = HERE / "representatives.tsv.gz"
    ledger_path = R50 / "campaign-ledger.tsv.gz"
    reps_bytes = raw_gzip(reps_path)
    ledger_bytes = raw_gzip(ledger_path)
    assert reps_bytes == ledger_bytes
    report["input"] = {
        "rows": 150000,
        "decompressed_sha256": sha(reps_bytes),
        "decompressed_bytes": len(reps_bytes),
        "byte_identical_to_campaign_ledger": True,
    }
    R = rows(reps_path)
    assert len(R) == 150000
    by_conv = {c: [r for r in R if r["convention"] == c] for c in ("sorted", "preferred", "round50")}
    assert sum(map(len, by_conv.values())) == len(R)
    assert len({(r["convention"], *identity(r)) for r in R}) == len(R)
    for c, rs in by_conv.items():
        assert [int(r["rank"]) for r in rs] == list(range(50000))
        assert {r["cap"] for r in rs} == {"128"}

    report["cohorts"] = {}
    for c, rs in by_conv.items():
        cf = [int(r["conflicts"]) for r in rs]
        status = Counter(r["cadical"] for r in rs)
        arm = Counter(r["sorted_arm"] for r in rs)
        item = {
            "jobs": len(rs),
            "distinct_rows": len({r["row_id"] for r in rs}),
            "arm_sizes": dict(sorted(Counter(int(r["arm"]) for r in rs).items())),
            "cadical_status": dict(sorted(status.items())),
            "sorted_arm": dict(sorted(arm.items())),
            "conflicts": dist(cf),
            "conflicts_equal_128": sum(x == 128 for x in cf),
            "conflicts_above_128": sum(x > 128 for x in cf),
            "conflicts_below_128": sum(x < 128 for x in cf),
        }
        if c != "sorted":
            affected = sum(r["joining_colors_after_proofs"] != r["joining_colors_triangle"] for r in rs)
            forced = sum(len(r["joining_colors_after_proofs"]) == 1 and len(r["joining_colors_triangle"]) > 1 for r in rs)
            excluded = sum(len(r["joining_colors_triangle"]) - len(r["joining_colors_after_proofs"]) for r in rs)
            assert all(set(r["joining_colors_after_proofs"]) <= set(r["joining_colors_triangle"]) for r in rs)
            item["joining"] = {"affected": affected, "newly_forced": forced, "color_children_excluded": excluded}
        report["cohorts"][c] = item

    s = by_conv["sorted"]
    assert sum(r["cadical"] != "OPEN" for r in s) == 12835
    assert sum(r["sorted_arm"] == "EXCLUDED" for r in s) == 17424
    assert all(r["sorted_arm"] == "EXCLUDED" for r in s if r["cadical"] != "OPEN")
    sorted_strata = {
        "solver_false_and_local_excluded": [r for r in s if r["cadical"] == "UNSAT_SORTED_ARM"],
        "cap_open_but_local_excluded": [r for r in s if r["cadical"] == "OPEN" and r["sorted_arm"] == "EXCLUDED"],
        "cap_open_and_arm_witness": [r for r in s if r["cadical"] == "OPEN" and r["sorted_arm"] == "ARM_WITNESS"],
    }
    report["sorted_partition"] = {
        "counts": {k: len(v) for k, v in sorted_strata.items()},
        "conflicts": {k: dist([int(r["conflicts"]) for r in v]) for k, v in sorted_strata.items()},
    }

    sets = {c: {identity(r) for r in rs} for c, rs in by_conv.items()}
    overlap = {}
    for a, b in (("sorted", "preferred"), ("sorted", "round50"), ("preferred", "round50")):
        overlap[f"{a}__{b}"] = len(sets[a] & sets[b])
    T = rows(OUT / "trials.tsv.gz")
    assert len(T) == 40000
    assert len({identity(r) for r in T}) == 40000
    old = {identity(r) for r in T}
    for c in sets:
        overlap[f"{c}__prior_40000"] = len(sets[c] & old)
    report["raw_identity_overlaps"] = overlap
    assert overlap["preferred__round50"] == 92
    assert overlap["sorted__round50"] == 49
    assert overlap["round50__prior_40000"] == 35
    assert overlap["sorted__preferred"] == 0
    assert overlap["sorted__prior_40000"] == 0
    assert overlap["preferred__prior_40000"] == 0

    waves = {}
    for w in "ABCD":
        rs = [r for r in T if r["wave"] == w]
        assert len(rs) == 10000
        waves[w] = {
            "probe_raw": dict(sorted(Counter(r["probe_raw"] for r in rs).items())),
            "probe_sorted": dict(sorted(Counter(r["probe_sorted"] for r in rs).items())),
            "probe_preferred": dict(sorted(Counter(r["probe_preferred"] for r in rs).items())),
            "possible_two_smallest": dict(sorted(Counter(r["possible_two_smallest"] for r in rs).items())),
            "preferred_label": dict(sorted(Counter(r["preferred_label"] for r in rs).items())),
            "ordering_stage": dict(sorted(Counter(r["ordering_stage"] for r in rs).items())),
        }
    report["prior_40000"] = waves
    report["ordered_rates"] = {
        "prior_C_10000": {"jobs": 10000, "solver_and_local_closed": 2418, "solver_rate": 0.2418, "exact_arm_excluded": 3359, "exact_arm_rate": 0.3359},
        "fresh_F_50000": {"jobs": 50000, "solver_and_local_closed": 12835, "solver_rate": 0.2567, "exact_arm_excluded": 17424, "exact_arm_rate": 0.34848},
        "solver_rate_difference_F_minus_C_percentage_points": 1.49,
        "exact_arm_rate_difference_F_minus_C_percentage_points": 1.258,
        "preferred_E_50000_solver_closed": 0,
        "new_G_50000_plain_solver_closed": 0,
        "new_G_50000_edge_solver_closed": 0,
        "inference_scope": "descriptive rates for these naming rules and deterministic samples only",
    }

    # Source-order and consolidated-receipt identity checks.
    specs = {
        "sorted": ("F", OUT / "round50-sorted-sample.tsv.gz", OUT / "round50-cheap-sorted.tsv.gz", OUT / "round50-cheap-sorted.json", OUT / "round50-cheap-sorted-blocks"),
        "preferred": ("E", OUT / "round50-sample.tsv.gz", OUT / "round50-cheap.tsv.gz", OUT / "round50-cheap.json", OUT / "round50-cheap-blocks"),
        "round50": ("G", OUT / "round50-new-sample.tsv.gz", OUT / "round50-cheap-new.tsv.gz", OUT / "round50-cheap-new.json", OUT / "round50-cheap-new-blocks"),
        "round50_with_cuts": ("G", OUT / "round50-new-sample.tsv.gz", OUT / "round50-cheap-new-edge.tsv.gz", OUT / "round50-cheap-new-edge.json", OUT / "round50-cheap-new-edge-blocks"),
    }
    consolidated = {}
    report["receipt_checks"] = {}
    for name, (wave, source_path, cheap_path, json_path, blocks_path) in specs.items():
        source = rows(source_path)
        cheap = rows(cheap_path)
        meta = json.loads(json_path.read_text())
        assert len(source) == len(cheap) == meta["records"] == 50000
        assert [int(r["rank"]) for r in source] == list(range(50000))
        assert [int(r["rank"]) for r in cheap] == list(range(50000))
        for a, b in zip(source, cheap, strict=True):
            assert a["wave"] == b["wave"] == wave
            assert identity(a) == identity(b)
            assert int(a["rank"]) == int(b["rank"])
        block_records = {}
        block_seconds = {}
        block_sizes = {}
        files = list(blocks_path.glob("*.json.gz"))
        for p in files:
            z = json.loads(gzip.decompress(p.read_bytes()))
            sec = float(z["seconds"])
            brs = z["records"]
            assert brs
            bids = {int(r["block"]) for r in brs}
            assert len(bids) == 1
            bid = bids.pop()
            assert bid not in block_records
            block_records[bid] = brs
            block_seconds[bid] = sec
            block_sizes[bid] = len(brs)
        assert len(block_records) == meta["blocks"] == len(files)
        assert set(block_seconds) == set(range(meta["blocks"]))
        for bid, sec in block_seconds.items():
            assert abs(sec - float(meta["seconds_by_block"][str(bid)])) < 1e-9
        flattened = [r for bid in sorted(block_records) for r in block_records[bid]]
        assert len(flattened) == 50000
        by_rank = {int(r["rank"]): r for r in flattened}
        assert len(by_rank) == 50000
        for r in cheap:
            assert normalized_receipt(r) == normalized_receipt(by_rank[int(r["rank"])])
        assert sum(int(r["conflicts"]) for r in cheap) == meta["conflicts"]
        assert dict(Counter(r["status"] for r in cheap)) == dict(meta["verdicts"])
        consolidated[name] = cheap
        secs = list(block_seconds.values())
        report["receipt_checks"][name] = {
            "source_and_consolidated_identity": "50,000/50,000 exact",
            "block_records_matching_consolidated": "50,000/50,000 exact",
            "blocks": len(files),
            "workers": meta["workers"],
            "run_wall_seconds": meta["run_seconds"],
            "sum_block_seconds": sum(secs),
            "block_seconds": dist(secs),
            "mean_block_ms_per_job_including_init": 1000 * sum(secs) / 50000,
            "block_size_min_max": [min(block_sizes.values()), max(block_sizes.values())],
            "conflicts": meta["conflicts"],
        }
    for c in ("sorted", "preferred", "round50"):
        for a, b in zip(by_conv[c], consolidated[c], strict=True):
            assert int(a["rank"]) == int(b["rank"])
            assert identity(a) == identity(b)
            assert a["cadical"] == b["status"]
            assert int(a["conflicts"]) == int(b["conflicts"])
    for a, b in zip(by_conv["round50"], consolidated["round50_with_cuts"], strict=True):
        assert a["cadical_with_cuts"] == b["status"]
        assert int(a["conflicts_with_cuts"]) == int(b["conflicts"])

    plain = consolidated["round50"]
    cuts = consolidated["round50_with_cuts"]
    deltas = []
    affected_deltas = []
    assumption_hash_changed = 0
    affected_hash_changed = 0
    for a, b, l in zip(plain, cuts, by_conv["round50"], strict=True):
        assert (a["wave"], a["rank"], *identity(a)) == (b["wave"], b["rank"], *identity(b))
        assert a["group"] == b["group"] and a["block"] == b["block"]
        d = int(b["conflicts"]) - int(a["conflicts"])
        deltas.append(d)
        affected = l["joining_colors_after_proofs"] != l["joining_colors_triangle"]
        if affected:
            affected_deltas.append(d)
        if a["assumptions_sha256"] != b["assumptions_sha256"]:
            assumption_hash_changed += 1
            if affected:
                affected_hash_changed += 1
    plain_meta = json.loads((OUT / "round50-cheap-new.json").read_text())
    cuts_meta = json.loads((OUT / "round50-cheap-new-edge.json").read_text())
    block_deltas = [float(cuts_meta["seconds_by_block"][str(i)]) - float(plain_meta["seconds_by_block"][str(i)]) for i in range(plain_meta["blocks"])]
    report["new_plain_vs_edge"] = {
        "same_jobs_order_group_block": "50,000/50,000 exact",
        "conflict_delta_cuts_minus_plain": dist(deltas),
        "delta_negative_zero_positive": [sum(x < 0 for x in deltas), sum(x == 0 for x in deltas), sum(x > 0 for x in deltas)],
        "conflict_delta_on_joining_affected": dist(affected_deltas),
        "assumption_hash_changed_jobs": assumption_hash_changed,
        "assumption_hash_changed_among_affected": affected_hash_changed,
        "plain_status": dict(Counter(r["status"] for r in plain)),
        "cuts_status": dict(Counter(r["status"] for r in cuts)),
        "paired_block_seconds_delta_cuts_minus_plain": dist(block_deltas),
        "paired_block_seconds_delta_negative_zero_positive": [sum(x < 0 for x in block_deltas), sum(x == 0 for x in block_deltas), sum(x > 0 for x in block_deltas)],
        "wall_seconds_delta_cuts_minus_plain": cuts_meta["run_seconds"] - plain_meta["run_seconds"],
        "runtime_comparison_valid": False,
        "runtime_reason": "4 workers versus 5 and different concurrent verification load; block timings are not per-call timers",
    }

    # Earlier solver receipts, including the same-C-job raw/sorted control.
    prior_specs = {
        "raw_A_B": (set("AB"), "raw-samples.tsv.gz", "cheap-raw.tsv.gz", "cheap-raw.json", "cheap-raw-blocks"),
        "raw_C_control": ({"C"}, "survivor-sample.tsv.gz", "cheap-C-control.tsv.gz", "cheap-C-control.json", "cheap-C-control-blocks"),
        "sorted_C": ({"C"}, "survivor-sample.tsv.gz", "cheap-sorted.tsv.gz", "cheap-sorted.json", "cheap-sorted-blocks"),
        "preferred_D": ({"D"}, "preferred-sample.tsv.gz", "cheap-preferred.tsv.gz", "cheap-preferred.json", "cheap-preferred-blocks"),
    }
    report["prior_receipt_checks"] = {}
    prior_consolidated = {}
    for name, (wave_set, source_name, cheap_name, json_name, blocks_name) in prior_specs.items():
        source = rows(OUT / source_name)
        assert {r["wave"] for r in source} == wave_set
        cheap = rows(OUT / cheap_name)
        meta = json.loads((OUT / json_name).read_text())
        assert len(cheap) == len(source) == meta["records"]
        assert {(r["wave"], int(r["rank"])) for r in cheap} == {(r["wave"], int(r["rank"])) for r in source}
        src = {(r["wave"], int(r["rank"])): r for r in source}
        trial_src = {(r["wave"], int(r["rank"])): r for r in T if r["wave"] in wave_set}
        assert src.keys() == trial_src.keys()
        for k in src:
            assert identity(src[k]) == identity(trial_src[k])
        for r in cheap:
            a = src[(r["wave"], int(r["rank"]))]
            assert r["wave"] == a["wave"] and identity(r) == identity(a)
        flattened = []
        files = list((OUT / blocks_name).glob("*.json.gz"))
        block_seconds = {}
        for p in files:
            z = json.loads(gzip.decompress(p.read_bytes()))
            brs = z["records"]
            assert brs
            bids = {int(r["block"]) for r in brs}
            assert len(bids) == 1
            bid = bids.pop()
            assert bid not in block_seconds
            block_seconds[bid] = float(z["seconds"])
            flattened.extend(brs)
        assert len(files) == len(block_seconds) == meta["blocks"]
        assert len(flattened) == len(cheap)
        got = {(r["wave"], int(r["rank"])): r for r in flattened}
        assert len(got) == len(cheap)
        for r in cheap:
            assert normalized_receipt(r) == normalized_receipt(got[(r["wave"], int(r["rank"]))])
        assert sum(int(r["conflicts"]) for r in cheap) == meta["conflicts"]
        assert dict(Counter(r["status"] for r in cheap)) == dict(meta["verdicts"])
        assert set(block_seconds) == set(range(meta["blocks"]))
        for bid, sec in block_seconds.items():
            assert abs(sec - float(meta["seconds_by_block"][str(bid)])) < 1e-9
        secs = list(block_seconds.values())
        prior_consolidated[name] = cheap
        report["prior_receipt_checks"][name] = {
            "jobs": len(cheap), "blocks": len(files), "workers": meta["workers"],
            "run_wall_seconds": meta["run_seconds"], "sum_block_seconds": sum(secs),
            "block_seconds": dist(secs), "mean_block_ms_per_job_including_init": 1000 * sum(secs) / len(cheap),
            "conflicts": meta["conflicts"], "verdicts": dict(sorted(Counter(r["status"] for r in cheap).items())),
            "identity_and_block_match": f"{len(cheap)}/{len(cheap)} exact",
        }
    raw_all = {}
    for name in ("raw_A_B", "raw_C_control"):
        for r in prior_consolidated[name]:
            raw_all[(r["wave"], int(r["rank"]))] = r
    sorted_c = {(r["wave"], int(r["rank"])): r for r in prior_consolidated["sorted_C"]}
    preferred_d = {(r["wave"], int(r["rank"])): r for r in prior_consolidated["preferred_D"]}
    for r in T:
        k = (r["wave"], int(r["rank"]))
        if r["wave"] in set("ABC"):
            q = raw_all[k]
            assert identity(r) == identity(q) and r["probe_raw"] == q["status"] and int(r["conflicts_raw"]) == int(q["conflicts"])
        if r["wave"] == "C":
            q = sorted_c[k]
            assert identity(r) == identity(q) and r["probe_sorted"] == q["status"] and int(r["conflicts_sorted"]) == int(q["conflicts"])
        if r["wave"] == "D":
            q = preferred_d[k]
            assert identity(r) == identity(q) and r["probe_preferred"] == q["status"] and int(r["conflicts_preferred"]) == int(q["conflicts"])
    report["trials_tsv_consistency"] = {"raw_A_B_C": 30000, "sorted_C": 10000, "preferred_D": 10000, "status_conflicts_and_identity": "exact"}

    raw_c = {(r["wave"], int(r["rank"])): r for r in prior_consolidated["raw_C_control"]}
    assert raw_c.keys() == sorted_c.keys()
    for k in raw_c:
        assert identity(raw_c[k]) == identity(sorted_c[k])
    report["matched_C_raw_vs_sorted"] = {
        "jobs": len(raw_c), "cap": 128,
        "raw_verdicts": dict(sorted(Counter(r["status"] for r in raw_c.values()).items())),
        "sorted_verdicts": dict(sorted(Counter(r["status"] for r in sorted_c.values()).items())),
        "raw_conflicts": sum(int(r["conflicts"]) for r in raw_c.values()),
        "sorted_conflicts": sum(int(r["conflicts"]) for r in sorted_c.values()),
        "same_raw_identities": True,
        "interpretation": "same jobs and nominal cap, but different formulas/groupings/shared-state paths and different worker counts; closure comparison is matched, timing is not controlled",
    }

    cold = rows(OUT / "cold-raw.tsv.gz")
    assert len(cold) == 512
    cold_source = {(r["wave"], int(r["rank"])): r for r in T if r["wave"] in set("AB")}
    for r in cold:
        a = cold_source[(r["wave"], int(r["rank"]))]
        assert (r["id"], r["w"], r["z"]) == identity(a)
        assert int(r["cap"]) == 512
        assert 512 <= int(r["conflicts"]) <= 518
        assert r["status"] == "OPEN"
    report["cold_Kissat_512"] = {
        "jobs": 512, "cap": 512, "status": {"OPEN": 512},
        "conflicts": dist([int(r["conflicts"]) for r in cold]),
        "per_query_seconds": dist([float(r["seconds"]) for r in cold]),
        "identity_matches_A_B_trials": "512/512 exact",
        "solver_caution": "cold Kissat controls, not shared-learning CaDiCaL and not a three-second campaign",
    }

    # Queue arithmetic is checked as data; its cover proof is outside this script's scope.
    queue = rows(R50 / "queue.tsv.gz")
    assert len(queue) == 11585
    assert {r["root_status"] for r in queue} == {"OPEN"}
    assert sum(int(r["new_count"]) for r in queue) == 1101974
    assert sum(int(r["previous_count"]) for r in queue) == 3604436
    pos = 0
    for r in queue:
        assert int(r["begin"]) == pos
        pos = int(r["end_exclusive"])
        assert pos - int(r["begin"]) == int(r["new_count"])
    assert pos == 1101974
    report["queue_data"] = {
        "rows": len(queue), "all_root_status_OPEN": True,
        "new_jobs": 1101974, "old_jobs": 3604436,
        "new_jobs_after_offset_50000": 1051974,
        "rows_represented_in_first_50000_new_jobs": len({r["row_id"] for r in by_conv["round50"]}),
        "rows_not_represented_in_first_50000_new_jobs": 11585 - len({r["row_id"] for r in by_conv["round50"]}),
    }

    # Existing timed receipts and their stored proof hashes (not proof validity).
    timed = []
    for d in ("timed", "timed-sorted", "timed-new"):
        for p in (R50 / d).glob("[0-9]*.json"):
            r = json.loads(p.read_text())
            r["_directory"] = d
            r["_index"] = int(p.stem)
            timed.append(r)
    assert len(timed) == 24
    timed.sort(key=lambda r: (("timed", "timed-sorted", "timed-new").index(r["_directory"]), r["_index"]))
    rep_exact = {(r["convention"], *identity(r)): r for r in R}
    trial_exact = {identity(r): r for r in T}
    timed_view = []
    for r in timed:
        source = r["source"]
        if source == "fresh-sorted-128-open":
            l = rep_exact[("sorted", r["row_id"], r["w"], r["z"])]
            local = l["sorted_arm"]
            bulk_status, bulk_conflicts = l["cadical"], int(l["conflicts"])
        elif source.startswith("prior-sorted") or source.startswith("preferred") or source == "new-cover":
            if source == "new-cover":
                l = rep_exact[("round50", r["row_id"], r["w"], r["z"])]
                bulk_status, bulk_conflicts = l["cadical"], int(l["conflicts"])
                local = "NEW_COVER_MEMBER"
            else:
                l = trial_exact[(r["row_id"], r["w"], r["z"])]
                if source.startswith("prior-sorted"):
                    local = "EXCLUDED" if l["possible_two_smallest"] == "0" else "ARM_WITNESS"
                    bulk_status, bulk_conflicts = l["probe_sorted"], int(l["conflicts_sorted"])
                else:
                    local = "OLD_COVER_MEMBER"
                    bulk_status, bulk_conflicts = l["probe_preferred"], int(l["conflicts_preferred"])
        else:
            raise AssertionError(source)
        if r["status"] == "VERIFIED_UNSAT":
            p = R50 / r["_directory"] / f"{r['_index']}.drat.gz"
            proof = gzip.decompress(p.read_bytes())
            assert len(proof) == r["proof_bytes"] and sha(proof) == r["proof_sha"]
        else:
            assert r["status"] == "OPEN" and r["proof_bytes"] == 0 and not r["proof_sha"]
        timed_view.append({
            "directory": r["_directory"], "test": r["_index"], "source": source,
            "row_id": r["row_id"], "profile": r["profile"], "arm": int(r["arm"]),
            "w": r["w"], "z": r["z"], "local_class": local,
            "bulk_status": bulk_status, "bulk_conflicts": bulk_conflicts,
            "status_3s": r["status"], "conflicts_3s": r["conflicts"],
            "encode_s": r["encode_s"], "setup_s": r["setup_s"], "search_s": r["search_s"],
            "check_s": r["check_s"], "receipt_encode_setup_search_check_s": r["encode_s"] + r["setup_s"] + r["search_s"] + r["check_s"],
            "query_sha": r["query_sha"], "parent_sha": r["parent_sha"],
            "proof_sha": r["proof_sha"],
        })
    with (HERE / "timed3s.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(timed_view[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(timed_view)
    report["timed_3s"] = {
        "jobs": len(timed),
        "by_source_status": {f"{k[0]} / {k[1]}": v for k, v in sorted(Counter((r["source"], r["status"]) for r in timed).items())},
        "proof_hashes_matching_stored_bytes": sum(r["status"] == "VERIFIED_UNSAT" for r in timed),
        "proofs_replayed_by_this_audit": 0,
        "open_search_seconds": dist([r["search_s"] for r in timed if r["status"] == "OPEN"]),
        "unsat_search_seconds": dist([r["search_s"] for r in timed if r["status"] == "VERIFIED_UNSAT"]),
        "open_conflicts": dist([r["conflicts"] for r in timed if r["status"] == "OPEN"]),
        "unsat_conflicts": dist([r["conflicts"] for r in timed if r["status"] == "VERIFIED_UNSAT"]),
        "max_search_overrun_ms": 1000 * max(0.0, max(r["search_s"] - 3.0 for r in timed)),
        "max_receipt_encode_setup_search_check_seconds": max(r["receipt_encode_setup_search_check_s"] for r in timed_view),
        "timer_scope": "search only; encoding, solver setup and proof checking are separate",
        "sorted_successes_already_local_excluded": sum(r["local_class"] == "EXCLUDED" and r["status_3s"] == "VERIFIED_UNSAT" for r in timed_view),
        "sorted_arm_witness_successes": sum(r["local_class"] == "ARM_WITNESS" and r["status_3s"] == "VERIFIED_UNSAT" for r in timed_view),
        "sorted_arm_witness_timeouts": sum(r["local_class"] == "ARM_WITNESS" and r["status_3s"] == "OPEN" for r in timed_view),
    }

    # Predeclared test set: 12 locally admitted sorted jobs, six in each of
    # two existing shared-formula blocks (one arm-13 and one arm-14 block).
    timed_ids = {(r["row_id"], r["w"], r["z"]) for r in timed_view}
    pool = []
    for l, c in zip(by_conv["sorted"], consolidated["sorted"], strict=True):
        if l["sorted_arm"] == "ARM_WITNESS" and l["cadical"] == "OPEN" and identity(l) not in timed_ids:
            pool.append((l, c))
    groups = defaultdict(list)
    for l, c in pool:
        groups[(c["group"], int(c["block"]), int(l["arm"]))].append((l, c))
    selected = []
    for arm in (13, 14):
        eligible = [(k, v) for k, v in groups.items() if k[2] == arm and len(v) >= 6]
        assert eligible
        key, vals = min(eligible, key=lambda kv: (kv[0][1], kv[0][0]))
        vals.sort(key=lambda lc: int(lc[0]["rank"]))
        for j, (l, c) in enumerate(vals[:6]):
            selected.append({
                "job_id": f"S{arm}-{j:02d}",
                "convention": "sorted", "row_id": l["row_id"], "profile": l["profile"],
                "arm": l["arm"], "w": l["w"], "z": l["z"], "rank": l["rank"],
                "raw_index": l["raw_index"], "shared_group": c["group"], "shared_block": c["block"],
                "bulk_assumptions_sha256": c["assumptions_sha256"], "bulk_cap": c["cap"],
                "bulk_conflicts": c["conflicts"], "bulk_status": c["status"],
                "local_arm": l["sorted_arm"], "prior_3s": "UNTESTED",
            })
    assert len(selected) == 12
    assert len({(r["shared_group"], r["shared_block"], r["arm"]) for r in selected}) == 2
    with (HERE / "candidates.tsv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(selected[0]), delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(selected)
    report["predeclared_candidates"] = {
        "jobs": len(selected),
        "groups": [{"arm": arm, "group": k[0], "block": k[1], "jobs": sum(1 for r in selected if (r["shared_group"], int(r["shared_block"]), int(r["arm"])) == k)} for k in sorted({(r["shared_group"], int(r["shared_block"]), int(r["arm"])) for r in selected}) for arm in [k[2]]],
        "eligibility": "sorted ARM_WITNESS, cap-128 OPEN, no existing 3-second receipt; deterministic first six in selected existing block",
        "group_field_warning": "cheap.py's group is a canonical grouping-metadata hash, not a hash of the generated CNF; query/parent hashes must be regenerated and matched before any run",
    }

    (HERE / "audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
