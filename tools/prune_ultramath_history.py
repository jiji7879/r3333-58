#!/usr/bin/env python3
"""Discard non-preserved raw files, guarded by an existing checked archive.

Default is a CHECK ONLY. --apply additionally requires allow_raw_discard in
an explicit retention policy. No live or unindexed path is deleted.
"""
import argparse
import gzip
import hashlib
import json
import os
from pathlib import Path


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(4*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def covered(path, roots):
    return any(path == r or r in path.parents for r in roots)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--core', required=True)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    core = Path(args.core)
    policy = json.loads((core / 'retention-policy.json').read_text())
    assert policy['allow_raw_discard'] is True
    roots = [Path(p) for p in policy['protected_tree_prefixes']]
    for p in roots + [Path('.ultramath') / p for p in policy['live_swarms']]:
        assert p.exists(), f'protected path absent: {p}'
        assert not p.is_symlink(), f'protected link not supported: {p}'
    records = [json.loads(line) for line in gzip.open(core / 'raw-file-index.jsonl.gz', 'rt')]
    known_paths = {Path(row['path']) for row in records}
    hashes_checked = 0
    deletion, mismatch, missing, unexpected = [], [], [], []
    for index, row in enumerate(records):
        if index and index % 10000 == 0:
            print(f'PROGRESS {index}/{len(records)} indexed files; verified source hashes continue', flush=True)
        p = Path(row['path'])
        assert not p.is_absolute() and p.parts[0] == '.ultramath', f'out of scope: {p}'
        assert not p.is_symlink() and p.resolve() == Path.cwd() / p, f'link traversal refused: {p}'
        if not p.exists():
            missing.append(row)
            continue
        if covered(p, roots) or (p.parts[1:2] and p.parts[1] in policy['live_swarms']):
            continue
        assert not p.is_symlink(), f'symlink not expected in index: {p}'
        if row['preserved_in_archive']:
            assert p.stat().st_size == row['bytes'], f'size changed: {p}'
            actual = sha256(p)
            if actual != row['sha256']:
                mismatch.append(p)
            hashes_checked += 1
        else:
            deletion.append((p, p.stat().st_size, p.stat().st_blocks * 512))
    if mismatch:
        raise SystemExit('ABORT: source files changed after archiving: ' +
                         ', '.join(map(str, mismatch[:20])))
    for p in roots:
        for here, dirs, files in os.walk(p):
            for f in files:
                q = Path(here, f)
                if q.is_file() and q not in known_paths:
                    unexpected.append(q)
    if unexpected:
        raise SystemExit('ABORT: unindexed files in protected tree; regenerate archive first: ' +
                         ', '.join(map(str, unexpected[:20])))
    record = {
        'mode': 'apply' if args.apply else 'check-only',
        'input_file_records': len(records),
        'previously_absent_file_records': missing,
        'source_hash_checks_passed': hashes_checked,
        'source_hash_mismatches': [],
        'protected_tree_prefixes': [str(p) for p in roots],
        'live_swarms_untouched': policy['live_swarms'],
        'would_delete' if not args.apply else 'deleted': [
            {'path': str(p), 'bytes': b, 'allocated_bytes': a} for p,b,a in deletion],
        'would_delete_file_count' if not args.apply else 'deleted_file_count': len(deletion),
        'would_delete_allocated_bytes' if not args.apply else 'deleted_allocated_bytes': sum(a for _,_,a in deletion),
        'would_delete_logical_bytes' if not args.apply else 'deleted_logical_bytes': sum(b for _,b,_ in deletion),
    }
    output = core / ('prune-measurement.json' if args.apply else 'prune-dry-run.json')
    if output.exists():
        raise SystemExit(f'refusing to overwrite {output}')
    if args.apply:
        st = os.statvfs('.')
        record['free_bytes_before'] = st.f_bavail * st.f_frsize
        for p, _, _ in deletion:
            p.unlink()
        assert not any(p.exists() for p,_,_ in deletion)
        st = os.statvfs('.')
        record['free_bytes_after'] = st.f_bavail * st.f_frsize
        record['free_bytes_increase'] = record['free_bytes_after'] - record['free_bytes_before']
        record['missing_paths_verified_after'] = len(deletion)
    output.write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps({k:v for k,v in record.items() if k not in {'deleted','would_delete'}}, indent=2))
    for row in missing:
        print('PREVIOUSLY_ABSENT', row['path'])


if __name__ == '__main__':
    main()
