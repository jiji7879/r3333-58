#!/usr/bin/env python3
"""Conservative same-query accounting and split/stop decisions.

This module performs no search. A CLOSED flag is an input assertion whose proof
and coverage obligations have already been discharged elsewhere. Solver UNKNOWN
and TIMEOUT are normalized to OPEN and can never produce CLOSED.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

OPEN_ALIASES = {"OPEN", "UNKNOWN", "TIMEOUT", "LIMIT", "CONFLICT_LIMIT"}


def child_closure(
    statuses: list[str],
    *,
    coverage_verified: bool,
    all_unsat_proofs_replayed: bool,
    intended_parent: bool = True,
) -> str:
    """Return CLOSED_CUTOFF only under every proof-side prerequisite.

    SAT of an exact child may refute a universal cutoff goal, but is not an
    UNSAT result for that cutoff or for its unrestricted parent. We consequently
    return OPEN here and require a separately checked witness workflow.
    """
    normalized = ["OPEN" if s.upper() in OPEN_ALIASES else s.upper() for s in statuses]
    if not normalized or "SAT" in normalized:
        return "OPEN"
    if (
        intended_parent
        and coverage_verified
        and all_unsat_proofs_replayed
        and all(s == "UNSAT" for s in normalized)
    ):
        return "CLOSED_CUTOFF"
    return "OPEN"


def compare_pair(observation: dict[str, Any]) -> dict[str, Any]:
    """Compare two attempts only with identical scope and a declared equal cap.

    Expected input shape::

      {case_id, scope,
       budget_relation: "EQUAL_TOTAL_CONFLICT_ALLOCATION",
       split: {closed, conflicts, budget_conflicts},
       direct: {closed, conflicts, budget_conflicts}}

    `closed` concerns the named scope (typically an H cutoff), not a whole row.
    Actual conflicts are kept distinct from the allocation. The caller must not
    mark budgets equal merely because unequal historical caps look similar.
    """
    split = observation["split"]
    direct = observation["direct"]
    base = {
        "case_id": observation.get("case_id"),
        "scope": observation.get("scope"),
        "wall_clock_conclusion": "NOT_MEASURED",
        "general_speedup_claim": False,
    }
    if not observation.get("case_id") or not observation.get("scope"):
        return {**base, "outcome": "MISSING_IDENTITY", "may_split_on_this_evidence": False}
    if observation.get("budget_relation") != "EQUAL_TOTAL_CONFLICT_ALLOCATION":
        return {**base, "outcome": "INCOMPARABLE_BUDGETS", "may_split_on_this_evidence": False}
    if not (0 <= split["conflicts"] <= split["budget_conflicts"]):
        return {**base, "outcome": "INVALID_SPLIT_WORK", "may_split_on_this_evidence": False}
    if not (0 <= direct["conflicts"] <= direct["budget_conflicts"]):
        return {**base, "outcome": "INVALID_DIRECT_WORK", "may_split_on_this_evidence": False}
    if split["budget_conflicts"] != direct["budget_conflicts"]:
        return {**base, "outcome": "INCOMPARABLE_BUDGETS", "may_split_on_this_evidence": False}

    if not isinstance(split.get("closed"), bool) or not isinstance(direct.get("closed"), bool):
        return {**base, "outcome": "INVALID_BOOLEAN_STATUS", "may_split_on_this_evidence": False}
    sc, dc = split["closed"], direct["closed"]
    if sc and dc:
        if split["conflicts"] < direct["conflicts"]:
            outcome = "SPLIT_FEWER_TOTAL_CONFLICTS"
        elif split["conflicts"] > direct["conflicts"]:
            outcome = "DIRECT_FEWER_TOTAL_CONFLICTS"
        else:
            outcome = "EQUAL_TOTAL_CONFLICTS"
    elif sc:
        outcome = "ONLY_SPLIT_CLOSED_WITHIN_EQUAL_ALLOCATION"
    elif dc:
        outcome = "ONLY_DIRECT_CLOSED_WITHIN_EQUAL_ALLOCATION"
    else:
        outcome = "BOTH_OPEN_INCONCLUSIVE"
    support = outcome in {
        "SPLIT_FEWER_TOTAL_CONFLICTS", "ONLY_SPLIT_CLOSED_WITHIN_EQUAL_ALLOCATION"
    }
    return {**base, "outcome": outcome, "may_split_on_this_evidence": support}


def next_split_decision(
    comparison: dict[str, Any], *, coverage_verified: bool,
    total_budget_exhausted: bool, already_split: bool,
    direct_pilot_open: bool = False,
    split_measurement_budget_reserved: bool = False,
) -> dict[str, Any]:
    """Bound experiments to one level; never recursively spawn a solver herd.

    With no matched result, a caller may explicitly reserve a single split-pilot
    allocation after a direct pilot ended OPEN. That action gathers measurement;
    it is not evidence of a speedup. Existing plans are not recursively deepened.
    """
    if not coverage_verified:
        action, reason = "HOLD_OPEN", "MISSING_COVERAGE_PROOF"
    elif total_budget_exhausted:
        action, reason = "STOP_OPEN", "TOTAL_BUDGET_EXHAUSTED"
    elif already_split:
        action, reason = "HOLD_OPEN", "NO_RECURSIVE_SPLIT_BY_DEFAULT"
    elif comparison.get("may_split_on_this_evidence"):
        action, reason = "SPLIT_ONCE_WITH_SHARED_TOTAL_CAP", comparison["outcome"]
    elif direct_pilot_open and split_measurement_budget_reserved:
        action, reason = "MEASURE_ONE_BOUNDED_SPLIT", "DIRECT_OPEN_PILOT_NOT_SPEEDUP_EVIDENCE"
    else:
        action, reason = "HOLD_OPEN_OR_DIRECT_WITHIN_CAP", "INSUFFICIENT_COMPARABLE_MEASUREMENT"
    return {
        "action": action,
        "reason": reason,
        "timeout_is_open": True,
        "new_solver_herd": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("observation", type=Path, help="JSON input for compare_pair")
    args = parser.parse_args()
    print(json.dumps(compare_pair(json.loads(args.observation.read_text())), indent=2))


if __name__ == "__main__":
    main()
