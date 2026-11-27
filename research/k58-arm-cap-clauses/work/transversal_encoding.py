#!/usr/bin/env python3
"""Replace the published three-per-arm cap by all inclusion-minimal transversals."""
import argparse
import collections
import hashlib
import json
import sys
import time
from pathlib import Path

from counter_encoding import load_probe, serialize


def sha(data):
    return hashlib.sha256(data).hexdigest()


def all_transversals(union, choices):
    """All inclusion-minimal sets meeting every choice, by exact mask census."""
    vertices = sorted(set().union(*choices))
    if not vertices:
        raise AssertionError("nonempty choices have empty union")
    index = {v: i for i, v in enumerate(vertices)}
    masks = [sum(1 << index[v] for v in choice) for choice in choices]
    hit = bytearray(1 << len(vertices))
    hit[0] = not choices
    for mask in range(1, 1 << len(vertices)):
        hit[mask] = all(mask & item for item in masks)
    answers = []
    for mask in range(1, 1 << len(vertices)):
        if not hit[mask]:
            continue
        bits = mask
        minimal = True
        while bits:
            bit = bits & -bits
            if hit[mask ^ bit]:
                minimal = False
                break
            bits ^= bit
        if minimal:
            answer = tuple(v for v in vertices if mask & (1 << index[v]))
            answers.append(answer)
    return answers


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--ranks", default="1200,1300")
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    probe = load_probe(args.source)
    original_hitting = probe.hitting
    # Bound the exact enumeration to these 15/16-vertex arms. The mask census
    # deliberately allocates 2^|union|, so do not silently use it generically.
    audit = []
    stats = []

    def full_hitting(n, choices):
        if not choices:
            stats.append({"kind": "no_feasible_support", "choices": 0,
                          "transversals": 1, "length_histogram": {"0": 1}})
            return [()]
        if () in choices:
            stats.append({"kind": "already_realized", "choices": len(choices),
                          "transversals": 0, "length_histogram": {}})
            return []
        start = time.process_time()
        answer = all_transversals(range(n), choices)
        lengths = collections.Counter(map(len, answer))
        stats.append({"kind": "ordinary", "choices": len(choices),
                      "union": len(set().union(*choices)),
                      "transversals": len(answer),
                      "minimum_size": min(lengths),
                      "minimum_count": lengths[min(lengths)],
                      "length_histogram": {str(k): v for k, v in sorted(lengths.items())},
                      "cpu": time.process_time() - start})
        return answer

    for rank in map(int, args.ranks.split(",")):
        row = probe.rows[rank - 1]
        stats.clear()
        guards = {}
        begin = time.process_time()
        raw, form, baseline, old_selectors = probe.build(row, guards)
        baseline_cpu = time.process_time() - begin
        assert sha(raw) == row["input_sha256"]
        probe.hitting = full_hitting
        begin = time.process_time()
        try:
            raw2, form2, clauses, _ = probe.build(row, {})
        finally:
            probe.hitting = original_hitting
        full_cpu = time.process_time() - begin
        assert raw2 == raw and form2.clauses == form.clauses
        baseline_set = set(baseline)
        new = [clause for clause in clauses if clause not in baseline_set]
        rank_dir = args.out / str(rank)
        rank_dir.mkdir()
        for name, extra in (("all-transversals", clauses),
                            ("new-transversals", new)):
            data = serialize(raw, extra)
            (rank_dir / (name + ".cnf")).write_bytes(data)
        # This explicit literal file permits independent clause selection and replay.
        (rank_dir / "all-transversals.json").write_text(
            json.dumps(clauses) + "\n")
        (rank_dir / "baseline-direct.json").write_text(
            json.dumps(baseline) + "\n")
        rec = {"rank": rank, "id": row["id"], "input_sha256": row["input_sha256"],
               "baseline_direct": len(baseline), "all_direct": len(clauses),
               "new_direct": len(new),
               "new_length_histogram": dict(collections.Counter(map(len, new))),
               "baseline_generation_cpu": baseline_cpu,
               "all_generation_cpu_including_parent": full_cpu,
               "arms": list(stats),
               "queries": {}}
        for name, extra in (("all-transversals", clauses), ("new-transversals", new)):
            data = (rank_dir / (name + ".cnf")).read_bytes()
            rec["queries"][name] = {"clauses_added": len(extra), "bytes": len(data),
                                    "sha256": sha(data)}
        audit.append(rec)
        (rank_dir / "build.json").write_text(json.dumps(rec, indent=2, sort_keys=True) + "\n")
        print(json.dumps({k: rec[k] for k in ("rank", "baseline_direct", "all_direct",
                                             "new_direct", "new_length_histogram",
                                             "all_generation_cpu_including_parent")}), flush=True)
    (args.out / "summary.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
