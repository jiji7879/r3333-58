#!/usr/bin/env python3
"""Replay all fourteen distinct closed H11p terminals named by m6."""
import hashlib
from pathlib import Path
import json
import subprocess
import time


def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    member = repo / '.ultramath/smwxbvh79/m6'
    checker = member / 'checker/drat-trim'
    checker_sha = hashlib.sha256(checker.read_bytes()).hexdigest()
    old = json.loads((here / 'm6-closed-subtree-coordinator-replay.json').read_text())
    by_id = {x['id']: x for x in old['leaves']}
    frontier = json.loads((member / 'frontier-c488_021-001.json').read_text())
    assert len(frontier['closed']) == 14
    for leaf in frontier['closed']:
        node = leaf['id']
        if node in by_id:
            assert by_id[node]['cnf_sha256'] == leaf['H11p_cnf_sha256']
            assert by_id[node]['drat_sha256'] == leaf['drat_sha256']
            continue
        cnf = member / 'cnf' / f'H11p-{node}.cnf'
        proof = member / leaf['drat_path']
        assert hashlib.sha256(cnf.read_bytes()).hexdigest() == leaf['H11p_cnf_sha256']
        assert hashlib.sha256(proof.read_bytes()).hexdigest() == leaf['drat_sha256']
        log = here / f'm6-{node}-coordinator-replay.log'
        before = time.monotonic()
        with log.open('wb') as stream:
            run = subprocess.run([str(checker), str(cnf), str(proof), '-i', '-w'],
                                 stdout=stream, stderr=subprocess.STDOUT, check=False)
        text = log.read_text(errors='replace')
        rec = {'id': node, 'returncode': run.returncode,
               'verified': any(line.strip() == 's VERIFIED' for line in text.splitlines()),
               'wall_seconds': round(time.monotonic() - before, 3),
               'cnf_sha256': leaf['H11p_cnf_sha256'], 'drat_sha256': leaf['drat_sha256'],
               'log': str(log.relative_to(repo))}
        assert run.returncode == 0 and rec['verified'], rec
        by_id[node] = rec
        print(json.dumps(rec), flush=True)
    result = {'augmentation': 'reverse H>=11 plus 590 exact-11 physical mask exclusions',
              'checker_sha256': checker_sha, 'distinct_terminals_replayed': 14,
              'scope': 'All 14 exact split-tree terminal certificates; not an original baseline or full-row closure.',
              'leaves': [by_id[x['id']] for x in frontier['closed']],
              'frontier_residuals': {},
              'cover_audit': 'audit_frontier.py rebuilt both frontier receipts byte-identically; exact signed cube splits checked',
             }
    for name in ['c488_021-001', 'c488_021-002']:
        data = json.loads((member / f'frontier-{name}.json').read_text())
        assert all(by_id[x['id']]['cnf_sha256'] == x['H11p_cnf_sha256']
                   for x in data['closed'])
        result['frontier_residuals'][name] = [x['id'] for x in data['open_residual']]
    (here / 'm6-all-terminal-proofs-coordinator-replay.json').write_text(
        json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
