#!/usr/bin/env python3
"""Run one hash-pinned wall-row CNF with an explicit solver wall clock.

Only a completed UNSAT result with native DRAT replay is called a certificate.
OPEN runs delete their traces; SAT retains only the encoding/model log.
The caller controls concurrency; the default is 300 seconds per run.
"""
import argparse
import hashlib
from pathlib import Path
import json
import resource
import subprocess
import time


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('cnf', type=Path)
    p.add_argument('expected_sha256')
    p.add_argument('engine', choices=['kissat', 'cadical'])
    p.add_argument('work', type=Path)
    p.add_argument('--seconds', type=int, default=300)
    p.add_argument('--results-dir', type=Path, default=Path('results/wall-row-300-2026-11-26'))
    args = p.parse_args()
    if args.seconds <= 0:
        p.error('--seconds must be positive')
    assert sha(args.cnf) == args.expected_sha256, 'input hash mismatch'
    args.work.mkdir(parents=True, exist_ok=False)
    root = Path(__file__).resolve().parents[1]
    results = args.results_dir if args.results_dir.is_absolute() else root / args.results_dir
    results.mkdir(parents=True, exist_ok=True)
    kissat = args.work.parent / 'bin/kissat'
    assert sha(kissat) == 'b77de62fb1945d2ffab165b1f05e25c9e8ae7fc43de3a4fb8346fc2c9954097f'
    checker = root / '.ultramath/smwxbvh79/m6/checker/drat-trim'
    assert sha(checker) == 'dc0fb03ed4a924d9721545baa215941d336d296719796f05747970ee63aac6de'
    drat = args.work / 'proof.drat'
    log = args.work / 'solver.log'
    if args.engine == 'kissat':
        argv = [str(kissat), f'--time={args.seconds}', str(args.cnf.resolve()), str(drat)]
    else:
        argv = ['/opt/lean/bin/cadical', '-t', str(args.seconds), str(args.cnf.resolve()), str(drat)]
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    begin = time.monotonic()
    started_utc = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    with log.open('wb') as stream:
        try:
            completed = subprocess.run(argv, stdout=stream, stderr=subprocess.STDOUT,
                                       check=False, timeout=args.seconds + 60)
            rc = completed.returncode
            timed_out = False
        except subprocess.TimeoutExpired as exc:
            rc = None
            timed_out = exc
    elapsed = time.monotonic() - begin
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    record = {
        'cnf': str(args.cnf), 'cnf_sha256': args.expected_sha256,
        'engine': args.engine, 'command': argv,
        'solver_wall_limit_seconds': args.seconds, 'conflict_limit': None,
        'watchdog_seconds': args.seconds + 60, 'started_utc': started_utc,
        'wall_seconds': elapsed, 'returncode': rc,
        'user_cpu_seconds': after.ru_utime - before.ru_utime,
        'system_cpu_seconds': after.ru_stime - before.ru_stime,
        'log': str(log), 'log_sha256': sha(log), 'watchdog_timeout': bool(timed_out),
        'process_scope': 'one solver subprocess per invocation; caller controls concurrency',
        'scope': 'The complete hash-pinned first-tier-row formula plus its named directional cuts. Not a Ramsey conclusion by itself.',
    }
    text = log.read_text(errors='replace')
    if rc == 20:
        record['solver_result'] = 'UNSAT'
        record['drat_bytes'] = drat.stat().st_size
        record['drat_sha256'] = sha(drat)
        verify_log = args.work / 'verify.log'
        begin_check = time.monotonic()
        with verify_log.open('wb') as stream:
            checked = subprocess.run([str(checker), str(args.cnf.resolve()), str(drat), '-i', '-w'],
                                     stdout=stream, stderr=subprocess.STDOUT, check=False)
        verify_text = verify_log.read_text(errors='replace')
        record['verification_wall_seconds'] = time.monotonic() - begin_check
        record['verification_returncode'] = checked.returncode
        record['verification_log'] = str(verify_log)
        record['verified'] = checked.returncode == 0 and any(
            line.strip() == 's VERIFIED' for line in verify_text.splitlines())
        record['status'] = 'CERTIFIED_ROW_UNSAT' if record['verified'] else 'UNVERIFIED_PROOF_ERROR'
    elif rc == 10:
        record['solver_result'] = 'SAT_ENCODING_MODEL'
        record['status'] = 'SAT_ENCODING_MODEL_REQUIRES_INDEPENDENT_PHYSICAL_DECODING'
        drat.unlink(missing_ok=True)
    elif rc == 0 or timed_out:
        record['solver_result'] = 'OPEN'
        record['status'] = f'OPEN_AT_{args.seconds}_SECONDS' if not timed_out else 'OPEN_WATCHDOG_TIMEOUT'
        drat.unlink(missing_ok=True)
        record['unfinished_trace_deleted'] = not drat.exists()
    else:
        record['status'] = 'SOLVER_ERROR'
        record['unfinished_trace_deleted'] = True
        drat.unlink(missing_ok=True)
    (args.work / 'result.json').write_text(json.dumps(record, indent=2) + '\n')
    (results / f'{args.work.name}.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2), flush=True)
    if record['status'] in {'SOLVER_ERROR', 'UNVERIFIED_PROOF_ERROR'}:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
