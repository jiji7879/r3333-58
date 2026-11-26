#!/usr/bin/env python3
"""Positive-control hash, unit-aware encoding, and collision rejection.

Run with the project's pinned Python (currently .scratch/k58/.venv/bin/python).
No CDCL run and no DRAT verdict is implied by these encoder checks.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PYTHON = sys.executable


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(*args):
    proc = subprocess.run([PYTHON, *[str(x) for x in args]], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    return proc.stdout


def expect_failure(*args):
    proc = subprocess.run([PYTHON, *[str(x) for x in args]], capture_output=True, text=True)
    assert proc.returncode != 0, 'negative control unexpectedly succeeded'
    return proc.stderr


with tempfile.TemporaryDirectory(dir=ROOT / '.scratch') as td:
    td = Path(td)
    # A real independently certified augmented leaf from the verified K58 work.
    src = ROOT / '.ultramath/smwwdcyxb/m6/leaf-n017.cnf'
    expected = ROOT / '.ultramath/smwwdcyxb/m6/leaf-n017-dcap.cnf'
    out = td / 'n017-dcap.cnf'
    raw = run(HERE / 'global_degree_caps.py', src, out)
    print(raw, end='')
    assert sha(out) == sha(expected) == 'eb37b0697699c0a20213b906f305e6a86fda44dcfd4c776fb2a43729e526889a'
    run(HERE / 'validate_degree_caps.py', src, out)
    print('PASS exact existing m6 degree-cap parent (same bytes and hash)')

    # Unit-aware counter trimming, checked by an independent suffix rewrite.
    parent = td / 'small-parent.cnf'
    parent.write_text('p cnf 6612 4\n1 0\n-2 0\n5 0\n6612 0\n')
    out = td / 'small-unit-aware.cnf'
    run(HERE / 'global_degree_caps.py', parent, out, '--unit-aware')
    run(HERE / 'validate_degree_caps.py', parent, out, '--unit-aware')
    meta = json.loads(out.with_suffix('.json').read_text())
    assert meta['unit_aware'] is True and meta['parent_sha256'] == sha(parent)
    print('PASS unit-aware suffix and parent hash')

    # An undeclared parent variable must be refused before generating output.
    bad = td / 'undeclared.cnf'
    bad.write_text('p cnf 6611 1\n6612 0\n')
    no_output = td / 'must-not-exist.cnf'
    err = expect_failure(HERE / 'global_degree_caps.py', bad, no_output)
    assert 'input maximum/declaration mismatch' in err and not no_output.exists()
    print('PASS rejected undeclared parent maximum')

print('All encoder tests passed. No solver status or speedup is claimed.')
