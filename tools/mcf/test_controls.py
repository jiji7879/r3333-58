#!/usr/bin/env python3
"""Offline controls for the opt-in MCF primitives (no production sweep)."""
import hashlib
import itertools
import os
from pathlib import Path
import tempfile
import unittest

from normal_form import (McfError, assert_disjoint_and_allocated, augment_maximal,
                         freeze_cube, normalise_colouring, parse_cube, read_dimacs)
from proof import normalize_additions


class DimacsControls(unittest.TestCase):
    def test_positive_freeze_preserves_body_and_order(self):
        parent = b"p cnf 3 2\n1 2 0\n-1 3 0\n"
        query = freeze_cube(parent, [-2, 3])
        self.assertEqual(query, b"p cnf 3 4\n1 2 0\n-1 3 0\n-2 0\n3 0\n")
        self.assertEqual(hashlib.sha256(query).hexdigest(),
                         "3055bbee92770d3c6e74ebc6e1bbfad28137515f170e08bf87a75aaf1a50bea7")

    def test_bad_cubes_and_dimacs_rejected(self):
        parent = b"p cnf 3 1\n1 2 0\n"
        for cube in ("", "1,1", "1,-1", "4", "0", "x", "1,,2"):
            with self.subTest(cube=cube), self.assertRaises(McfError):
                parse_cube(cube, 3)
        for malformed in (b"", b"p cnf 2 2\n1 0\n", b"p cnf 1 1\n2 0\n",
                          b"p cnf 1 1\n1\n", b"p cnf x 1\n1 0\n"):
            with self.subTest(malformed=malformed), self.assertRaises(McfError):
                read_dimacs(malformed)
        with self.assertRaises(McfError):
            freeze_cube(parent, [True])


class AllocationControls(unittest.TestCase):
    def setUp(self):
        self.parent = b"p cnf 6612 0\n"
        self.augmented, self.rules, self.additions = augment_maximal(
            self.parent, [(3, 47, 52)], 0)

    def test_positive_shape(self):
        self.assertEqual(len(self.rules), 1)
        self.assertEqual(len(self.rules[0]["witnesses"]), 56)
        self.assertEqual(len(self.additions), 169)
        self.assertEqual(self.rules[0]["witnesses"][0]["witness"], 6613)
        self.assertEqual(self.rules[0]["witnesses"][-1]["witness"], 6668)
        assert_disjoint_and_allocated(self.parent, self.rules, [], [1], self.augmented)

    def test_suffix_collision_rejected(self):
        variable = self.rules[0]["physical_variables"][0]
        with self.assertRaisesRegex(McfError, "non-host suffix"):
            assert_disjoint_and_allocated(self.parent, self.rules, [(variable,)], [1],
                                          self.augmented)

    def test_cube_collision_rejected(self):
        variable = self.rules[0]["edge_variable"]
        with self.assertRaisesRegex(McfError, "cube touches"):
            assert_disjoint_and_allocated(self.parent, self.rules, [], [variable],
                                          self.augmented)

    def test_wrong_allocation_rejected(self):
        with self.assertRaises(McfError):
            assert_disjoint_and_allocated(b"p cnf 6613 0\n", self.rules, [], [1],
                                          self.augmented)

    def test_empty_or_same_colour_arm_rejected(self):
        with self.assertRaises(McfError):
            augment_maximal(self.parent, [], 0)
        with self.assertRaises(McfError):
            augment_maximal(self.parent, [(0, 47, 52)], 0)
        with self.assertRaises(McfError):
            augment_maximal(self.parent, [(3, 47, 52), (3, 47, 52)], 0)


class ProofNormalizationControls(unittest.TestCase):
    def test_deletion_only_and_malformed(self):
        with tempfile.TemporaryDirectory(prefix="mcf-proof-control-", dir=os.getcwd()) as name:
            root = Path(name)
            # a(1), d(1), a(empty): only the middle command may disappear.
            raw = b"a\x02\x00d\x02\x00a\x00"
            (root / "raw.drat").write_bytes(raw)
            receipt = normalize_additions(root / "raw.drat", root / "clean.drat")
            self.assertEqual((root / "clean.drat").read_bytes(), b"a\x02\x00a\x00")
            self.assertEqual(receipt["commands"]["d"]["commands"], 1)
            self.assertEqual(receipt["commands"]["a"]["commands"], 2)
            self.assertTrue(receipt["complete_parse"])
            (root / "bad.drat").write_bytes(raw + b"x\x00")
            with self.assertRaises(McfError):
                normalize_additions(root / "bad.drat", root / "bad-clean.drat")
            self.assertFalse((root / "bad-clean.drat").exists())


class SemanticControl(unittest.TestCase):
    def test_normalise_colouring_with_generator_rule_schema(self):
        matrix = [[0, 3, 3, 1], [3, 0, 1, 2], [3, 1, 0, 0], [1, 2, 0, 0]]
        before, normal = normalise_colouring(matrix, [(3, 1, 2)], 0)
        self.assertEqual(before[1][2], 1)
        self.assertEqual(normal[1][2], 0)
        self.assertEqual(matrix, normal)
        self.assertTrue(normal[1][2] == 0 or
                        any(w not in (1, 2) and normal[1][w] == normal[2][w] == 0
                            for w in range(4)))
        for u, v in itertools.combinations(range(4), 2):
            if (u, v) != (1, 2):
                self.assertEqual(normal[u][v], before[u][v])
        for u, v, w in itertools.combinations(range(4), 3):
            self.assertFalse(normal[u][v] == normal[u][w] == normal[v][w])
        with self.assertRaises(McfError):
            normalise_colouring(matrix, [(1, 2)], 0)
        with self.assertRaises(McfError):
            normalise_colouring(matrix, [(3, 1, 2), (3, 1, 2)], 0)

    def test_exhaustive_k4_normalisations(self):
        # Independent finite semantic control: enumerate every good labelled
        # K4 colouring, every fixed-edge subset and every target colour.
        edges = list(itertools.combinations(range(4), 2))
        models = runs = steps = 0
        for values in itertools.product(range(4), repeat=len(edges)):
            source = [[0] * 4 for _ in range(4)]
            for (u, v), colour in zip(edges, values):
                source[u][v] = source[v][u] = colour
            if any(source[u][v] == source[u][w] == source[v][w]
                   for u, v, w in itertools.combinations(range(4), 3)):
                continue
            models += 1
            for mask in range(1 << len(edges)):
                fixed = {edge for i, edge in enumerate(edges) if mask >> i & 1}
                for colour in range(4):
                    arms = tuple(arm for arm in range(4) if arm != colour)
                    matrix = [row[:] for row in source]
                    before = [row[:] for row in source]
                    changing = [(u, v) for u, v in edges if u != 0 and v != 0
                                and before[0][u] == before[0][v]
                                and before[0][u] in arms and (u, v) not in fixed]
                    for u, v in changing:
                        if matrix[u][v] == colour:
                            continue
                        if not any(w not in (u, v) and matrix[u][w] == colour == matrix[v][w]
                                   for w in range(4)):
                            matrix[u][v] = matrix[v][u] = colour
                    for u, v, w in itertools.combinations(range(4), 3):
                        self.assertFalse(matrix[u][v] == matrix[u][w] == matrix[v][w])
                    for u, v in edges:
                        if (u, v) in fixed or (u, v) not in changing:
                            self.assertEqual(matrix[u][v], before[u][v])
                    for u, v in changing:
                        self.assertTrue(matrix[u][v] == colour or
                                        any(w not in (u, v) and matrix[u][w] == colour == matrix[v][w]
                                            for w in range(4)))
                    for x in range(1, 4):
                        arm = before[0][x]
                        if arm in arms:
                            self.assertEqual(
                                sum(matrix[x][y] == arm for y in range(4) if y != x),
                                sum(before[x][y] == arm for y in range(4) if y != x))
                    runs += 1
                    steps += len(changing)
        self.assertEqual((models, runs, steps), (3156, 807936, 183168))


if __name__ == "__main__":
    unittest.main(verbosity=2)
