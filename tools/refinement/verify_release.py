#!/usr/bin/env python3
"""Fresh strict replay of a refinement evidence set; no campaign imports."""
import argparse
import hashlib
import json
from pathlib import Path
import stat
import subprocess


def sha(data):
    return hashlib.sha256(data).hexdigest()


def binary_records(data):
    records = []
    position = 0
    while position < len(data):
        kind = data[position]
        assert kind in (ord("a"), ord("d")), (position, kind)
        start = position
        position += 1
        while True:
            assert position < len(data)
            byte = data[position]
            position += 1
            if byte == 0:
                break
        records.append((kind, data[start:position]))
    return records


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cohort", type=Path, required=True)
    ap.add_argument("--assembled", type=Path, required=True)
    ap.add_argument("--comparison", type=Path, required=True)
    ap.add_argument("--checker", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    args.checker = args.checker.resolve()
    # Python's zipfile.extractall does not restore executable mode bits.
    # The caller explicitly selected this local checker as the executable.
    args.checker.chmod(args.checker.stat().st_mode | stat.S_IXUSR)
    args.out.mkdir(parents=True, exist_ok=False)
    log = args.out / "replay.log"
    records = []

    def check(label, case, query, proof, expected_query=None, expected_proof=None):
        qdata, pdata = query.read_bytes(), proof.read_bytes()
        if expected_query is not None:
            assert sha(qdata) == expected_query, label
        if expected_proof is not None:
            assert sha(pdata) == expected_proof, label
        run = subprocess.run([str(args.checker), str(query), str(proof), "-i", "-U", "-t", "300"],
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
        text = run.stdout.decode(errors="replace")
        verified = (run.returncode == 0 and run.stdout.count(b"s VERIFIED") == 1
                    and b"WARNING" not in run.stdout.upper())
        with log.open("a") as stream:
            stream.write(f"===== {case} / {label} =====\n{text}\n")
        assert verified, (case, label, text[-2000:])
        records.append({"case": case, "label": label, "query_sha256": sha(qdata),
                        "proof_sha256": sha(pdata), "query_bytes": len(qdata),
                        "proof_bytes": len(pdata), "checker_returncode": run.returncode,
                        "warnings": False, "verified": True})

    cohort_summary = args.cohort / "summary.json"
    ledger_path = args.assembled / "ledger.json"
    ledger = json.loads(ledger_path.read_text())
    assert sha(cohort_summary.read_bytes()) == ledger["summary_sha256"]
    assert ledger["schema"] == "verified-conditional-refinement/v1"
    assert ledger["count"] == 9 == len(ledger["conditional_refinements"])

    # All 19 source full-query proofs, including the nine conditional siblings.
    source_cases = sorted((args.cohort / "full").iterdir(), key=lambda p: int(p.name))
    assert len(source_cases) == 31
    for directory in source_cases:
        check("cohort", directory.name, directory / "query.cnf", directory / "proof.drat")

    for index, entry in enumerate(ledger["conditional_refinements"], 1):
        parent = args.assembled / "nodes" / str(index) / "parent.cnf"
        refined = args.assembled / "nodes" / str(index) / "refined.cnf"
        assert sha(parent.read_bytes()) == entry["source_parent"]
        assert sha(refined.read_bytes()) == entry["refined_query"] == entry["refined_query_verified"]
        excluded = entry["excluded_sibling_replays"][0]
        source_log = Path(entry["excluded_checks"][0]["log"])
        source_dir = args.cohort / source_log.parent
        assert (source_dir / "query.cnf").read_bytes() == (args.assembled / "replays" / str(index) / "query.cnf").read_bytes()
        assert (source_dir / "proof.drat").read_bytes() == (args.assembled / "replays" / str(index) / "proof.drat").read_bytes()
        check("excluded-sibling", index, args.assembled / "replays" / str(index) / "query.cnf",
              args.assembled / "replays" / str(index) / "proof.drat", excluded["query"], excluded["proof"])
        cover = entry["complete_child_cover"]
        check("complete-two-child-cover", index, args.assembled / "nodes" / str(index) / "cover.cnf",
              args.assembled / "nodes" / str(index) / "cover.drat", cover["query"], cover["proof"])

    # Every stock parent/root/branch transport rebuilt by the assembler.
    for directory in sorted((args.assembled / "source" / "full").iterdir(), key=lambda p: int(p.name)):
        check("stock-transport", directory.name, directory / "query.cnf", directory / "proof.drat")

    # This control is rejected by warning policy even though drat-trim returns 0.
    bad = subprocess.run([str(args.checker), str(args.assembled / "malformed-query.cnf"),
                          str(args.assembled / "malformed-proof.drat"), "-i", "-U", "-t", "300"],
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
    bad_text = bad.stdout.decode(errors="replace")
    assert b"WARNING" in bad.stdout.upper() and b"wrong binary prefix" in bad.stdout
    assert (args.assembled / "malformed-proof.drat").read_bytes().startswith(b"X\0")
    with log.open("a") as stream:
        stream.write("===== malformed-prefix control (strictly rejected) =====\n" + bad_text + "\n")

    comparison = json.loads((args.comparison / "summary.json").read_text())
    assert comparison["completed_physical_solver_calls"] == 8
    assert len(comparison["records"]) == 8
    statuses = []
    for result in comparison["records"]:
        node, kind = result["node"], result["kind"]
        query = args.assembled / "nodes" / str(node) / (
            "parent.cnf" if kind == "guard_parent" else "refined.cnf")
        assert sha(query.read_bytes()) == result["query_sha256"]
        assert not result["cut_off"] and result["native_deadline_seconds"] == 3.0
        directory = next(args.comparison.glob(f"{result['sequence']:02d}-{result['arm']}-{kind}"))
        if result["status"] == "OPEN_UNKNOWN":
            assert result["decision_unknown_after_budget"]
            statuses.append(result["status"])
            continue
        assert result["status"] == "VERIFIED_UNSAT"
        raw = (directory / "leaf" / "proof.drat").read_bytes()
        normalized = (directory / "leaf" / "proof-nodeletions.drat").read_bytes()
        receipt = result["proof_normalization"]
        assert sha(raw) == receipt["original_proof_sha256"]
        assert sha(normalized) == receipt["deletion_free_proof_sha256"]
        old_additions = [payload for tag, payload in binary_records(raw) if tag == ord("a")]
        new_additions = [payload for tag, payload in binary_records(normalized) if tag == ord("a")]
        assert old_additions == new_additions
        assert len(binary_records(normalized)) == receipt["additions_preserved"]
        check("fresh-" + kind, result["arm"], query, directory / "leaf" / "proof-nodeletions.drat",
              result["query_sha256"], receipt["deletion_free_proof_sha256"])
        statuses.append(result["status"])
    assert statuses.count("OPEN_UNKNOWN") == 6
    assert statuses.count("VERIFIED_UNSAT") == 2

    summary = {
        "schema": "refinement-independent-replay/v1",
        "strict_positive_checks": len(records),
        "distinct_positive_query_proof_pairs": len({(r["query_sha256"], r["proof_sha256"]) for r in records}),
        "checks_by_label": {label: sum(r["label"] == label for r in records)
                            for label in sorted({r["label"] for r in records})},
        "all_positive_checks_warning_free": True,
        "malformed_binary_prefix_strictly_rejected": True,
        "malformed_control_returncode": bad.returncode,
        "malformed_control_printed_s_VERIFIED": b"s VERIFIED" in bad.stdout,
        "comparison_statuses": statuses,
        "conditional_refinement_count": 9,
        "fresh_proof_deletions_removed_only_additions_retained": True,
        "no_cached_status_used_as_acceptance": True,
        "closure_boundary": "Conditional guarded refinements and two guarded-search refutations only; no original parent, wall row or Ramsey closure.",
        "records": records,
    }
    (args.out / "replay-summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: summary[k] for k in
                      ("strict_positive_checks", "distinct_positive_query_proof_pairs",
                       "checks_by_label", "malformed_control_returncode",
                       "malformed_control_printed_s_VERIFIED")}, indent=2))


if __name__ == "__main__":
    main()
