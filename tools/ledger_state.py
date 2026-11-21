#!/usr/bin/env python3
"""Fold a release index and the hard-tail binding into one per-case ledger.

The release index (`cases.jsonl.gz`) records what the pipeline itself replayed.
It cannot express two things we know: the 20 `(16,15,15,11)` rows refuted as
*split* certificates, and the prior status of a row that never had a proof.
This writes one line per cover case with a single status vocabulary:

    CERTIFIED          one DRAT per case, replayed here against the regenerated CNF
    SPLIT_CERTIFIED    refuted by a split argument (core or cube-and-conquer),
                       accepted by the archive's verifier, not replayable here
    LEGACY_HISTORICAL  ledger-CERTIFIED; proof bytes live in an archive not held here
    LEGACY_EXCLUSION   profile or template exclusion; an argument, not a certificate
    OPEN               no evidence

    python3 tools/ledger_state.py --release release/2026-11-21-checkpoint \
        --ledger .scratch/k58/case-ledger.jsonl.gz \
        --split runs/2026-11-21-hard-tail-16-15-15-11/BINDING.jsonl \
        --out results/ledger-2026-11-22.tsv.gz
"""
import argparse
import collections
import csv
import gzip
import json
from pathlib import Path

COLUMNS = ["id", "profile", "kinds", "marked_size", "arm", "branch",
           "status", "tier", "proof_bytes", "note"]


def ledger_rows(path):
    with gzip.open(path, "rt") as handle:
        for line in handle:
            row = json.loads(line)
            yield row["id"], row["family"], row["branch"]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--release", type=Path, required=True)
    p.add_argument("--ledger", type=Path, required=True)
    p.add_argument("--split", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--summary", type=Path)
    a = p.parse_args()

    family, branch = {}, {}
    for cid, fam, br in ledger_rows(a.ledger):
        family[cid], branch[cid] = fam, br
    split = {}
    for line in a.split.read_text().splitlines():
        if line.strip():
            row = json.loads(line)
            split[row["id"]] = row["kind"]

    status = {}
    detail = {}
    with gzip.open(a.release / "cases.jsonl.gz", "rt") as handle:
        for line in handle:
            row = json.loads(line)
            cid = row["id"]
            tier, proof, note = "", "", ""
            if row["status"] == "CERTIFIED":
                recipe = row.get("recipe") or {}
                tier = "retry" if recipe.get("full_root") else "first"
                proof = (row.get("proof") or {}).get("bytes", "")
                code = "CERTIFIED"
            elif row["status"] == "LEGACY_EVIDENCE_NEEDED":
                prior = row.get("prior_status")
                code = "LEGACY_EXCLUSION" if prior in ("PROFILE_EXCLUSION", "TEMPLATE_EXCLUSION") else "LEGACY_HISTORICAL"
                note = prior if code == "LEGACY_EXCLUSION" else "ledger CERTIFIED"
            else:
                code = "OPEN"
            if cid in split:
                code, note = "SPLIT_CERTIFIED", split[cid]
            status[cid] = code
            detail[cid] = (tier, proof, note)

    if set(status) != set(family):
        raise SystemExit(f"ledger/index disagree: {len(set(status) ^ set(family))} ids")

    a.out.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(a.out, "wt", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(COLUMNS)
        for cid in sorted(family):
            f = family[cid]
            tier, proof, note = detail[cid]
            writer.writerow([cid, ",".join(map(str, f["profile"])), "".join(f["root_kinds"]),
                             f["marked_size"], f["arm"], branch[cid], status[cid],
                             tier, proof, note])

    by_profile = collections.defaultdict(collections.Counter)
    overall = collections.Counter()
    for cid, code in status.items():
        key = ",".join(map(str, family[cid]["profile"]))
        by_profile[key][code] += 1
        overall[code] += 1
    order = sorted(by_profile, key=lambda k: -sum(by_profile[k].values()))
    codes = ["CERTIFIED", "SPLIT_CERTIFIED", "LEGACY_HISTORICAL", "LEGACY_EXCLUSION", "OPEN"]
    width = max(len(k) for k in order) + 2
    lines = ["".join(["profile".ljust(width)] + [c.replace("LEGACY_", "L_").rjust(16) for c in codes] + ["total".rjust(9)])]
    for key in order:
        row = by_profile[key]
        lines.append("".join([key.ljust(width)] + [f"{row[c]:,}".rjust(16) for c in codes]
                             + [f"{sum(row.values()):,}".rjust(9)]))
    lines.append("".join(["TOTAL".ljust(width)] + [f"{overall[c]:,}".rjust(16) for c in codes]
                         + [f"{sum(overall.values()):,}".rjust(9)]))
    text = "\n".join(lines)
    print(text)
    if a.summary:
        a.summary.write_text(text + "\n")


if __name__ == "__main__":
    main()
