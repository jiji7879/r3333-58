"""Independent re-derivation of the one-template capacity table for sizes 1..4.

Tight(P) for a position set P with |P| = k means: at most k outsiders can have
their whole c-support contained in P.  Refuting tightness means producing k+1
outsiders whose c-support is contained in P, so the CNF here has the H42
template plus k+1 outsiders whose c-spokes are free inside P (enc.build with
free=True) and asks for a model.  UNSAT is the certificate "at most k".

The table is the finite input of the crossing-cut theorem:
  * every 1-, 2- and 3-set is tight (so every outsider in the split argument has
    |S(w)| >= 4);
  * of the 1001 four-sets, the ones that are tight (at most 4) admit no outsider
    with that exact support once the four singleton witnesses are in place, and
    the others admit at most one -- which is exactly the multiplicity fact the
    packing enumeration needs.  Six outsiders inside a four-set must be
    impossible for every four-set.

Every UNSAT instance gets a CaDiCaL DRAT verified by drat-trim; every SAT
instance gets its model checked clause by clause.  Writes pack/capacity.json.
"""
import gzip
import itertools
import json
import subprocess
import tempfile
from pathlib import Path

import enc

ARCH = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54cut')
BUILD = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54/build')
CADICAL = BUILD / 'cadical/build/cadical'
DRAT = BUILD / 'drat-trim'
HERE = Path(__file__).resolve().parent
PROOFS = HERE / 'proofs'


def run(nv, clauses, tmp):
    raw = enc.to_dimacs(nv, clauses)
    cnf = tmp / 'f.cnf'
    cnf.write_bytes(raw)
    pr = tmp / 'p.drat'
    res = subprocess.run([str(CADICAL), '-c', '1000000', str(cnf), str(pr)],
                         capture_output=True, text=True)
    out = dict(nv=nv, nclauses=len(clauses), cnf_sha256=enc.sha(raw),
               status={20: 'UNSAT', 10: 'SAT'}.get(res.returncode, 'OPEN'))
    if out['status'] == 'UNSAT':
        out['proof_sha256'] = enc.sha(pr.read_bytes())
        ck = subprocess.run([str(DRAT), str(cnf), str(pr)], capture_output=True, text=True)
        out['drat_verified'] = ck.returncode == 0 and 's VERIFIED' in ck.stdout.splitlines()
        assert out['drat_verified']
        out['_proof'] = gzip.compress(pr.read_bytes(), mtime=0)
    elif out['status'] == 'SAT':
        model = {int(v) for line in res.stdout.splitlines() if line.startswith('v ')
                 for v in line.split()[1:] if int(v)}
        assert model and all(any(v in model for v in cl) for cl in clauses)
        out['model_ok'] = True
    assert out['status'] in ('UNSAT', 'SAT')
    return out


def main():
    H = enc.load_h42(ARCH / 'data/h42.json')
    exceptional = set(json.loads((ARCH / 'results/saturated4.json').read_text()))
    PROOFS.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(dir=HERE, prefix='tmp-'))
    table = []
    sat4 = []
    total_proof = 0
    for k in (1, 2, 3, 4):
        for P in itertools.combinations(range(14), k):
            allowed = sum(1 << i for i in P)
            nv, clauses = enc.build([allowed] * (k + 1), H, free=True)
            rec = run(nv, clauses, tmp)
            rec.update(size=k, allowed=allowed, outsiders=k + 1)
            want = 'UNSAT'
            if k == 4 and allowed in exceptional:
                want = 'SAT'
                sat4.append(allowed)
            assert rec['status'] == want, (k, allowed, rec)
            if k == 4:
                if allowed in exceptional:
                    nv, clauses = enc.build([allowed] * 6, H, free=True)
                    rec6 = run(nv, clauses, tmp)
                    rec6.update(size=k, allowed=allowed, outsiders=6)
                    assert rec6['status'] == 'UNSAT', (allowed, rec6)
                    rec['six_outsiders'] = {kk: vv for kk, vv in rec6.items() if kk != '_proof'}
                    assert enc.sha(gzip.decompress(rec6['_proof'])) == rec6['proof_sha256']
                    (PROOFS / ('cap6-%d.drat.gz' % allowed)).write_bytes(rec6['_proof'])
                    total_proof += len(rec6['_proof'])
            if '_proof' in rec:
                assert enc.sha(gzip.decompress(rec['_proof'])) == rec['proof_sha256']
                (PROOFS / ('cap%d-%d-%d.drat.gz' % (k, allowed, k + 1))).write_bytes(rec['_proof'])
                total_proof += len(rec['_proof'])
                del rec['_proof']
            table.append(rec)
        n_tight = sum(1 for r in table if r['size'] == k and r['status'] == 'UNSAT')
        print('size', k, ':', n_tight, 'sets tight at', k, 'outsiders;',
              'k+1 =', k + 1, 'refuted' if k < 4 else '', flush=True)
    assert sorted(sat4) == sorted(exceptional), (sorted(sat4), sorted(exceptional))
    print('four-sets with capacity 5:', len(sat4), 'and they are exactly saturated4.json')
    print('six outsiders inside any four-set: refuted for all', len(exceptional), 'of them')
    (HERE / 'capacity.json').write_text(json.dumps(table) + '\n')
    print('table entries:', len(table), '; stored proofs:', total_proof, 'bytes gzipped')
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


if __name__ == '__main__':
    main()
