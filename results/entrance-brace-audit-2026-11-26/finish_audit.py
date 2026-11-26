#!/usr/bin/env python3
"""Combine the completed structural audit with the independent replay receipts.

The expensive case/CNF audit is reused only after every source input checksum is
confirmed unchanged. This script does not create or upgrade proof verifications.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / '.ultramath/smwwdcyxb/m2/proofs'
OUT = ROOT / 'results/entrance-brace-audit-2026-11-26'
FILES = ['manifest.jsonl', 'residual.tsv', 'replay.jsonl']


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        while chunk := fh.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


def main():
    receipt_path = OUT / 'geometry-receipt.json'
    receipt = json.loads(receipt_path.read_text())
    with open(receipt_path) as fh:
        assert json.load(fh)['proof_replays_complete'] is False
    for name in FILES:
        assert sha(SRC / name) == receipt['sha256'][name], ('source changed', name)
    doc = json.loads((OUT / 'store-audit.json').read_text())
    assert doc['cnf_hashes_rebuilt'] == 2830
    assert doc['proof_gz_hashes_checked'] == 2830
    assert doc['residual_cases'] == 3600
    assert doc['residual_cases_open'] == 770
    replayed = {}
    log = OUT / 'replayed-missing.jsonl'
    for path in [SRC / 'replay.jsonl', log]:
        for line in open(path):
            rec = json.loads(line)
            if rec.get('replay') == 'VERIFIED':
                assert rec.get('cnf_match') is True
                assert rec.get('proof_match') is True
                replayed[(rec['family'], rec['key'])] = rec
    manifest = {}
    for line in open(SRC / 'manifest.jsonl'):
        rec = json.loads(line)
        if rec.get('drat') == 'VERIFIED':
            manifest[(rec['family'], rec['key'])] = rec
    assert len(manifest) == 2830
    assert set(replayed) == set(manifest), ('proof replay coverage', len(replayed), len(manifest))
    doc.update(complete=True, replayed_verified=len(replayed),
               geometry_receipt=str(receipt_path.relative_to(ROOT)),
               replay_receipts=[str((SRC / 'replay.jsonl').relative_to(ROOT)),
                                str(log.relative_to(ROOT))],
               source_inputs_unchanged=True)
    per = {}
    for family, _ in replayed:
        per[family] = per.get(family, 0) + 1
    doc['per_family_replayed'] = dict(sorted(per.items()))
    text = json.dumps(doc, indent=2, sort_keys=True) + '\n'
    tmp = OUT / 'store-audit.json.tmp'
    tmp.write_text(text)
    tmp.replace(OUT / 'store-audit.json')
    print('PASS: frozen structural audit unchanged; 2830/2830 stored proofs replay VERIFIED')
    print('This completes the scoped proof-store audit only; strict/mixed/full rows remain open.')


if __name__ == '__main__':
    main()
