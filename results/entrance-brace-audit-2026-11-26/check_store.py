#!/usr/bin/env python3
"""Audit the scoped m2 entrance proof store; no solving or proof changes."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / '.ultramath/smwwdcyxb/m2'
P = BASE / 'proofs'
OUT = ROOT / 'results/entrance-brace-audit-2026-11-26'
sys.path.insert(0, str(BASE))
import drive_ent as D
import entcases as E


def formula(fam, facts):
    kinds = (fam[:2][0], fam[:2][1])
    clauses = E.base_cnf(kinds, facts)
    nv = max(abs(lit) for cl in clauses for lit in cl)
    text = ('p cnf %d %d\n' % (nv, len(clauses)) +
            ''.join(' '.join(map(str, cl)) + ' 0\n' for cl in clauses))
    return text.encode()


def main():
    manifest = [json.loads(line) if line.strip() else None for line in open(P / 'manifest.jsonl')]
    records = {}
    for rec in manifest:
        if rec.get('drat') != 'VERIFIED':
            continue
        key = (rec['family'], rec['key'])
        assert key not in records, ('duplicate certified record', key)
        records[key] = rec
    old_replays = [json.loads(line) for line in open(P / 'replay.jsonl')]
    replayed = {tuple([r['family'], r['key']]): r for r in old_replays if r.get('replay') == 'VERIFIED'}
    new_path = OUT / 'replayed-missing.jsonl'
    if new_path.exists():
        for line in open(new_path):
            r = json.loads(line)
            if r.get('replay') == 'VERIFIED':
                replayed[(r['family'], r['key'])] = r
    residual = [r.rstrip().split('\t') for r in open(P / 'residual.tsv') if r.strip()][1:]
    residual_map = {(r[0], r[1]): r[2] for r in residual}
    assert len(residual_map) == 3600
    summary = {}
    all_keys = set()
    checks = []
    for fam in ['TT:2:5,5,5', 'UU:2:5,5,5', 'UT:2:5,5,5',
                'TT:3:5,5,5', 'UU:3:5,5,5', 'UT:3:5,5,5']:
        kinds = (fam[0], fam[1])
        p, shape = fam.split(':')[1:]
        cases, raw = D.enumerate_cases(kinds, int(p), tuple(map(int, shape.split(','))))
        keys = {k for k, _ in cases}
        assert len(cases) == 600 and len(keys) == 600
        all_keys |= {(fam, k) for k in keys}
        verified = {k for f, k in records if f == fam}
        replay = verified & {k for f, k in replayed}
        assert verified <= keys
        summary[fam] = dict(cases=600, raw=raw, certified=len(verified), replayed=len(replay), open=len(keys-verified))
        for key, facts in cases:
            pair = (fam, key)
            assert (residual_map[pair] == 'VERIFIED') == (pair in records), pair
            if pair not in records:
                continue
            rec = records[pair]
            blob = formula(fam, facts)
            assert hashlib.sha256(blob).hexdigest() == rec['cnf_sha256'], pair
            proof_gz = BASE / rec['proof_gz']
            with open(proof_gz, 'rb') as fh:
                assert hashlib.sha256(fh.read()).hexdigest() == rec['proof_gz_sha256']
            if pair in replayed:
                assert replayed[pair].get('cnf_match') is True, pair
                assert replayed[pair].get('proof_match') is True, pair
            checks.append((fam, key, rec['cnf_sha256']))
        print(fam, json.dumps(summary[fam]), flush=True)
    assert all_keys == set(residual_map)
    assert set(records) <= all_keys
    assert set(replayed) <= set(records)
    counts = collections.Counter(r['family'] for r in records.values())
    verified_counts = collections.Counter(f for f, k in replayed)
    doc = {
        'source_manifest': str((P / 'manifest.jsonl').relative_to(ROOT)),
        'manifest_lines': len(manifest),
        'unknown_manifest_lines': sum(r.get('drat') != 'VERIFIED' for r in manifest),
        'certified_records': len(records),
        'cnf_hashes_rebuilt': len(checks),
        'proof_gz_hashes_checked': len(checks),
        'replayed_verified': len(replayed),
        'all_replays_cnf_and_proof_match': True,
        'residual_cases': len(residual),
        'residual_cases_open': sum(v == 'OPEN' for v in residual_map.values()),
        'families': summary,
        'per_family_certified': dict(sorted(counts.items())),
        'per_family_replayed': dict(sorted(verified_counts.items())),
        'complete': len(replayed) == len(records),
        'scope_warning': 'Only these listed cases are certified. This is not a strict/mixed/profile elimination.',
    }
    assert doc['cnf_hashes_rebuilt'] == 2830
    assert len(records) == 2830
    (OUT / 'store-audit.json').write_text(json.dumps(doc, indent=2, sort_keys=True) + '\n')
    print(json.dumps(doc, indent=2, sort_keys=True), flush=True)
    if not doc['complete']:
        raise SystemExit('proof replay incomplete: %d/%d' % (len(replayed), len(records)))
    print('PASS: 3600 enumerated keys, 2830 rebuilt CNFs, 2830 hash-checked and replayed proofs', flush=True)


if __name__ == '__main__':
    main()
