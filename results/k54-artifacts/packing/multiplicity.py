"""Certify the multiplicity gap in the packing argument.

work/k54cut's packing bound counts sets of *distinct* exceptional four-masks.
An implicit extra claim is that no two outsiders can have the same exact
four-support once the 13 singleton witnesses are in place (README: "Each
exceptional set can consequently occur at most once").  That claim is what makes
the distinct-mask packing enumeration bound the number of four-support
outsiders.

For every one of the 12 exceptional masks and every pole it avoids, this script
builds the CNF with the 13 singleton witnesses plus TWO outsiders of that exact
support.  UNSAT (certified by a CaDiCaL DRAT that drat-trim accepts, and by an
independent pysat solve) is exactly "at most one".

Controls, same CNF shape:
  * a nonexceptional four-mask (capacity 4) together with the 13 singletons and
    ONE such outsider must be UNSAT -- spot samples of the cited capacity claim;
  * the 13 singletons plus one exceptional-mask outsider must be SAT (the
    capacity-5 side), so the refutations are not vacuous.
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
PROOFS = HERE / "proofs"


def run(nv, clauses, want, tmp, tag):
    raw = enc.to_dimacs(nv, clauses)
    cnf = tmp / 'f.cnf'
    cnf.write_bytes(raw)
    pr = tmp / 'p.drat'
    run = subprocess.run([str(CADICAL), '-c', '400000', str(cnf), str(pr)],
                         capture_output=True, text=True)
    rec = dict(tag=tag, nv=nv, nclauses=len(clauses), cnf_sha256=enc.sha(raw),
               status={20: 'UNSAT', 10: 'SAT'}.get(run.returncode, 'OPEN'),
               proof_sha256=None, drat_verified=None)
    if rec['status'] == 'UNSAT' and want == 'UNSAT':
        rec['proof_sha256'] = enc.sha(pr.read_bytes())
        ck = subprocess.run([str(DRAT), str(cnf), str(pr)], capture_output=True, text=True)
        rec['drat_verified'] = ck.returncode == 0 and 's VERIFIED' in ck.stdout.splitlines()
        assert rec['drat_verified'], tag
        PROOFS.mkdir(exist_ok=True)
        (PROOFS / (tag + '.drat.gz')).write_bytes(gzip.compress(pr.read_bytes(), mtime=0))
    if want == 'SAT' and rec['status'] == 'SAT':
        model = {int(v) for line in run.stdout.splitlines() if line.startswith('v ')
                 for v in line.split()[1:] if int(v)}
        if not model:  # fall back to a plain run, cadical prints the model on stdout
            run2 = subprocess.run([str(CADICAL), '-c', '400000', str(cnf)],
                                  capture_output=True, text=True)
            model = {int(v) for line in run2.stdout.splitlines() if line.startswith('v ')
                     for v in line.split()[1:] if int(v)}
        rec['model_ok'] = bool(model) and all(any(v in model for v in cl) for cl in clauses)
        assert rec['model_ok'], tag
    assert rec['status'] == want, (tag, rec)
    print(tag, rec['status'], rec['cnf_sha256'][:16],
          rec['proof_sha256'][:16] if rec['proof_sha256'] else '', flush=True)
    return rec


def main():
    H = enc.load_h42(ARCH / 'data/h42.json')
    exceptional = json.loads((ARCH / 'results/saturated4.json').read_text())
    out = dict(multiplicity=[], controls_nonexceptional=[], controls_capacity5=[])
    tmp = Path(tempfile.mkdtemp(dir=HERE, prefix='tmp-'))
    for mask in exceptional:
        for pole in (0, 2, 4):
            if mask >> pole & 1:
                continue
            nv, clauses = enc.build(enc.supports_for(pole, [mask, mask]), H)
            out['multiplicity'].append(run(nv, clauses, 'UNSAT', tmp,
                                           'dup-%d-%d' % (pole, mask)))
    # capacity-5 side: one exceptional-mask outsider is possible at all
    for mask in [m for m in exceptional if any(not m >> p & 1 for p in (0, 2, 4))][:6]:
        pole = next(p for p in (0, 2, 4) if not mask >> p & 1)
        nv, clauses = enc.build(enc.supports_for(pole, [mask]), H)
        out['controls_capacity5'].append(run(nv, clauses, 'SAT', tmp,
                                            'cap5-%d-%d' % (pole, mask)))
    # capacity-4 controls: one nonexceptional four-mask outsider must be impossible
    all4 = [sum(1 << i for i in c) for c in __import__('itertools').combinations(range(14), 4)]
    free = [m for m in all4
            if m not in set(exceptional) and any(not m >> p & 1 for p in (0, 2, 4))]
    sample = free[::len(free) // 12][:12]
    for mask in sample:
        pole = next(p for p in (0, 2, 4) if not mask >> p & 1)
        nv, clauses = enc.build(enc.supports_for(pole, [mask]), H)
        out['controls_nonexceptional'].append(run(nv, clauses, 'UNSAT', tmp,
                                                  'cap4-%d-%d' % (pole, mask)))
    (HERE / 'multiplicity.json').write_text(json.dumps(out, indent=1) + '\n')
    print('multiplicity instances:', len(out['multiplicity']),
          '; capacity-5 SAT controls:', len(out['controls_capacity5']),
          '; capacity-4 UNSAT controls:', len(out['controls_nonexceptional']))
    for f in tmp.iterdir():
        f.unlink()
    tmp.rmdir()


if __name__ == '__main__':
    main()
