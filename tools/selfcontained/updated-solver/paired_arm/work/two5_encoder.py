#!/usr/bin/env python3
"""Guarded exact-support lower bounds for the hard1300 original CNFs.

Under g[x] (at least 14 colour-c spokes outside x's root arm), each other
arm supplies >=4 spokes and each pair of other arms supplies >=9.  This is
an immediate consequence of the <=5 per-arm cap proved by R(3,3)=6.
"""
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import sys
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PKG = HERE.parent / 'source' / 'hard-study'
sys.path.insert(0, str(PKG))
sys.path.insert(0, str(PKG / 'encoder'))
from pysat.card import CardEnc, EncType
from cover_evidence import formula_chunks, identity
from gluing import Family, units, host

ROWS = __import__('probe').rows
GEOMETRY = __import__('probe').geometry


def sha(data):
    return hashlib.sha256(data).hexdigest()


def original(rank):
    r = ROWS[rank - 1]
    row = GEOMETRY[r['id']]
    assert identity(row) == r['id']
    raw = b''.join(formula_chunks(row, dict(tables=True, total_critical=True,
                                           full_root=True)))
    assert sha(raw) == r['input_sha256'], (rank, sha(raw), r['input_sha256'])
    return r, row, raw


def family(row):
    d = dict(row['family'])
    for k in ('profile', 'root_kinds'):
        d[k] = tuple(d[k])
    return Family(**d)


def guard_map(row):
    guards = {}
    def watch(frame, event, arg):
        if event == 'call' and frame.f_code.co_name == 'atleast':
            prev = frame.f_back
            if prev.f_code.co_name == 'marked_threshold':
                v = prev.f_locals
                if frame.f_locals.get('lits') is v.get('candidates') and 'guard' in v:
                    guards[v['x']] = (v['c'], v['guard'])
    sys.setprofile(watch)
    try:
        b''.join(formula_chunks(row, dict(tables=True, total_critical=True,
                                         full_root=True)))
    finally:
        sys.setprofile(None)
    assert len(guards) > 20
    return guards


def dimensions(row, guards):
    f = family(row)
    fixed = {v for v, in units(f, row['placement'])}
    pos = {v for v in fixed if v > 0}
    neg = {-v for v in fixed if v < 0}
    known = {(v - 1)//4 for v in pos}
    edge, _ = host(58)
    groups = [list(range(sum(f.profile[:i])+1, sum(f.profile[:i+1])+1))
              for i in range(4)]
    answer = []
    for x in sorted(guards):
        c, g = guards[x]
        arms = []
        for b, other in enumerate(groups):
            if b == c:
                continue
            spokes = [edge(x, y, c) for y in other]
            must = [l for l in spokes if l in pos]
            optional = [l for l in spokes if l not in pos and l not in neg
                        and (l-1)//4 not in known]
            omitted = [l for l in spokes if l not in must and l not in optional]
            assert len(must)+len(optional)+len(omitted) == len(spokes)
            assert not set(must) & set(optional)
            arms.append(dict(arm=b, vertices=other, spokes=spokes,
                             must=must, optional=optional, omitted=omitted))
        answer.append(dict(sender=x, color=c, guard=g, arms=arms))
    return answer


def bound_specs(row, guards, pairs=False):
    specs = []
    for sender in dimensions(row, guards):
        g = sender['guard']
        arm_sets = list(itertools.combinations(sender['arms'], 2)) if pairs \
                   else [(a,) for a in sender['arms']]
        target = 9 if pairs else 4
        for aa in arm_sets:
            must = sum((a['must'] for a in aa), [])
            optional = sum((a['optional'] for a in aa), [])
            key = '-'.join(str(a['arm']) for a in aa)
            k = target - len(must)
            specs.append(dict(sender=sender['sender'], color=sender['color'],
                              guard=g, arms=key, must=must,
                              optional=optional, need=k, target=target))
    return specs


def generate(rank, mode='arm', encoding='seq', scope='all'):
    assert mode in ('arm', 'pair', 'two5', 'distribution')
    assert scope in ('all', 'marked', 'critical')
    assert encoding in ('seq', 'direct')
    assert mode in ('arm', 'pair') or encoding == 'seq'
    r, row, raw = original(rank)
    guards = guard_map(row)
    f = family(row)
    if scope == 'marked':
        guards = {x:(c,g) for x,(c,g) in guards.items() if c == f.arm}
    elif scope == 'critical':
        guards = {x:(c,g) for x,(c,g) in guards.items() if f.profile[c] >= 15}
    assert guards
    header, rest = raw.split(b'\n', 1)
    p, cnf, nv, nc = header.split()
    assert (p, cnf) == (b'p', b'cnf')
    top, count = int(nv), int(nc)
    lines, emitted = [], []

    def emit(spec, gate=None):
        nonlocal top
        g = spec['guard'] if gate is None else gate
        optional, k = spec['optional'], spec['need']
        if k <= 0:
            clauses = []
        elif k > len(optional):
            clauses = [[-g]]
        elif encoding == 'seq':
            enc = CardEnc.atleast(optional, bound=k, top_id=top,
                                  encoding=EncType.seqcounter)
            top = max(top, enc.nv)
            clauses = [[-g] + c for c in enc.clauses]
        else:
            width = len(optional)-k+1
            clauses = [[-g] + list(s)
                       for s in itertools.combinations(optional, width)]
        for c in clauses:
            lines.append(' '.join(map(str, c)).encode() + b' 0\n')
        emitted.append(dict(sender=spec['sender'], color=spec['color'],
                            guard=g, arms=spec['arms'], fixed=len(spec['must']),
                            optional=len(optional), need=k,
                            clauses=len(clauses),
                            first=clauses[0] if clauses else None))

    if mode in ('arm', 'pair'):
        for spec in bound_specs(row, guards, pairs=(mode == 'pair')):
            emit(spec)
    else:
        # q[x,b] means arm b really supplies at least five.  Under g, the
        # three pair clauses make at least two q's true.  Model extension is
        # valid because the original formula gives distribution 5,5,4/5,5,5.
        for sender in dimensions(row, guards):
            lower = {a['arm']: a for a in sender['arms']}
            specs = {a['arm']: spec for a, spec in
                     zip(sender['arms'], bound_specs(row, {sender['sender']:
                         (sender['color'], sender['guard'])}))}
            qs = {}
            for a in sender['arms']:
                top += 1
                q = qs[a['arm']] = top
                spec = dict(specs[a['arm']])
                spec['need'] -= 1  # five rather than four
                emit(spec, gate=q)
                if mode == 'distribution':
                    lower_spec = dict(specs[a['arm']])
                    emit(lower_spec)
            for b, d in itertools.combinations(sorted(qs), 2):
                clause = [-sender['guard'], qs[b], qs[d]]
                lines.append(' '.join(map(str, clause)).encode() + b' 0\n')
                emitted.append(dict(sender=sender['sender'],
                                    color=sender['color'], guard=sender['guard'],
                                    arms=f'{b}-{d}', selector_clause=clause,
                                    clauses=1, first=clause))
    out = f'p cnf {top} {count+len(lines)}\n'.encode() + rest + b''.join(lines)
    info = dict(schema='guarded-support-lower-bound/v1', rank=rank,
                id=r['id'], original_sha256=r['input_sha256'],
                original_variables=int(nv), original_clauses=count,
                mode=mode, encoding=encoding, scope=scope,
                variables=top, added_variables=top-int(nv),
                added_clauses=len(lines), augmented_sha256=sha(out),
                specifications=emitted)
    return out, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('rank', type=int)
    ap.add_argument('--mode', choices=['arm', 'pair', 'two5', 'distribution'], default='arm')
    ap.add_argument('--encoding', choices=['seq', 'direct'], default='seq')
    ap.add_argument('--scope', choices=['all', 'marked', 'critical'], default='all')
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--info', action='store_true')
    args = ap.parse_args()
    t0 = time.process_time()
    out, info = generate(args.rank, args.mode, args.encoding, args.scope)
    info['generation_cpu_seconds'] = time.process_time()-t0
    info['generator_sha256'] = sha(Path(__file__).read_bytes())
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_bytes(out)
    args.out.with_suffix('.json').write_text(json.dumps(info, indent=2, sort_keys=True)+'\n')
    if args.info:
        print(json.dumps(info, indent=2, sort_keys=True))
    else:
        print(json.dumps({k:v for k,v in info.items() if k != 'specifications'}, sort_keys=True))

if __name__ == '__main__':
    main()
