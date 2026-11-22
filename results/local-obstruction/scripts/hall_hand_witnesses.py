"""The two pair-level witnesses the record describes but does not store as files.

(a) WALL §13, the five-line construction:  A = Q1|Q2|Q3 with
    Q1={0,1,4,12,14}, Q2={3,7,8,9,10}, Q3={2,5,6,11,13}, sigma=(3,1,2);
    word j has M_0 = Q_j, M_{sigma(i)} = Q_i for i != j, empty at sigma(j);
    seven copies of word j go in each arm whose root colour is not sigma(j).
(b) WALL §16, "a fifth witness": the extremal words 002102211112020 (missing 3,
    arm 1), 332032200002323 (missing 1, arm 2), 330130011110303 (missing 2,
    arm 3), fourteen copies each, pair colour = the smaller endpoint's missing
    colour.

In both, the colour-0 support of every outside vertex is fixed by the words, so
the I = A half of the Hall test -- |N_0(S) cap A| >= |S| - 1 for every S -- is
decided by the words alone, with no reference to the (partly free) pair colours.
The reduced test is  (forall T subset of A with |T| <= 13)  c(T) <= |T| + 1,
c(T) = #{x : M_0(x) subset of T}, and it also gives the exact worst margin
max_S (|S| - 1 - |U M_0(S)|) subject to |S| <= 15.
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def zeta_test(words, n=15, cap=15):
    """words: list of 15-tuples.  Returns (max_margin, argmax T, argmax S)."""
    cnt = [0] * (1 << n)
    for w in words:
        m = 0
        for a, c in enumerate(w):
            if c == 0:
                m |= 1 << a
        cnt[m] += 1
    z = cnt[:]
    for b in range(n):
        bit = 1 << b
        for T in range(1 << n):
            if T & bit:
                z[T] += z[T ^ bit]
    best = None
    for T in range(1 << n):
        tsz = bin(T).count("1")
        if tsz > cap - 2:
            continue
        # S = the words inside T; we may take any |T|+2 of them if there are enough
        k = min(z[T], cap)
        margin = k - 1 - tsz
        if best is None or margin > best[0]:
            best = (margin, T, k)
    return best

# (a) the five-line construction
Q = [{0, 1, 4, 12, 14}, {3, 7, 8, 9, 10}, {2, 5, 6, 11, 13}]
sigma = {1: 3, 2: 1, 3: 2}
w13 = []
for j in (1, 2, 3):
    w = [None] * 15
    for a in Q[j - 1]:
        w[a] = 0
    for i in (1, 2, 3):
        if i == j:
            continue
        for a in Q[i - 1]:
            w[a] = sigma[i]
    for a in range(15):
        if w[a] is None:
            w[a] = sigma[j]
    assert w.count(0) == 5 and None not in w
    assert sum(1 for v in w if v == sigma[j]) == 0      # sigma(j) is the empty colour
    w13 += [tuple(w)] * 14

# (b) the extremal-word witness
ext = ["002102211112020", "332032200002323", "330130011110303"]
wet = []
for s in ext:
    w = tuple(int(c) for c in s)
    assert len(w) == 15 and w.count(0) == 5, s
    wet += [w] * 14

for name, ws in (("WALL §13 five-line construction", w13),
                 ("WALL §16 extremal-word witness", wet)):
    m, T, k = zeta_test(ws)
    print("%-34s supports: %s" % (name, sorted(set(tuple(a for a, c in enumerate(w) if c == 0) for w in ws))))
    print("   distinct words %d, copies 14 each; worst margin with |S|<=15 and I = A: %d"
          % (len(set(ws)), m))
    print("   violating T = %s (|T|=%d), S = %d words inside T, |U M_0(S)| <= %d < %d = |S|-1"
          % (sorted(a for a in range(15) if (T >> a) & 1), bin(T).count("1"), k, bin(T).count("1"), k - 1))
    assert m > 0, "no violation"
print("\nBoth described constructions violate the Hall inequality on the I = A half already.")
