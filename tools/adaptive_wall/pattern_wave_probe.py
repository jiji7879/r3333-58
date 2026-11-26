#!/usr/bin/env python3
"""Bounded physical-survivor probe over the new ordinary-wall campaign.

Selects live third-word patterns (not already known UNSAT at the shared local
layer), across distinct original rows/arms. Every invocation uses the original
first-tier parent plus fifteen physical spoke units, via word_wave's existing
run_native implementation. UNSAT must verify against the exact physical parent,
not just a local arm query. OPEN remains unresolved; SAT is only a physical
model of that word's constraints, not a whole-row coloring.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import json
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import zip_longest
from pathlib import Path

SKIP_EXISTING_WAVE = "05dd65df8f6e"


def run_group(task):
    campaign, rid, words, cap = task
    sys.path.insert(0, campaign)
    from word_wave import worker
    result = worker((rid, words, cap))
    return campaign, rid, result


def select_patterns(campaign: Path, limit: int):
    sys.path.insert(0, str(campaign))
    from frontier import context
    from third_star import DEST, WORDS, candidates
    allowed = set(candidates())
    tag = {w: (json.loads((DEST / (w + ".json")).read_bytes())["status"]
               if w in allowed else "PAIR_EXCLUDED") for w in WORDS}
    live = sorted(w for w, status in tag.items() if status == "SAT")
    if len(live) != 61:
        raise ValueError(f"expected 61 live third words, got {len(live)}")
    _, bindings, sr, _ = context()
    groups = collections.defaultdict(list)
    for rid in sorted(sr):
        arms = bindings[rid]["pentagons"]
        if not arms:
            continue
        ai = max(range(len(arms)), key=lambda i: arms[i]["size"])
        if arms[ai]["size"] == 14 and not rid.startswith(SKIP_EXISTING_WAVE):
            groups[sr[rid]["profile"]].append((rid, ai))
    selected = []
    for profile_group in zip_longest(*(groups[p] for p in sorted(groups))):
        selected.extend(x for x in profile_group if x is not None)
        if len(selected) * len(live) >= limit:
            break
    result = []
    for rid, ai in selected:
        result.extend((rid, ai, word) for word in live)
        if len(result) >= limit:
            return result[:limit]
    raise ValueError(f"only {len(result)} distinct new physical patterns available")


def verify_closure(campaign: Path, rid: str, receipt: dict):
    """Re-read an UNSAT_BASE proof against its exact physical parent+cube."""
    from arm_pairs import check_drat
    from compile import append
    assert receipt["status"] == "UNSAT_BASE"
    receipt_path = (campaign / "results/word-runs" / rid /
                    f"{receipt['node']}-{receipt['mode']}-{receipt['cap']}.json")
    saved = json.loads(receipt_path.read_bytes())
    assert saved == receipt, "receipt changed or was replayed from another pattern"
    rows, _, _, _ = __import__("frontier").context()
    from pentagons import compile_cas
    from problem import family_and_pins, row_formula
    base = row_formula(rows[rid], "first")
    assert receipt["parent_sha256"] == __import__("arm_pairs").sha(base)
    _, plain = append(base, [[v] for v in receipt["cube"]])
    proof = gzip.decompress((campaign / "results/word-runs" / rid / receipt["proof"]).read_bytes())
    assert __import__("arm_pairs").sha(proof) == receipt["proof_sha256"]
    _, pins = family_and_pins(rows[rid])
    _, prefix, _ = compile_cas(rows[rid], set(pins))
    from compile import produce
    _, spoken_prefix = produce(rows[rid])
    cutproof = prefix + spoken_prefix
    with tempfile.TemporaryDirectory(prefix="verify-closure-", dir=campaign / "results") as temp:
        plain_path, proof_path = Path(temp) / "plain.cnf", Path(temp) / "proof.drat"
        plain_path.write_bytes(plain)
        proof_path.write_bytes(proof)
        check_drat(plain_path, proof_path)
    return {"replayed_formula_sha256": receipt["plain_sha256"],
            "original_parent_sha256": receipt["parent_sha256"],
            "verified": True,
            "prefix_and_leaf_proof_present": bool(cutproof),
            "saved_proof_uses_campaign_prefix": proof.startswith(cutproof)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--limit", type=int, default=1000)
    parser.add_argument("--cap", type=int, default=5000)
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if min(args.limit, args.cap, args.jobs) <= 0 or args.out.exists():
        parser.error("positive integers and a new --out receipt are required")
    campaign = args.campaign.resolve()
    patterns = select_patterns(campaign, args.limit)
    jobs = []
    for rid in dict.fromkeys(rid for rid, _, _ in patterns):
        wave = [word for r, _, word in patterns if r == rid]
        ai = next(ai for r, ai, _ in patterns if r == rid)
        jobs.append((str(campaign), rid, wave, args.cap, ai))
    started = time.monotonic()
    results = []
    with ProcessPoolExecutor(args.jobs) as pool:
        futures = [pool.submit(run_group, job[:4]) for job in jobs]
        for future, job in zip(futures, jobs):
            campaign_text, rid, records = future.result()
            if campaign_text != str(campaign):
                raise AssertionError("worker changed campaign directory")
            _, _, word, _, ai = job
            expected_words = set(word)
            if {r["node"][1:] for r in records} != expected_words:
                raise AssertionError(f"incomplete wave on {rid}")
            results.extend((rid, ai, r) for r in records)
    result_by_key = {(rid, r["node"]): (rid, ai, r) for rid, ai, r in results}
    ordered = []
    for rid, ai, word in patterns:
        _, _, receipt = result_by_key[rid, "w" + word]
        # Avoid local pattern labels hiding changed physical parents/cubes.
        receipt = dict(receipt)
        record = {"row_id": rid, "arm_index": ai, "third_word": word, **receipt}
        if receipt["status"] == "UNSAT_BASE":
            record["closure_replay"] = verify_closure(campaign, rid, receipt)
        elif receipt["status"] == "SAT_BASE":
            from compile import append
            from problem import read_dimacs, check_model
            _, _, _, _, ai_actual, _ = __import__("word_wave").setup(rid)
            assert ai_actual == ai
            base = __import__("problem").row_formula(
                __import__("frontier").context()[0][rid], "first")
            _, plain = append(base, [[v] for v in receipt["cube"]])
            model = json.loads(gzip.decompress(
                (campaign / "results/word-runs" / rid / receipt["model"]).read_bytes()))
            nv, clauses = read_dimacs(plain)
            check_model(clauses, receipt["cube"], model, nv)
            record["physical_model_verified"] = True
        ordered.append(record)
    statuses = collections.Counter(r["status"] for r in ordered)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "k58-pattern-wave-probe/v1",
        "scope": "Exact original first-tier parents plus physical-word cubes only; not whole-row certification",
        "selection": "61 model-supported third words per largest size-14 pentagon; distinct row/arm combinations, existing 61-word example excluded",
        "limit": args.limit, "cap_per_case": args.cap, "jobs": args.jobs,
        "wall_seconds": time.monotonic() - started,
        "case_count": len(ordered), "status_counts": dict(statuses),
        "closed_unsat_count": statuses["UNSAT_BASE"],
        "unresolved_open_count": statuses["OPEN"],
        "augmented_unsat_pending_base_count": statuses["AUGMENTED_UNSAT_PENDING_BASE"],
        "patterns": ordered,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "patterns"}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
