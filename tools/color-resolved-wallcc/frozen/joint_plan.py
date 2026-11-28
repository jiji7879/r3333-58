"""Optimize the cover after grouping mark positions under global palette symmetry."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from functools import cache
from itertools import islice, product
from pathlib import Path

from dense import solve_case
from gluing import automorphisms, normalized_kinds, positions, profiles
from palette_quotient import family_representatives, normalize_position, palette_map, palettes


@cache
def mark_classes(profile, kinds, arm):
    size, kind = profile[arm], kinds[arm]
    if kind == "-":
        return ((0, size),)
    changes = palettes(profile, kinds, arm)
    moves = [palette_map(size,kind,arm,arm,p) for p in changes]
    group = automorphisms(size,kind)
    options = []
    for q in positions(size,kind):
        orbit = {q, *(normalize_position(size,kind,g[q])[0] for g in moves)}
        if q != min(orbit):
            continue
        weight = len({g[x] for g in group for x in orbit})
        options.append((q, weight))
    assert sum(weight for _, weight in options) == size
    return tuple(options)


def arm_options(p, kinds, arm, copies):
    size = p[arm]
    costs = [
        (q, weight, sum(1 for _ in family_representatives(p,kinds,arm,(q,))))
        for q, weight in mark_classes(p,kinds,arm)
    ]
    weighted = {0:(0,())}
    for q, weight, cost in costs:
        for covered,(past,qs) in tuple(weighted.items()):
            total = covered+weight
            candidate = (past+cost,(*qs,q))
            weighted[total] = min(weighted.get(total,candidate),candidate)
    for required in range(1,size+2):
        enough = size-required+1
        cost, qs = min(value for w,value in weighted.items() if w >= enough)
        yield copies*(required-1), cost, (arm, required, qs, cost)


@cache
def choose_plan(profile, kinds, surplus=0):
    groups = defaultdict(list)
    for i, spec in enumerate(zip(profile,kinds)):
        groups[spec].append(i)
    target = surplus + sum(size for size in profile if size>=15)
    dp = {0:(0,())}
    for arms in groups.values():
        a = min(arms)
        choices = list(arm_options(profile,kinds,a,len(arms)))
        updated = {}
        for prior_maximum,(prior_cost,prior_choices) in dp.items():
            for misses, cost, choice in choices:
                maximum = prior_maximum+misses
                if maximum >= target:
                    continue
                candidate=(prior_cost+cost,(*prior_choices,choice))
                updated[maximum] = min(updated.get(maximum,candidate),candidate)
        dp=updated
    return min((cost,-maximum,chosen) for maximum,(cost,chosen) in dp.items())


def kinds_for(p):
    for kinds in product(*[("T","U") if size>=15 else ("-",) for size in p]):
        if normalized_kinds(p,kinds):
            yield kinds


def count(surplus=0):
    total=0
    for p in profiles(58):
        subtotal=0
        for kind in kinds_for(p):
            cost, neg_cap, plan=choose_plan(p,kind,surplus)
            subtotal+=cost
            print(p,"".join(kind),cost,-neg_cap,plan,flush=True)
        print("PROFILE",p,subtotal,flush=True)
        total+=subtotal
    print("TOTAL",total,flush=True)


def cases(profile, chosen_kinds=None, surplus=0):
    for kinds in kinds_for(profile):
        if chosen_kinds and kinds != chosen_kinds:
            continue
        cost, _, plan=choose_plan(profile,kinds,surplus)
        actual=0
        for arm, required, marks, expected in plan:
            emitted = 0
            for mark in marks:
                for f, placement in family_representatives(profile,kinds,arm,(mark,)):
                    yield f,placement,emitted,required
                    emitted+=1
            assert emitted==expected
            actual+=emitted
        assert actual==cost


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile")
    parser.add_argument("--strict",action="store_true")
    parser.add_argument("--kinds")
    parser.add_argument("--kissat")
    parser.add_argument("--output")
    parser.add_argument("--tables",action="store_true")
    parser.add_argument("--total-critical",action="store_true")
    parser.add_argument("--full-root",action="store_true")
    parser.add_argument("--workers",type=int,default=5)
    parser.add_argument("--budget",type=int,default=300000)
    parser.add_argument("--seconds",type=int,default=15)
    parser.add_argument("--start",type=int,default=0)
    parser.add_argument("--stop",type=int)
    args=parser.parse_args()
    if not args.profile:
        count(int(args.strict))
        return
    p=tuple(map(int,args.profile.split(",")))
    kinds=tuple(args.kinds) if args.kinds else None
    cohort=islice(cases(p,kinds,int(args.strict)),args.start,args.stop)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        while batch := tuple(islice(cohort, 2*args.workers)):
            for _ in pool.map(lambda case: solve_case(*case,args,Path(args.output)),batch):
                pass


if __name__=="__main__":
    main()
