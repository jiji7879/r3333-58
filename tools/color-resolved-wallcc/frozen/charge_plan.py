"""Minimize a weighted local cover over per-group incoming-ticket thresholds."""
from collections import defaultdict
from itertools import product

from dense import choose_dense_orbits
from gluing import counts, families, normalized_kinds, profiles


def plan_for_types(profile, kinds):
    groups = defaultdict(list)
    for arm, description in enumerate(zip(profile, kinds)):
        groups[description].append(arm)
    sent = sum(d for d in profile if d >= 15)
    dp = {0: (0, ())}
    for (size, kind), arms in groups.items():
        a = min(arms)
        costs = defaultdict(int)
        for f in families(58, profile, kinds, a):
            costs[f.mark_position] += counts(f)[1]
        states = []
        for minimum in range(1, size+2):
            if minimum == size+1:
                cost, chosen = 0, ()
            elif kind == "-":
                cost, chosen = costs[0], (0,)
            else:
                cost, chosen = choose_dense_orbits(size, kind, minimum, costs)
            states.append((len(arms)*(minimum-1), cost, (a, minimum, chosen)))
        new = {}
        for prev_max, (prev_cost, prev_chosen) in dp.items():
            for miss_max, cost, selection in states:
                maximum = prev_max + miss_max
                if maximum >= sent:
                    continue
                candidate = (prev_cost + cost, (*prev_chosen, selection))
                new[maximum] = min(new.get(maximum, candidate), candidate)
        dp = new
    assert dp
    return min(dp.values())


def main():
    old = {
        (16,16,16,9):360, (16,16,15,10):2832, (16,16,14,11):210,
        (16,15,15,11):27928, (16,16,13,12):210, (16,15,14,12):2058,
        (15,15,15,12):301576, (16,15,13,13):2058, (16,14,14,13):168,
        (15,15,14,13):12834, (15,14,14,14):1596,
    }
    overall = hybrid = 0
    for p in profiles(58):
        subtotal = 0
        for kinds in product(*[("T","U") if d >= 15 else ("-",) for d in p]):
            if normalized_kinds(p, kinds):
                cost, plan = plan_for_types(p, kinds)
                received_cap = sum(
                    (minimum-1) * sum((d, t) == (p[arm], kinds[arm])
                                      for d, t in zip(p, kinds))
                    for arm, minimum, _ in plan
                )
                assert received_cap < sum(d for d in p if d >= 15)
                subtotal += cost
                print(p, "".join(kinds), cost, plan)
        overall += subtotal
        hybrid += min(old[p], subtotal)
        print("PROFILE", p, old[p], subtotal)
    print("TOTAL", sum(old.values()), overall, hybrid)


if __name__ == "__main__":
    main()
