#!/usr/bin/env python3
"""Read-only, solver-free audit of the bounded stock/stock+short experiment inputs.

Run from member m2's directory with --package set to the extracted package.
This deliberately does not import or execute any package module.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import zipfile

PARENT_SHA = "33b7898ed58bd1a3a2e088f57d4bc9d01b5397e7b72f1f5f1449a7bf16f4a02a"
STOCK_SHA = "cb2df48f63eb7ba91d3bdb92a92cc830e5f0826d89366b52d68af80e221d33dd"
AUGMENTED_SHA = "6267a8fe7ee242ac6aabf18a440cc19686505ea78e269f465ec263a5636d856d"
PREFIX_SHA = "6bcc793f59fc3a4e3f4e04c751be03c8bddfc71208fe7f409b7934856d0d3936"
ROW = "4a71c66153af2a1cb64fc609b92bdd3dc93714fb3983a687812849a19f1798b2"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def clause_bytes(clauses) -> bytes:
    return "".join((" ".join(map(str, c)) + " " if c else "") + "0\n" for c in clauses).encode()


def append(parent: bytes, extra) -> bytes:
    header, body = parent.split(b"\n", 1)
    fields = header.split()
    assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
    variables, clauses = map(int, fields[2:])
    return f"p cnf {variables} {clauses + len(extra)}\n".encode() + body + clause_bytes(extra)


def header(data: bytes) -> tuple[int, int]:
    fields = data.split(b"\n", 1)[0].split()
    assert fields[:2] == [b"p", b"cnf"] and len(fields) == 4
    return tuple(map(int, fields[2:]))


def binary_drat_shape(data: bytes) -> dict:
    """Parse records only; this is deliberately not a proof validity check."""
    offset = 0
    counts = {"records": 0, "additions": 0, "deletions": 0,
              "unit_deletions": 0, "empty_additions": 0}
    while offset < len(data):
        op = data[offset]
        offset += 1
        if op not in (ord("a"), ord("d")):
            raise ValueError(f"invalid binary DRAT opcode at byte {offset - 1}: {op}")
        size = 0
        while True:
            encoded = 0
            shift = 0
            while True:
                if offset >= len(data):
                    raise ValueError("truncated binary DRAT varint")
                byte = data[offset]
                offset += 1
                encoded |= (byte & 127) << shift
                if byte < 128:
                    break
                shift += 7
                if shift > 63:
                    raise ValueError("oversized binary DRAT varint")
            if encoded == 0:
                break
            if encoded == 1:
                raise ValueError("invalid negative zero in binary DRAT")
            size += 1
        counts["records"] += 1
        if op == ord("a"):
            counts["additions"] += 1
            counts["empty_additions"] += (size == 0)
        else:
            counts["deletions"] += 1
            counts["unit_deletions"] += (size <= 1)
    return counts


def check(parsed: dict, name: str, condition: bool, detail=None) -> None:
    parsed["checks"].append({"name": name, "pass": bool(condition), "detail": detail})
    if not condition:
        raise AssertionError(f"{name}: {detail}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--package", required=True, type=Path)
    ap.add_argument("--zip", type=Path)
    args = ap.parse_args()
    root = args.package.resolve()
    evidence = root / "evidence"
    out = {"package": str(root), "checks": []}

    manifest_rows = []
    for line in (root / "SHA256SUMS").read_text().splitlines():
        digest, relative = line.split("  ", 1)
        blob = (root / relative).read_bytes()
        check(out, f"manifest:{relative}", sha(blob) == digest)
        manifest_rows.append((relative, digest))
    check(out, "manifest_has_38_files", len(manifest_rows) == 38, len(manifest_rows))
    if args.zip:
        with zipfile.ZipFile(args.zip) as archive:
            files = {n: archive.read(n) for n in archive.namelist() if not n.endswith("/")}
        by_basename = {n.split("/", 1)[-1] if n.startswith("K58_square_six/") else n: n for n in files}
        check(out, "zip_manifest_coverage", all(r in by_basename for r, _ in manifest_rows),
              {"zip_files": len(files), "manifest_files": len(manifest_rows)})
        for relative, digest in manifest_rows:
            check(out, f"zip:{relative}", sha(files[by_basename[relative]]) == digest)
        extras = sorted(set(by_basename) - {r for r, _ in manifest_rows} - {"SHA256SUMS"})
        check(out, "zip_has_no_unmanifested_payload", not extras, extras)

    parent = gzip.decompress((evidence / "parent.cnf.gz").read_bytes())
    study = json.loads((evidence / "study.json").read_text())
    wedges = json.loads((evidence / "wedges.json").read_text())
    plan = json.loads((evidence / "stock-plan.json").read_text())
    build_receipt = json.loads((evidence / "build-check.json").read_text())
    stock_clauses = study["stock"]
    short_clauses = wedges["clauses"]
    stock = append(parent, stock_clauses)
    augmented = append(parent, stock_clauses + short_clauses)
    prefix = (evidence / "stock-prefix.drat").read_bytes() + (evidence / "wedges-prefix.drat").read_bytes()

    check(out, "row_id", study["row"]["id"] == ROW and plan["origin"]["id"] == ROW)
    check(out, "original_parent_sha", sha(parent) == PARENT_SHA == plan["parent_sha256"])
    check(out, "parent_header", header(parent) == (19425, 184117), header(parent))
    check(out, "stock_and_short_counts", (len(stock_clauses), len(short_clauses)) == (189, 1020),
          (len(stock_clauses), len(short_clauses)))
    check(out, "stock_sha", sha(stock) == STOCK_SHA == plan["working_sha256"], sha(stock))
    check(out, "augmented_sha", sha(augmented) == AUGMENTED_SHA == build_receipt["augmented_sha256"], sha(augmented))
    check(out, "combined_prefix_sha", sha(prefix) == PREFIX_SHA == build_receipt["prefix_sha256"], sha(prefix))
    check(out, "stock_prefix_sha", sha((evidence / "stock-prefix.drat").read_bytes()) == plan["cas_proof_sha256"])
    out["binary_proof_shapes"] = {
        name: binary_drat_shape((evidence / name).read_bytes())
        for name in ("stock-prefix.drat", "wedges-prefix.drat", "implication.drat", "wedges.drat")
    }
    check(out, "prefix_has_no_unit_deletion_records",
          sum(out["binary_proof_shapes"][name]["unit_deletions"]
              for name in ("stock-prefix.drat", "wedges-prefix.drat")) == 0,
          out["binary_proof_shapes"])
    check(out, "short_prefix_has_exactly_1020_additions_only",
          out["binary_proof_shapes"]["wedges-prefix.drat"] == {
              "records": 1020, "additions": 1020, "deletions": 0,
              "unit_deletions": 0, "empty_additions": 0})
    check(out, "stock_header", header(stock) == (19425, 184306), header(stock))
    check(out, "augmented_header", header(augmented) == (19425, 185326), header(augmented))

    parent_body = parent.split(b"\n", 1)[1]
    stock_body = stock.split(b"\n", 1)[1]
    augmented_body = augmented.split(b"\n", 1)[1]
    check(out, "stock_serialization_exact", stock_body == parent_body + clause_bytes(stock_clauses))
    check(out, "augmented_serialization_exact", augmented_body == stock_body + clause_bytes(short_clauses))
    check(out, "original_parent_body_is_byte_prefix", augmented_body.startswith(parent_body))
    check(out, "no_new_variables_in_direct_formulas", header(augmented)[0] == header(stock)[0] == header(parent)[0])
    check(out, "stock_internally_ordered_unique", len({tuple(c) for c in stock_clauses}) == 189)
    check(out, "short_internally_ordered_unique", len({tuple(c) for c in short_clauses}) == 1020)
    check(out, "stock_short_disjoint", not ({tuple(c) for c in stock_clauses} & {tuple(c) for c in short_clauses}))
    all_added_literals = [abs(v) for c in stock_clauses + short_clauses for v in c]
    check(out, "added_literals_in_parent_range", bool(all_added_literals) and max(all_added_literals) <= 19425,
          max(all_added_literals))

    cubes = {}
    for bits in itertools.product((0, 1), repeat=3):
        node = "r"
        assumptions = []
        for bit in bits:
            assumptions.append(plan["splits"][node] * (1 if bit else -1))
            node += str(bit)
        cubes[node] = assumptions
    check(out, "eight_original_depth_three_cubes", len(cubes) == plan["leaf_count"] == 8 and plan["depth"] == 3,
          sorted(cubes))
    expected_nodes = [f"r{bits[0]}{bits[1]}{bits[2]}" for bits in itertools.product((0, 1), repeat=3)]
    check(out, "cube_names_exact", sorted(cubes) == sorted(expected_nodes))
    check(out, "all_cube_assumptions_physical_and_distinct",
          all(len(c) == 3 and len({abs(v) for v in c}) == 3 and max(map(abs, c)) <= plan["split_limit"]
              for c in cubes.values()))
    split_variables = (plan["splits"]["r"], plan["splits"]["r0"], plan["splits"]["r00"])
    coverage = []
    for values in itertools.product((-1, 1), repeat=3):
        assignment = {abs(v): v * s for v, s in zip(split_variables, values)}
        hits = [name for name, cube in cubes.items() if all(assignment[abs(v)] == v for v in cube)]
        coverage.append((values, hits))
    check(out, "cube_partition_exhaustive_and_pairwise_disjoint", all(len(hits) == 1 for _, hits in coverage), coverage)

    old = [json.loads(line) for line in (evidence / "benchmarks.jsonl").read_text().splitlines()]
    old += json.loads((evidence / "short-bench.json").read_text())
    methods = ("stock", "square", "six", "both", "factored")
    check(out, "old_panel_has_40_records", len(old) == 40)
    for method in methods:
        records = [r for r in old if r["method"] == method]
        check(out, f"old_cube_assumptions_match:{method}", len(records) == 8 and
              all(r["assumptions"] == cubes[r["cube"]] for r in records))
    check(out, "old_records_are_not_new_timed_certificates",
          all(r["status"] == "OPEN" and r["cap"] == 30000 and "query_sha256" not in r and "proof_sha256" not in r
              for r in old))

    leaves = []
    for name, cube in cubes.items():
        units = [[v] for v in cube]
        unit_fragment = clause_bytes(units)
        original_leaf = append(parent, units)
        stock_leaf = append(stock, units)
        augmented_leaf = append(augmented, units)
        check(out, f"leaf_body_identity:{name}",
              stock_leaf.split(b"\n", 1)[1] == stock_body + unit_fragment and
              augmented_leaf.split(b"\n", 1)[1] == augmented_body + unit_fragment)
        check(out, f"leaf_headers:{name}", header(stock_leaf) == (19425, 184309) and
              header(augmented_leaf) == (19425, 185329))
        leaves.append({"cube": name, "assumptions": cube,
                       "cube_unit_fragment_sha256": sha(unit_fragment),
                       "original_parent_leaf_sha256": sha(original_leaf),
                       "stock_leaf_sha256": sha(stock_leaf),
                       "stock_plus_1020_leaf_sha256": sha(augmented_leaf)})
    out["leaf_identities"] = leaves
    out["interpretation"] = {
        "native_leaf_formula": "parent + 189 stock (+ 1020 short in the second arm) + 3 cube units; no selectors",
        "original_parent_leaf_formula": "parent + the same 3 cube units",
        "original_parent_proof_stock_arm": "stock-prefix.drat + deletion-free native DRAT",
        "original_parent_proof_augmented_arm": "stock-prefix.drat + wedges-prefix.drat + deletion-free native DRAT",
        "scope": "Static byte/cube consistency checks only. No solver or proof checker was run and no search status is inferred."
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
