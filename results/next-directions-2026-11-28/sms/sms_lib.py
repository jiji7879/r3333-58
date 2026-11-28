#!/usr/bin/env python3
"""Shared coordinates for the restricted one-colour (colour 0) SMS *reimplementation*.

NOT stock SMS.  Native SMS at commit 63958bd could not be built here (see
sms-blocker.md).  This module only provides:
  * the exact K58 colour-0 coordinates of the retained ordinary parent,
  * the candidate relabelling group H = Sym({38..46}) x Sym({52..57}),
  * the recorded formula bijection used for an SMS-shaped variable numbering,
  * the strict lex-indicator (``certificate'') rule for one colour only.

All mathematical assertions live in the callers' verification scripts.
"""
from itertools import combinations
from math import comb

ORDER = 58
PAIRS = list(combinations(range(ORDER), 2))
NEDGE = len(PAIRS)                      # 1653
INDEX = {pair: r for r, pair in enumerate(PAIRS)}
CELL2 = tuple(range(38, 47))            # 9 frozen-unit twin vertices
CELL3 = tuple(range(52, 58))            # 6 frozen-unit twin vertices
NVAR = 19533
PHYS = 4 * NEDGE                        # 6612


def colour0_var(r):
    """Original DIMACS id of the colour-0 variable of pair index r."""
    return 4 * r + 1


def c0_lit(r, value):
    """Signed original literal asserting G[pair_r] == value (value 1 == colour 0)."""
    var = colour0_var(r)
    return var if value else -var


# ---------------------------------------------------------------- formula bijection
def reindex(old):
    """Recorded bijection 1..19533 -> 1..19533.

    colour-0 physical vars  (4r+1)      -> r+1          (first 1653, SMS edge order)
    other physical vars                 -> 1654 .. 6612
    auxiliaries 6613..19533             -> unchanged
    """
    if old <= PHYS:
        v = old - 1
        r, colour = divmod(v, 4)
        if colour == 0:
            return r + 1
        return NEDGE + 1 + 3 * r + (colour - 1)
    return old


def unindex(new):
    if new <= NEDGE:
        return 4 * (new - 1) + 1
    if new <= PHYS:
        w = new - NEDGE - 1
        r, k = divmod(w, 3)
        return 4 * r + 1 + (k + 1)
    return new


def check_bijection():
    image = [reindex(v) for v in range(1, NVAR + 1)]
    assert sorted(image) == list(range(1, NVAR + 1)), "reindex is not a bijection"
    assert all(unindex(reindex(v)) == v for v in range(1, NVAR + 1))
    return True


# ---------------------------------------------------------------- candidate group
def cell_of(v):
    if v in CELL2:
        return 2
    if v in CELL3:
        return 3
    return None


def transpositions():
    """The 51 within-cell transpositions; every one preserves the 438 signed units."""
    out = []
    for cell in (CELL2, CELL3):
        for a, b in combinations(cell, 2):
            out.append((a, b))
    return tuple(out)


def perm_of_transposition(a, b):
    perm = list(range(ORDER))
    perm[a], perm[b] = b, a
    return tuple(perm)


def inverse(perm):
    inv = [0] * ORDER
    for u, w in enumerate(perm):
        inv[w] = u
    return tuple(inv)


def apply_to_pair(perm, pair):
    u, v = pair
    a, b = perm[u], perm[v]
    return (a, b) if a < b else (b, a)


def moved_pairs(perm):
    """Sorted (i, phi(i)) over colour-0 positions, where W(perm.G)[i] = G[phi(i)].

    phi is induced by perm^{-1} on pairs.  For a transposition phi is an
    involution, so each unordered pair of positions appears twice; the walk in
    ``certificate`` stops at the first forced difference, so that is harmless.
    Nothing below assumes an involution.
    """
    inv = inverse(perm)
    out = []
    for r, pair in enumerate(PAIRS):
        image = apply_to_pair(inv, pair)
        other = INDEX[image]
        if other != r:
            out.append((r, other))
    return tuple(out)


_CACHE = {}


def move_table(perm):
    key = perm
    if key not in _CACHE:
        _CACHE[key] = moved_pairs(perm)
    return _CACHE[key]


# ---------------------------------------------------------------- lex indicator
def certificate(assignment, perm):
    """Strict lex-indicator certificate, or None.

    ``assignment`` maps colour-0 pair index -> forced value (1 == edge of colour 0)
    for a partial assignment A.  Returns ``(clause_pairs, witness)`` where
    ``clause_pairs`` is the list of (pair_index, forced_value) making up the
    certificate: every completion of A must have L(perm.G) < L(G), first
    differing at the final entry, which is (1, 0) for (r, r') with r < r'.

    Rule (partial check in the sense of the CP2021 method): walk positions in
    increasing lex order; positions fixed by perm are identical in both words;
    a moved position is only usable if A forces *both* copies, and if it forces
    them equal it is added to the prefix; the first moved position whose two
    copies are forced to different values ends the walk, and it witnesses a
    strict decrease exactly when W(G)=1 and W(perm.G)=0.
    """
    table = move_table(perm)
    prefix = []
    for r, other in table:
        a = assignment.get(r)
        b = assignment.get(other)
        if a is None or b is None:
            return None
        if a != b:
            if a == 1 and b == 0:
                return prefix + [(r, 1), (other, 0)], (r, other)
            return None                     # strict increase: not a witness
        prefix.append((r, a))
        prefix.append((other, b))
    return None                              # words identical everywhere


def clause_of(cert):
    """Clause (original DIMACS literals) falsified exactly by the certificate."""
    lits = []
    seen = set()
    for r, value in cert:
        if r in seen:
            continue
        seen.add(r)
        lits.append(-colour0_var(r) if value else colour0_var(r))
    return tuple(lits)


def evaluate_words(word, perm):
    """Independent numeric check of the strict lex indicator on a total word."""
    inv = inverse(perm)
    image = [word[INDEX[apply_to_pair(inv, pair)]] for pair in PAIRS]
    return image


def first_difference(word, perm):
    image = evaluate_words(word, perm)
    for r in range(NEDGE):
        if image[r] != word[r]:
            return r, image[r], word[r]
    return None
