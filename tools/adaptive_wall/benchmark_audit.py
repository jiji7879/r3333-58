#!/usr/bin/env python3
"""Recompute the outside-27 split/direct accounting without running a solver.

The script reads the original ZIP in place. It authenticates retained DRAT bytes
against receipt hashes, but does not mistake that integrity check for DRAT replay.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
from collections import Counter
from pathlib import Path
from typing import Any
from zipfile import ZipFile

from projection_bindings import CATALOGUE, catalogue_bindings

RECEIPT_PREFIX = "K58_wall_copy_maps/data/wall-copy/outside-27/"
LEDGER = "K58_wall_copy_maps/results/wall_937_rows.tsv"
MANIFEST = "K58_wall_copy_maps/SHA256SUMS"
REQUIRED = {
    "key", "exterior_vertices", "n", "q", "cutoff", "cap",
    "map_representatives", "query_sha256", "status", "conflicts",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _proof_integrity(zf: ZipFile, receipt_name: str, receipt: dict[str, Any]) -> dict[str, Any]:
    """Hash proof contents; this is deliberately not a proof verdict."""
    proof_name = str(Path(receipt_name).with_name("proof.drat.gz"))
    try:
        info = zf.getinfo(proof_name)
    except KeyError as exc:
        raise ValueError(f"missing proof for {receipt_name}") from exc
    with gzip.open(zf.open(proof_name), "rb") as stream:
        actual = hashlib.file_digest(stream, "sha256").hexdigest()
    _require(actual == receipt.get("proof_sha256"), f"proof hash mismatch: {receipt_name}")
    return {
        "member": proof_name,
        "member_bytes": info.file_size,
        "uncompressed_sha256": actual,
        "digest_matches_receipt": True,
        "drat_replayed_here": False,
    }


def audit_archive(zip_path: Path, check_proof_hashes: bool = True) -> dict[str, Any]:
    cases: dict[str, dict[str, Any]] = {}
    checks: list[dict[str, Any]] = []
    with ZipFile(zip_path) as zf:
        archive_names = zf.namelist()
        _require(len(archive_names) == len(set(archive_names)), "duplicate archive member name")
        names = sorted(
            n for n in zf.namelist()
            if n.startswith(RECEIPT_PREFIX) and n.endswith("/receipt.json")
        )
        _require(names, "no outside-27 receipts found")
        manifest_checks = 0
        if MANIFEST in zf.namelist():
            expected = {}
            for line in zf.read(MANIFEST).decode().splitlines():
                digest, relative = line.split(maxsplit=1)
                expected[relative.strip()] = digest
            prefix = "K58_wall_copy_maps/"
            members = [
                n for n in zf.namelist() if n.startswith(RECEIPT_PREFIX)
                and (n.endswith("/receipt.json") or n.endswith("/proof.drat.gz"))
            ]
            for name in members:
                relative = name.removeprefix(prefix)
                _require(relative in expected, f"member absent from SHA256SUMS: {name}")
                actual = hashlib.sha256(zf.read(name)).hexdigest()
                _require(actual == expected[relative], f"archive member hash mismatch: {name}")
                manifest_checks += 1
            _require(manifest_checks == 76, f"unexpected outside-27 manifest size: {manifest_checks}")
        for name in names:
            r = json.loads(zf.read(name))
            _require(REQUIRED <= r.keys(), f"missing receipt fields: {name}")
            _require(r["key"] in name, f"case key not bound to path: {name}")
            _require(r["status"] in {"UNSAT", "OPEN", "SAT"}, f"bad status: {name}")
            _require(isinstance(r["conflicts"], int) and r["conflicts"] >= 0, name)
            if r["status"] == "OPEN":
                _require(r["conflicts"] >= r["cap"], f"premature OPEN: {name}")
            c = cases.setdefault(r["key"], {"children": [], "direct": []})
            target = c["children"] if "partition" in r else c["direct"]
            target.append((name, r))

        projections = catalogue_bindings(zf) if CATALOGUE in zf.namelist() else {}
        ledger_by_proof: dict[str, list[dict[str, str]]] = {}
        with io.TextIOWrapper(zf.open(LEDGER), encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                ledger_by_proof.setdefault(row["derived_from"], []).append(row)

        rendered: list[dict[str, Any]] = []
        for key, grouped in sorted(cases.items()):
            children = sorted(grouped["children"], key=lambda item: item[1]["partition"])
            direct = grouped["direct"]
            parts = [r["partition"] for _, r in children]
            _require(parts == [[i, 8] for i in range(8)], f"bad eight-part cover: {key}")
            _require(len(direct) == 1, f"expected one direct control: {key}")
            for _, r in children + direct:
                _require(r["n"] == 58 and r["exterior_vertices"] == 27, f"wrong query scope: {key}")
            statuses = Counter(r["status"] for _, r in children)
            for name, r in children:
                if r["status"] == "UNSAT" and check_proof_hashes:
                    checks.append(_proof_integrity(zf, name, r))

            # These are receipt aggregates, not independently established semantics.
            receipt_cover = statuses["UNSAT"] == 8
            dr_name, dr = direct[0]
            total = sum(r["conflicts"] for _, r in children)
            caps = sorted({r["cap"] for _, r in children})
            proof_gzip_bytes = sum(c["member_bytes"] for c in checks if key in c["member"])
            bindings = []
            if receipt_cover:
                total_maps = children[0][1]["map_representatives"]
                marker = f"all {total_maps} map representatives at H <= {children[0][1]['cutoff']}, 27 exterior vertices, {key}"
                for row in ledger_by_proof.get(marker, []):
                    bindings.append({
                        "row_id": row["row_id"], "profile": row["profile"],
                        "direction": row["direction"], "earlier_H": int(row["earlier_H"]),
                        "certified_H_after_ledger": int(row["certified_H"]),
                        "binding_source": "results/wall_937_rows.tsv",
                    })
            rendered.append({
                "case_key": key,
                "query_scope": {
                    "vertices": 58, "exterior_vertices": 27,
                    "cutoff": children[0][1]["cutoff"],
                    "map_representatives": children[0][1]["map_representatives"],
                    "q": children[0][1]["q"],
                    "note": "copy-map H-cutoff gate query; never an unrestricted-row verdict",
                },
                "split": {
                    "children": 8,
                    "per_child_conflict_caps": caps,
                    "status_counts": dict(sorted(statuses.items())),
                    "total_conflicts_including_open": total,
                    "receipt_complete_eight_part_cutoff": receipt_cover,
                    "still_open": not receipt_cover,
                    "proof_gzip_member_bytes": proof_gzip_bytes,
                    "query_sha256_by_partition": [r["query_sha256"] for _, r in children],
                },
                "archived_direct": {
                    "status": dr["status"], "cap": dr["cap"], "conflicts": dr["conflicts"],
                    "query_sha256": dr["query_sha256"],
                    "receipt_member": dr_name,
                },
                "ledger_bindings_when_complete": bindings,
                "regenerated_projection_bindings": projections.get(key, []),
                "unrestricted_row_verdict": "NOT_EVALUATED",
            })

    _require(len(rendered) == 6, f"expected six cases, got {len(rendered)}")
    totals = Counter()
    for c in rendered:
        totals.update(c["split"]["status_counts"])
    with zip_path.open("rb") as stream:
        source_digest = hashlib.file_digest(stream, "sha256").hexdigest()
    return {
        "source_zip": str(zip_path),
        "source_zip_sha256": source_digest,
        "manifest_members_verified": manifest_checks,
        "case_count": len(rendered),
        "split_children": sum(totals.values()),
        "split_status_counts": dict(sorted(totals.items())),
        "split_total_conflicts_including_open": sum(c["split"]["total_conflicts_including_open"] for c in rendered),
        "receipt_complete_cutoffs": sum(c["split"]["receipt_complete_eight_part_cutoff"] for c in rendered),
        "archived_direct_closed": sum(c["archived_direct"]["status"] != "OPEN" for c in rendered),
        "archived_direct_total_conflicts": sum(c["archived_direct"]["conflicts"] for c in rendered),
        "proof_integrity": {
            "unsat_proofs_checked": len(checks),
            "all_uncompressed_digests_match": all(c["digest_matches_receipt"] for c in checks),
            "total_gzip_member_bytes": sum(c["member_bytes"] for c in checks),
            "drat_replayed": False,
        },
        "unavailable_in_receipts": [
            "elapsed and CPU seconds", "proof-generation and replay seconds",
            "wall-clock makespan and parallelism", "engine random-seed sensitivity",
            "equal-total-conflict direct run closing one case",
        ],
        "cases": rendered,
    }


def write_table(report: dict[str, Any], path: Path) -> None:
    fields = [
        "case_prefix", "cutoff", "parts_unsat", "parts_open",
        "split_conflicts", "receipt_complete_cutoff", "direct_status",
        "direct_cap", "direct_conflicts", "physical_rows_and_direction",
    ]
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        for c in report["cases"]:
            counts = c["split"]["status_counts"]
            writer.writerow({
                "case_prefix": c["case_key"][:12], "cutoff": c["query_scope"]["cutoff"],
                "parts_unsat": counts.get("UNSAT", 0), "parts_open": counts.get("OPEN", 0),
                "split_conflicts": c["split"]["total_conflicts_including_open"],
                "receipt_complete_cutoff": c["split"]["receipt_complete_eight_part_cutoff"],
                "direct_status": c["archived_direct"]["status"],
                "direct_cap": c["archived_direct"]["cap"],
                "direct_conflicts": c["archived_direct"]["conflicts"],
                "physical_rows_and_direction": ",".join(
                    f"{b['row_id'][:12]}:{b['direction']}"
                    for b in (c["regenerated_projection_bindings"] or c["ledger_bindings_when_complete"])
                ),
            })


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--table", type=Path)
    parser.add_argument("--no-proof-hashes", action="store_true")
    args = parser.parse_args()
    report = audit_archive(args.zip, not args.no_proof_hashes)
    text = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.table:
        write_table(report, args.table)


if __name__ == "__main__":
    main()
