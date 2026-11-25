#!/usr/bin/env python3
"""kcheck.py -- replace an external drat-trim check by a Lean-kernel check.

Given an UNSAT CNF plus a DRAT proof, this script

  1. runs drat-trim once to verify the proof and to extract the UNSAT core
     (core.cnf) and the core lemmas as ASCII DRAT (core.drat);
  2. runs drat-trim again on core.cnf + core.drat to emit an LRAT file whose
     clause ids are numbered against *core.cnf*, and to confirm that the core
     contains no RAT steps (Mathlib's LRAT checker is RUP-only);
  3. checks that every clause of core.cnf occurs verbatim in the original
     instance, so that UNSAT(core) implies UNSAT(instance);
  4. writes Cert.lean using Mathlib's `lrat_proof` command and elaborates it
     with the Lean 4 kernel, recording the `#print axioms` line;
  5. appends a JSON record (all sha256s, sizes, statuses) to a manifest.

Usage:
  python3 kcheck.py OUTDIR NAME INSTANCE.cnf PROOF.drat [--manifest F]

Exit status 0 only if every step succeeded and the Lean check passed.
"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

K54 = Path('/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/work/k54')
DRAT_TRIM = K54 / 'build' / 'drat-trim'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def drat_trim(*args, timeout=1800):
    r = subprocess.run([str(DRAT_TRIM), *map(str, args)],
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout.replace('\r', '\n')


def parse_status(out):
    """Return (verified, core_line, rat_line)."""
    verified = any(l.strip() == 's VERIFIED' for l in out.splitlines())
    core = next((l.strip() for l in out.splitlines()
                 if 'clauses in core' in l), '')
    rat = next((l.strip() for l in out.splitlines()
                if 'RAT lemmas in core' in l), '')
    return verified, core, rat


def read_cnf(path):
    """Parse a DIMACS file with no comments -> (nvars, nclauses, [tuple[int]])"""
    txt = Path(path).read_text()
    lines = [l for l in txt.splitlines() if l.strip()]
    head = lines[0].split()
    assert head[0] == 'p' and head[1] == 'cnf', head
    nv, nc = int(head[2]), int(head[3])
    clauses, cur = [], []
    for l in lines[1:]:
        for tok in l.split():
            v = int(tok)
            if v == 0:
                clauses.append(tuple(cur))
                cur = []
            else:
                cur.append(v)
    assert not cur, 'unterminated clause'
    return nv, nc, clauses


def canon(clauses):
    return set(tuple(sorted(c)) for c in clauses)


def main(argv):
    if len(argv) < 5:
        print(__doc__)
        return 2
    outdir, name, cnf, drat = Path(argv[1]), argv[2], Path(argv[3]), Path(argv[4])
    manifest = Path(argv[6]) if len(argv) > 6 and argv[5] == '--manifest' else outdir / 'manifest.jsonl'
    work = outdir / name
    work.mkdir(parents=True, exist_ok=True)
    rec = {'name': name, 'instance': str(cnf), 'proof': str(drat),
           'instance_sha256': sha(cnf), 'proof_sha256': sha(drat),
           'instance_bytes': cnf.stat().st_size,
           'proof_bytes': drat.stat().st_size}
    t0 = time.time()

    # step 1: verify + core extraction
    rc, out = drat_trim(cnf, drat, '-c', work / 'core.cnf', '-l', work / 'core.drat')
    ver1, core1, rat1 = parse_status(out)
    rec['trim1'] = {'rc': rc, 'verified': ver1, 'core': core1, 'rat': rat1}
    if rc != 0 or not ver1:
        rec['ok'] = False
        rec['error'] = 'pass 1 did not verify'
        work.joinpath('log.txt').write_text(out)
        json_append(manifest, rec)
        print(json.dumps(rec['trim1']))
        return 1

    # step 2: LRAT numbered against the core
    rc, out = drat_trim(work / 'core.cnf', work / 'core.drat', '-L', work / 'core.lrat')
    ver2, core2, rat2 = parse_status(out)
    rec['trim2'] = {'rc': rc, 'verified': ver2, 'core': core2, 'rat': rat2}
    work.joinpath('trim2.log').write_text(out)
    if rc != 0 or not ver2:
        rec['ok'] = False
        rec['error'] = 'pass 2 did not verify'
        json_append(manifest, rec)
        print(json.dumps(rec['trim2']))
        return 1
    if 'RAT' in rat2 and not re.search(r'0 RAT lemmas', rat2):
        rec['ok'] = False
        rec['error'] = 'core uses RAT steps; Mathlib checker is RUP-only: ' + rat2
        json_append(manifest, rec)
        print(rec['error'])
        return 1

    # step 3: core is a subformula of the instance (monotonicity)
    nv, nc, inst_clauses = read_cnf(cnf)
    cnv, cnc, core_clauses = read_cnf(work / 'core.cnf')
    missing = canon(core_clauses) - canon(inst_clauses)
    rec['core'] = {'vars': cnv, 'clauses': cnc, 'bytes': (work / 'core.cnf').stat().st_size,
                   'sha256': sha(work / 'core.cnf'),
                   'lrat_sha256': sha(work / 'core.lrat'),
                   'lrat_bytes': (work / 'core.lrat').stat().st_size,
                   'clauses_outside_instance': len(missing)}
    if missing:
        rec['ok'] = False
        rec['error'] = f'{len(missing)} core clauses are not clauses of the instance'
        json_append(manifest, rec)
        print(rec['error'])
        return 1

    # step 4: Lean kernel check
    thm = 'unsat_' + re.sub(r'[^0-9A-Za-z_]', '_', name)
    work.joinpath('Cert.lean').write_text(
        'import Mathlib\n\n'
        'lrat_proof ' + thm + '\n'
        '  (include_str "core.cnf")\n'
        '  (include_str "core.lrat")\n\n'
        '#print axioms ' + thm + '\n')
    t = time.time()
    r = subprocess.run(['lean', str((work / 'Cert.lean').resolve())],
                       capture_output=True, text=True, timeout=3600)
    rec['lean'] = {'rc': r.returncode, 'seconds': round(time.time() - t, 2),
                   'stdout': r.stdout.strip()[-2000:], 'stderr': r.stderr.strip()[-4000:]}
    m = re.search(r"depends on axioms: \[(.*?)\]", r.stdout)
    ax = sorted(x.strip() for x in m.group(1).split(',')) if m else None
    rec['lean']['axioms'] = ax
    ok = r.returncode == 0 and ax is not None and set(ax) <= ALLOWED_AXIOMS
    if not m and r.returncode == 0:
        # no axioms at all is also acceptable
        ok = 'depends on axioms' not in r.stdout
    rec['ok'] = ok
    record = r.stdout.strip() or r.stderr.strip()
    work.joinpath('lean.log').write_text(record + '\n')
    rec['lean']['log'] = record[-500:]
    rec['seconds'] = round(time.time() - t0, 2)
    json_append(manifest, rec)
    print(f'{name}: kernel-checked={ok} axioms={ax} core={cnc} clauses '
          f'lrat={rec["core"]["lrat_bytes"]}B lean={rec["lean"]["seconds"]}s')
    return 0 if ok else 1


def json_append(path, rec):
    with open(path, 'a') as f:
        f.write(json.dumps(rec) + '\n')


if __name__ == '__main__':
    sys.exit(main(sys.argv))
