#!/usr/bin/env python3
"""Exhaustively test the actual one-adjacent-pair lexicographic CNF."""
from itertools import product
from pathlib import Path
import json
import sys

HERE = Path(__file__).resolve().parent
BASE = HERE / "extracted" / "K58_wall_10k_batches"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "engine"))
from arm_pairs import base
from sorted_arm import sorted_base


def main():
    ps, ids, old = base(7)
    top, all_clauses = sorted_base(7)
    clauses = all_clauses[len(old):]
    physical = {ids[i, x] + c for x in (5, 6) for i in range(5) for c in range(3)}
    auxiliary = sorted({abs(v) for c in clauses for v in c} - physical)
    assert len(auxiliary) == 4
    assert {abs(v) for c in clauses for v in c} <= physical | set(auxiliary)

    checked = accepted = expected_accepted = 0
    for left in product(range(3), repeat=5):
        for right in product(range(3), repeat=5):
            values = [False] * (top + 1)
            for x, word in ((5, left), (6, right)):
                for i, color in enumerate(word):
                    for c in range(3):
                        values[ids[i, x] + c] = color == c
            possible = False
            for mask in range(1 << len(auxiliary)):
                for k, var in enumerate(auxiliary):
                    values[var] = bool(mask >> k & 1)
                if all(any(values[abs(v)] == (v > 0) for v in clause) for clause in clauses):
                    possible = True
                    break
            expected = left <= right
            assert possible == expected, (left, right, mask)
            checked += 1
            accepted += possible
            expected_accepted += expected
    result = {"ordered_pairs_of_all_3_color_5_digit_words": checked,
              "auxiliary_assignments_per_word_pair": 1 << len(auxiliary),
              "cnf_existentiably_accepts_lexicographically_nondecreasing_pairs": accepted,
              "expected_nondecreasing_pairs": expected_accepted,
              "sorting_clauses_tested": len(clauses),
              "mismatches": 0,
              "scope": "Actual sorted_base(7) comparator, exhaustive over physical words and all four auxiliary variables"}
    assert (checked, accepted, expected_accepted) == (59049, 29646, 29646)
    (HERE / "sorting_encoding_audit_results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
