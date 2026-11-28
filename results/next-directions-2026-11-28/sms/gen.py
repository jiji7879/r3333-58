#!/usr/bin/env python3
"""Bounded one-colour symmetry-clause generator for the retained K58 parent.

THIS IS NOT STOCK SMS.  Upstream SMS (commit 63958bd) could not be built here
(no Boost headers or libraries, and the ``cadical_sms`` submodule is empty; see
sms-blocker.md), so this is an explicitly labelled substitute: a bounded,
deterministic enumeration of one-colour lex-leader certificates.

Setup
-----
* one designated colour ``c = 0``; Boolean word ``W(G)[r] = 1`` iff the r-th
  pair in row-wise upper-triangle order has colour 0;
* candidate group ``H = Sym({38..46}) x Sym({52..57})``; 51 transpositions,
  each preserving the 438 explicit signed units and the 2-clause cube
  (rechecked by verify_clauses.py);
* for a transposition ``p``, ``W(p.G)[r] = W(G)[phi(r)]`` with ``phi`` induced
  by ``p^{-1}``.  A *certificate* is a partial assignment A such that every
  total word extending A has ``W(p.G) < W(G)``, first differing at a fixed
  position with values ``(1, 0)``.  The clause ``not A`` then holds at every
  orbit-minimal representative.

Grounding used here
-------------------
``A`` is always ``root_closure(F) union decisions``:
  * ``root_closure(F)`` is the unit-propagation closure of the *exact*
    parent+cube, so each of its literals is a consequence of F;
  * ``decisions`` are free assumptions and appear literally in the clause.
Clause literals falsified by the root closure are dropped (equivalence modulo
F).  A certificate all of whose literals are falsified by the closure would
give the empty clause and is EXCLUDED: adding it would make F trivially
BCP-UNSAT.  Those are recorded separately.  The final pinned run found none:
all 51 transpositions are lex-minimal under the root closure.

Every emitted clause is re-verified from scratch by verify_clauses.py.
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, "/opt/math/lib/python3.12/site-packages")   # numpy from /opt/math
import sms_lib as L                                             # noqa: E402
from bcp import CNF                                             # noqa: E402

HERE = Path(__file__).resolve().parent
CPU_CAP = 60.0          # hard generation cap required by the direction
MAX_FREE_ROWS = 3       # free prefix rows explored per transposition
MAX_LENGTH = 12         # reduced clause length cap
TOTAL_CAP = 900


def value_of(lit):
    return (abs(lit) - 1) // 4, (1 if lit > 0 else 0)


def reduce_clause(clause, root_c0):
    keep, dropped = [], []
    for x in clause:
        r, want = value_of(x)
        base = root_c0.get(r)
        if base is None:
            keep.append(x)
        elif base == want:
            return [], [], True
        else:
            dropped.append(x)
    return keep, dropped, False


def main():
    t0 = time.process_time()
    deadline = t0 + CPU_CAP
    cnf = CNF(HERE / "parent_cube.cnf")
    root = cnf.propagate([])
    assert root is not None, "root unit propagation already conflicts"
    root_c0 = {r: (1 if root[L.colour0_var(r)] > 0 else 0)
               for r in range(L.NEDGE) if root[L.colour0_var(r)] != 0}
    del root

    emitted = {}
    empty = {}
    stats = {"certificates": 0, "vacuous": 0, "duplicate": 0, "empty_reduced": 0,
             "too_long": 0, "per_perm": {}, "length_histogram": {}, "deadline_hit": False}
    assign = dict(root_c0)

    def try_emit(perm_ab, perm):
        got = L.certificate(assign, perm)
        if got is None:
            return False
        cert, wit = got
        stats["certificates"] += 1
        clause = L.clause_of(cert)
        keep, dropped, satisfied = reduce_clause(clause, root_c0)
        if satisfied:
            stats["vacuous"] += 1
            return False
        if not keep:
            stats["empty_reduced"] += 1
            empty[tuple(sorted(clause))] = {"transposition": perm_ab, "length": len(clause)}
            return False
        if len(keep) > MAX_LENGTH:
            stats["too_long"] += 1
            return False
        key = tuple(sorted(keep))
        if key in emitted:
            stats["duplicate"] += 1
            return False
        emitted[key] = {
            "clause": list(key),
            "full_clause": list(clause),
            "dropped_false_literals": dropped,
            "transposition": list(perm_ab),
            "witness_positions": list(wit),
            "witness_values": [1, 0],
            "prefix_decisions": [[r, assign[r]] for r in sorted(assign)
                                 if r not in root_c0],
            "length_full": len(clause),
        }
        stats["length_histogram"][len(key)] = stats["length_histogram"].get(len(key), 0) + 1
        return True

    def walk(perm_ab, perm, table, index, free_rows):
        if time.process_time() > deadline:
            stats["deadline_hit"] = True
            return
        while index < len(table):
            r, other = table[index]
            a, b = assign.get(r), assign.get(other)
            if a is not None and b is not None:
                if a == b:
                    index += 1
                    continue
                if a == 1 and b == 0:
                    try_emit(perm_ab, perm)
                return
            if a is None and b is None:
                assign[r], assign[other] = 1, 0
                try_emit(perm_ab, perm)
                del assign[r], assign[other]
            elif a == 1:
                assign[other] = 0
                try_emit(perm_ab, perm)
                del assign[other]
            elif b == 0:
                assign[r] = 1
                try_emit(perm_ab, perm)
                del assign[r]
            if free_rows >= MAX_FREE_ROWS:
                return
            for value in (0, 1):
                added = []
                if a is None:
                    assign[r] = value
                    added.append(r)
                if b is None:
                    assign[other] = value
                    added.append(other)
                walk(perm_ab, perm, table, index + 1, free_rows + 1)
                for k in added:
                    del assign[k]
            return

    for a, b in L.transpositions():
        before = len(emitted)
        perm = L.perm_of_transposition(a, b)
        walk((a, b), perm, L.move_table(perm), 0, 0)
        stats["per_perm"][f"{a}-{b}"] = len(emitted) - before
        if len(emitted) >= TOTAL_CAP or time.process_time() > deadline:
            stats["deadline_hit"] = stats["deadline_hit"] or time.process_time() > deadline
            break

    clauses = [emitted[k] for k in sorted(emitted)]
    cpu = time.process_time() - t0
    receipt = {
        "generator": "one-colour lex-leader certificate enumeration (NOT stock SMS)",
        "colour": 0,
        "group": "Sym(38..46) x Sym(52..57), transpositions only",
        "transpositions": len(L.transpositions()),
        "parent": "parent_cube.cnf",
        "root_colour0_fixed": len(root_c0),
        "cpu_seconds": round(cpu, 3),
        "caps": {"cpu": CPU_CAP, "free_rows": MAX_FREE_ROWS,
                 "length": MAX_LENGTH, "total": TOTAL_CAP},
        "stats": stats,
        "empty_reduced_clauses": list(empty.values()),
        "clauses": clauses,
    }
    (HERE / "gen_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    with open(HERE / "clauses.txt", "w") as out:
        for entry in clauses:
            out.write(" ".join(map(str, entry["clause"])) + " 0\n")
    print(json.dumps({k: receipt[k] for k in ("cpu_seconds", "stats", "caps")}, indent=2, sort_keys=True))
    print("emitted", len(clauses), "empty-reduced distinct", len(empty))


if __name__ == "__main__":
    main()
