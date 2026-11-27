#!/usr/bin/env python3
"""Generate and benchmark the R(3,3)=6 cap on each other-arm sender neighborhood."""
import argparse
import contextlib
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.solvers import Cadical195

REPO = Path(__file__).resolve().parents[3]
HARD_STUDY = Path(os.environ.get(
    "K58_HARD_STUDY", REPO / ".scratch/hard1300-paired-arm-v1/src/hard-study"))
sys.path.insert(0, str(HARD_STUDY))
import probe  # noqa: E402


def require(ok, message):
    if not ok:
        raise ValueError(message)


def family_groups(row):
    f = probe.Family(**{k: tuple(v) if k in ("profile", "root_kinds") else v
                       for k, v in row["family"].items()})
    fixed = {v for v, in probe.units(f, row["placement"])}
    positive = {v for v in fixed if v > 0}
    negative = {-v for v in fixed if v < 0}
    known = {(v - 1) // 4 for v in positive}
    edge, _ = probe.host(58)
    groups = []
    start = 1
    for n in f.profile:
        groups.append(list(range(start, start + n)))
        start += n
    return f, positive, negative, known, edge, groups


def cap_clauses(row, form, guards, scope="unconditional", encoding=EncType.seqcounter,
                top_start=None):
    """At most five color-c neighbors of x in each other root arm.

    scope=guard only emits the weaker guard-conditional form for vertices with an
    encoder guard. scope=unconditional emits the actual entailment for every
    nonroot vertex in its own root-arm color, whether or not a guard exists.
    """
    require(scope in {"guard", "unconditional"}, "unknown cap scope")
    f, positive, negative, known, edge, groups = family_groups(row)
    if scope == "guard":
        senders = [(x, c, g) for x, (c, g) in sorted(guards.items())]
    else:
        senders = [(x, c, None) for c, sites in enumerate(groups) for x in sites]
    clauses = []
    top = form.nv if top_start is None else top_start
    require(top >= form.nv, "auxiliary variable range overlaps the base formula")
    initial_top = top
    encoded_groups = 0
    candidate_literals = 0
    binary_units = 0
    for x, c, guard in senders:
        for b, other in enumerate(groups):
            if b == c:
                continue
            spokes = [edge(x, y, c) for y in other]
            candidates = [lit for lit in spokes
                          if lit not in positive and -lit not in negative
                          and (lit - 1) // 4 not in known]
            must = sum(lit in positive for lit in spokes)
            cap = 5 - must
            require(cap >= 0, "frozen spokes already violate the arm cap")
            prefix = [] if guard is None else [-guard]
            if cap == 0:
                clauses.extend([prefix + [-lit] for lit in candidates])
                binary_units += len(candidates)
            elif len(candidates) > cap:
                encoded = CardEnc.atmost(candidates, bound=cap, top_id=top,
                                         encoding=encoding)
                top = max(top, encoded.nv)
                clauses.extend([prefix + clause for clause in encoded.clauses])
                encoded_groups += 1
                candidate_literals += len(candidates)
    stats = dict(scope=scope, encoding=encoding, clauses=len(clauses),
                 new_variables=top - initial_top, next_top=top,
                 encoded_groups=encoded_groups,
                 candidate_literals=candidate_literals, zero_cap_literals=binary_units,
                 clause_literals=sum(map(len, clauses)))
    return clauses, stats


def lower_clauses(row, form, guards, kind="arm4", top_start=None):
    """Conditional lower counts following from total >= 14 and each arm <= 5.

    arm4 encodes each residual arm count >= 4; pair9 encodes every residual
    two-arm count >= 9. Fixed positive spokes reduce these residual bounds.
    The guard is exactly the original at-least-14 guard, never an assumption.
    """
    require(kind in {"arm4", "pair9"}, "unknown lower-count family")
    f, positive, negative, known, edge, groups = family_groups(row)
    top = form.nv if top_start is None else top_start
    require(top >= form.nv, "auxiliary variable range overlaps the base formula")
    initial_top = top
    clauses = []
    counter_groups = 0
    impossible_guards = 0
    for x, (c, guard) in sorted(guards.items()):
        arms = []
        for b, other in enumerate(groups):
            if b == c:
                continue
            spokes = [edge(x, y, c) for y in other]
            candidates = [lit for lit in spokes
                          if lit not in positive and -lit not in negative
                          and (lit - 1) // 4 not in known]
            must = sum(lit in positive for lit in spokes)
            arms.append((candidates, must))
        selected = [([arm], 4) for arm in arms] if kind == "arm4" else [
            (list(pair), 9) for pair in itertools.combinations(arms, 2)]
        for chosen, full_bound in selected:
            candidates = [lit for arm in chosen for lit in arm[0]]
            must = sum(arm[1] for arm in chosen)
            bound = full_bound - must
            if bound <= 0:
                continue
            if len(candidates) < bound:
                clauses.append([-guard])
                impossible_guards += 1
                continue
            encoded = CardEnc.atleast(candidates, bound=bound, top_id=top,
                                      encoding=EncType.seqcounter)
            top = max(top, encoded.nv)
            clauses.extend([[-guard] + clause for clause in encoded.clauses])
            counter_groups += 1
    stats = dict(kind=kind, clauses=len(clauses), new_variables=top - initial_top,
                 next_top=top, counter_groups=counter_groups,
                 impossible_guards=impossible_guards,
                 clause_literals=sum(map(len, clauses)))
    return clauses, stats


def prepare(rank):
    record = probe.rows[rank - 1]
    guards = {}
    start = time.process_time()
    raw, form, direct, extended = probe.build(record, guards)
    base_cpu = time.process_time() - start
    require(hashlib.sha256(raw).hexdigest() == record["input_sha256"],
            "original input hash mismatch")
    require(form.clauses == list(__import__("pysat.formula", fromlist=["CNF"]).CNF(
        from_string=raw.decode()).clauses), "base CNF changed")
    return record, raw, form, direct, extended, guards, base_cpu


def solve_one(form, extra, conflicts, seed):
    with Cadical195(bootstrap_with=form.clauses) as solver:
        solver.configure({"seed": seed})
        solver.append_formula(extra)
        before = time.process_time()
        solver.conf_budget(conflicts)
        answer = solver.solve_limited()
        search_cpu = time.process_time() - before
        stats = solver.accum_stats()
    require(answer is None or answer is False,
            "this exploratory UNSAT-only panel unexpectedly returned SAT")
    return dict(status="OPEN" if answer is None else "UNSAT",
                conflicts=stats["conflicts"], decisions=stats["decisions"],
                propagations=stats["propagations"], restarts=stats["restarts"],
                search_cpu_seconds=search_cpu)


def run_panel(ranks, conflicts, seed, output):
    results = []
    for rank in ranks:
        record, raw, form, direct, extended, guards, base_cpu = prepare(rank)
        variants = {}
        for scope in ("guard", "unconditional"):
            start = time.process_time()
            clauses, stats = cap_clauses(probe.geometry[record["id"]], form, guards, scope)
            stats["generation_cpu_seconds"] = time.process_time() - start
            variants[scope] = (clauses, stats)
        extras = {
            "stock": [],
            "guard_caps": variants["guard"][0],
            "unconditional_caps": variants["unconditional"][0],
            "unconditional_caps_plus_direct": variants["unconditional"][0] + direct,
        }
        names = list(extras)
        if rank % 2 == 0:
            names.reverse()
        policies = {}
        for name in names:
            extra = extras[name]
            result = solve_one(form, extra, conflicts, seed)
            result["added_clauses"] = len(extra)
            policies[name] = result
            print(rank, name, json.dumps(result, sort_keys=True), flush=True)
        row_result = dict(rank=rank, id=record["id"], input_sha256=record["input_sha256"],
                          profile=record["profile"], kinds=record["kinds"],
                          charge=int(record["charge"]), proof_bytes=int(record["proof_bytes"]),
                          seed=seed, conflict_budget=conflicts,
                          base_clauses=len(form.clauses), base_variables=form.nv,
                          base_generation_cpu_seconds=base_cpu,
                          cap_variants={k: v[1] for k, v in variants.items()},
                          direct_clauses=len(direct), policies=policies)
        results.append(row_result)
        temporary = output.with_suffix(output.suffix + ".tmp")
        temporary.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
        temporary.replace(output)
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ranks", default="8,132,255,340")
    parser.add_argument("--conflicts", type=int, default=60000)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(args.conflicts > 0 and args.seed >= 0, "invalid budget or seed")
    ranks = [int(x) for x in args.ranks.split(",")]
    require(all(1 <= rank <= len(probe.rows) for rank in ranks), "invalid rank")
    require(not args.output.exists(), "output exists; refusing to overwrite")
    run_panel(ranks, args.conflicts, args.seed, args.output)


if __name__ == "__main__":
    main()
