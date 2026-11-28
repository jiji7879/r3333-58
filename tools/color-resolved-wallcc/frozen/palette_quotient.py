"""Normalize the remaining global color permutations in a marked-root cover."""
from dataclasses import replace
from functools import cache
from itertools import permutations, product

from charge_plan import plan_for_types
from gluing import (
    automorphisms, data, families, named_template, normalized_kinds, profiles,
    representatives,
)


@cache
def palette_map(size, kind, old_color, new_color, palette):
    before = named_template(size, kind, old_color)
    after = named_template(size, kind, new_color)

    def extend(prefix, remaining):
        i = len(prefix)
        if not remaining:
            return prefix
        for x in sorted(remaining):
            if all(after[x][y] == palette[before[i][j]] for j, y in enumerate(prefix)):
                result = extend((*prefix, x), remaining - {x})
                if result is not None:
                    return result
        return None

    result = extend((), set(range(size)))
    if result is None:
        raise AssertionError((size, kind, old_color, new_color, palette))
    return result


def normalize_position(size, kind, x):
    automorphism = min(automorphisms(size, kind), key=lambda g: g[x])
    return automorphism[x], automorphism


def key(family, indices):
    return (
        family.mark_position, family.marked_size, family.marked_kind,
        family.root_position, indices,
    )


@cache
def transporter(f, palette):
    profile, kinds, arm = f.profile, f.root_kinds, f.arm
    size, kind = f.marked_size, f.marked_kind
    beta = palette_map(size, kind, arm, arm, palette)
    root, correction = normalize_position(size, kind, beta[f.root_position])
    beta = tuple(correction[x] for x in beta)
    mark = 0
    if kinds[arm] != "-":
        alpha = palette_map(profile[arm], kinds[arm], arm, arm, palette)
        mark, _ = normalize_position(profile[arm], kinds[arm], alpha[f.mark_position])
    new_family = replace(f, root_position=root, mark_position=mark)
    supports, choices, _ = data(f)
    new_supports, new_choices, actions = data(new_family)
    options = []
    for b, new_source in new_supports:
        old_index = next(i for i,(c,_) in enumerate(supports) if palette[c] == b)
        c, source = supports[old_index]
        if kinds[c] == "-":
            options.append((old_index, (0,)))
            continue
        row = len(options)
        index = {embedding:i for i,embedding in enumerate(new_choices[row])}
        alpha = palette_map(profile[c], kinds[c], c, b, palette)
        alpha_order = [next(i for i,s in enumerate(source) if beta[s] == t)
                       for t in new_source]
        group = automorphisms(profile[b], kinds[b])
        indices = tuple(
            index[min(tuple(auto[alpha[placement[i]]] for i in alpha_order) for auto in group)]
            for placement in choices[old_index]
        )
        options.append((old_index, indices))
    return new_family, tuple(options), actions


def palettes(profile, kinds, arm):
    return tuple(p for p in permutations(range(4))
                 if p[arm] == arm and p != (0,1,2,3)
                 and all((profile[i],kinds[i]) == (profile[p[i]],kinds[p[i]]) for i in range(4)))


def transport(f, indices, palette):
    other, options, actions = transporter(f, palette)
    raw = tuple(index[indices[i]] for i,index in options)
    rep = min(tuple(action[i] for action,i in zip(row,raw)) for row in actions)
    return other, rep


def family_representatives(profile, kinds, arm, chosen):
    colors = palettes(profile, kinds, arm)
    for f in families(58, profile, kinds, arm):
        if f.mark_position not in chosen:
            continue
        for indices in representatives(f):
            orig = key(f, indices)
            keep = True
            for palette in colors:
                alternative, rep = transport(f, indices, palette)
                if alternative.mark_position in chosen and key(alternative, rep) < orig:
                    keep = False
                    break
            if keep:
                yield f, indices


def main():
    raw = normalized = 0
    for p in profiles(58):
        before = after = 0
        for k in product(*[("T","U") if x >= 15 else ("-",) for x in p]):
            if not normalized_kinds(p,k):
                continue
            c, plan = plan_for_types(p,k)
            d = sum(1 for arm, _, chosen in plan if chosen
                    for _ in family_representatives(p,k,arm,chosen))
            print(p, "".join(k), c, d, plan, flush=True)
            before += c
            after += d
        print("PROFILE", p, before, after, flush=True)
        raw += before
        normalized += after
    print("TOTAL",raw,normalized)


if __name__ == "__main__":
    main()
