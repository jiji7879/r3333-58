"""Use the largest incoming-ticket count among the critical root groups."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha256
from itertools import islice, product
import json
import os
from pathlib import Path
from time import monotonic
import subprocess

from pysat.formula import CNF

from gluing import (
    automorphisms, counts, families, host, normalized_kinds, profiles,
    representatives, units,
)


def threshold(profile):
    """At least this many senders in one critical group of a balanced root."""
    critical = [d for d in profile if d >= 15]
    incoming_from_critical = sum(critical) - (sum(profile) - sum(critical))
    return max(0, -(-incoming_from_critical // len(critical)))


def critical_arms(profile, kinds):
    """Choose one arm for each class permutable by global color renaming."""
    seen = set()
    for arm, (size, kind) in enumerate(zip(profile, kinds)):
        if size >= 15 and (size, kind) not in seen:
            yield arm
            seen.add((size, kind))


def choose_dense_orbits(size, kind, target, costs):
    needed = size - target + 1
    best = {0: (0, ())}
    for slot, cost in sorted(costs.items()):
        weight = len({auto[slot] for auto in automorphisms(size, kind)})
        for covered, (old_cost, chosen) in tuple(best.items()):
            new = min(needed, covered + weight)
            pair = (old_cost + cost, (*chosen, slot))
            best[new] = min(pair, best.get(new, pair))
    return best[needed]


def make_plan(profile):
    bound = threshold(profile)
    if bound <= 0:
        return {}
    plan = {}
    options = [("T","U") if d >= 15 else ("-",) for d in profile]
    for kinds in product(*options):
        if not normalized_kinds(profile, kinds):
            continue
        for arm in critical_arms(profile, kinds):
            fs = tuple(families(58, profile, kinds, arm))
            costs = {}
            for f in fs:
                costs[f.mark_position] = costs.get(f.mark_position, 0) + counts(f)[1]
            cost, selected = choose_dense_orbits(profile[arm], kinds[arm], bound, costs)
            plan["".join(kinds), arm] = (cost, selected)
    return plan


def branch_iterator(profile):
    for (kind, arm), (cost, chosen) in make_plan(profile).items():
        index = 0
        for f in families(58, profile, tuple(kind), arm):
            if f.mark_position not in chosen:
                continue
            for placement in representatives(f):
                yield f, placement, index
                index += 1
        assert index == cost


def marked_threshold(family, fixed, bound, tables=False, total_critical=False, full_root=False):
    """Require at least bound neighbors in the selected arm to send a ticket."""
    from pysat.card import CardEnc

    p = family.profile
    n = sum(p) + 1
    lit, _ = host(n)
    highest = 4 * (n * (n - 1) // 2)
    positive = {clause[0] for clause in fixed if clause[0] > 0}
    negative = {-clause[0] for clause in fixed if clause[0] < 0}
    known = {(literal - 1) // 4 for literal in positive}
    colors = [c for c, d in enumerate(p) for _ in range(d)]
    extra, selectors, all_selectors, root_selectors = [], [], [], []
    critical_mass = sum(d for d in p if d >= 15)
    total = 2*critical_mass - sum(p) if total_critical else 0
    root_goal = critical_mass if full_root else 0
    a = family.arm
    for x, c in enumerate(colors, 1):
        if c != a and not full_root and (not total_critical or p[c] < 15):
            continue
        candidates = []
        needed = 14
        for y, b in enumerate(colors, 1):
            if b == c:
                continue
            e = lit(x, y, c)
            if e in positive:
                needed -= 1
            elif e not in negative and (e - 1) // 4 not in known:
                candidates.append(e)
        if needed <= 0:
            root_goal -= 1
            if c == a:
                bound -= 1
            if p[c] >= 15:
                total -= 1
        elif needed <= len(candidates):
            highest += 1
            guard = highest
            root_selectors.append(guard)
            if p[c] >= 15:
                all_selectors.append(guard)
            if c == a:
                selectors.append(guard)
            threshold_clauses = CardEnc.atleast(candidates, bound=needed, top_id=highest)
            highest = max(highest, threshold_clauses.nv)
            extra.extend([-guard, *clause] for clause in threshold_clauses.clauses)
            if tables and c == a:
                from support_tables import support_clauses
                highest, support = support_clauses(
                    family, x, guard, highest, positive, negative, known
                )
                extra.extend(support)
    for limits, minimum in ((selectors, bound), (all_selectors, total), (root_selectors, root_goal)):
        if minimum > len(limits):
            return [[]]
        if minimum > 0:
            requirement = CardEnc.atleast(limits, bound=minimum, top_id=highest)
            highest = max(highest, requirement.nv)
            extra.extend(requirement.clauses)
    return extra


def solve_case(family, placement, branch, bound, args, output):
    stem = output / f"{''.join(family.root_kinds)}_{family.arm}_{branch}"
    receipt = stem.with_suffix(".jsonl")
    if receipt.exists():
        return
    fixed = units(family, placement)
    _, base = host(58)
    extra = marked_threshold(
        family, fixed, bound, getattr(args, "tables", False), getattr(args, "total_critical", False),
        getattr(args, "full_root", False)
    )
    stem.parent.mkdir(exist_ok=True, parents=True)
    cnf, drat, log = (stem.with_suffix(s) for s in (".cnf", ".drat", ".log"))
    CNF(from_clauses=base + fixed + extra).to_file(str(cnf))
    solver = getattr(args, "solver_identity", None)
    if solver:
        formula_hash = sha256(cnf.read_bytes()).hexdigest()
    start = monotonic()
    command = [args.kissat, "--quiet", f"--time={args.seconds}",
               f"--conflicts={args.budget}", str(cnf), str(drat)]
    with log.open("wb") as stream:
        with subprocess.Popen(command, stdout=stream, stderr=subprocess.STDOUT) as process:
            _, wait_status, usage = os.wait4(process.pid, 0)
            process.returncode = os.waitstatus_to_exitcode(wait_status)
    elapsed = monotonic() - start
    status = {20: "UNSAT", 10: "SAT", 0: "OPEN"}.get(process.returncode, "ERROR")
    if status == "OPEN":
        cnf.unlink()
        drat.unlink(missing_ok=True)
    execution = {}
    if solver:
        execution = dict(solver=solver, command=command, exit_code=process.returncode,
                         formula_sha256=formula_hash)
    temporary = receipt.with_suffix(".tmp")
    temporary.write_text(json.dumps(dict(
        family=vars(family), placement=placement, branch=branch, status=status,
        charge=bound, extra_clauses=len(extra), elapsed=round(elapsed, 4),
        cpu_seconds=round(usage.ru_utime+usage.ru_stime, 4),
        peak_rss_kib=usage.ru_maxrss, proof_bytes=drat.stat().st_size if drat.exists() else 0,
        formula_bytes=cnf.stat().st_size if cnf.exists() else 0,
        budget=args.budget, seconds=args.seconds, tables=getattr(args, "tables", False),
        total_critical=getattr(args, "total_critical", False), full_root=getattr(args, "full_root", False),
        **execution,
    )) + "\n")
    temporary.replace(receipt)
    if status in {"SAT", "ERROR"}:
        raise RuntimeError(f"{status}: {log}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile")
    parser.add_argument("--kissat")
    parser.add_argument("--output")
    parser.add_argument("--seconds", type=int, default=18)
    parser.add_argument("--budget", type=int, default=400000)
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()
    if args.profile is None:
        for p in profiles(58):
            plan = make_plan(p)
            print(p, threshold(p), sum(c for c, _ in plan.values()), plan)
        return
    p = tuple(map(int, args.profile.split(",")))
    bound = threshold(p)
    stream = iter(branch_iterator(p))
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        while batch := tuple(islice(stream, 2*args.workers)):
            for _ in pool.map(lambda case: solve_case(*case, bound, args, Path(args.output)), batch):
                pass


if __name__ == "__main__":
    main()
