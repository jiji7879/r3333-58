"""Stage 2b: root-level unit-propagation agreement on logical literals.

Runs a plain counter-based BCP on parent+cube for both encodings and compares
the implied literal sets after applying the recorded auxiliary/guard map.  A
difference here would not by itself be a semantic error (propagation strength
differs between encodings), but agreement is a cheap whole-formula receipt.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kmt_wall as W  # noqa: E402
from kmt_stage1 import inverse_map, parse  # noqa: E402


def bcp(clauses):
    value = {}
    changed = True
    rounds = 0
    while changed:
        changed = False
        rounds += 1
        for clause in clauses:
            unassigned = None
            satisfied = False
            count = 0
            for literal in clause:
                state = value.get(abs(literal))
                if state is None:
                    count += 1
                    unassigned = literal
                elif state == (literal > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if count == 0:
                return value, False, rounds
            if count == 1:
                value[abs(unassigned)] = unassigned > 0
                changed = True
    return value, True, rounds


def main():
    item = W.row()
    family = W.family_of(item)
    scratch = W.REPO / ".scratch/m7"
    _, stock_clauses = parse(scratch / "stock-cube.cnf")
    _, kmt_clauses = parse(scratch / "kmt-cube.cnf")
    _, _, _, stock_blocks, _ = W.parent_bytes(family, item, "stock")
    _, _, _, kmt_blocks, _ = W.parent_bytes(family, item, "kmt")
    mapping = inverse_map(stock_blocks, kmt_blocks)
    stock_value, stock_ok, stock_rounds = bcp(stock_clauses)
    kmt_value, kmt_ok, kmt_rounds = bcp(kmt_clauses)

    def logical(value, inverse):
        out = set()
        for variable, truth in value.items():
            if variable > W.PHYSICAL_MAX:
                old = inverse.get(variable) if inverse else variable
                if old is None:
                    continue
                out.add((old, truth))
            else:
                out.add((variable, truth))
        return out

    left = logical(stock_value, None)
    right = logical(kmt_value, mapping)
    # Compare only literals that are logical objects on both sides.
    shared = {v for v, _ in left} & {v for v, _ in right}
    disagreement = sorted({(v, dict(left)[v], dict(right)[v])
                           for v in shared if dict(left)[v] != dict(right)[v]})
    receipt = dict(
        schema=1,
        stock=dict(propagated=len(stock_value), consistent=stock_ok, rounds=stock_rounds),
        kmt=dict(propagated=len(kmt_value), consistent=kmt_ok, rounds=kmt_rounds),
        logical_stock=len(left),
        logical_kmt=len(right),
        shared_logical=len(shared),
        only_stock=len({v for v, _ in left} - {v for v, _ in right}),
        only_kmt=len({v for v, _ in right} - {v for v, _ in left}),
        disagreements=disagreement[:20],
        agreement=not disagreement and {v for v, _ in left} == {v for v, _ in right},
        scope=("root-level BCP agreement is a receipt, not a semantic proof; "
               "it cannot certify UNSAT or replace the gadget controls"),
    )
    (HERE / "stage2b.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
