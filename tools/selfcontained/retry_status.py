#!/usr/bin/env python3
"""Is the retry pass actually doing anything?  Read the receipts, not the log.

A retry attempt writes `<evidence>/<xx>/<case>/retry/<sec>s-<budget>/<name>.jsonl`.
This counts them, separates UNSAT from OPEN, and reports the conversion rate
against the first-pass cut-offs.

    python3 retry_status.py --evidence evidence
    python3 retry_status.py --evidence evidence --watch 60
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path


def scan(evidence):
    first = Counter()       # first-pass statuses
    retry = Counter()       # retry attempt statuses
    retry_dirs = Counter()  # which (secs,budget) settings were used
    verified = 0
    for marker in evidence.glob("[0-9a-f][0-9a-f]/*/verified.json"):
        verified += 1
    for case in evidence.glob("[0-9a-f][0-9a-f]/*"):
        for r in case.glob("first/*.jsonl"):
            try:
                first[json.loads(r.read_text())["status"]] += 1
            except Exception:
                first["unreadable"] += 1
        for r in case.glob("retry/*/*.jsonl"):
            try:
                retry[json.loads(r.read_text())["status"]] += 1
                retry_dirs[r.parent.name] += 1
            except Exception:
                retry["unreadable"] += 1
    return first, retry, retry_dirs, verified


def report(evidence):
    first, retry, retry_dirs, verified = scan(evidence)
    open_first = first.get("OPEN", 0)
    done = sum(retry.values())
    unsat = retry.get("UNSAT", 0)
    still = retry.get("OPEN", 0)
    print(f"first-pass attempts : {sum(first.values()):,}  {dict(first)}")
    print(f"verified cases      : {verified:,}")
    print(f"retry attempts      : {done:,}"
          + (f"  settings {dict(retry_dirs)}" if retry_dirs else ""))
    if done:
        print(f"  retry closed      : {unsat:,}")
        print(f"  retry still OPEN  : {still:,}")
        print(f"  conversion        : {unsat/done:.1%}")
    if open_first:
        remaining = open_first - done
        print(f"cut off at first pass: {open_first:,}")
        print(f"not yet retried      : {max(remaining,0):,}"
              + (f" ({max(remaining,0)/open_first:.0%} of the queue)" if open_first else ""))
    if done == 0 and open_first == 0:
        print("\nNothing to retry: every attempted case closed on the first pass.")
    elif done == 0:
        print("\nNo retry receipts yet.")
        print("If a retry job has been running for more than a few minutes, that is wrong:")
        print("  - check batch-state/batch.log for 'tier=retry' START/END pairs")
        print("  - an END only minutes after START, with this counter still 0,")
        print("    means the shard selected no OPEN cases (wrong --shards, or wrong --out)")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--evidence", required=True)
    p.add_argument("--watch", type=int, default=0, help="repeat every N seconds")
    a = p.parse_args()
    ev = Path(a.evidence)
    if not ev.is_dir():
        sys.exit(f"no such directory: {ev}")
    while True:
        print(time.strftime("%H:%M:%S"))
        report(ev)
        if not a.watch:
            return 0
        print("-" * 60, flush=True)
        time.sleep(a.watch)


if __name__ == "__main__":
    main()
