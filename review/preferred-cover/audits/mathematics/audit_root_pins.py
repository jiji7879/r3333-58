#!/usr/bin/env python3
"""Independently census signed units incident on every nominated outside set.

Only the frozen units() generator is imported. Edge numbers and expected pins
are recomputed here; no SAT solver or K58 search is invoked.
"""
from collections import Counter
from itertools import combinations
from pathlib import Path
import csv
import gzip
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE / "extracted" / "K58_wall_10k_batches"
sys.path.insert(0, str(BASE / "engine" / "frozen"))
from gluing import Family, units  # frozen source under audit

PAIRS = list(combinations(range(58), 2))
EDGE_INDEX = {e: i for i, e in enumerate(PAIRS)}

def lit(u, v, c):
    return 4 * EDGE_INDEX[min(u, v), max(u, v)] + c + 1

def main():
    wall_raw = gzip.decompress((BASE / "inputs" / "wall.jsonl.gz").read_bytes())
    roster = {r["id"]: r for r in map(json.loads, wall_raw.splitlines())}
    with (BASE / "inputs" / "campaign.tsv").open(newline="") as f:
        campaign = {r["row_id"]: r for r in csv.DictReader(f, delimiter="\t")}
    bind_raw = gzip.decompress((BASE / "inputs" / "physical-bindings.jsonl.gz").read_bytes())
    bindings = {r["id"]: r for r in map(json.loads, bind_raw.splitlines())}
    assert len(roster) == len(campaign) == len(bindings) == 11585

    sizes = Counter()
    profiles = Counter()
    incident_counts = Counter()
    total_units = 0
    for rid, row in roster.items():
        fields = dict(row["family"])
        for key in ("profile", "root_kinds"):
            fields[key] = tuple(fields[key])
        f = Family(**fields)
        fixed = units(f, row["placement"])
        total_units += len(fixed)
        arm_index = int(campaign[rid]["arm_index"])
        arm = bindings[rid]["pentagons"][arm_index]
        T = tuple(arm["pentagon"])
        n = arm["size"]
        O = tuple(v for v in range(arm["block_start"], arm["block_start"] + n) if v not in T)
        assert len(O) == n - 5 == len(set(O)) and 11 <= n <= 14
        assert [campaign[rid]["outside_x"], campaign[rid]["outside_y"]] == [str(O[0]), str(O[1])]
        b = arm["missing_color"]
        a = f.arm
        assert b != a and f.root_kinds[b] == "-"
        assert len(arm["palette"]) == 3 and set(arm["palette"]) == set(range(4)) - {b}
        assert arm["palette"][0] == a  # word color 0 is the marked color
        starts = [1 + sum(f.profile[:i]) for i in range(4)]
        q = starts[a] + f.mark_position
        assert q not in O and q not in T

        expected = {lit(0, x, b) for x in O} | {-lit(q, x, a) for x in O}
        incident = set()
        fixed_by_variable = {}
        for clause in fixed:
            assert len(clause) == 1
            literal = clause[0]
            assert abs(literal) not in fixed_by_variable
            fixed_by_variable[abs(literal)] = literal
            edge_vertices = PAIRS[(abs(literal) - 1) // 4]
            if set(edge_vertices) & set(O):
                incident.add(literal)
        assert incident == expected, (rid, sorted(incident ^ expected))
        # Check exact local pentagon convention in every physical binding.
        for i, j in combinations(range(5), 2):
            local_color = 1 if (j - i) % 5 in (1, 4) else 2
            literal = lit(T[i], T[j], arm["palette"][local_color])
            assert fixed_by_variable.get(abs(literal)) == literal, (rid, i, j, literal)
        # Pentagon sites have fixed marked color and root color stars too.
        for v in T:
            pins = set(next(c for c in fixed if abs(c[0]) == abs(lit(0, v, b))))
            assert pins == {lit(0, v, b)}
            pins = set(next(c for c in fixed if abs(c[0]) == abs(lit(q, v, a))))
            assert pins == {lit(q, v, a)}
        sizes[n] += 1
        profiles[tuple(f.profile)] += 1
        incident_counts[len(incident)] += 1

    result = {
        "rows_checked": len(roster),
        "arm_size_counts": dict(sorted(sizes.items())),
        "profiles": {",".join(map(str, k)): v for k, v in sorted(profiles.items())},
        "incident_pin_count_per_row_histogram": dict(sorted(incident_counts.items())),
        "total_signed_units_generated": total_units,
        "physical_pentagon_edges_checked_against_local_convention": 10 * len(roster),
        "roster_decompressed_sha256": hashlib.sha256(wall_raw).hexdigest(),
        "claim_per_row": "Exactly the positive root-color star and negative marked-color star are incident on O; no other fixed signed unit touches O.",
        "aux_predicate_conditions": "For every row: nominated arm is size 11..14, unnamed ('-'), and distinct from marked arm."
    }
    out = HERE / "root_pin_audit_results.json"
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
