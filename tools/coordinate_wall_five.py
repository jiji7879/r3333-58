#!/usr/bin/env python3
"""Coordinator-managed idle-lane S3/S4 rows for the wall5x300 pilot.

The two batches are distinct: S3 has two five-row profiles, S4 one. Never
run both batches in more than one process at once. Parent CNFs are rebuilt
from the pinned frozen roster before any solver process is launched.
"""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / '.scratch/wall-five-300'
RESULTS = REPO / 'results/wall-five-300'
WANTED = {
    'S3': ['15,15,14,13', '16,15,13,13'],
    'S4': ['16,15,14,12'],
}


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ('prepare', 'S3', 'S4'):
        raise SystemExit('usage: coordinate_wall_five.py prepare | S3 | S4')
    sys.path.insert(0, str(REPO / 'tools/selfcontained/wallcc'))
    from problem import lookup, row_formula, roster, read_dimacs, identity
    with (REPO / '.ultramath/smwxrqkfl/m6/selection.tsv').open() as stream:
        rows = list(csv.DictReader(stream, delimiter='\t'))
    selected = {}
    for profile in WANTED['S3'] + WANTED['S4']:
        candidates = [rid for rid, row in roster().items()
                      if ','.join(map(str, row['family']['profile'])) == profile]
        expected = sorted(candidates, key=lambda rid: hashlib.sha256(
            f'wall5x300-v1|{profile}|{rid}'.encode()).hexdigest())[:5]
        seen = [r for r in rows if r['profile'] == profile]
        assert [r['row_id'] for r in seen] == expected
        for rec in seen:
            assert rec['key_sha256'] == hashlib.sha256(
                f'wall5x300-v1|{profile}|{rec["row_id"]}'.encode()).hexdigest()
            row = lookup(rec['row_id'])
            assert identity(row) == row['id']
            assert ','.join(map(str, row['family']['profile'])) == profile
            parent_sha = hashlib.sha256(row_formula(row, 'first')).hexdigest()
            selected[rec['row_id']] = {
                'row_id': row['id'], 'profile': profile, 'branch': row['branch'],
                'charge': row['charge'], 'parent_sha256': parent_sha,
                'tier': 'first', 'tables': True, 'total_critical': True,
                'full_root': False, 'cas': 'off', 'depth': 0,
                'engine': 'kissat', 'wall_seconds_cap': 300, 'conflict_limit': None,
                'selection_key_sha256': rec['key_sha256'], 'lane': next(
                    lane for lane, profiles in WANTED.items() if profile in profiles),
            }
    RESULTS.mkdir(exist_ok=True)
    (RESULTS / 'coordinator-allocation.json').write_text(json.dumps({
        'scope': 'Coordinator fills formerly unclaimed S3/S4; no overlap with member S1/S2 allocation',
        'cap': 300, 'conflict_limit': None, 'profiles': WANTED,
        'rows': list(selected.values())}, indent=2) + '\n')
    path = RESULTS / 'coordinator-manifest.json'
    if path.exists():
        assert json.loads(path.read_text()) == selected, 'frozen manifest changed'
    else:
        path.write_text(json.dumps(selected, indent=2) + '\n')
    if sys.argv[1] == 'prepare':
        print(f'Validated {len(selected)} parent SHA-256 values in S3/S4', flush=True)
        return
    ROOT.mkdir(exist_ok=True)
    (ROOT / 'bin').mkdir(exist_ok=True)
    source = REPO / '.scratch/wall-profile-16-16-14-11-600/bin/kissat'
    binary = ROOT / 'bin/kissat'
    if not binary.exists():
        shutil.copyfile(source, binary)
    binary.chmod(0o755)
    assert hashlib.sha256(binary.read_bytes()).hexdigest() == 'b77de62fb1945d2ffab165b1f05e25c9e8ae7fc43de3a4fb8346fc2c9954097f'
    for profile in WANTED[sys.argv[1]]:
        for info in selected.values():
            if info['profile'] != profile:
                continue
            row = lookup(info['row_id'])
            raw = row_formula(row, 'first')
            nv, clauses = read_dimacs(raw)
            assert hashlib.sha256(raw).hexdigest() == info['parent_sha256']
            parent = ROOT / 'rows' / info['row_id']
            run = ROOT / 'runs' / (info['row_id'][:12] + '--' + sys.argv[1])
            if run.exists() or parent.joinpath('work').exists():
                raise RuntimeError('work directory already exists: ' + str(run))
            parent.mkdir(parents=True, exist_ok=True)
            if parent.joinpath('parent.cnf').exists():
                assert parent.joinpath('parent.cnf').read_bytes() == raw
            else:
                parent.joinpath('parent.cnf').write_bytes(raw)
            parent_sha = hashlib.sha256(raw).hexdigest()
            parent.joinpath('row.json').write_text(json.dumps({
                **info, 'cnf': str(parent / 'parent.cnf'), 'variables': nv,
                'clauses': len(clauses), 'run': str(run)}, indent=2) + '\n')
            parent.joinpath('prepared.sha256').write_text(parent_sha + '  parent.cnf\n')
            command = [sys.executable, str(REPO / 'tools/run_wall_300.py'),
                       str(parent / 'parent.cnf'), parent_sha, 'kissat', str(run),
                       '--seconds', '300', '--results-dir', 'results/wall-five-300/receipts',
                       '--bin-dir', str(ROOT / 'bin')]
            print('START', info['profile'], info['row_id'], parent_sha, flush=True)
            completed = subprocess.run(command, check=False)
            (parent / 'driver.returncode').write_text(str(completed.returncode) + '\n')
            print('END', info['row_id'][:12], 'driver_rc', completed.returncode, flush=True)
            if completed.returncode:
                raise SystemExit(completed.returncode)


if __name__ == '__main__':
    main()
