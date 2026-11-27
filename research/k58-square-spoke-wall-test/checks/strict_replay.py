#!/usr/bin/env python3
"""Strict, warning-hostile native replay of the shared K15 proof.

Usage: strict_replay.py SOURCE_DIR DRAT_TRIM_BINARY OUTPUT_DIR
Writes queries and decompressed proof bytes to OUTPUT_DIR. No proof warning
is suppressed. The path variant is an actual rejecting query control.
"""
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

SRC = Path(sys.argv[1]).resolve()
CHECKER = Path(sys.argv[2]).resolve()
OUT = Path(sys.argv[3]).resolve()
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(SRC / 'next'))
import block


def parse_binary_drat(raw):
    records, kind, literals, i = [], 'a', [], 0
    while i < len(raw):
        if raw[i] in (97, 100):
            assert not literals
            kind, i = chr(raw[i]), i + 1
            continue
        value = shift = 0
        while True:
            byte = raw[i]
            i += 1
            value |= (byte & 127) << shift
            if not byte & 128:
                break
            shift += 7
        if value == 0:
            records.append((kind, literals))
            literals, kind = [], 'a'
        else:
            literals.append(-(value >> 1) if value & 1 else value >> 1)
    assert i == len(raw) and not literals and raw[-1] == 0
    return records


def main():
    receipt = {}
    for name, formula in [('matching', block.formula(True)), ('path', block.formula(False))]:
        text = 'p cnf %d %d\n' % (formula.nv, len(formula.clauses)) + ''.join(
            ' '.join(map(str, c)) + ' 0\n' for c in formula.clauses)
        (OUT / (name + '.cnf')).write_text(text)
        receipt[name] = {'sha256': hashlib.sha256(text.encode()).hexdigest(),
                         'variables': formula.nv, 'clauses': len(formula.clauses)}
    assert receipt['matching']['sha256'] == '9fb32091685b9e3adf1e7e670c3d4333f35b0d12ed6990e968a44b83fb180b01'
    packed = (SRC / 'next' / 'matching.drat.gz').read_bytes()
    raw = gzip.decompress(packed)
    (OUT / 'matching.drat').write_bytes(raw)
    receipt['proof'] = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
                        'gz_sha256': hashlib.sha256(packed).hexdigest()}
    assert len(raw) == 470852
    assert receipt['proof']['sha256'] == '4ca7a5d302ceadc4afb5d8d54e4f9c3d5613f48cf08681fe0461a05acb6085d7'
    for name, query, flags in [('strict_original', 'matching.cnf', []),
                               ('strict_deletions_ignored', 'matching.cnf', ['-p', '-U', '-W']),
                               ('negative_path', 'path.cnf', ['-p', '-U', '-W'])]:
        result = subprocess.run([str(CHECKER), str(OUT / query), str(OUT / 'matching.drat'), *flags],
                                capture_output=True)
        output = (result.stdout + result.stderr).decode('utf-8', 'replace')
        (OUT / (name + '.log')).write_text(output + '\nexit=%s\n' % result.returncode)
        receipt[name] = {
            'exit': result.returncode,
            'verified': output.splitlines().count('s VERIFIED'),
            'warnings': [s for s in output.splitlines() if 'WARNING' in s or 'ERROR' in s],
            'full_read': 'read %d bytes from proof file' % len(raw) in output,
            'rat_zero': 'c 0 RAT lemmas in core' in output,
        }
        # No -w anywhere in the replay contract, not even in the negative query.
        assert '-w' not in flags and all(receipt[name][k] for k in ('full_read',))
        assert receipt[name]['warnings'] == []
    for positive in ['strict_original', 'strict_deletions_ignored']:
        assert receipt[positive]['exit'] == 0 and receipt[positive]['verified'] == 1
        assert receipt[positive]['rat_zero']
    assert receipt['negative_path']['exit'] != 0 and receipt['negative_path']['verified'] == 0
    records = parse_binary_drat(raw)
    additions = [clause for kind, clause in records if kind == 'a']
    deletions = [clause for kind, clause in records if kind == 'd']
    receipt['trace'] = {
        'records': len(records), 'additions': len(additions), 'deletions': len(deletions),
        'clauses_with_duplicate_literals': sum(len(c) != len(set(c)) for c in additions),
        'clauses_with_complementary_literals': sum(any(-x in c for x in c) for c in additions),
        'ends_in_complete_record': raw[-1] == 0,
    }
    receipt['matching']['clauses_with_duplicate_literals'] = sum(
        len(c) != len(set(c)) for c in block.formula(True).clauses)
    assert receipt['trace']['clauses_with_duplicate_literals'] == 0
    assert receipt['trace']['clauses_with_complementary_literals'] == 0
    (OUT / 'direct-receipts.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
