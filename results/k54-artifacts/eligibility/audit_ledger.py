"""m3 / direction d5 -- independent audit of the k54cut case-reduction ledger.

Checks, from the archive's raw data only (h42.json, placements.json, rect_reps,
cover.json, omitted_orbit_ids), never importing the archive's src/:

  A. every stored rectangle rep really is one representative of one orbit of the
     placement symmetry group, the orbits are pairwise disjoint, and together
     they partition all 78*78 = 6084 raw rectangles; stored orbit sizes match;
  B. every stored weight equals the number of inequivalent ordinary colourings
     of that rectangle's four crossing edges;
  C. for each placement the stored cut (side, mask) reproduces exactly the
     stored omitted-orbit list under the "every image misses the cut" rule,
     and no other stored eligible partition would have removed more;
  D. the per-placement kept/original mark and coloured-case numbers and the four
     published totals.

Usage:  python3 audit_ledger.py [--archive DIR]
Exit status 0 iff every check passed.
"""
import argparse
import gzip
import json
import sys
from itertools import combinations

sys.path.insert(0, __file__.rsplit('/', 1)[0])
import audit_lib as A

DEFAULT = ('/workspace/nucleus/work/projects/'
           'p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut')


def bit_index(pairs):
    return {p: i for i, p in enumerate(pairs)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--archive', default=DEFAULT)
    ap.add_argument('--verbose', action='store_true')
    args = ap.parse_args()
    K = args.archive.rstrip('/') + '/'

    H = A.load_h42(K + 'data/h42.json')
    A.degenerate(H)
    pls = json.load(open(K + 'data/placements.json'))
    reps = json.loads(gzip.decompress(open(K + 'data/rect_reps.json.gz', 'rb').read()))
    cover = json.load(open(K + 'results/cover.json'))
    omitted = json.loads(gzip.decompress(open(K + 'results/omitted_orbit_ids.json.gz', 'rb').read()))
    cuts = {int(k): v for k, v in cover['cuts_by_pole'].items()}
    assert len(pls) == len(reps) == len(cover['placements']) == len(omitted) == 24

    failures = []
    def bad(msg):
        failures.append(msg)
        print('FAIL:', msg)

    table = []
    for k, (pl, rs, entry, om) in enumerate(zip(pls, reps, cover['placements'], omitted), 1):
        pa, ca = pl['a']
        pb, cb = pl['b']
        poles = (pa, pb)
        group = A.placement_group(pa, ca, pb, cb, H)
        A.is_group(group)

        # ---------- A. orbits ----------
        left = [(i, j) for i, j in combinations([v for v in range(14) if v != pa], 2)]
        right = [(i, j) for i, j in combinations([v + 14 for v in range(14) if v != pb], 2)]
        allrects = set((l, r) for l in left for r in right)
        if len(allrects) != 6084:
            bad(f'placement {k}: raw rectangle set has {len(allrects)} elements')
        seen = set()
        orbits = []
        for (a, b, x, y, n, w) in rs:
            R = ((a, b), (14 + x, 14 + y))
            if R not in allrects:
                bad(f'placement {k}: rep {R} is not a raw rectangle')
            imgs = [A.act(R, g) for g in group]
            orb = set(imgs)
            if len(orb) != n:
                bad(f'placement {k}: rep {R} orbit size {len(orb)} != stored {n}')
            if orb & seen:
                bad(f'placement {k}: rep {R} orbit overlaps an earlier orbit')
            seen |= orb
            orbits.append((R, orb, imgs, w))
        if seen != allrects:
            bad(f'placement {k}: orbits cover {len(seen)} of {len(allrects)} raw rectangles')

        # ---------- B. weights ----------
        for (R, orb, imgs, w) in orbits:
            (a, b), (xx, yy) = R
            c = ca[H[a][b]]
            d = cb[H[xx - 14][yy - 14]]
            stab = [g for g, im in zip(group, imgs) if im == R]
            mine = A.weight(R, c, d, stab)
            if mine != w:
                bad(f'placement {k}: rep {R} weight {mine} != stored {w}')

        # ---------- C. cut, projections, drop rule ----------
        idx = ({p: i for i, p in enumerate(left)}, {p: i for i, p in enumerate(right)})
        proj = ([], [])
        for (R, orb, imgs, w) in orbits:
            p0 = 0
            p1 = 0
            for (l, r) in orb:
                p0 |= 1 << idx[0][l]
                p1 |= 1 << idx[1][r]
            proj[0].append(p0)
            proj[1].append(p1)
        weights = [o[3] for o in orbits]

        def crossmask(side, mask):
            out = 0
            for i, (u, v) in enumerate((left, right)[side]):
                uu, vv = u - 14 * side, v - 14 * side
                if ((mask >> uu) ^ (mask >> vv)) & 1:
                    out |= 1 << i
            return out

        def score(side, mask):
            cross = crossmask(side, mask)
            drop = [i for i, p in enumerate(proj[side]) if not p & cross]
            return sum(weights[i] for i in drop), drop

        side = entry['cut_side']
        mask = entry['first_part']
        if side not in (0, 1):
            bad(f'placement {k}: cut_side {side}')
        if mask not in cuts[poles[side]]:
            bad(f'placement {k}: stored mask {mask} not in cuts_by_pole[{poles[side]}]')
        best, drop = score(side, mask)
        if drop != om:
            bad(f'placement {k}: drop list differs from stored omitted ids '
                f'({len(drop)} vs {len(om)})')
        # no stored eligible partition of either side removes more
        bestall = -1
        bestarg = None
        for s2 in (0, 1):
            for m2 in cuts[poles[s2]]:
                v, _ = score(s2, m2)
                if v > bestall:
                    bestall, bestarg = v, (s2, m2)
        if best < bestall:
            bad(f'placement {k}: stored cut removes {best} but {bestarg} removes {bestall}')
        if entry.get('raw_permitted') != 78 * bin(crossmask(side, mask)).count('1'):
            bad(f'placement {k}: raw_permitted {entry.get("raw_permitted")} != 78*|cross|')
        if best != entry['old_colored'] - entry['kept_colored']:
            bad(f'placement {k}: stored kept_colored inconsistent')

        # ---------- D. per-placement numbers ----------
        oldm, keptm = len(rs), len(rs) - len(drop)
        oldc, keptc = sum(weights), sum(weights) - best
        for key, mine in (('old_marks', oldm), ('kept_marks', keptm),
                          ('old_colored', oldc), ('kept_colored', keptc)):
            if entry[key] != mine:
                bad(f'placement {k}: {key} stored {entry[key]} != {mine}')
        table.append(dict(placement=k, placed_poles=list(poles), group=len(group),
                          orbits=len(rs),
                          old_marks=oldm, kept_marks=keptm, old_colored=oldc, kept_colored=keptc,
                          removed_marks=len(drop), removed_colored=best,
                          cut_side=side, cut_pole=poles[side], cut_mask=mask,
                          cut_parts=(mask.bit_count(), (16383 ^ (1 << poles[side]) ^ mask).bit_count())))
        if args.verbose:
            print(k, table[-1])

    totals = {key: sum(r[key] for r in table)
              for key in ('old_marks', 'kept_marks', 'old_colored', 'kept_colored')}
    for key, val in totals.items():
        if cover['totals'][key] != val:
            bad(f'totals: {key} stored {cover["totals"][key]} != {val}')
    print('totals (independent):', totals)
    print('published totals     :', cover['totals'])
    print('placements audited:', len(table))
    print('FAILURES:', len(failures))
    json.dump(dict(totals=totals, table=table, failures=failures),
              open('ledger_audit.json', 'w'), indent=1)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
