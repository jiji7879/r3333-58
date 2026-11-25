#!/usr/bin/env python3
"""Arithmetic checks for the manuscript's snapshot and reciprocity table.

This does not replay SAT proofs or certify the owner-reported ledger status.
Run from the repository root with python3 paper/check_claims.py.
"""
from __future__ import annotations

import csv
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def profile(text: str) -> tuple[int, ...]:
    return tuple(map(int, text.split(",")))


def main() -> None:
    with (PAPER / "status-2026-11-25.csv").open(newline="") as f:
        rows = list(csv.DictReader(f))
    state = {
        profile(r["profile"]): {k: int(r[k]) for k in ("certified", "open", "legacy")}
        for r in rows
    }

    profiles = {
        d
        for d in itertools.product(range(17), repeat=4)
        if sum(d) == 57 and tuple(sorted(d, reverse=True)) == d
    }
    assert len(profiles) == 11
    assert set(state) == profiles

    reciprocal = sorted(
        (p for p in profiles if sum(d >= 15 for d in p) == 1), reverse=True
    )
    assert reciprocal == [(16, 14, 14, 13), (15, 14, 14, 14)]
    assert all(sum(d) == 57 and 9 <= min(d) for d in profiles)

    totals = {k: sum(v[k] for v in state.values()) for k in ("certified", "open", "legacy")}
    assert totals == {"certified": 98142, "open": 12893, "legacy": 2144}
    assert sum(totals.values()) == 113179

    big = {(15, 15, 15, 12), (16, 15, 15, 11)}
    assert sum(state[p]["open"] for p in big) == 1308
    small = {
        (15, 15, 14, 13), (16, 15, 14, 12), (16, 15, 13, 13),
        (15, 14, 14, 14), (16, 16, 14, 11), (16, 16, 13, 12),
        (16, 14, 14, 13),
    }
    assert sum(state[p]["open"] for p in small) == 11585
    assert state[(16, 15, 15, 11)]["open"] == 20

    replay_path = ROOT / "results/common-critical-audit-2026-11-25/full-replay.log"
    replay = json.loads(replay_path.read_text().splitlines()[0])
    assert replay["total"] == 496
    assert replay["placements"] == 4356
    assert replay["orbits"] == 247
    assert replay["checked"] == {"catalog": 2, "slots": 247, "words": 247}
    assert 2 + 247 + 247 == replay["total"]
    assert 190736 == 113179 + 77557

    # The two elementary bounds used in the mixed-colour cut argument.
    assert min(h * (16 - h) for h in range(1, 15)) >= 15
    assert min(9 * ell - 2 * (ell * ell // 4) for ell in range(2, 15)) >= 16

    print(f"profiles: {len(profiles)}")
    print("reciprocal candidates:", reciprocal)
    print("ledger snapshot:", totals, "total:", sum(totals.values()))
    print("OPEN: big-profile tail 1308; seven small profiles 11585")
    print("finite record: 496 = 2 + 247 + 247; placements 4356; orbits 247")
    print("All manuscript arithmetic checks passed; no SAT or ledger proof was rerun by this script.")


if __name__ == "__main__":
    main()
