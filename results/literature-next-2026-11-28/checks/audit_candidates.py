#!/usr/bin/env python3
"""Bounded metadata/counter checks; no wall solving and no output CNFs."""
import hashlib
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "tools/color-resolved-wallcc"))
sys.path.insert(0, str(ROOT / "tools/color-resolved-wallcc/frozen"))
import problem  # noqa: E402
from dense import marked_threshold  # noqa: E402
from gluing import units  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.solvers import Minisat22  # noqa: E402

EXPECTED_PARENT = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
ROW = "06861a3df60c"


def actual_metadata():
    row = problem.lookup(ROW)
    raw = problem.row_formula(row, "first")
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_PARENT
    family, _ = problem.family_and_pins(row)
    fixed = units(family, row["placement"])
    original = CardEnc.atleast
    calls = []

    def record(lits, bound, top_id, encoding=EncType.seqcounter):
        out = original(lits=lits, bound=bound, top_id=top_id, encoding=encoding)
        calls.append((len(lits), bound, out.nv - top_id, len(out.clauses),
                      sum(map(len, out.clauses))))
        return out

    CardEnc.atleast = staticmethod(record)
    try:
        extra = marked_threshold(family, fixed, row["charge"], tables=True,
                                 total_critical=True, full_root=False)
    finally:
        CardEnc.atleast = original
    senders, finals = calls[:-2], calls[-2:]
    assert Counter((n, k) for n, k, *_ in senders) == Counter({(41, 14): 27, (30, 10): 4})
    assert [(n, k) for n, k, *_ in finals] == [(15, 6), (31, 6)]
    assert len(extra) == 48902

    table = []
    totals = Counter()
    for n, k in sorted(set((n, k) for n, k, *_ in senders)):
        multiplicity = sum(1 for a, b, *_ in senders if (a, b) == (n, k))
        entry = {"n": n, "k": k, "multiplicity": multiplicity, "encodings": {}}
        for name in ("seqcounter", "kmtotalizer", "totalizer", "cardnetwrk"):
            enc = original(lits=list(range(1, n + 1)), bound=k, top_id=n,
                           encoding=getattr(EncType, name))
            aux = enc.nv - n
            nc = len(enc.clauses)
            nl = sum(map(len, enc.clauses))
            entry["encodings"][name] = {"aux": aux, "clauses": nc, "literals": nl,
                                         "total_aux": multiplicity * aux,
                                         "total_clauses": multiplicity * nc,
                                         "total_literals": multiplicity * nl}
            totals[(name, "aux")] += multiplicity * aux
            totals[(name, "clauses")] += multiplicity * nc
            totals[(name, "literals")] += multiplicity * nl
        table.append(entry)
    savings = {key: totals[("seqcounter", key)] - totals[("kmtotalizer", key)]
               for key in ("aux", "clauses", "literals")}
    return {"parent_sha256": EXPECTED_PARENT, "host_fixed_extra": [134995, len(fixed), len(extra)],
            "sender_shapes": [{"n": n, "k": k, "multiplicity": v}
                              for (n, k), v in sorted(Counter((n, k) for n, k, *_ in senders).items())],
            "final_shapes": [{"n": n, "k": k} for n, k, *_ in finals],
            "encoding_sizes": table, "sender_totals": {name: {key: totals[(name, key)]
                       for key in ("aux", "clauses", "literals")}
                   for name in ("seqcounter", "kmtotalizer")},
            "kmtotalizer_minus_sinz_savings_unsigned": savings}


def guarded_projection_controls():
    checks = 0
    for n in range(1, 8):
        for k in range(1, n + 1):
            guard = n + 1
            encs = {}
            for name in ("seqcounter", "kmtotalizer"):
                enc = CardEnc.atleast(list(range(1, n + 1)), bound=k, top_id=guard,
                                      encoding=getattr(EncType, name))
                encs[name] = [[-guard, *clause] for clause in enc.clauses]
            for bits in itertools.product((False, True), repeat=n + 1):
                expected = (not bits[-1]) or sum(bits[:-1]) >= k
                for name, clauses in encs.items():
                    assumptions = [i if bits[i - 1] else -i for i in range(1, n + 2)]
                    with Minisat22(bootstrap_with=clauses) as solver:
                        got = solver.solve(assumptions=assumptions)
                    assert got == expected, (n, k, bits, name, got, expected)
                    checks += 1
    # A guard-free negative control must reject a violating assignment with g=false.
    n, k = 5, 3
    hard = CardEnc.atleast(list(range(1, n + 1)), bound=k, top_id=n + 1,
                           encoding=EncType.kmtotalizer).clauses
    assumptions = [-1, -2, -3, 4, 5, -6]
    with Minisat22(bootstrap_with=hard) as solver:
        assert not solver.solve(assumptions=assumptions)
    return {"projected_assignment_checks": checks,
            "scope": "n=1..7, every k and every guard/input assignment, both encoders",
            "unguarded_violation_rejected": True}


def main():
    result = {"actual": actual_metadata(), "toy_controls": guarded_projection_controls()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
