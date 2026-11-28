#!/usr/bin/env python3
"""Require rejection of an actually halved normalized proof (no `-w`)."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
import sys


def main():
    folder = Path(sys.argv[1])
    original = (folder / 'proof-nodeletions.drat').read_bytes()
    half = original[:(len(original) // 2)]
    assert len(half) < len(original)
    target = folder / 'negative-truncated.drat'
    target.write_bytes(half)
    assert target.stat().st_size == len(half)
    command = [folder / 'query.cnf', target]
    checker = json.loads((folder / 'strict-replay.json').read_text())['checker_command'][0]
    run = subprocess.run([checker, str(command[0]), str(command[1]), '-i', '-U', '-W', '-t', '300'],
                         capture_output=True, timeout=300)
    log = (run.stdout + run.stderr).decode('latin1')
    (folder / 'negative-truncated.log').write_text(log)
    status = [line for line in log.splitlines() if line.startswith('s ')]
    rejected = run.returncode != 0 and status != ['s VERIFIED'] and b's VERIFIED' not in run.stdout
    result = {'rejected': rejected, 'returncode': run.returncode,
              'original_normalized_bytes': len(original), 'truncated_bytes': len(half),
              'original_normalized_sha256': hashlib.sha256(original).hexdigest(),
              'truncated_sha256': hashlib.sha256(half).hexdigest(),
              'status_lines': status, 'flags': ['-i', '-U', '-W', '-t', '300'],
              'warning_suppression': False}
    (folder / 'negative-replay.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))
    raise SystemExit(0 if rejected else 1)


if __name__ == '__main__':
    main()
