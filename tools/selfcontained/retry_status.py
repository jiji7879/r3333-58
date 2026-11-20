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
import os
import sys
import time
from collections import Counter
from pathlib import Path


def scan(evidence, progress=False):
    """One walk over the evidence tree; no per-case globbing."""
    first = Counter()       # first-pass statuses
    retry = Counter()       # retry attempt statuses
    retry_dirs = Counter()  # which (secs,budget) settings were used
    verified = 0
    seen = 0
    for case in os.scandir(evidence):
        if not case.is_dir() or len(case.name) != 2:
            continue
        for ent in os.scandir(case.path):
            if not ent.is_dir():
                continue
            seen += 1
            if progress and seen % 20000 == 0:
                print(f"  ... {seen:,} cases scanned", file=sys.stderr, flush=True)
            sub = case.path + "/" + ent.name
            if os.path.exists(sub + "/verified.json"):
                verified += 1
            for kind, bucket in (("first", first), ("retry", retry)):
                d = sub + "/" + kind
                if not os.path.isdir(d):
                    continue
                for entry in os.scandir(d):
                    if early := (entry.name.endswith(".jsonl") and kind == "first"):
                        bucket[_status(entry.path)] += 1
                    elif kind == "retry" and entry.is_dir():
                        retry_dirs[entry.name] += 1
                        for f in os.scandir(entry.path):
                            if f.name.endswith(".jsonl"):
                                retry[_status(f.path)] += 1
    return first, retry, retry_dirs, verified


def _status(path):
    try:
        with open(path) as fh:
            return json.load(fh).get("status", "unknown")
    except Exception:
        return "unreadable"


def batch_says(batch_log):
    """Has a retry job been started according to the batch log?"""
    started = finished = False
    try:
        for line in Path(batch_log).read_text().splitlines():
            if "tier=retry" in line and "START" in line:
                started = True
            if "tier=retry" in line and "END" in line:
                finished = True
    except Exception:
        return None, None
    return started, finished


def report(evidence, batch_log=None):
    first, retry, retry_dirs, verified = scan(evidence, progress=True)
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
        started, finished = batch_says(batch_log) if batch_log else (None, None)
        if started is False or started is None:
            print("\nNo retry receipts yet, and the batch log shows no retry job started.")
            print("That is expected while the first pass is still running: the batch")
            print("does every first-pass shard before it begins retrying.")
        else:
            print("\nA retry job started but has produced no receipts yet.")
            print("Recent lines to look at:")
            print(f"  tail -5 {batch_log}")
            print("An END only minutes after START with 0 receipts means the shard")
            print("selected no OPEN cases (wrong --shards, or wrong --out).")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--evidence", required=True)
    p.add_argument("--watch", type=int, default=0, help="repeat every N seconds")
    p.add_argument("--batch-log", default=None, help="batch-state/batch.log")
    a = p.parse_args()
    ev = Path(a.evidence)
    if not ev.is_dir():
        sys.exit(f"no such directory: {ev}")
    while True:
        print(time.strftime("%H:%M:%S"), flush=True)
        report(ev, a.batch_log)
        if not a.watch:
            return 0
        print("-" * 60, flush=True)
        time.sleep(a.watch)


if __name__ == "__main__":
    main()
