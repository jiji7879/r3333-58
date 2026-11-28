#!/usr/bin/env python3
"""Independent full-scan BCP and clause-wise residual audit (different algorithm)."""
import argparse, hashlib, json
from pathlib import Path


def parse(path):
    raw = Path(path).read_bytes(); lines = raw.splitlines(); f = lines[0].split()
    assert f[:2] == [b'p', b'cnf']; nv, nc = int(f[2]), int(f[3]); clauses = []
    for line in lines[1:]:
        if not line or line.startswith(b'c'): continue
        vals = [int(x) for x in line.split()]; assert vals[-1] == 0
        clauses.append(tuple(vals[:-1]))
    assert len(clauses) == nc
    return raw, nv, clauses


def value(lit, ass):
    a = ass[abs(lit)] if abs(lit) < len(ass) else 0
    if not a: return None
    return (a == 1) if lit > 0 else (a == -1)


def closure(clauses, nv):
    ass = [0] * (nv + 1); passes = 0
    while True:
        passes += 1; inferred = set()
        for ci, clause in enumerate(clauses):
            unknown = 0; last = None; satisfied = False
            for x in clause:
                v = value(x, ass)
                if v is True: satisfied = True; break
                if v is None: unknown += 1; last = x
            if satisfied: continue
            assert unknown, ('BCP conflict', ci, clause)
            if unknown == 1: inferred.add(last)
        if not inferred: break
        changed = False
        for x in sorted(inferred, key=abs):
            old = ass[abs(x)]; wanted = 1 if x > 0 else -1
            assert old in (0, wanted), ('opposing BCP units', x, old)
            if not old: ass[abs(x)] = wanted; changed = True
        assert changed
    # A separate final scan certifies actual fixpoint, including no hidden units.
    for ci, clause in enumerate(clauses):
        values = [value(x, ass) for x in clause]
        assert any(v is True for v in values) or values.count(None) >= 2, ('not a BCP fixpoint', ci)
    return ass, passes


def residual(clause, ass):
    out = []
    for x in clause:
        v = value(x, ass)
        if v is True: return None
        if v is None: out.append(x)
    return tuple(out)


def compare(actual, expected):
    assert actual == expected, ('residual suffix mismatch', len(actual), len(expected),
                                next(((i,a,e) for i,(a,e) in enumerate(zip(actual,expected)) if a != e), None))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent',default='inputs/parent.cnf'); ap.add_argument('--augmented',required=True)
    ap.add_argument('--simplified',required=True); ap.add_argument('--metadata',required=True)
    ap.add_argument('--report',required=True); args=ap.parse_args()
    praw,pnv,parent=parse(args.parent); araw,anv,aug=parse(args.augmented)
    sraw,snv,simp=parse(args.simplified); meta=json.loads(Path(args.metadata).read_text())
    assert hashlib.sha256(praw).hexdigest()==meta['parent_sha256']
    assert hashlib.sha256(araw).hexdigest()==meta['augmented_sha256']
    assert hashlib.sha256(sraw).hexdigest()==meta['output_sha256']
    assert pnv==19533 and hashlib.sha256(praw).hexdigest()=='90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae'
    assert aug[:len(parent)]==parent and simp[:len(parent)]==parent
    pbody=praw.split(b'\n',1)[1]; sbody=sraw.split(b'\n',1)[1]; assert sbody[:len(pbody)]==pbody
    ass,passes=closure(parent,pnv)
    units=[i if a==1 else -i for i,a in enumerate(ass) if i and a]
    units_sha=hashlib.sha256((' '.join(map(str,units))+' 0\n').encode()).hexdigest()
    assert len(units)==1813==meta['parent_bcp_units'] and units_sha==meta['parent_bcp_units_sha256']
    mapping=dict(meta['fresh_variable_map']); assert len(mapping)==meta['used_fresh_variables']
    assert set(mapping.values())==set(range(pnv+1,pnv+1+len(mapping)))
    expected=[]; satisfied=0
    for clause in aug[len(parent):]:
        r=residual(clause,ass)
        if r is None: satisfied+=1; continue
        assert r
        expected.append(tuple(mapping.get(abs(x),abs(x))*(-1 if x<0 else 1) for x in r))
    compare(simp[len(parent):],expected)
    assert satisfied==meta['suffix_clauses_satisfied'] and len(expected)==meta['residual_suffix_clauses']
    assert snv==pnv+len(mapping)==meta['output_variables']
    bad=list(expected); bad[0]=(-bad[0][0],*bad[0][1:])
    try: compare(bad,expected); raise RuntimeError('negative residual control accepted')
    except AssertionError: pass
    try: compare(expected[:-1],expected); raise RuntimeError('negative deletion control accepted')
    except AssertionError: pass
    report={'result':'PASS','parent_sha256':meta['parent_sha256'],'augmented_sha256':meta['augmented_sha256'],
      'simplified_sha256':meta['output_sha256'],'independent_algorithm':'repeated complete-clause scans to fixpoint',
      'full_scan_passes':passes,'parent_bcp_units':len(units),'parent_bcp_units_sha256':units_sha,
      'satisfied_suffix_clauses':satisfied,'residual_suffix_clauses':len(expected),
      'used_fresh_variables':len(mapping),'all_residuals_and_renaming_exact':True,
      'negative_controls':['rejected flipped residual sign','rejected deleted residual clause'],
      'scope':'Parent-clause BCP equivalence only; not a DRAT certificate or physical colouring result.'}
    Path(args.report).write_text(json.dumps(report,indent=2)+'\n'); print(json.dumps(report,indent=2))

if __name__=='__main__': main()
