#!/usr/bin/env python3
"""Bounded fresh-CaDiCaL leaf controls; strict replay only for actual UNSAT."""
import argparse, hashlib, json, resource, shutil, subprocess, time
from pathlib import Path
from audit_cubes import read_cubes


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def without_deletions(data):
    """Remove binary d records, preserving additions; independently replay afterwards."""
    output = bytearray()
    additions = deletions = 0
    position = 0
    while position < len(data):
        kind = data[position]
        if kind not in (ord('a'), ord('d')):
            raise ValueError(f'invalid binary DRAT tag {kind} at {position}')
        start = position
        position += 1
        while True:
            if position >= len(data):
                raise ValueError('truncated binary DRAT literal')
            byte = data[position]
            position += 1
            if byte == 0:
                break
        if kind == ord('a'):
            output.extend(data[start:position])
            additions += 1
        else:
            deletions += 1
    if not output.endswith(b'a\0'):
        raise ValueError('proof has no final added empty clause')
    return bytes(output), {'additions_preserved': additions, 'deletions_removed': deletions}


def write_query(parent, cube, out):
    first = parent.open('rb').readline().split()
    nv, nc = int(first[2]), int(first[3])
    with out.open('wb') as dst:
        dst.write(f'p cnf {nv} {nc + len(cube)}\n'.encode())
        with parent.open('rb') as src:
            src.readline()  # discard the old header after writing the updated one
            shutil.copyfileobj(src, dst, 1 << 20)
        for lit in cube:
            dst.write(f'{lit} 0\n'.encode())


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--label', required=True)
    p.add_argument('--cubes', type=Path, required=True)
    p.add_argument('--python', type=Path, required=True)
    p.add_argument('--worker', type=Path, required=True)
    p.add_argument('--run', type=Path, required=True, help='contains parent/working/cas.drat')
    p.add_argument('--checker', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--conflicts', type=int, default=1000000)
    p.add_argument('--seconds', type=int, default=300)
    p.add_argument('--check-seconds', type=int, default=300)
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    cubes = read_cubes(args.cubes)
    receipts = []
    for index, cube in enumerate(cubes):
        started = time.monotonic()
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        attempt = args.out / f'leaf-{index}'
        attempt.mkdir()
        cmd = [str(args.python.absolute()), str(args.worker.resolve()), str((args.run / 'working.cnf').resolve()),
               str(attempt), str(args.conflicts), 'trace', *map(str, cube)]
        run = subprocess.run(cmd, capture_output=True, timeout=args.seconds)
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        elapsed = time.monotonic() - started
        (attempt / 'worker.stdout').write_bytes(run.stdout)
        (attempt / 'worker.stderr').write_bytes(run.stderr)
        if run.returncode:
            raise RuntimeError(f'worker failed on {cube}: {run.stderr[-1000:]!r}')
        result = json.loads(run.stdout)
        rec = {'index': index, 'label': args.label, 'cube': cube,
               'status': result['status'], 'conflicts_used': result['conflicts_used'],
               'elapsed_s': elapsed, 'cpu_s': (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime),
               'budget': {'conflicts': args.conflicts, 'seconds': args.seconds, 'proof': 'eager'},
               'working_sha256': sha(args.run / 'working.cnf'), 'parent_sha256': sha(args.run / 'parent.cnf')}
        proof = attempt / 'leaf.drat'
        if result['status'] == 'UNSAT':
            if not proof.is_file():
                raise RuntimeError('UNSAT without proof')
            query = attempt / 'query.cnf'
            write_query(args.run / 'parent.cnf', cube, query)
            joined = attempt / 'joined.drat'
            with joined.open('wb') as dst:
                for path in (args.run / 'cas.drat', proof):
                    with path.open('rb') as src:
                        shutil.copyfileobj(src, dst, 1 << 20)
            normalized, normalization = without_deletions(joined.read_bytes())
            normalized_path = attempt / 'joined.additions-only.drat'
            normalized_path.write_bytes(normalized)
            check = subprocess.run([str(args.checker.resolve()), str(query), str(normalized_path),
                                    '-i', '-U', '-t', str(args.check_seconds)],
                                   capture_output=True, timeout=args.check_seconds + 2)
            log = (check.stdout + check.stderr).replace(b'\r', b'\n')
            (attempt / 'strict-replay.log').write_bytes(log)
            lines = log.decode(errors='replace').splitlines()
            clean = not any('WARNING' in x or 'ERROR' in x for x in lines)
            passed = check.returncode == 0 and lines.count('s VERIFIED') == 1 and clean
            rec.update(query_sha256=sha(query), proof_sha256=sha(proof), joined_sha256=sha(joined),
                       normalized_proof_sha256=sha(normalized_path), normalization=normalization,
                       strict_verified=passed, checker_returncode=check.returncode,
                       checker_warning_or_error=not clean, checker_mode='binary additions-only RUP: -i -U; no -w')
            rec['status'] = 'CHECKED_UNSAT' if passed else 'CHECK_FAILED'
        elif result['status'] == 'SAT':
            rec['status'] = 'SAT_UNVERIFIED'
        if proof.exists() and rec['status'] == 'OPEN':
            rec['discarded_open_proof_bytes'] = proof.stat().st_size
            proof.unlink()  # incomplete traces are not evidence.
        receipts.append(rec)
        (args.out / 'receipts.json').write_text(json.dumps(receipts, indent=2, sort_keys=True) + '\n')
        print(json.dumps(rec, sort_keys=True), flush=True)
    counts = {s: sum(r['status'] == s for r in receipts) for s in sorted({r['status'] for r in receipts})}
    print(json.dumps({'label': args.label, 'leaves': len(receipts), 'counts': counts}, sort_keys=True))


if __name__ == '__main__':
    main()
