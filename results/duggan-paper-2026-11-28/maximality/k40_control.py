#!/usr/bin/env python3
"""Pin-preservation control on the repository's K40 two-16-arm colouring."""
import argparse
import json
from pathlib import Path
from mcf_pilot import (load_col, save_col, bad_triangles, missing_paths,
                       maximize, check_trace, root_profile, incidence_records)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.out.mkdir(exist_ok=True)
    source = load_col(args.source)
    n = len(source)
    assert n == 40 and not bad_triangles(source)
    assert root_profile(source) == (16, 16, 7, 0)
    # Root star and every internal edge of the two 16-vertex arms.
    arms = [tuple(range(1, 17)), tuple(range(17, 33))]
    pins = {(0, v) for v in range(1, n)}
    for arm in arms:
        pins |= {(u, v) for i, u in enumerate(arm) for v in arm[i+1:]}
    records = []
    for c in range(4):
        final, steps = maximize(source, c)
        check_trace(source, steps, final, c)
        touched = [s for s in steps if tuple(sorted(s[:2])) in pins]
        preserved = all(final[u][v] == source[u][v] for u, v in pins)
        assert preserved == (len(touched) == 0)
        rec = {"source": args.source, "colour": c, "pins_checked": len(pins),
               "root_star_and_arm_interiors_preserved": preserved,
               "source_root_profile": root_profile(source),
               "final_root_profile": root_profile(final),
               "steps": len(steps), "frozen_steps": touched,
               "steps_detail": steps, "initial_missing_paths": len(missing_paths(source, c)),
               "final_missing_paths": len(missing_paths(final, c)),
               "incidence": incidence_records(final, c)}
        if preserved:
            target = args.out/f"k40_two16arms_max_c{c}.col"
            save_col(target, final)
            rec["output"] = str(target)
        records.append(rec)
    args.out.joinpath("k40_results.json").write_text(json.dumps(records, indent=2)+"\n")
    print(json.dumps([{k: v for k, v in r.items()
                       if k not in ("steps_detail", "incidence")} for r in records], indent=2))
    assert records[0]["root_star_and_arm_interiors_preserved"]
    assert records[1]["root_star_and_arm_interiors_preserved"]
    assert not records[2]["root_star_and_arm_interiors_preserved"]


if __name__ == "__main__":
    main()
