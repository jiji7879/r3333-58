#!/usr/bin/env python3
"""Exhaustive small-coverage tests for the refinement queue policy."""
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from queue_refine import append_unit, decide


class QueueTests(unittest.TestCase):
    def test_exact_unit_extension(self):
        parent = b"c sample\np cnf 2 1\n1 2 0\n"
        self.assertEqual(append_unit(parent, -1),
                         b"c sample\np cnf 2 2\n1 2 0\n-1 0\n")
        self.assertNotEqual(append_unit(parent, 1), append_unit(parent, -1))

    def test_every_status_vector_and_backpressure(self):
        for size in range(1, 5):
            for statuses in itertools.product(("VERIFIED_UNSAT", "OPEN_UNKNOWN"), repeat=size):
                children = [{"status": s} for s in statuses]
                open_count = statuses.count("OPEN_UNKNOWN")
                if not open_count:
                    expected = "CLOSE_NODE_BY_COMPLETE_COVER"
                elif open_count == 1:
                    expected = "REPLACE_WITH_ONE_OPEN_CHILD"
                else:
                    expected = "KEEP_PARENT_QUEUED"
                for capacity in range(1, 6):
                    result = decide(children, capacity, True)
                    wanted = expected
                    if open_count > 1 and open_count <= capacity - 1:
                        wanted = "EXPAND_ALL_OPEN_CHILDREN"
                    self.assertEqual(result["action"], wanted)
                    if wanted == "EXPAND_ALL_OPEN_CHILDREN":
                        self.assertLessEqual(1 + result["queue_delta"], capacity)
                    else:
                        self.assertEqual(result["queue_delta"] if open_count else -1,
                                         result["queue_delta"])
        for statuses in itertools.product(("VERIFIED_UNSAT", "OPEN_UNKNOWN"), repeat=3):
            result = decide([{"status": s} for s in statuses], 5, False)
            self.assertEqual(result["action"], "KEEP_PARENT_QUEUED")

    def test_models_are_never_pruned_on_valid_moves(self):
        # Abstract children cover a parent model set. OPEN children can be empty
        # in reality: UNKNOWN is deliberately not promoted to either verdict.
        universe = range(1 << 3)
        for left, right in itertools.product(universe, repeat=2):
            parent = left | right
            children = [{"status": "VERIFIED_UNSAT" if not left else "OPEN_UNKNOWN", "models": left},
                        {"status": "VERIFIED_UNSAT" if not right else "OPEN_UNKNOWN", "models": right}]
            action = decide(children, 1, True)["action"]
            if action == "CLOSE_NODE_BY_COMPLETE_COVER":
                self.assertEqual(parent, 0)
            elif action == "REPLACE_WITH_ONE_OPEN_CHILD":
                remaining = [c for c in children if c["status"] == "OPEN_UNKNOWN"]
                self.assertEqual(len(remaining), 1)
                self.assertEqual(remaining[0]["models"], parent)
            else:
                # A retained parent represents exactly the original region.
                self.assertEqual(action, "KEEP_PARENT_QUEUED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
