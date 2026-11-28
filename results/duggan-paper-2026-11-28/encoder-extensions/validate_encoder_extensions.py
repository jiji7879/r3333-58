#!/usr/bin/env python3
"""Artifact-matched controls for EncoderExtensions.lean.

Run from .ultramath/smwzxq4fl/m6 after installing python-sat into ./vendor:
  PYTHONPATH=vendor python3 validate_encoder_extensions.py

The script never invokes a solver and emits no wall/UNSAT claim.  It checks
(1) the exact PySAT/Lean staggered-counter clauses and the guarded extension,
including exhaustive rejection when a true guard is semantically false; and
(2) a real support_tables.py sample, including wrong-selector controls.
"""
from __future__ import annotations

from hashlib import sha256
from importlib.metadata import version
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
VENDOR = HERE / "vendor"
sys.path.insert(0, str(VENDOR))
sys.path.insert(0, str(ROOT / "tools/color-resolved-wallcc/frozen"))

from pysat.card import CardEnc, EncType  # noqa: E402
import gluing  # noqa: E402
import support_tables  # noqa: E402


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def seq_index(k, d, j):
    if d == 0:
        return 2 * j
    if d == 1:
        return 2 * j + 1
    return d * k + j


def lean_counter_dimacs(x, n, k, top):
    """Independent DIMACS transcription of K58.SequentialCounter.counter."""
    def cell(d, j):
        return top + 1 + seq_index(k, d, j)

    out = []
    if n <= k:
        return out, 0
    if k == 0:
        return [[-x[i]] for i in range(n)], 0
    if k == n - 1:
        return [[-x[i] for i in range(n)]], 0
    for d in range(n - k):
        for j in range(k):
            if j == 0:
                out.append([-x[d + j], cell(d, j)])
            else:
                out.append([-x[d + j], -cell(d, j - 1), cell(d, j)])
            if d + 1 < n - k:
                out.append([-cell(d, j), cell(d + 1, j)])
        out.append([-x[d + k], -cell(d, k - 1)])
    return out, (n - k) * k


def lean_atleast_dimacs(x, bound, top):
    # Flip only physical input literals; leave every counter cell unchanged.
    return lean_counter_dimacs([-a for a in x], len(x), len(x) - bound, top)


def satisfies(assignment, clauses):
    return all(any(assignment.get(abs(l), False) == (l > 0) for l in c)
               for c in clauses)


def constructive_atleast_extension(x, bound, guard, nv, bits, guard_bit):
    """The valuation constructed by the native-at-least extension proof."""
    n = len(x)
    a = {guard: guard_bit}
    a.update({v: bit for v, bit in zip(x, bits)})
    for v in range(max([guard, *x], default=0) + 1, nv + 1):
        a[v] = False
    k = n - bound
    if guard_bit and n > k and k != 0 and k != n - 1:
        top = guard
        false_prefix = [0]
        for bit in bits:
            false_prefix.append(false_prefix[-1] + int(not bit))
        for d in range(n - k):
            for j in range(k):
                cell = top + 1 + seq_index(k, d, j)
                # Native PySAT leaves the at-most counter cells unflipped.
                # Only its physical input literals are negated.
                a[cell] = (j + 1 <= false_prefix[d + j + 1])
    return a


def counter_controls():
    exact_formulas = exact_clause_count = 0
    positive_extensions = negative_rejections = 0
    legacy_flip_all_mismatches = 0
    legacy_example = None
    checked_real = None
    for n in range(2, 10):
        x = list(range(1, n + 1))
        guard = n + 1
        for bound in range(n + 1):
            enc = CardEnc.atleast(x, bound=bound, top_id=guard,
                                  encoding=EncType.seqcounter)
            mirror, used = lean_atleast_dimacs(x, bound, guard)
            guarded = [[-guard, *c] for c in enc.clauses]
            guarded_mirror = [[-guard, *c] for c in mirror]
            counter_positive, _ = lean_counter_dimacs(
                x, n, n - bound, guard)
            legacy_flip_all = [[-ell for ell in c] for c in counter_positive]
            if legacy_flip_all != mirror:
                legacy_flip_all_mismatches += 1
                if n == 3 and bound == 2:
                    legacy_example = dict(n=n, bound=bound,
                        native=mirror, legacy_flip_all=legacy_flip_all)
            require(guarded == guarded_mirror,
                    f"ordered counter mismatch n={n} bound={bound}")
            if bound == 0:
                # PySAT discards top_id for its empty, trivially true encoding;
                # the Lean CNF is empty too and has no allocation field.
                require((enc.nv, used) == (0, 0),
                        f"unexpected bound-zero allocation n={n}")
            else:
                require(enc.nv == guard + used,
                        f"counter top mismatch n={n} bound={bound}")
            exact_formulas += 1
            exact_clause_count += len(guarded)
            if n <= 6:
                for bits in product((False, True), repeat=n):
                    count = sum(bits)
                    # Both a semantically correct true guard and an arbitrary
                    # false guard must admit the proof's extension.
                    for guard_bit in (False, True):
                        if guard_bit and count < bound:
                            continue
                        a = constructive_atleast_extension(
                            x, bound, guard, enc.nv, bits, guard_bit)
                        require(satisfies(a, guarded),
                                f"counter extension failed n={n} bound={bound}")
                        require(all(a[v] == bit for v, bit in zip(x, bits))
                                and a[guard] == guard_bit,
                                "counter extension changed an old variable")
                        positive_extensions += 1
            if n <= 5 and bound > 0:
                aux = list(range(guard + 1, enc.nv + 1))
                require(len(aux) <= 10, "negative control unexpectedly large")
                for bits in product((False, True), repeat=n):
                    if sum(bits) >= bound:
                        continue
                    base = {guard: True, **dict(zip(x, bits))}
                    for aux_bits in product((False, True), repeat=len(aux)):
                        a = {**base, **dict(zip(aux, aux_bits))}
                        require(not satisfies(a, guarded),
                                f"unsound counter extension n={n} bound={bound}")
                    negative_rejections += 1

    require(legacy_flip_all_mismatches > 0 and legacy_example is not None,
            "legacy flip-all negative control failed to distinguish the CNFs")
    return dict(pysat_version=version("python-sat"), exact_formulas=exact_formulas,
                exact_clauses=exact_clause_count,
                positive_extensions=positive_extensions,
                exhaustive_false_guard_rejections=negative_rejections,
                legacy_flip_all_mismatches=legacy_flip_all_mismatches,
                legacy_flip_all_differs_from_native=True,
                legacy_example=legacy_example,
                real_candidate=checked_real)


def independently_allowed(size, kind, target_arm, marked_color):
    """Re-enumerate P4/C5 supports, then check their shape by permutations."""
    matrix = gluing.named_template(size, kind, target_arm)
    palette = [c for c in range(4) if c not in (target_arm, marked_color)]
    assert len(palette) == 2
    result = []
    for order in (4, 5):
        for pts_tuple in combinations(range(size), order):
            pts = frozenset(pts_tuple)
            if any(matrix[u][v] == marked_color for u, v in combinations(pts, 2)):
                continue
            edge = lambda u, v: matrix[u][v] == palette[0]
            if order == 5:
                good_shape = any(
                    all(edge(perm[i], perm[j]) ==
                        (j == i + 1 or (i == 0 and j == 4))
                        for i, j in combinations(range(5), 2))
                    for perm in permutations(pts_tuple))
            else:
                good_shape = any(
                    all(edge(perm[i], perm[j]) == (j == i + 1)
                        for i, j in combinations(range(4), 2))
                    for perm in permutations(pts_tuple))
            if good_shape:
                result.append(pts)
    return tuple(result)


def support_controls():
    profile = (16, 16, 13, 12)
    kinds = ("U", "T", "-", "-")
    family = next(gluing.families(58, profile, kinds, 0))
    indices = next(gluing.representatives(family))
    fixed = gluing.units(family, indices)
    positive = {c[0] for c in fixed if c[0] > 0}
    negative = {-c[0] for c in fixed if c[0] < 0}
    known = {(literal - 1) // 4 for literal in positive}
    lit, _ = gluing.host(58)
    colors = [c for c, d in enumerate(profile) for _ in range(d)]
    x = 2
    require(colors[x - 1] == family.arm, "unexpected real candidate colour")
    candidates = []
    needed = 14
    for y, b in enumerate(colors, 1):
        if b == family.arm:
            continue
        e = lit(x, y, family.arm)
        if e in positive:
            needed -= 1
        elif e not in negative and (e - 1) // 4 not in known:
            candidates.append(e)
    require((needed, len(candidates)) == (14, 41), "real candidate changed")

    # Match the genuinely emitted guarded counter for that candidate too.
    counter_guard = 6614
    enc = CardEnc.atleast(candidates, bound=needed, top_id=counter_guard,
                          encoding=EncType.seqcounter)
    actual_guarded = [[-counter_guard, *c] for c in enc.clauses]
    mirror, used = lean_atleast_dimacs(candidates, needed, counter_guard)
    require(actual_guarded == [[-counter_guard, *c] for c in mirror],
            "real guarded counter differs from Lean mirror")
    require(enc.nv == counter_guard + used, "real counter allocation differs")

    # Mirror dense.py's contiguous allocation for this candidate: the guarded
    # counter is followed immediately by support selectors.
    guard = counter_guard
    highest = enc.nv
    highest_actual, actual = support_tables.support_clauses(
        family, x, guard, highest, positive, negative, known)
    require((highest_actual - highest, len(actual)) == (112, 1793),
            "support sample is no longer the intended nontrivial control")

    expected = []
    full = []  # supportFamilyCNF, modulo placement of its one disjunction.
    groups = []
    for b, (size, kind) in enumerate(zip(profile, kinds)):
        if b == family.arm or kind == "-":
            continue
        # This enumeration is independent of support_tables.allowed_supports.
        allowed_all = independently_allowed(size, kind, b, family.arm)
        require(allowed_all == support_tables.allowed_supports(
                    size, kind, b, family.arm),
                "independent P4/C5 catalogue differs")
        start = sum(profile[:b]) + 1
        adjacent = [lit(x, start + j, family.arm) for j in range(size)]
        must = {j for j, ell in enumerate(adjacent) if ell in positive}
        cannot = {j for j, ell in enumerate(adjacent)
                  if ell not in positive and
                  (ell in negative or (ell - 1) // 4 in known)}
        feasible = [p for p in allowed_all if must <= p and not (cannot & p)]
        selectors = []
        records = []
        for possible in feasible:
            highest += 1
            selector = highest
            selectors.append(selector)
            records.append((selector, possible))
            for j, ell in enumerate(adjacent):
                emitted = [-selector, ell if j in possible else -ell]
                full.append(emitted)  # Lean also includes pinned positions.
                if j not in must and j not in cannot:
                    expected.append(emitted)
        group_disjunction = [-guard, *selectors]
        expected.append(group_disjunction)
        full.append(group_disjunction)
        groups.append(dict(arm=b, size=size, kind=kind, adjacent=adjacent,
                           feasible=feasible, selectors=selectors))

    require(actual == expected, "actual support output differs in order or content")
    require(highest == highest_actual, "independent selector allocation differs")
    actual_set = {tuple(c) for c in actual}
    full_set = {tuple(c) for c in full}
    require(actual_set <= full_set, "actual support clauses are not a proved subset")
    require(len(actual) == len(actual_set) and len(full) == len(full_set),
            "duplicate clauses make the subset count ambiguous")
    require(len(groups) == 1 and len(groups[0]["feasible"]) == 112,
            "unexpected group count")

    # Choose one feasible physical support, complete its candidate list to
    # exactly 14 true inputs, and use one joint counter+support extension.
    # This is the actual contiguous dense.py clause order, not two unrelated
    # gadgets sharing a fresh-variable range.
    group = groups[0]
    adjacent = group["adjacent"]
    physical0 = group["feasible"][0]
    support_values = {ell: (j in physical0) for j, ell in enumerate(adjacent)}
    true_left = needed - sum(support_values.get(ell, False) for ell in candidates)
    require(0 <= true_left <= sum(ell not in support_values for ell in candidates),
            "cannot complete real candidate to its threshold")
    bits = []
    for ell in candidates:
        if ell in support_values:
            bits.append(support_values[ell])
        elif true_left:
            bits.append(True)
            true_left -= 1
        else:
            bits.append(False)
    bits = tuple(bits)
    require(sum(bits) == needed, "candidate completion missed threshold")
    witness = constructive_atleast_extension(
        candidates, needed, guard, enc.nv, bits, True)
    counter_and_old = dict(witness)
    for index, selector in enumerate(group["selectors"]):
        witness[selector] = (index == 0)
    combined = actual_guarded + actual
    require(satisfies(witness, combined) and satisfies(witness, full),
            "correct joint counter/support extension failed")
    require(all(witness[v] == val for v, val in counter_and_old.items()),
            "support extension changed a counter or old value")

    # A wrong selected support must fail an actually emitted implication while
    # leaving the valid counter extension unchanged.
    wrong = dict(witness)
    for index, selector in enumerate(group["selectors"]):
        wrong[selector] = (index == 1)
    require(not satisfies(wrong, actual), "wrong selector was accepted by emitted CNF")
    require(not satisfies(wrong, full), "wrong selector was accepted by full CNF")

    # False guard admits an arbitrary support with all selectors false.
    invalid_base = {guard: False, **{ell: False for ell in adjacent}}
    false_guard = dict(invalid_base)
    false_guard.update({s: False for s in group["selectors"]})
    require(satisfies(false_guard, actual) and satisfies(false_guard, full),
            "false-guard extension failed")

    # With a true guard and an invalid support every individual selector is
    # wrong, so no choice of one or several selectors can repair the formula.
    invalid_true = dict(invalid_base)
    invalid_true[guard] = True
    wrong_selector_failures = 0
    for selector, possible in zip(group["selectors"], group["feasible"]):
        trial = dict(invalid_true)
        trial.update({s: False for s in group["selectors"]})
        trial[selector] = True
        require(not satisfies(trial, actual),
                "invalid support acquired a valid selector")
        wrong_selector_failures += 1
    trial = dict(invalid_true)
    trial.update({s: False for s in group["selectors"]})
    require(not satisfies(trial, actual), "empty selector disjunction accepted")

    serial = json.dumps(actual, separators=(",", ":")).encode()
    full_serial = json.dumps(full, separators=(",", ":")).encode()
    combined_serial = json.dumps(combined, separators=(",", ":")).encode()
    return dict(
        family=dict(profile=profile, kinds=kinds, arm=family.arm,
                    mark_position=family.mark_position,
                    marked_size=family.marked_size,
                    marked_kind=family.marked_kind,
                    root_position=family.root_position, indices=indices),
        fixed_units=len(fixed), fixed_sha256=sha256(
            json.dumps(fixed, separators=(",", ":")).encode()).hexdigest(),
        candidate=dict(vertex=x, needed=needed, candidate_count=len(candidates),
                       guard=counter_guard, clauses=len(actual_guarded),
                       auxiliary_top=enc.nv, exact_lean_match=True),
        support=dict(guard=guard, selector_count=len(group["selectors"]),
                     first_selector=group["selectors"][0],
                     last_selector=group["selectors"][-1],
                     emitted_clauses=len(actual), full_learn_clause_count=len(full),
                     emitted_sha256=sha256(serial).hexdigest(),
                     full_sha256=sha256(full_serial).hexdigest(),
                     contiguous_counter_support_clauses=len(combined),
                     contiguous_counter_support_sha256=sha256(combined_serial).hexdigest(),
                     actual_equals_independent_regeneration=True,
                     emitted_is_exact_subset_of_proved_full_family=True,
                     joint_counter_support_extension_accepted=True,
                     wrong_selector_rejected=True,
                     false_guard_extension_accepted=True,
                     invalid_true_guard_selector_rejections=wrong_selector_failures)
    )


def main():
    counters = counter_controls()
    support = support_controls()
    counters["real_candidate"] = support["candidate"]
    receipt = dict(status="PASS", scope="encoding extension controls only; no UNSAT or wall claim",
                   counters=counters, support=support["support"],
                   real_case={k: v for k, v in support.items() if k not in ("support", "candidate")})
    out = HERE / "validation.json"
    out.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
