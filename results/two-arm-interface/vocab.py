"""Under the "cross pairs are all colour 1" construction, every word of arm B
must have its 1-part inside a fixed 5-set P and every word of arm C its 1-part
inside A \\ P.  This counts, for every 5-set M_0, how many completions exist
under each of the two constraints, and how many completions exist at all.
"""
import itertools
import sys

from model import template_colours

M = template_colours(15, twisted=True)
N = 15
ADJ = {f: [0] * N for f in (1, 2, 3)}
for a in range(N):
    for b in range(a + 1, N):
        ADJ[M[a][b]][a] |= 1 << b
        ADJ[M[a][b]][b] |= 1 << a


def indep(f, mask):
    m = mask
    while m:
        v = (m & -m).bit_length() - 1
        if ADJ[f][v] & m:
            return False
        m &= m - 1
    return True


def completions(zero_mask, one_allowed=None):
    """All (m1, m2, m3) partitions of the complement of zero_mask with each mf
    f-independent and m1 inside one_allowed (a mask) if given."""
    allmask = (1 << N) - 1
    rest = allmask & ~zero_mask
    out = 0
    pts = [v for v in range(N) if rest >> v & 1]
    for m1 in range(1 << len(pts)):
        s1 = 0
        for i, v in enumerate(pts):
            if m1 >> i & 1:
                s1 |= 1 << v
        if one_allowed is not None and (s1 & ~one_allowed):
            continue
        if not indep(1, s1):
            continue
        rem = rest & ~s1
        pts2 = [v for v in range(N) if rem >> v & 1]
        for m2 in range(1 << len(pts2)):
            s2 = 0
            for i, v in enumerate(pts2):
                if m2 >> i & 1:
                    s2 |= 1 << v
            if not indep(2, s2):
                continue
            s3 = rem & ~s2
            if indep(3, s3):
                out += 1
    return out


if __name__ == "__main__":
    P = (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4)
    ALL = (1 << N) - 1
    tot = [0, 0, 0]
    worst = [10 ** 9, 10 ** 9, 10 ** 9]
    zero_count = {0: 0, 1: 0, 2: 0}
    hist = [[0] * 4 for _ in range(3)]
    for z in itertools.combinations(range(N), 5):
        zm = sum(1 << v for v in z)
        c0 = completions(zm, None)
        cB = completions(zm, P)
        cC = completions(zm, ALL & ~P)
        for i, c in enumerate((c0, cB, cC)):
            tot[i] += c
            worst[i] = min(worst[i], c)
            zero_count[i] += (1 if c == 0 else 0)
        for i, c in enumerate((c0, cB, cC)):
            if c == 0:
                hist[i][0] += 1
            elif c <= 5:
                hist[i][1] += 1
            elif c <= 50:
                hist[i][2] += 1
            else:
                hist[i][3] += 1
    print("total completions over all 3003 five-sets:")
    print("   unconstrained:", tot[0], " min per five-set:", worst[0], " empty:", zero_count[0])
    print("   M_1 inside P :", tot[1], " min per five-set:", worst[1], " empty:", zero_count[1])
    print("   M_1 inside A\\\\P:", tot[2], " min per five-set:", worst[2], " empty:", zero_count[2])
    print("histograms [0, 1-5, 6-50, >50]:")
    for i, name in enumerate(("unconstrained", "in P", "in A\\P")):
        print("  ", name, hist[i])
