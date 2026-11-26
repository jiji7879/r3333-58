#!/usr/bin/env python3
"""Finish the six omitted entrance DRAT replays, with bounded concurrency."""
import gzip
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'results/entrance-brace-audit-2026-11-26'
儿 = ROOT / '.ultramath/smwwdcyxb/m2'
sys.path.insert(0, str(儿))
import drive_ent as D
import entcases as E

TMP = ROOT / '.scratch/coordinator-entrance'
TMP.mkdir(parents=True, exist_ok=True)
DRAT = 儿 / '.scratch/bin/drat-trim'
CACHE = {}


def one(rec):
    fam, key = rec['family'], rec['key']
    kinds_s, p_s, shape_s = fam.split(':')
    kinds = (kinds_s[0], kinds_s[1])
    if fam not in CACHE:
        CACHE[fam] = dict(D.enumerate_cases(kinds, int(p_s), tuple(map(int, shape_s.split(','))))[0])
    clauses = E.base_cnf(kinds, CACHE[fam][key])
    nv = max(abs(lit) for cl in clauses for lit in cl)
    body = ['p cnf %d %d' % (nv, len(clauses))]
    body.extend(' '.join(map(str, c)) + ' 0' for c in clauses)
    blob = ('\n'.join(body) + '\n').encode()
    result = {'family': fam, 'key': key, 'cnf_match': hashlib.sha256(blob).hexdigest() == rec['cnf_sha256']}
    assert result['cnf_match'], 'CNF mismatch for %s %s' % (fam, key)
    with tempfile.TemporaryDirectory(dir=TMP) as td:
        cnf, prf = Path(td) / 'case.cnf', Path(td) / 'case.drat'
        cnf.write_bytes(blob)
        raw = gzip.open(儿 / rec['proof_gz'], 'rb').read()
        result['proof_match'] = hashlib.sha256(raw).hexdigest() == rec['proof_sha256']
        assert result['proof_match'], 'proof mismatch for %s %s' % (fam, key)
        prf.write_bytes(raw)
        del raw
        start = time.monotonic()
        run = subprocess.run([str(DRAT), str(cnf), str(prf)], capture_output=True, text=True)
        result['seconds'] = round(time.monotonic() - start, 3)
        log = OUT / ('verify-' + key + '.log')
        log.write_text(run.stdout + '\n--- stderr ---\n' + run.stderr +
                       '\n--- command ---\n' + ' '.join(run.args) + '\nexit=%d\n' % run.returncode)
        result['verify_log'] = str(log.relative_to(ROOT))
        result['replay'] = 'VERIFIED' if 's VERIFIED' in run.stdout else 'FAILED'
        result['exit'] = run.returncode
    with open(OUT / 'replayed-missing.jsonl', 'a') as fh:
        fh.write(json.dumps(result) + '\n')
    print(json.dumps(result), flush=True)
    return result


if __name__ == '__main__':
    manifest = [json.loads(x) for x in open(儿 / 'proofs/manifest.jsonl')]
    seen = set()
    legacy = OUT / 'replayed-missing.jsonl'
    if legacy.exists():
        for line in open(legacy):
            rec = json.loads(line)
            if rec.get('replay') == 'VERIFIED':
                seen.add((rec['family'], rec['key']))
    for line in open(儿 / 'proofs/replay.jsonl'):
        rec = json.loads(line)
        if rec.get('replay') == 'VERIFIED':
            seen.add((rec['family'], rec['key']))
    todo = [r for r in manifest if r.get('drat') == 'VERIFIED' and (r['family'], r['key']) not in seen]
    todo.sort(key=lambda r: r['proof_bytes'])
    print('remaining certificates:', len(todo), flush=True)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(one, todo))
    assert all(r['replay'] == 'VERIFIED' for r in results)
    print('ALL REMAINING CERTIFICATES VERIFIED:', len(results), flush=True)
