#!/usr/bin/env python3
"""Restore and import the 1,743 historical K58 closures.

`check` needs only the handoff bundle: it cross-checks every certified row of
the five historical manifests against the recovery kit's index, and confirms
that a proof is archived for each one.

`run` needs the evidence store (the .tar.zst shards) as well.  For every
certified row it restores the proof with the kit's `restore_evidence.py`, then
imports it through the bundle's `cover_evidence.py import-legacy` (which must
carry the `full_root` default; apply `tools/cover_evidence_full_root.patch`
first).  It is resumable: rows whose `verified.json` already exists are skipped.

Examples
--------
    python3 tools/import_historical.py check --bundle /path/to/k58
    python3 tools/import_historical.py run --bundle /path/to/k58 \
        --store /path/to/r58_evidence_store --out /path/to/evidence \
        --checker /path/to/drat-trim --only ttt --limit 20
"""
import argparse
import gzip
import json
import shutil
import subprocess
import sys
from pathlib import Path

MANIFESTS = {
    "campaign": ("r58_campaign", "historical/campaign.jsonl"),
    "ttt": ("r58_ttt_run", "historical/ttt.jsonl"),
    "anchor": ("r58_campaign", "historical/anchor-and-full-root.jsonl"),
    "pilot": ("r58_pilot_run", "historical/pilot.jsonl"),
    "pilot-tail": ("r58_pilot_run", "historical/pilot-tail.jsonl"),
}
CERTIFIED = ("UNSAT", "CERTIFIED")


def rows(path):
    with path.open() as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def index_paths(kit):
    with gzip.open(kit / "index.jsonl.gz", "rt") as fh:
        return {json.loads(line)["path"] for line in fh}


def proof_path(name, prefix, row, paths):
    """The archived path of a certified row's proof, or None."""
    if "proof" in row:
        candidate = f"workspace/{prefix}/{row['proof']}"
        return candidate if candidate in paths else None
    cid = row.get("id")
    if not cid:
        return None
    hits = [p for p in paths
            if f"/{cid}/" in p and (p.endswith(".drat") or p.endswith(".compact"))]
    return sorted(hits)[0] if hits else None


def case_id(bundle, row):
    sys.path.insert(0, str(bundle))
    import cover_evidence  # noqa: E402
    return cover_evidence.identity(row)


def cmd_check(args):
    bundle, kit = Path(args.bundle), Path(args.bundle) / "recovery"
    if not (kit / "index.jsonl.gz").exists():
        sys.exit(f"recovery index not found under {kit}")
    paths = index_paths(kit)
    total = found = 0
    for name, (prefix, rel) in MANIFESTS.items():
        if args.only and name != args.only:
            continue
        rows_here = 0
        for row in rows(bundle / rel):
            if row["status"] not in CERTIFIED:
                continue
            rows_here += 1
            total += 1
            p = proof_path(name, prefix, row, paths)
            if p:
                found += 1
            elif args.verbose:
                print(f"  missing: {name} {row.get('id', row.get('proof'))}")
        print(f"{name}: {rows_here} certified rows")
    print(f"total certified {total}, proofs present in the index {found}")
    return 0 if found == total else 1


def cmd_run(args):
    bundle = Path(args.bundle).resolve()
    kit = bundle / "recovery"
    paths = index_paths(kit)
    out = Path(args.out).resolve()
    work = Path(args.work).resolve()
    work.mkdir(parents=True, exist_ok=True)
    done = skipped = failed = 0
    log = (work / "import-log.jsonl").open("a")
    for name, (prefix, rel) in MANIFESTS.items():
        if args.only and name != args.only:
            continue
        for row in rows(bundle / rel):
            if row["status"] not in CERTIFIED:
                continue
            cid = case_id(bundle, row)
            if (out / cid[:2] / cid / "verified.json").exists():
                skipped += 1
                continue
            p = proof_path(name, prefix, row, paths)
            if p is None:
                failed += 1
                log.write(json.dumps(dict(id=cid, manifest=name, error="not indexed")) + "\n")
                continue
            if args.dry_run:
                print(f"would restore {p} and import {cid}")
                done += 1
                if args.limit and done >= args.limit:
                    print(f"would import {done} (limit reached)")
                    return 0
                continue
            restored = work / "restore" / name
            r = subprocess.run(
                [sys.executable, str(kit / "restore_evidence.py"), "--store", args.store,
                 "--match", p, "--output", str(restored)],
                capture_output=True, text=True)
            if r.returncode != 0:
                failed += 1
                log.write(json.dumps(dict(id=cid, manifest=name, error=r.stderr[-400:])) + "\n")
                continue
            legacy = restored / "workspace" / prefix
            if "attempt" in row:
                src = bundle / "historical" / "pilot-attempts" / row["attempt"]
                dst = legacy / row["attempt"]
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    shutil.copy2(src, dst)
            r = subprocess.run(
                [sys.executable, str(bundle / "cover_evidence.py"), "--root", str(out),
                 "import-legacy", str(bundle / rel), "--legacy-root", str(legacy),
                 "--checker", args.checker, "--case-id", cid],
                capture_output=True, text=True)
            ok = r.returncode == 0
            done += ok
            failed += not ok
            log.write(json.dumps(dict(id=cid, manifest=name, ok=ok,
                                      error=None if ok else r.stderr[-400:])) + "\n")
            log.flush()
            if args.limit and done >= args.limit:
                print(f"imported {done}, failed {failed}, skipped {skipped} (limit reached)")
                return 0
    print(f"imported {done}, failed {failed}, skipped {skipped}")
    return 0 if failed == 0 else 1


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=("check", "run"))
    p.add_argument("--bundle", required=True, help="unpacked K58 bundle")
    p.add_argument("--store", help="r58_evidence_store (run mode)")
    p.add_argument("--out", help="evidence root to write (run mode)")
    p.add_argument("--work", default="work/import", help="scratch dir (run mode)")
    p.add_argument("--checker", help="drat-trim binary (run mode)")
    p.add_argument("--only", choices=tuple(MANIFESTS), help="one manifest")
    p.add_argument("--limit", type=int, help="stop after N successful imports")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verbose", action="store_true")
    args = p.parse_args()
    if args.mode == "check":
        return cmd_check(args)
    if not (args.store and args.out and args.checker):
        p.error("run mode needs --store, --out and --checker")
    return cmd_run(args)


if __name__ == "__main__":
    sys.exit(main())
