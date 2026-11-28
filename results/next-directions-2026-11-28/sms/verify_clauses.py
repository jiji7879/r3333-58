#!/usr/bin/env python3
"""Independent re-verification of the one-colour symmetry clauses.

Nothing here trusts the generator: the parent bytes are re-hashed, the unit set
and the cube are re-derived from the frozen recipe, the group membership and
unit/cube preservation are recomputed, the strict lex indicator is re-derived
symbolically *and* spot-checked numerically on random total words, the root
closure is recomputed with the scalar reference propagation, and the augmented
formula is required to survive unit propagation.

Exit status 1 on any failed check.
"""
import gzip
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, "/opt/math/lib/python3.12/site-packages")
import sms_lib as L                                             # noqa: E402
from bcp import CNF                                             # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ROW_ID = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
CUBE = [-1413, 1014]
EXPECT_PARENT = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
EXPECT_CUBE = "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8"


def fail(message):
    raise SystemExit("VERIFY FAILED: " + message)


def main():
    receipt = json.loads((HERE / "gen_receipt.json").read_text())
    parent = (HERE / "parent_cube.cnf").read_bytes()
    if hashlib.sha256(parent).hexdigest() != EXPECT_CUBE:
        fail("parent_cube.cnf hash mismatch")
    header, _, rest = parent.partition(b"\n")
    nvars, nclauses = map(int, header.split()[2:])

    # ---- 438 signed units + cube, re-derived from the frozen recipe
    sys.path.insert(0, str(ROOT / "tools/color-resolved-wallcc/frozen"))
    from gluing import Family, units                     # noqa: E402
    row = None
    with gzip.open(ROOT / "tools/color-resolved-wallcc/data/wall.jsonl.gz", "rt") as stream:
        for line in stream:
            value = json.loads(line)
            if value["id"] == ROW_ID:
                row = value
                break
    if row is None:
        fail("retained row absent")
    fields = dict(row["family"])
    for field in ("profile", "root_kinds"):
        fields[field] = tuple(fields[field])
    family = Family(**fields)
    fixed = units(family, row["placement"])
    if len(fixed) != 438:
        fail("expected 438 explicit signed units, got %d" % len(fixed))
    unit_lits = [c[0] for c in fixed] + CUBE

    def apply_lit(literal, perm):
        """Image of a physical literal under a vertex permutation (aux fixed)."""
        if abs(literal) > L.PHYS:
            return literal
        u, v, colour, positive = (None, None, None, None)
        rank, colour = divmod(abs(literal) - 1, 4)
        u, v = L.PAIRS[rank]
        a, b = perm[u], perm[v]
        image = L.colour0_var(L.INDEX[(min(a, b), max(a, b))]) + colour
        return image if literal > 0 else -image

    cube_set = set(CUBE)
    unit_set = set(unit_lits)

    # ---- root closure, scalar reference implementation
    cnf = CNF(HERE / "parent_cube.cnf")
    closure = cnf.propagate_naive([])
    if closure is None:
        fail("parent+cube is unit-propagation inconsistent")
    root_c0 = {}
    for r in range(L.NEDGE):
        value = closure.get(L.colour0_var(r))
        if value is not None:
            root_c0[r] = 1 if value > 0 else 0
    if len(root_c0) != receipt["root_colour0_fixed"]:
        fail("root colour-0 closure size %d != generator %d"
             % (len(root_c0), receipt["root_colour0_fixed"]))

    results = {"clauses": len(receipt["clauses"]), "checks": 0, "transpositions": {},
               "lengths": {}}
    for entry in receipt["clauses"]:
        clause = tuple(entry["clause"])
        full = tuple(entry["full_clause"])
        a, b = entry["transposition"]
        results["checks"] += 1

        # V1 tier, shape
        for literal in clause:
            if abs(literal) > L.PHYS or (abs(literal) - 1) % 4 != 0:
                fail("literal %d is not a physical colour-0 variable" % literal)
        if len(clause) < 2:
            fail("unit or empty clause %s" % (clause,))
        if len(set(clause)) != len(clause):
            fail("duplicate literal in %s" % (clause,))
        if any(-x in clause for x in clause):
            fail("tautological clause %s" % (clause,))

        # V2 group membership
        if a >= b or L.cell_of(a) is None or L.cell_of(a) != L.cell_of(b):
            fail("transposition %s is not inside a twin cell" % ((a, b),))
        perm = L.perm_of_transposition(a, b)
        results["transpositions"][f"{a}-{b}"] = results["transpositions"].get(f"{a}-{b}", 0) + 1

        # V3 unit and cube preservation, recomputed
        if {apply_lit(x, perm) for x in unit_lits} != unit_set:
            fail("transposition %s does not preserve the 438 units + cube" % ((a, b),))
        if {apply_lit(x, perm) for x in CUBE} != cube_set:
            fail("transposition %s does not preserve the cube" % ((a, b),))

        # V4 symbolic strict indicator of the FULL certificate
        # a clause literal +var is falsified by position value 1, -var by value 0
        assign = {}
        for literal in full:
            r = (abs(literal) - 1) // 4
            assign[r] = 0 if literal > 0 else 1
        witness = None
        for r in range(L.NEDGE):
            other = L.INDEX[L.apply_to_pair(L.inverse(perm), L.PAIRS[r])]
            if other == r:
                continue
            x, y = assign.get(r), assign.get(other)
            if x is None or y is None:
                fail("certificate does not fix position %d" % r)
            if x != y:
                witness = r
                if not (x == 1 and y == 0):
                    fail("certificate witnesses an increase at %d" % r)
                break
        if witness is None:
            fail("certificate has no strict difference")
        if list(entry["witness_positions"])[0] != witness:
            fail("recorded witness %s != recomputed %d"
                 % (entry["witness_positions"], witness))

        # V5 reduction: emitted clause == negation(full) minus closure-false literals
        expected_keep, expected_drop = [], []
        for literal in L.clause_of([(r, v) for r, v in assign.items()]):
            if root_c0.get((abs(literal) - 1) // 4) is None:
                expected_keep.append(literal)
            else:
                expected_drop.append(literal)
        if sorted(expected_keep) != sorted(clause):
            fail("emitted clause is not the reduction of the full certificate")
        for literal in expected_drop:
            r, want = (abs(literal) - 1) // 4, (1 if literal > 0 else 0)
            if root_c0[r] == want:
                fail("dropped literal %d is true under the closure (vacuous clause)" % literal)

        # V6 numeric spot check on random total words extending the certificate
        import random
        random.seed(1000 + witness)
        free = [r for r in range(L.NEDGE) if r not in assign]
        for _ in range(60):
            word = [0] * L.NEDGE
            for r, v in assign.items():
                word[r] = v
            for r in free:
                word[r] = random.randint(0, 1)
            image = L.evaluate_words(word, perm)
            first = next((r for r in range(L.NEDGE) if image[r] != word[r]), None)
            if first != witness or image[first] != 0 or word[first] != 1:
                fail("numeric lex check disagrees at witness %d" % witness)
        results["lengths"][len(clause)] = results["lengths"].get(len(clause), 0) + 1

    # V7 augmented formula must survive unit propagation
    extra = "".join(" ".join(map(str, entry["clause"])) + " 0\n" for entry in receipt["clauses"])
    augmented = (HERE / "augmented.cnf")
    augmented.write_text(
        ("p cnf %d %d\n" % (nvars, nclauses + len(receipt["clauses"])))
        + rest.decode() + extra)
    if hashlib.sha256(augmented.read_bytes()).hexdigest() != hashlib.sha256(
            parent.replace(header, b"p cnf %d %d" % (nvars, nclauses + len(receipt["clauses"])), 1)
            + extra.encode()).hexdigest():
        fail("augmented file layout mismatch")
    aug = CNF(augmented)
    status = aug.propagate_naive([])
    if status is None:
        fail("parent+cube+clauses is unit-propagation inconsistent")
    implied = sum(1 for entry in receipt["clauses"]
                  if any(closure.get(abs(x)) == (1 if x > 0 else -1) for x in entry["clause"]))
    results["augmented_closure_size"] = len(status)
    results["clauses_satisfied_by_parent_closure"] = implied
    results["augmented_sha256"] = hashlib.sha256(augmented.read_bytes()).hexdigest()
    results["parent_cube_sha256"] = EXPECT_CUBE
    results["root_colour0_fixed"] = len(root_c0)
    results["status"] = "PASS"
    (HERE / "verify_receipt.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: results[k] for k in
                      ("status", "clauses", "lengths", "augmented_closure_size",
                       "clauses_satisfied_by_parent_closure", "augmented_sha256")},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
