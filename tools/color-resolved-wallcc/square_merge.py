#!/usr/bin/env python3
"""Append audited K15 square clauses to an already checked first-tier parent.

Square clauses use only variables of the original first-tier parent.  They do
not renumber a single colour-counter variable.  For rows supported by the
first-tier parent hash, both orders, colour-then-square or square-then-colour,
produce exactly the same augmented formula.
"""
from functools import lru_cache
import gzip
import hashlib
import json
import os
from pathlib import Path

from problem import ROOT, digest, json_bytes, require, row_formula

COMPONENT = ROOT.parent / "square_spoke"


def source_root():
    root = Path(os.environ.get("K58_SQUARE_ROOT", COMPONENT)).resolve()
    require((root / "source" / "next" / "batches.json").is_file(),
            "square-spoke data not installed; use the full modified solver or set K58_SQUARE_ROOT")
    return root / "source" / "next"


@lru_cache(maxsize=1)
def rows():
    return {row["id"]: (index, row) for index, row in
            json.loads((source_root() / "wall-rows.json").read_text())}


def unsupported_row(row):
    require(row["id"] in rows(), "square-spoke merging is supported only on the 14 audited ordinary rows")


def checked_batch(row, tier):
    """Validate the source URI, frozen row identity, tier and whole batch bytes."""
    require(tier == "first", "square-spoke merging requires --tier first")
    unsupported_row(row)
    index, shape = rows()[row["id"]]
    require(shape["id"] == row["id"], "square/wall row identity mismatch")
    raw = row_formula(row, tier)
    next_dir = source_root()
    batches = {i: (sha, count) for i, sha, count in json.loads((next_dir / "batches.json").read_text())}
    packed = (next_dir / f"batch-{index}.json.gz").read_bytes()
    require(digest(packed) == batches[index][0], "audited square batch compressed hash mismatch")
    batch = json.loads(gzip.decompress(packed))
    require(batch["parent"] == digest(raw), "ordinary parent does not own this square batch")
    require(batch["id"] == row["id"] and batch["tier"] == "first",
            "square batch is not the selected ordinary first-tier row")
    require(batch["cube"] == [] and batch["palette"] == [0, 1, 2, 3],
            "square batch is unsplit or has a nonphysical palette")
    proof = gzip.decompress((next_dir / "matching.drat.gz").read_bytes())
    require(batch["local_proof"] == digest(proof), "shared K15 proof binding mismatch")
    clauses = [tuple(clause) for clause, _ in batch["rules"]]
    screen = next(item for item in json.loads((next_dir / 'wall-screen.json').read_text())
                  if item['index'] == index)
    require(len(clauses) == screen['clauses'] == len(set(clauses)),
            "duplicate or miscounted square clauses")
    require(screen['novel'] == batches[index][1],
            "batch and wall-screen propagation counts differ")
    return index, clauses, {"index": index, "row": row["id"],
                            "original_parent_sha256": digest(raw),
                            "batch_sha256": digest(packed),
                            "batch_clause_count": len(clauses),
                            "K15_raw_proof_sha256": digest(proof)}


def apply(raw, row, tier):
    """Preserve the supplied parent's body byte-for-byte, then append squares."""
    from color_pivot import encode, header
    index, clauses, receipt = checked_batch(row, tier)
    parent_n, parent_m = header(raw)
    largest = max([parent_n] + [abs(literal) for clause in clauses for literal in clause])
    require(largest <= parent_n, "colour auxiliary namespace differs from the square batch")
    combined = (f"p cnf {largest} {parent_m + len(clauses)}\n".encode()
                + raw.split(b"\n", 1)[1] + encode(clauses))
    receipt.update({"input_parent_sha256": digest(raw),
                    "composed_parent_sha256": digest(combined),
                    "auxiliary_variables_unchanged": True,
                    "original_body_preserved": True,
                    "applies_after_variant": "off/counter/escape/color",
                    "scope": "square-strengthened aux-extended parent when colour is enabled; no monolithic original-parent proof"})
    return combined, receipt


def expected_parent(raw, row, tier):
    combined, _ = apply(raw, row, tier)
    return combined


def publish(out, receipt):
    """Retain the exact object whose digest a run plan binds."""
    from color_pivot import write_if_absent
    write_if_absent(Path(out) / "square-receipt.json", json_bytes(receipt))


def verify_saved(out, receipt_sha256):
    """Read the saved square receipt, rather than trusting a variant's label."""
    path = Path(out) / "square-receipt.json"
    require(path.is_file(), "missing saved square merge receipt")
    data = json.loads(path.read_bytes())
    require(digest(path.read_bytes()) == receipt_sha256,
            "saved square merge receipt does not match the plan")
    return data
