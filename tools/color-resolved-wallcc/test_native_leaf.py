"""Micro integration tests for the opt-in native engine and its policy binding."""
import itertools
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

import native_leaf
from campaign import check_trace, replay
from problem import ROOT, check_model, file_hash, read_dimacs


def args(seconds=10, conflicts=100000, policy="default"):
    return SimpleNamespace(seconds=seconds, conflicts=conflicts, native_policy=policy)


def cli(*arguments):
    run = subprocess.run([sys.executable, str(ROOT / 'wallcc.py'), *map(str, arguments)],
                         text=True, capture_output=True, timeout=30)
    assert run.returncode == 0, (run.returncode, run.stdout, run.stderr)
    return json.loads(run.stdout.splitlines()[-1])


def ramsey(n):
    edge = {uv: i for i, uv in enumerate(itertools.combinations(range(n), 2), 1)}
    clauses = []
    for u, v, w in itertools.combinations(range(n), 3):
        t = [edge[u, v], edge[v, w], edge[u, w]]
        clauses.extend((t, [-x for x in t]))
    return f'p cnf {len(edge)} {len(clauses)}\n'.encode() + b''.join(
        ' '.join(map(str, c)).encode() + b' 0\n' for c in clauses)


def main():
    assert file_hash(native_leaf.BINARY) == 'a4a6dc61458f4fbb86cd4084e0249b0e93aae239816d58c3fb707a0a0bc7e48b'
    with tempfile.TemporaryDirectory(prefix='native-leaf-', dir=Path(__file__).resolve().parents[2] / '.scratch') as name:
        out = Path(name)
        (out / 'cas.drat').write_bytes(b'')
        parent = out / 'parent.cnf'
        parent.write_bytes(b'p cnf 2 2\n1 2 0\n-1 2 0\n')
        for policy in ('default', 'search-only'):
            result = native_leaf.solve(parent, out, [], args(policy=policy), True)
            assert result['status'] == 'SAT' and result['native_policy'] == policy
            nv, clauses = read_dimacs(parent.read_bytes())
            check_model(clauses, [], json.loads((out / 'model.json').read_text()), nv)

        parent.write_bytes(b'p cnf 1 2\n1 0\n-1 0\n')
        result = native_leaf.solve(parent, out, [], args(), True)
        assert result['status'] == 'UNSAT', result
        good, log = replay(out, out, [], out / 'leaf.drat',
                           ROOT / 'tools/drat-trim', 10)
        assert good, log
        bad = out / 'damaged.drat'
        bad.write_bytes((out / 'leaf.drat').read_bytes() + b'not a proof')
        good, _ = replay(out, out, [], bad, ROOT / 'tools/drat-trim', 10)
        assert not good, 'suffix-corrupted proof was accepted'
        try:
            check_trace(parent, out / 'leaf.drat', ROOT / 'tools/drat-trim', 10, '-w')
        except ValueError as error:
            assert 'warning controls are forbidden' in str(error)
        else:
            raise AssertionError('warning-suppressed checker invocation was accepted')

        parent.write_bytes(ramsey(6))
        result = native_leaf.solve(parent, out, [], args(conflicts=1), True)
        assert result['status'] == 'OPEN' and result['reason'] == 'conflict limit'
        result = native_leaf.solve(parent, out, [], args(seconds=0), False)
        assert result['status'] == 'OPEN' and result['reason'] == 'wall-time limit'
        try:
            native_leaf.solve(parent, out, [], args(policy='not-a-policy'), False)
        except ValueError:
            pass
        else:
            raise AssertionError('invalid native policy accepted')

        run = out / 'whole'
        cli('run', '--cnf', parent, '--out', run, '--depth', 0,
            '--engine', 'native', '--native-policy', 'default', '--conflicts', 1, '--seconds', 5)
        first = json.loads((run / 'leaves/r/receipt.json').read_text())
        assert first['status'] == 'OPEN' and first['budget']['native_policy'] == 'default'
        assert first['budget']['native_sha256'] == file_hash(native_leaf.BINARY)
        cli('resume', run, '--engine', 'native', '--native-policy', 'search-only',
            '--conflicts', 1, '--seconds', 5)
        second = json.loads((run / 'leaves/r/receipt.json').read_text())
        assert second['status'] == 'OPEN' and second['budget']['native_policy'] == 'search-only'
        assert second['conflicts_used'] == first['conflicts_used'] == 1
        assert second['status_line'] == 'c UNKNOWN' and second['solver_exit'] == 0

        closed_run = out / 'closed'
        cli('run', '--cnf', run / 'parent.cnf', '--out', closed_run, '--depth', 0,
            '--engine', 'native', '--native-policy', 'default', '--conflicts', 100000,
            '--seconds', 5)
        verified = json.loads((closed_run / 'leaves/r/receipt.json').read_text())
        assert verified['status'] == 'CHECKED_UNSAT'
        cli('resume', closed_run, '--engine', 'native', '--native-policy', 'search-only',
            '--conflicts', 100000, '--seconds', 5)
        switched = json.loads((closed_run / 'leaves/r/receipt.json').read_text())
        assert switched['status'] == 'CHECKED_UNSAT'
        assert switched['budget']['native_policy'] == 'search-only'
        cli('resume', closed_run, '--conflicts', 100000, '--seconds', 5)
        restored = json.loads((closed_run / 'leaves/r/receipt.json').read_text())
        assert restored['solver'] == 'CaDiCaL 1.9.5 / python-sat 1.9.dev22'
        assert 'engine' not in restored['budget']

        default_run = out / 'default'
        cli('run', '--cnf', parent, '--out', default_run, '--depth', 0,
            '--conflicts', 1, '--seconds', 5)
        legacy = json.loads((default_run / 'leaves/r/receipt.json').read_text())
        assert legacy['solver'] == 'CaDiCaL 1.9.5 / python-sat 1.9.dev22'
        assert 'engine' not in legacy['budget']

    print('PASS native SAT, UNSAT replay, corrupt-proof rejection, bounded OPEN, '
          'unknown/invalid policies, resume budget binding and unchanged PySAT defaults.')


if __name__ == '__main__':
    main()
