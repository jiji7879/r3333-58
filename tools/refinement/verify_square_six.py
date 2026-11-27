#!/usr/bin/env python3
"""Strictly verify the K58_square_six package and build its augmentation."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def require(ok, message):
    if not ok:
        raise ValueError(message)


def main():
    if not __debug__:
        raise RuntimeError('Python assertions must be enabled for proof replay.')
    args = sys.argv[1:]
    if len(args) != 3:
        raise SystemExit('usage: verify_square_six.py PACKAGE CHECKER OUTPUT_DIR')
    package, checker, out = (Path(p).resolve() for p in args)
    out.mkdir(parents=True, exist_ok=False)
    require(checker.is_file(), 'checker is missing')
    sys.path.insert(0, str(package))
    import verify
    seen = []

    def strict(executable, formula, proof):
        index = len(seen) + 1
        with tempfile.TemporaryDirectory() as td:
            tmp = Path(td)
            q, p = tmp / 'query.cnf', tmp / 'proof.drat'
            q.write_bytes(formula)
            p.write_bytes(proof)
            command = [str(checker), str(q), str(p), '-i', '-U', '-t', '300']
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
            statuses = [line for line in result.stdout.splitlines() if line.startswith(b's ')]
            good = (result.returncode == 0 and statuses == [b's VERIFIED']
                    and b'WARNING' not in result.stdout.upper())
            (out / f'proof-check-{index}.log').write_bytes(result.stdout)
            require(good, f'strict proof check {index} failed: {result.stdout[-500:]!r}')
        observed = {'query_sha256': hashlib.sha256(formula).hexdigest(),
                    'proof_sha256': hashlib.sha256(proof).hexdigest(),
                    'proof_bytes': len(proof), 'warning_free': True,
                    'flags': ['-i', '-U', '-t', '300']}
        seen.append(observed)
        print(json.dumps(observed, sort_keys=True))

    verify.check_proof = strict
    verify.main()
    (out / 'receipts.json').write_text(json.dumps(seen, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
