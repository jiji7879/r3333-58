#!/usr/bin/env python3
"""Bounded independent replay of supplied case 941d51630693 only.

The _prepare subcommand is re-executed with the checked installation's existing
Python environment because importing its frozen encoder requires PySAT. Nothing
is installed and no SAT search is launched; this driver only checks proofs.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZipFile

import cubelearn as cl

PREFIX = "941d51630693"
MEMBERS = {"core.cnf": "core.cnf.gz", "trim.drat": "trim.drat.gz"}


def prepare(archive: Path, shared: Path, out: Path) -> None:
    if out.exists():
        raise cl.LearningError(f"output already exists: {out}")
    out.mkdir(parents=True)
    with ZipFile(archive) as z:
        results = json.loads(z.read("K58_ranked_rows/results.json"))
        matches = [e for e in results if e["row"]["id"].startswith(PREFIX)]
        if len(matches) != 1:
            raise cl.LearningError(f"expected one {PREFIX} row, found {len(matches)}")
        entry = matches[0]
        encoder_audit = []
        for name in sorted(n for n in z.namelist()
                           if n.startswith("K58_ranked_rows/solver/") and not n.endswith("/")):
            relative = name.removeprefix("K58_ranked_rows/solver/")
            local = shared / relative
            if not local.is_file():
                raise cl.LearningError(f"encoder file missing from checked install: {relative}")
            archived = z.read(name)
            identical = archived == local.read_bytes()
            if not identical:
                raise cl.LearningError(f"checked-install encoder differs from ZIP: {relative}")
            encoder_audit.append({"file": relative, "identical": True,
                                  "sha256": hashlib.sha256(archived).hexdigest()})
        if not encoder_audit:
            raise cl.LearningError("no solver encoder files found in ZIP")
        cl.write_json(out / "encoder-file-audit.json", encoder_audit)
        for filename, member in MEMBERS.items():
            data = gzip.decompress(z.read(f"K58_ranked_rows/proofs/{PREFIX}/{member}"))
            if hashlib.sha256(data).hexdigest() != entry["hashes"][filename]:
                raise cl.LearningError(f"published decompressed hash mismatch: {filename}")
            (out / filename).write_bytes(data)
    # This imports source previously checked byte-for-byte against the ZIP's
    # solver/ files; it does not execute setup.sh or bundle instructions.
    sys.path.insert(0, str(shared.resolve()))
    from problem import checked_case, row_formula  # type: ignore
    row = checked_case(entry["row"])
    for tier in ("first", "retry"):
        data = row_formula(row, tier)
        if hashlib.sha256(data).hexdigest() != entry["hashes"][tier + ".cnf"]:
            raise cl.LearningError(f"regenerated parent hash mismatch: {tier}")
        (out / (tier + ".cnf")).write_bytes(data)
    (out / "empty-cube.json").write_text("[]\n")
    cl.write_json(out / "source-entry.json", entry)


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "_prepare":
        prepare(Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]))
        return 0
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True,
                        help="K58_six_whole_rows.zip (read-only)")
    parser.add_argument("--shared", type=Path, required=True,
                        help="checked K58_shared_learning installation (read-only)")
    parser.add_argument("--checker", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=90)
    args = parser.parse_args()
    if args.out.exists():
        parser.error("choose a new output directory")
    # Formula generation uses the already installed environment, while proof
    # normalization and all subsequent checks run in this standard interpreter.
    subprocess.run([str(args.shared / ".venv/bin/python"), str(Path(__file__).resolve()),
                    "_prepare", str(args.archive), str(args.shared), str(args.out)], check=True)
    rule = cl.bind_rule(args.out / "first.cnf", args.out / "empty-cube.json",
                        args.out / "trim.drat", args.out / "core.cnf", args.checker,
                        args.out / "source-rule", args.seconds)
    transported = cl.transport_rule(args.out / "source-rule", args.out / "retry.cnf",
                                    None, args.checker, args.out / "retry-transport", args.seconds)
    if transported["status"] != "VERIFIED_UNSAT":
        raise cl.LearningError("retry transport did not verify")

    nv, retry = cl.read_dimacs(args.out / "retry.cnf")
    _, core = cl.read_dimacs(args.out / "core.cnf")
    unit = next(clause[0] for clause in core if len(clause) == 1)
    clauses = []
    removed = False
    for clause in retry:
        if not removed and clause == (unit,):
            removed = True
            continue
        clauses.append(clause)
    if not removed:
        raise cl.LearningError("negative-control unit was not found in retry")
    (args.out / "relaxed-retry.cnf").write_bytes(cl.dimacs_bytes(nv, clauses))
    cl.write_json(args.out / "removed-unit.json", {
        "removed_exact_unit": unit, "original_clauses": len(retry),
        "relaxed_clauses": len(clauses),
        "semantic": "one-clause relaxation; no SAT/UNSAT verdict"})
    negative = cl.transport_rule(args.out / "source-rule", args.out / "relaxed-retry.cnf",
                                 None, args.checker, args.out / "relaxed-transport", args.seconds)
    if (negative["status"], negative["target_status"]) != ("NOT_APPLICABLE", "OPEN"):
        raise cl.LearningError("relaxation negative control did not fail closed")

    entry = json.loads((args.out / "source-entry.json").read_text())
    summary = {
        "schema": "m5-supplied-proof-replay/v1",
        "scope": "One supplied full original-formula case: " + entry["row"]["id"],
        "row_identity": {k: v for k, v in entry["row"].items() if k != "status"},
        "archive_historical_status": entry["row"].get("status"),
        "source_archive": str(args.archive),
        "checker": {"path": str(args.checker), "sha256": cl.sha256(args.checker)},
        "core": {"sha256": rule["core"]["sha256"], "clauses": rule["core"]["clauses"],
                 "units": sum(len(x) == 1 for x in core),
                 "published_vertices": entry["core_vertices"]},
        "proof": {"sha256": rule["proof"]["sha256"],
                  "bytes": (args.out / "trim.drat").stat().st_size,
                  "steps": rule["proof"]["steps"],
                  "normalization_byte_identical": ((args.out / "trim.drat").read_bytes() ==
                                                    (args.out / "source-rule/trim.drat").read_bytes())},
        "first": {"sha256": rule["parent"]["sha256"],
                  "variables": rule["parent"]["variables"],
                  "clauses": rule["parent"]["clauses"], "child_cube": [],
                  "replay": rule["validation"]["exact_child_replay"]["status"],
                  "checker_wall_seconds": rule["validation"]["exact_child_replay"]["seconds"]},
        "core_replay": {"status": rule["validation"]["core_replay"]["status"],
                        "checker_wall_seconds": rule["validation"]["core_replay"]["seconds"]},
        "retry_transport": {"sha256": transported["target"]["sha256"],
                            "variables": transported["target"]["variables"],
                            "clauses": transported["target"]["clauses"],
                            "map": "identity over every core/proof variable",
                            "status": transported["status"],
                            "target_status": transported["target_status"],
                            "proof_byte_identical": ((args.out / "trim.drat").read_bytes() ==
                                                      (args.out / "retry-transport/transported.drat").read_bytes()),
                            "receipt_sha256": cl.sha256(args.out / "retry-transport/transport.json")},
        "relaxation_negative_control": {
            "removed_signed_unit": unit, "clauses": len(clauses),
            "status": negative["status"], "target_status": negative["target_status"],
            "missing_clause_count": negative["missing_clause_count"],
            "satisfiability_verdict": None,
            "receipt_sha256": cl.sha256(args.out / "relaxed-transport/transport.json")},
        "limits": ["No other row or proof was run.",
                   "No H, H(r), contact-statistic, cohort, or six-unrestricted-row claim is used.",
                   "No complete wall, profile, or R(3,3,3,3) result is asserted."],
    }
    cl.write_json(args.out / "summary.json", summary)
    print(json.dumps({"first": summary["first"]["replay"],
                      "retry": transported["status"],
                      "relaxation": negative["status"],
                      "target_after_relaxation": negative["target_status"],
                      "out": str(args.out)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
