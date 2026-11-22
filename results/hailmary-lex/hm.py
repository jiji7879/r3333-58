#!/usr/bin/env python3
"""Hail-mary harness for the cover's hard cases.

Cuts here are SOUND only. The one implemented is a lex-leader symmetry break:
two vertices u,v are twins when swapping them preserves the pinned unit set
exactly, so the transposition is an automorphism of the case formula; applying
lex-leaders for a *matching* of such transpositions (they commute) cannot lose a
model. Validated on a satisfiable instance with 45 twin pairs: SAT before and
after (`python3 probe3.py`).

Nothing unproved is applied. A case closed here is a closure; a lead obtained
with a speculative cut would be labelled as such, and none is used.
"""
import sys, os, json, subprocess
sys.path.insert(0, '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.ultramath/smwp3xc7p/m3/w/k58-solver/k58')
from joint_plan import cases
from gluing import host, units
from pysat.formula import CNF, IDPool

KISSAT = '/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'
ORDER = 58


def case_cnf(profile, idx):
    it = cases(tuple(int(x) for x in profile))
    for k, (f, pl, i, ch) in enumerate(it):
        if k == idx:
            break
    else:
        raise SystemExit(f'{profile} has no case {idx}')
    lit, base = host(ORDER)
    raw = units(f, pl)
    us = sorted({c[0] for c in raw if isinstance(c, (list, tuple)) and len(c) == 1})
    extra = [c for c in raw if not (isinstance(c, (list, tuple)) and len(c) == 1)]
    return f, lit, base, us, extra


def twins(lit, us, nv=ORDER):
    pinned = set(us)
    out = []
    for u in range(nv):
        for v in range(u + 1, nv):
            ok = True
            for w in range(nv):
                if w == u or w == v:
                    continue
                for c in range(4):
                    if ((lit(min(u, w), max(u, w), c) in pinned) !=
                            (lit(min(v, w), max(v, w), c) in pinned)):
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                out.append((u, v))
    return out


def matching(tw):
    used = set()
    out = []
    for u, v in tw:
        if u in used or v in used:
            continue
        used.add(u)
        used.add(v)
        out.append((u, v))
    return out


def lex_leader(cnf, lit, u, v, nv=ORDER):
    vp = IDPool(start_from=cnf.nv + 1)
    ws = [w for w in range(nv) if w != u and w != v]
    peq_prev = None
    peqs, lts = [], []
    for w in ws:
        x = [lit(min(u, w), max(u, w), c) for c in range(4)]
        y = [lit(min(v, w), max(v, w), c) for c in range(4)]
        lt = vp.id(('lt', w))
        for c in range(4):
            for c2 in range(c + 1, 4):
                cnf.append([-x[c], -y[c2], lt])
        lts.append(lt)
        peq = vp.id(('peq', w))
        if peq_prev is None:
            for c in range(4):
                cnf.append([-x[c], -y[c], peq])
        else:
            for c in range(4):
                cnf.append([-peq_prev, -x[c], -y[c], peq])
        peqs.append(peq)
        peq_prev = peq
    big = []
    for i, lt in enumerate(lts):
        p = vp.id(('p', i))
        if i == 0:
            cnf.append([-lt, p])
        else:
            cnf.append([-peqs[i - 1], -lt, p])
        big.append(p)
    big.append(peqs[-1])
    cnf.append(big)


def main():
    profile = sys.argv[1].split(',')
    indices = [int(x) for x in sys.argv[2].split(',')]
    secs = int(sys.argv[3])
    use_lex = '--lex' in sys.argv
    out = []
    for idx in indices:
        f, lit, base, us, extra = case_cnf(profile, idx)
        tw = twins(lit, set(us))
        mt = matching(tw)
        print(json.dumps(dict(case=idx, profile=profile, units=len(us),
                              twin_pairs=len(tw), matching=len(mt))), flush=True)
        for name in (['bare', 'lex'] if use_lex else ['bare']):
            cnf = CNF(from_clauses=base + [[x] for x in us] + extra)
            if name == 'lex':
                for u, v in mt:
                    lex_leader(cnf, lit, u, v)
            path = f'{name}_{idx}.cnf'
            cnf.to_file(path)
            drat = f'{name}_{idx}.drat'
            r = subprocess.run([KISSAT, '-q', '--time=%d' % secs, path, drat],
                               capture_output=True, text=True)
            st = 'UNSAT' if r.returncode == 20 else ('SAT' if r.returncode == 10 else 'UNKNOWN')
            size = os.path.getsize(drat) if st == 'UNSAT' and os.path.exists(drat) else 0
            rec = dict(case=idx, arm=name, status=st, drat=size, vars=cnf.nv,
                       clauses=len(cnf.clauses), lex_pairs=(len(mt) if name == 'lex' else 0))
            print(json.dumps(rec), flush=True)
            out.append(rec)
    json.dump(out, open('hm_results.json', 'w'), indent=1)


if __name__ == '__main__':
    main()
