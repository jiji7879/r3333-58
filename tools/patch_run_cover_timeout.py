#!/usr/bin/env python3
"""Cap the checker at N seconds and let a failed check skip the case.

Two changes to `run_cover.py`, neither touching how anything is verified:

1. `-t N` is appended to every drat-trim invocation, so a pathological
   certificate stops after N seconds instead of drat-trim's default 40000
   (~11 hours). The checker argument itself is untouched, so the recorded
   `checker_sha256` remains the real binary.
2. A checker failure is caught: the case gets `CHECK_FAILED.json` and no
   `verified.json`, so it stays OPEN in any release, and the shard continues
   instead of the exception killing the batch.

    python3 patch_run_cover_timeout.py /path/to/k58/run_cover.py [--seconds 300]
"""
import argparse
import sys
from pathlib import Path

OLD = '''        check_time,check_cpu = replay(args.checker,formula,proof,root.with_suffix(".check.log"),trim_args)
        kept = proof
        if args.trim:
            trim_wall,trim_cpu = replay(args.checker,formula,trimmed,root.with_suffix(".compact.log"))
            check_time += trim_wall
            check_cpu += trim_cpu
            kept = trimmed
'''

TEMPLATE = '''        limit = ("-t", str(CHECK_SECONDS))
        try:
            check_time,check_cpu = replay(args.checker,formula,proof,
                                          root.with_suffix(".check.log"),trim_args + limit)
            kept = proof
            if args.trim:
                trim_wall,trim_cpu = replay(args.checker,formula,trimmed,
                                            root.with_suffix(".compact.log"),limit)
                check_time += trim_wall
                check_cpu += trim_cpu
                kept = trimmed
        except RuntimeError as exc:
            # The checker rejected the proof or hit the time limit.  Write no
            # verified.json, so the case stays OPEN, and keep the shard running.
            (case/"CHECK_FAILED.json").write_text(
                __import__("json").dumps(dict(id=row["id"], stage=tier,
                                              reason=str(exc)[:400]), sort_keys=True) + "\\n")
            return "CHECK_FAILED"
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path", nargs="?", default="k58/run_cover.py")
    ap.add_argument("--seconds", type=int, default=300)
    a = ap.parse_args()
    path = Path(a.path)
    s = path.read_text()
    if "CHECK_FAILED" in s:
        print("already patched")
        return 0
    if OLD not in s:
        print("PATTERN NOT FOUND - file differs from the bundle version", file=sys.stderr)
        return 1
    text = s.replace(OLD, TEMPLATE.replace("CHECK_SECONDS", str(a.seconds)), 1)
    text = text.replace("def open_rows(args):",
                        f"CHECK_SECONDS = {a.seconds}\n\n\ndef open_rows(args):", 1)
    path.write_text(text)
    print(f"patched {path}: checker limit {a.seconds}s, failures skip the case")
    return 0


if __name__ == "__main__":
    sys.exit(main())
