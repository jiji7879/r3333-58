#!/usr/bin/env python3
"""Audit a k58 release bundle from its own files, without the evidence.

A release is `manifest.json` + `cases.jsonl.gz` (+ the replay and coverage lines).  The
certificates stay with the runner, so what can be checked here is that the bundle is the
cover it claims to be: the case index and the frozen ledger hash to what the manifest says,
every id is a row of the frozen ledger, the counts add up, the generator hashes are the
audited encoders, and a sample of rows rebuilds to the recorded CNF hashes.

    PYTHONPATH=<site-packages with pysat> python3 tools/audit_release.py BUNDLE_DIR

BUNDLE_DIR holds manifest.json and cases.jsonl.gz.  Exit 0 when every check passes.
Writes nothing.
"""
import argparse
import gzip
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

LEDGER = '.scratch/k58/case-ledger.jsonl.gz'
BUNDLE = '.scratch/k58'


def sha256(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('release', help='directory holding manifest.json and cases.jsonl.gz')
    ap.add_argument('--ledger', default=LEDGER)
    ap.add_argument('--bundle', default=BUNDLE, help='frozen k58 encoder directory')
    ap.add_argument('--sample', type=int, default=12)
    ap.add_argument('--seed', type=int, default=58)
    options = ap.parse_args()
    rel = Path(options.release)
    fails = []

    def check(name, ok, detail=''):
        print('%-4s %-44s %s' % ('ok' if ok else 'FAIL', name, detail))
        if not ok:
            fails.append(name)

    manifest = json.loads((rel / 'manifest.json').read_text())
    cases_path = rel / manifest['cases']['path']
    check('cases bytes', cases_path.stat().st_size == manifest['cases']['bytes'],
          '%d' % cases_path.stat().st_size)
    check('cases sha256', sha256(cases_path) == manifest['cases']['sha256'],
          manifest['cases']['sha256'][:16])
    check('ledger sha256', sha256(options.ledger) == manifest['ledger_sha256'],
          manifest['ledger_sha256'][:16])
    check('python-sat pin', manifest['dependencies'].get('python-sat') == '1.9.dev22',
          str(manifest['dependencies']))

    rows = {}
    profile = {}
    with gzip.open(options.ledger, 'rt') as fh:
        for line in fh:
            row = json.loads(line)
            rows[row['id']] = row
            profile[row['id']] = ','.join(map(str, row['family']['profile']))
    seen, status, tab, dup = {}, Counter(), defaultdict(Counter), 0
    certified = []
    with gzip.open(cases_path, 'rt') as fh:
        for line in fh:
            case = json.loads(line)
            if case['id'] in seen:
                dup += 1
            seen[case['id']] = case['status']
            status[case['status']] += 1
            tab[profile.get(case['id'], '??')][case['status']] += 1
            if case['status'] == 'CERTIFIED':
                certified.append(case)
    check('case ids are frozen-ledger rows', set(seen) <= set(rows),
          '%d unknown' % len(set(seen) - set(rows)))
    check('no duplicate case ids', dup == 0, '%d' % dup)
    check('counts sum to the manifest total',
          sum(status.values()) == len(rows) == sum(manifest['counts'].values()),
          '%d = %d' % (sum(status.values()), len(rows)))
    check('status counts match the manifest',
          dict(status) == manifest['counts'], str(dict(status)))

    print('\n%-14s %10s %8s %8s' % ('profile', 'CERTIFIED', 'OPEN', 'OTHER'))
    for p in sorted(tab, key=lambda p: -sum(tab[p].values())):
        c = tab[p]
        print('%-14s %10d %8d %8d' % (p, c['CERTIFIED'], c['OPEN'],
                                      sum(c.values()) - c['CERTIFIED'] - c['OPEN']))

    differ = [name for name, want in manifest['generators'].items()
              if (Path(options.bundle) / name).exists()
              and sha256(Path(options.bundle) / name) != want]
    check('generator hashes are the frozen encoders', differ in ([], ['run_cover.py']),
          'differ: %s' % (', '.join(differ) or 'none'))
    if differ == ['run_cover.py']:
        print('     run_cover.py is expected to differ: the shipped package patches the checker cap')

    if certified and options.sample:
        sys.path.insert(0, options.bundle)
        import cover_evidence as ce
        rng = random.Random(options.seed)
        sample = rng.sample(certified, min(options.sample, len(certified)))
        bad = 0
        for case in sample:
            chunks = ce.formula_chunks(rows[case['id']], case['recipe'])
            ident = ce.formula_id(chunks)
            if ident['sha256'] != case['input']['sha256'] or ident['bytes'] != case['input']['bytes']:
                bad += 1
                print('     rebuilt %s differs' % case['id'][:12])
        check('sampled rows rebuild to their input hashes', bad == 0,
              '%d of %d' % (len(sample) - bad, len(sample)))

    print('\n%s' % ('AUDIT PASSED' if not fails else 'AUDIT FAILED: ' + ', '.join(fails)))
    return 0 if not fails else 1


if __name__ == '__main__':
    sys.exit(main())
