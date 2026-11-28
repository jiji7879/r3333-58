"""Stage 2: projected guarded-counter semantics on the 31 actual gadgets.

For each actual sender gadget, in the stock (Sinz) and KMT form, check:

  E  enforcement   F & g & AtMost(k-1)          UNSAT
  T  tightness     F & g & exactly-k witness    SAT, for every candidate index
  G  guard-false   F & -g & all candidates 0    SAT
  N  negative      unguarded F & violation      UNSAT
  W  wrong bound   g & encoder at k+1 & k true  UNSAT  (harness detects strength)
                   g & encoder at k-1 & k-1 true SAT   (harness detects weakness)

Plus exhaustive equivalence of both encodings for n=1..9 over every k and
every guard/input assignment, and a self-control for the AtMost encodings.
"""
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kmt_wall as W  # noqa: E402
from pysat.card import CardEnc, EncType  # noqa: E402
from pysat.solvers import Minisat22  # noqa: E402

SAT_CALLS = 0


def solve(clauses, assumptions):
    global SAT_CALLS
    SAT_CALLS += 1
    with Minisat22(bootstrap_with=clauses) as solver:
        return solver.solve(assumptions=assumptions)


def guarded(block):
    guard = block["guard"]
    return [[-guard, *clause] for clause in block["clauses"]]


def counters(block, encoding):
    """Regenerate the same gadget standalone (same literal list and top id)."""
    guard = block["guard"]
    enc = CardEnc.atleast(block["candidates"], bound=block["needed"], top_id=guard,
                          encoding=encoding)
    return [[-guard, *clause] for clause in enc.clauses]


def atmost(candidates, bound, top):
    return CardEnc.atmost(candidates, bound=bound, top_id=top,
                          encoding=EncType.seqcounter).clauses


def assignment(candidates, true_set):
    return [x if x in true_set else -x for x in candidates]


def windows(candidates, k):
    """Positional witness families: all k-blocks, and both ends plus one."""
    n = len(candidates)
    sets = []
    for start in range(n - k + 1):
        sets.append(frozenset(candidates[start:start + k]))
    for i in range(n):
        rest = [x for j, x in enumerate(candidates) if j != i][:k - 1]
        sets.append(frozenset([candidates[i], *rest]))
    for i in range(n):
        rest = [x for j, x in enumerate(candidates) if j != i][-(k - 1):]
        sets.append(frozenset([candidates[i], *rest]))
    return sets


def gadget_report(block, encoding, name):
    guard, k, candidates = block["guard"], block["needed"], block["candidates"]
    clauses = counters(block, encoding)
    top = max(max(map(abs, clause)) for clause in clauses)
    out = dict(ordinal=block["ordinal"], color=block["color"], vertex=block["vertex"],
               n=len(candidates), k=k, encoding=name,
               clauses=len(clauses), aux=top - guard)
    # E enforcement
    enforcement = clauses + atmost(candidates, k - 1, top)
    out["enforcement_unsat"] = not solve(enforcement, [guard])
    # T tightness: one witness per candidate index, three positional families
    families = windows(candidates, k)
    witnesses = 0
    for true_set in families:
        if solve(clauses, [guard, *assignment(candidates, true_set)]):
            witnesses += 1
    out["witness_sets"] = len(families)
    out["witness_sat"] = witnesses
    # G guard-false freedom
    out["guard_false_sat"] = solve(clauses, [-guard, *[-x for x in candidates]])
    # N negative control: unguarded clauses must reject a violating assignment
    assert all(clause and clause[0] == -guard for clause in clauses)
    stripped = [clause[1:] for clause in clauses]
    violating = frozenset(candidates[:k - 1])
    out["unguarded_violation_unsat"] = not solve(stripped, assignment(candidates, violating))
    # W wrong-bound sensitivity
    strong = [[-guard, *c] for c in CardEnc.atleast(
        candidates, bound=k + 1, top_id=guard, encoding=encoding).clauses]
    top_strong = max(max(map(abs, clause)) for clause in strong)
    out["too_strong_rejects_k_unsat"] = not solve(strong, [guard, *assignment(
        candidates, frozenset(candidates[:k]))])
    weak = [[-guard, *c] for c in CardEnc.atleast(
        candidates, bound=k - 1, top_id=guard, encoding=encoding).clauses]
    out["too_weak_accepts_k_minus_1_sat"] = solve(weak, [guard, *assignment(
        candidates, frozenset(candidates[:k - 1]))])
    out["true_rejects_k_minus_1_unsat"] = not solve(clauses, [guard, *assignment(
        candidates, frozenset(candidates[:k - 1]))])
    return out


def exhaustive(max_n=9):
    checks = 0
    mismatches = []
    for n in range(1, max_n + 1):
        for k in range(1, n + 1):
            guard = n + 1
            encs = {name: [[-guard, *clause] for clause in CardEnc.atleast(
                list(range(1, n + 1)), bound=k, top_id=guard,
                encoding=getattr(EncType, name)).clauses]
                for name in ("seqcounter", "kmtotalizer")}
            for bits in itertools.product((False, True), repeat=n + 1):
                expected = (not bits[-1]) or sum(bits[:-1]) >= k
                assumptions = [i if bits[i - 1] else -i for i in range(1, n + 2)]
                for name, clauses in encs.items():
                    got = solve(clauses, assumptions)
                    if got != expected:
                        mismatches.append((n, k, name, bits, got, expected))
                    checks += 1
    return dict(checks=checks, mismatches=mismatches[:5], max_n=max_n)


def atmost_controls():
    controls = []
    for n, k in ((30, 10), (41, 14), (15, 6), (31, 6)):
        top = n
        clauses = atmost(list(range(1, n + 1)), k - 1, top)
        accepts = solve(clauses, [x for x in range(1, k)])
        rejects = not solve(clauses, [x for x in range(1, k + 1)])
        controls.append(dict(n=n, k=k, accepts_k_minus_1=accepts, rejects_k=rejects))
    return controls


def main():
    started = time.time()
    item = W.row()
    family = W.family_of(item)
    _, _, _, stock_blocks, _ = W.parent_bytes(family, item, "stock")
    _, _, _, kmt_blocks, _ = W.parent_bytes(family, item, "kmt")
    senders = [b for b in stock_blocks if b["kind"] == "sender"]
    kmt_senders = [b for b in kmt_blocks if b["kind"] == "sender"]
    assert len(senders) == len(kmt_senders) == 31
    for left, right in zip(senders, kmt_senders):
        assert left["candidates"] == right["candidates"] and left["needed"] == right["needed"]

    reports = {"stock": [gadget_report(b, EncType.seqcounter, "seqcounter") for b in senders],
               "kmt": [gadget_report(b, EncType.kmtotalizer, "kmtotalizer") for b in kmt_senders]}
    small = exhaustive(9)
    controls = atmost_controls()

    def summarise(rows):
        return dict(gadgets=len(rows),
                    enforcement_unsat=sum(r["enforcement_unsat"] for r in rows),
                    witness_sat=sum(r["witness_sat"] for r in rows),
                    witness_sets=sum(r["witness_sets"] for r in rows),
                    guard_false_sat=sum(r["guard_false_sat"] for r in rows),
                    unguarded_violation_unsat=sum(r["unguarded_violation_unsat"] for r in rows),
                    too_strong_rejects=sum(r["too_strong_rejects_k_unsat"] for r in rows),
                    too_weak_accepts=sum(r["too_weak_accepts_k_minus_1_sat"] for r in rows),
                    true_rejects_k_minus_1=sum(r["true_rejects_k_minus_1_unsat"] for r in rows),
                    total_aux=sum(r["aux"] for r in rows),
                    total_clauses=sum(r["clauses"] for r in rows))

    summary = dict(
        schema=1,
        row="06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06",
        stock=summarise(reports["stock"]),
        kmt=summarise(reports["kmt"]),
        exhaustive_small=small,
        atmost_controls=controls,
        sat_calls=SAT_CALLS,
        cpu_seconds=round(time.time() - started, 3),
    )
    summary["all_checks_pass"] = (
        all(r["enforcement_unsat"] and r["guard_false_sat"] and r["unguarded_violation_unsat"]
            and r["too_strong_rejects_k_unsat"] and r["too_weak_accepts_k_minus_1_sat"]
            and r["true_rejects_k_minus_1_unsat"] and r["witness_sat"] == r["witness_sets"]
            for rows in reports.values() for r in rows)
        and not small["mismatches"]
        and all(c["accepts_k_minus_1"] and c["rejects_k"] for c in controls))
    (HERE / "stage2.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in ("stock", "kmt", "exhaustive_small",
                                              "atmost_controls", "sat_calls",
                                              "cpu_seconds", "all_checks_pass")}, indent=2))
    assert summary["all_checks_pass"], "semantic control failed"


if __name__ == "__main__":
    main()
