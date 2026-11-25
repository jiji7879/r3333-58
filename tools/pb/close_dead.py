#!/usr/bin/env python3
"""Close the ticket-pin rows: build, solve, replay, record.

Every row of profile (15,14,14,14) with marked_size = 16 has d_arm(q) = 16 forced by the
ticket pin, so under perfect balance (all four degrees in {14,15}) it is dead by
16 + 3*14 > 57.  This decides that instance for real, on the relaxation
(host + units + balance, without the row threshold, so UNSAT transfers to the row) and
keeps the certificate:

    PYTHONPATH=<site-packages> python3 tools/pb/close_dead.py OUTDIR [--kissat K] [--checker D]

OUTDIR/ticketpin29.tsv has one line per row: id, status, seconds, CNF clauses, CNF sha256,
proof bytes, proof sha256, and the checker's verdict line.  Nothing is written outside
OUTDIR.  The balance encoding is two-sided: the upper bound is implied, but without it
CDCL leaves these rows UNKNOWN past 300 s.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, 'tools/pb')
from balance import build

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def dead_rows():
    """The marked_size = 16 rows of profile (15,14,14,14), from the frozen ledger."""
    import gzip
    out = []
    with gzip.open(ROOT / '.scratch/k58/case-ledger.jsonl.gz', 'rt') as fh:
        for line in fh:
            row = json.loads(line)
            fam = row['family']
            if tuple(fam['profile']) == (15, 14, 14, 14) and fam['marked_size'] == 16:
                out.append(row['id'])
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('outdir')
    parser.add_argument('--kissat', default=str(ROOT / '.ultramath/smwmq7hji/m3/bin/kissat'))
    parser.add_argument('--checker', default=str(ROOT / '.ultramath/smwmq7hji/m3/bin/drat-trim'))
    options = parser.parse_args()
    out = Path(options.outdir)
    out.mkdir(parents=True, exist_ok=True)

    rows = dead_rows()
    print('%d ticket-pin rows' % len(rows), flush=True)
    lines = ['id\tstatus\tseconds\tclauses\tcnf_sha256\tproof_bytes\tproof_sha256\tchecker']
    for i, rid in enumerate(rows, 1):
        cnf, _ = build(rid, balance=True, stats=False)
        cnf_path = out / (rid + '.cnf')
        proof_path = out / (rid + '.drat')
        cnf.to_file(str(cnf_path))
        started = time.time()
        run = subprocess.run([options.kissat, '-q', str(cnf_path), str(proof_path)],
                             capture_output=True, text=True)
        seconds = time.time() - started
        if run.returncode != 20:
            status = 'NOT_REFUTED(rc=%d)' % run.returncode
            checker = ''
        else:
            status = 'UNSAT'
            replay = subprocess.run([options.checker, str(cnf_path), str(proof_path)],
                                    capture_output=True, text=True)
            verdict = [l for l in replay.stdout.splitlines() if l.startswith('s ')]
            checker = verdict[0] if verdict else 'checker said nothing'
        lines.append('\t'.join([rid, status, '%.2f' % seconds, str(len(cnf.clauses)),
                                digest(cnf_path), str(proof_path.stat().st_size),
                                digest(proof_path), checker]))
        print('%2d/%d %s %s %.2fs %s' % (i, len(rows), rid[:12], status, seconds, checker), flush=True)
    (out / 'ticketpin29.tsv').write_text('\n'.join(lines) + '\n')
    bad = [l for l in lines[1:] if '\tUNSAT\t' not in l or 'VERIFIED' not in l]
    print('all 29 refuted and replayed' if not bad else 'FAILURES: %d' % len(bad))
    return 0 if not bad else 1


if __name__ == '__main__':
    sys.exit(main())
