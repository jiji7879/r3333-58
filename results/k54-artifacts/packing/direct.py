"""Direct, single-instance certification of the four-point packing bound.

The enumeration route (pack/replay.py + pack/enum_check.py) needs the
distinct-mask claim.  This route needs nothing: the CNF has the H42 template,
the 13 singleton witnesses at every non-pole position, and r further outsiders
that each choose *some* four c-neighbours among the 13 non-poles (an exactly-4
cardinality constraint, repetitions of the same support allowed).  UNSAT for r
is exactly "at most r-1 outsiders can have exactly four c-neighbours".

Result: pole 0 and pole 2 admit 4 but not 5, pole 4 admits 3 but not 4, so the
packing bound 4/4/3 of work/k54cut/README.md ("a sharper bound on four-point
supports") holds, and it is attained.  Each UNSAT instance carries a CaDiCaL
DRAT checked by drat-trim; each SAT instance a clause-checked model.
"""
import gzip
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
BOUND = {0: 4, 2: 4, 4: 3}     # the claim under test


def spec_of(pole, r):
    nonpole = sum(1 << j for j in range(14) if j != pole)
    return [(1 << j, 1) for j in range(14) if j != pole] + [(nonpole, 4)] * r


def main():
    H = enc.load_h42(ARCH / 'data/h42.json')
    PROOFS.mkdir(exist_ok=True)
    tmp = Path(tempfile.mkdtemp(dir=HERE, prefix='tmp-'))
    out = []
    for pole in (0, 2, 4):
        for r in (BOUND[pole] - 1, BOUND[pole], BOUND[pole] + 1):
            nv, clauses = enc.build_exact_k(spec_of(pole, r), H)
            raw = enc.to_dimacs(nv, clauses)
            cnf = tmp / 'f.cnf'
            cnf.write_bytes(raw)
            pr = tmp / 'p.drat'
            res = subprocess.run([str(CADICAL), '-c', '2000000', str(cnf), str(pr)],
                                 capture_output=True, text=True)
            rec = dict(pole=pole, outsiders=r, nv=nv, nclauses=len(clauses),
                       cnf_sha256=enc.sha(raw),
                       status={20: 'UNSAT', 10: 'SAT'}.get(res.returncode, 'OPEN'))
            want = 'UNSAT' if r > BOUND[pole] else 'SAT'
            assert rec['status'] == want, (pole, r, rec)
            if rec['status'] == 'UNSAT':
                rec['proof_sha256'] = enc.sha(pr.read_bytes())
                ck = subprocess.run([str(DRAT), str(cnf), str(pr)],
                                    capture_output=True, text=True)
                rec['drat_verified'] = (ck.returncode == 0
                                        and 's VERIFIED' in ck.stdout.splitlines())
                assert rec['drat_verified'], (pole, r)
                (PROOFS / ('direct-pole%d-r%d.drat.gz' % (pole, r))).write_bytes(
                    gzip.compress(pr.read_bytes(), mtime=0))
            else:
                model = {int(v) for line in res.stdout.splitlines() if line.startswith('v ')
                         for v in line.split()[1:] if int(v)}
                assert model and all(any(v in model for v in cl) for cl in clauses)
                rec['model_ok'] = True
            out.append(rec)
            print('pole %d, %d four-support outsiders: %s  %s'
                  % (pole, r, rec['status'], rec['cnf_sha256'][:16]), flush=True)
    (HERE / 'direct.json').write_text(json.dumps(out, indent=1) + '\n')
    for p in (0, 2, 4):
        assert BOUND[p] == max(r['outsiders'] for r in out
                               if r['pole'] == p and r['status'] == 'SAT')
    print('packing bound: pole 0 -> 4, pole 2 -> 4, pole 4 -> 3 (each attained)')
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


if __name__ == '__main__':
    main()
