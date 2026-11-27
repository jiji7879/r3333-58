#!/usr/bin/env python3
"""Strict, independent checker replay of a stratified closed-parent sample.

Only the producer's checker callback is replaced. Every representative and
proof is regenerated from the frozen revised row/owner identity. The final
query/proof must match its receipt and replay with independently built
DRAT-trim flags -i -U, without -w.
"""
from __future__ import annotations

import argparse
import ast
import csv
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def read_tsv(path: Path):
    with gzip.open(path, 'rt', newline='') as stream:
        return list(csv.DictReader(stream, delimiter='\t'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('campaign', type=Path)
    parser.add_argument('--checker', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    checker = args.checker.resolve()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(campaign))
    import closed_parents

    ledger = read_tsv(campaign / 'campaign/closed-parents/ledger.tsv.gz')
    revised = read_tsv(campaign / 'campaign/revised/queue.tsv.gz')
    row_by_id = {r['row_id']: r for r in revised}
    profile_groups = {}
    for row in ledger:
        profile_groups.setdefault(row_by_id[row['rid']]['profile'], []).append(row)
    selected = []
    for profile, rows in sorted(profile_groups.items()):
        rows.sort(key=lambda r: int(r['index']))
        positions = sorted({0, len(rows) // 3, 2 * len(rows) // 3, len(rows) - 1})
        selected.extend(rows[i] for i in positions)
    selected.sort(key=lambda r: int(r['index']))
    calls = []
    malformed_checked = False
    checker_sha256 = hashlib.sha256(checker.read_bytes()).hexdigest()

    def execute(query: Path, proof: Path, output: Path):
        command = [str(checker), str(query), str(proof), '-i', '-U', '-t', '300']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        statuses = [line for line in result.stdout.splitlines() if line.startswith(b's ')]
        output.write_bytes(b'$ ' + ' '.join(command).encode() + b'\nreturncode: ' +
                           str(result.returncode).encode() + b'\n' + result.stdout)
        return result.returncode, statuses

    def strict(query: Path, proof: Path, extra=()):
        nonlocal malformed_checked
        assert extra == ['-U']
        number = len(calls) + 1
        kept_query = out / f'{number:02d}-query.cnf'
        kept_proof = out / f'{number:02d}-proof.rup'
        kept_query.write_bytes(query.read_bytes())
        kept_proof.write_bytes(proof.read_bytes())
        rc, statuses = execute(kept_query, kept_proof, out / f'{number:02d}-check.log')
        if rc != 0 or statuses != [b's VERIFIED']:
            raise RuntimeError((query, rc, statuses))
        calls.append({'call': number, 'query_sha256': hashlib.sha256(kept_query.read_bytes()).hexdigest(),
                      'proof_sha256': hashlib.sha256(kept_proof.read_bytes()).hexdigest(),
                      'proof_bytes': kept_proof.stat().st_size,
                      'checker': str(checker), 'flags': ['-i', '-U', '-t', '300'],
                      'warning_suppression': False})
        if not malformed_checked:
            malformed = out / 'malformed-prefix.rup'
            blob = b'X\0' + kept_proof.read_bytes()
            assert blob != kept_proof.read_bytes()
            malformed.write_bytes(blob)
            bad_rc, bad_statuses = execute(kept_query, malformed, out / 'malformed-prefix.log')
            assert bad_rc != 0 and bad_statuses != [b's VERIFIED'], (bad_rc, bad_statuses)
            malformed_checked = True
        return True

    closed_parents.rup = strict
    results = []
    for row in selected:
        rid = row['rid']
        pair = tuple(ast.literal_eval(row['p']))
        assert len(pair) == 2
        job = (rid, int(row['arm']), pair, int(row['index']), True)
        actual = closed_parents.replay(job)
        receipt_path = campaign / 'campaign/closed-parents/rows' / rid[:2] / \
            (rid + '-' + '-'.join(pair) + '.json.gz')
        expected = json.loads(gzip.decompress(receipt_path.read_bytes()))
        assert actual == expected
        assert actual['rid'] == rid and actual['index'] == int(row['index'])
        assert actual['representative'] == row['representative']
        assert actual['proof'] == row['proof']
        assert actual['status'] == 'VERIFIED_UNSAT'
        results.append({'rid': rid, 'arm': actual['arm'], 'pair': list(pair),
                        'revised_index': actual['index'],
                        'profile': row_by_id[rid]['profile'],
                        'representative': actual['representative'],
                        'proof': actual['proof'], 'proof_bytes': actual['bytes']})
        print(f"verified {rid[:12]} revised={actual['index']} query={actual['representative'][:12]}", flush=True)
    assert len(calls) == len(results) == 16
    summary = {'schema': 'k58-closed-parent-independent-strict-sample/v1',
               'selected': len(results), 'positive_checks': len(calls),
               'malformed_negative_controls_rejected': int(malformed_checked),
               'warning_suppression': False, 'profiles': sorted(profile_groups),
               'checker_sha256': checker_sha256,
               'calls': calls, 'representatives': results,
               'boundary': '16 exact full revised representatives. This is not all 3,066 physical proofs and not a whole-row closure.'}
    (out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: summary[k] for k in ('selected', 'positive_checks',
          'malformed_negative_controls_rejected', 'profiles')}, indent=2))


if __name__ == '__main__':
    main()
