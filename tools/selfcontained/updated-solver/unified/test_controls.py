#!/usr/bin/env python3
"""Timeout/identity control tests; uses a temporary stub, never a real wall sweep."""
import json
import os
from pathlib import Path
import sys
import tempfile
import time

import driver


def main():
    with tempfile.TemporaryDirectory(prefix='k58-timeout-test-', dir=sys.argv[1]) as name:
        root = Path(name)
        (root / 'color-resolved-wallcc').mkdir()
        (root / 'bin').mkdir()
        stub = root / 'color-resolved-wallcc/wallcc.py'
        stub.write_text('import subprocess,time,json\n'
                        'p=subprocess.Popen(["sleep","30"])\n'
                        'print(json.dumps({"pid":p.pid}),flush=True)\n'
                        'time.sleep(30)\n')
        checker = root / 'bin/drat-trim'; checker.write_text('placeholder for timeout control\n')
        original_root = driver.ROOT
        driver.ROOT = root
        job = {'kind':'external','variant':'external','id':'test',
               'source':str(stub), 'name':'toy.cnf'}
        plan = {'split':{'depth':1,'lookahead':12}}
        limits = {'out':str(root), 'wall_seconds_per_call':1,
                  'seconds_per_leaf':1,'conflicts_per_leaf':1,'check_seconds':1}
        started=time.monotonic()
        result = driver.engine(job,plan,'prepare',limits)
        elapsed = time.monotonic()-started
        driver.ROOT=original_root
        assert result['timeout'] and result['exit_code'] is not None, result
        assert elapsed < 5, elapsed
        log=(root/'jobs/test/prepare.log').read_text()
        token=json.loads(log.splitlines()[0]);pid=token['pid']
        proc=Path('/proc')/str(pid)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if not proc.exists():
                break
            state = (proc/'stat').read_text().split()[2] if (proc/'stat').exists() else 'Z'
            if state == 'Z':
                break  # Already killed: not a running solver after group kill.
            time.sleep(0.01)
        if proc.exists():
            state = (proc/'stat').read_text().split()[2]
            assert state == 'Z', f'live timeout child {pid}: {state}'
        payload={'status':'PASS','whole_process_group_killed':True,'timeout_returncode':result['exit_code'],
                 'inference':'no SAT/UNSAT assertion from timeout'}
        print(json.dumps(payload,indent=2))


if __name__=='__main__': main()
