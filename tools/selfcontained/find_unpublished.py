#!/usr/bin/env python3
"""Find cases that the solver closed but which have no published certificate.

Two kinds of gap are reported separately:

  UNSAT, no certificate   an attempt returned UNSAT but verified.json is absent
                          (interrupted between receipt and certificate); the
                          certificate is rebuilt from the receipt by re-running
                          the shard, no re-solving.

  still OPEN              every attempt so far returned OPEN at its budget.

    python3 find_unpublished.py --evidence evidence [--write-open open-ids.txt]
"""
import argparse
import json
import os
from pathlib import Path


def statuses(case):
    out = []
    for kind in ("first", "retry"):
        for f in sorted((case / kind).rglob("*.jsonl")):
            try:
                out.append((kind, json.loads(f.read_text()).get("status")))
            except Exception:
                out.append((kind, "unreadable"))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--write-open", help="write the still-OPEN case ids here")
    a = ap.parse_args()
    ev = Path(a.evidence)
    closed_no_cert, still_open, verified = [], [], 0
    for two in os.scandir(ev):
        if not two.is_dir() or len(two.name) != 2:
            continue
        for ent in os.scandir(two.path):
            if not ent.is_dir():
                continue
            case = Path(ent.path)
            has_cert = (case / "verified.json").exists()
            verified += has_cert
            st = statuses(case) if not has_cert or a.write_open else []
            if has_cert:
                continue
            if any(s == "UNSAT" for _, s in st):
                closed_no_cert.append(case.name)
            elif st and all(s == "OPEN" for _, s in st):
                still_open.append(case.name)

    print(f"verified certificates      : {verified:,}")
    print(f"UNSAT without certificate  : {len(closed_no_cert):,}")
    print(f"still OPEN at every budget : {len(still_open):,}")
    if closed_no_cert:
        print("\nUNSAT but unpublished (re-run their shard; no re-solving needed):")
        for c in closed_no_cert[:20]:
            print("  ", c)
        if len(closed_no_cert) > 20:
            print(f"   ... and {len(closed_no_cert)-20:,} more")
    if a.write_open and still_open:
        Path(a.write_open).write_text("\n".join(sorted(still_open)) + "\n")
        print(f"\nwrote {len(still_open):,} OPEN case ids to {a.write_open}")


if __name__ == "__main__":
    main()
