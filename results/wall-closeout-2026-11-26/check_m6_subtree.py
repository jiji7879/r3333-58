#!/usr/bin/env python3
"""Replay the seven closed H11p terminals of m6's c488_021-005 subtree."""
import hashlib
from pathlib import Path
import json
import subprocess
import time


def main():
    here = Path(__file__).resolve().parent
    repo = here.parents[1]
    member = repo / '.ultramath/smwxbvh79/m6'
    closure = json.loads((member / 'closure-c488_021-005.json').read_text())
    leaves = closure['leaves']
    assert closure['closed'] is True and len(leaves) == 7
    checker = member / 'checker/drat-trim'
    checker_sha = hashlib.sha256(checker.read_bytes()).hexdigest()
    assert checker_sha == 'dc0fb03ed4a924d9721545baa215941d336d296719796f05747970ee63aac6de'
    results = []
    for leaf in leaves:
        node = leaf['id']
        cnf = member / 'cnf' / f'H11p-{node}.cnf'
        proof = member / 'runs' / f'H11p-{node}' / f'H11p-{node}.kissat.drat'
        assert hashlib.sha256(cnf.read_bytes()).hexdigest() == leaf['cnf_sha256']
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
               'cnf_sha256': leaf['cnf_sha256'], 'drat_sha256': leaf['drat_sha256'],
               'log': str(log.relative_to(repo))}
        assert run.returncode == 0 and rec['verified'], rec
        results.append(rec)
        print(json.dumps(rec), flush=True)
    receipt = {'parent': 'c488_021-005', 'augmentation': 'reverse H>=11 plus 590 certified exact-11 mask exclusions',
               'scope': 'Exact closed nested augmented subtree; not the baseline parent or any frozen-row closure.',
               'split_cover_receipt': 'm6/closure-c488_021-005.json and independently run m6/audit_frontier.py',
               'checker_sha256': checker_sha, 'all_seven_replayed': True, 'leaves': results}
    (here / 'm6-closed-subtree-coordinator-replay.json').write_text(json.dumps(receipt, indent=2) + '\n')


if __name__ == '__main__':
    main()
