#!/usr/bin/env python3
"""Compare actual run_native cache outcomes with the independent contract.

Default mode records a baseline and exits zero even when vulnerabilities are
found. After integrating a fix, run with --require-contract: invalid closure,
loss/substitution of any valid cached state, or a pending-state upgrade exits 1.
Kissat is forbidden throughout; only the oracle's drat-trim replay executes.
"""
from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
import tempfile

from test_cached_terminal import (
    CHECKER, EMPTY_CLAUSE_PROOF, Fixture, MEMBER, SAT_ONE, SAT_PARENT,
    UNSAT_TWO, UNSAT_TWO_PROOF, binary, model_bytes, oracle)


def build_cases(root: Path):
    cases = []

    def add(name, parent=SAT_PARENT, *, status="OPEN", cube=(), cuts=(), setup=None):
        folder = root / f"{len(cases):02d}-{name}"
        folder.mkdir()
        f = Fixture(folder, parent, cube=cube, cuts=cuts)
        if status is not None:
            f.receipt(status)
        if setup:
            setup(f)
        cases.append((name, f))

    def fallback_unsat(f, *, corrupt=False):
        f.use_fallback()
        f.receipt("UNSAT_BASE")
        f.proof(compressed=b"bad gzip") if corrupt else f.proof(UNSAT_TWO_PROOF)

    add("valid-unsat", UNSAT_TWO, status="UNSAT_BASE", setup=lambda f: f.proof(UNSAT_TWO_PROOF))
    add("valid-fallback-unsat", UNSAT_TWO, status="UNSAT_BASE", setup=fallback_unsat)
    add("fallback-corrupt-proof", UNSAT_TWO, status="UNSAT_BASE",
        setup=lambda f: fallback_unsat(f, corrupt=True))
    add("valid-sat", status="SAT_BASE", setup=lambda f: f.model([1, 2, 3]))
    add("open")
    add("valid-augmented-pending", SAT_ONE, status=oracle.PENDING, cuts=[[-1]],
        setup=lambda f: f.proof(EMPTY_CLAUSE_PROOF))
    add("unknown", status="UNKNOWN")
    add("timeout", status="TIMEOUT")
    add("raw-unsat-with-proof", UNSAT_TWO, status="UNSAT", setup=lambda f: f.proof(UNSAT_TWO_PROOF))
    add("missing-receipt", UNSAT_TWO, status=None)
    add("corrupt-receipt", UNSAT_TWO, status=None,
        setup=lambda f: f.receipt_path.write_bytes(b'{"status":"UNSAT_BASE"'))
    add("wrong-parent-binding", UNSAT_TWO, status="OPEN",
        setup=lambda f: (lambda r: (r.__setitem__("parent_sha256", "0" * 64), f.write_receipt(r)))(f.read_receipt()))
    add("wrong-query-binding", UNSAT_TWO, status="OPEN",
        setup=lambda f: (lambda r: (r.__setitem__("query_sha256", "0" * 64), f.write_receipt(r)))(f.read_receipt()))
    add("unsat-missing-proof", UNSAT_TWO, status="UNSAT_BASE",
        setup=lambda f: f.receipt("UNSAT_BASE", proof="absent.gz", proof_sha256="0" * 64))
    add("unsat-hash-mismatch", UNSAT_TWO, status="UNSAT_BASE",
        setup=lambda f: f.proof(UNSAT_TWO_PROOF, update_hash=False))
    add("unsat-corrupt-gzip", UNSAT_TWO, status="UNSAT_BASE",
        setup=lambda f: f.proof(compressed=b"not gzip"))
    packed = gzip.compress(UNSAT_TWO_PROOF, mtime=0)
    add("unsat-truncated-gzip", UNSAT_TWO, status="UNSAT_BASE",
        setup=lambda f: f.proof(compressed=packed[:-4]))
    add("unsat-truncated-binary-proof", UNSAT_TWO, status="UNSAT_BASE",
        setup=lambda f: f.proof(binary([2])[:-1]))
    add("unsat-malformed-prefix-accepted-by-w", UNSAT_TWO, status="UNSAT_BASE",
        setup=lambda f: f.proof(b"X\0" + UNSAT_TWO_PROOF))
    add("unsat-query-only-mislabeled-base", SAT_ONE, status="UNSAT_BASE", cuts=[[-1]],
        setup=lambda f: f.proof(EMPTY_CLAUSE_PROOF))
    add("sat-missing-model", status="SAT_BASE",
        setup=lambda f: f.receipt("SAT_BASE", model="absent.gz", model_sha256="0" * 64))
    add("sat-hash-mismatch", status="SAT_BASE", setup=lambda f: f.model(update_hash=False))
    add("sat-corrupt-gzip", status="SAT_BASE", setup=lambda f: f.model(compressed=b"bad gzip"))
    add("sat-truncated-model-json", status="SAT_BASE", setup=lambda f: f.model(data=b"[1, 2,"))
    add("sat-incomplete-model", status="SAT_BASE", setup=lambda f: f.model([1, 2]))
    add("sat-wrong-full-model", status="SAT_BASE", setup=lambda f: f.model([1, -2, -3]))
    add("sat-model-violates-cube", status="SAT_BASE", cube=[2], setup=lambda f: f.model([1, -2, 3]))
    add("pending-missing-proof", SAT_ONE, status=oracle.PENDING, cuts=[[-1]],
        setup=lambda f: f.receipt(oracle.PENDING, proof="absent.gz", proof_sha256="0" * 64))
    add("pending-hash-mismatch", SAT_ONE, status=oracle.PENDING, cuts=[[-1]],
        setup=lambda f: f.proof(EMPTY_CLAUSE_PROOF, update_hash=False))
    return cases


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-contract", action="store_true")
    parser.add_argument("--out", type=Path, default=MEMBER / "native-findings.json")
    args = parser.parse_args()
    scratch = MEMBER / ".scratch"
    scratch.mkdir(exist_ok=True)
    results = []
    with tempfile.TemporaryDirectory(prefix="native-matrix-", dir=scratch) as tmp:
        for name, fixture in build_cases(Path(tmp)):
            # Compute the independent decision first. The real native call then
            # sees exactly the same bytes and cannot invoke Kissat.
            expected = fixture.decision()
            actual = fixture.native()
            exact_valid_state = (actual["outcome"] == "RETURN" and
                                actual["status"] == expected["status"])
            contract_match = (exact_valid_state if expected["cache_valid"]
                              else not actual["terminal"])
            results.append({
                "name": name,
                "expected_terminal": expected["terminal"],
                "expected_cache_valid": expected["cache_valid"],
                "oracle": expected,
                "native_outcome": actual["outcome"],
                "native_status": actual["status"],
                "native_terminal": actual["terminal"],
                "terminal_semantics_match": actual["terminal"] == expected["terminal"],
                "contract_match": contract_match,
                "native_detail": actual.get("detail"),
            })
    false_closure = [r["name"] for r in results
                     if r["native_terminal"] and not r["expected_terminal"]]
    lost_valid_terminal = [r["name"] for r in results
                           if r["expected_terminal"] and not r["native_terminal"]]
    valid_state_mismatch = [r["name"] for r in results
                            if r["expected_cache_valid"] and not r["contract_match"]]
    contract_mismatch = [r["name"] for r in results if not r["contract_match"]]
    report = {
        "schema": "k58-native-cache-adversarial-matrix/v1",
        "campaign_frontier_sha256": oracle.sha((CHECKER.parents[1] / "frontier.py").read_bytes()),
        "checker": str(CHECKER),
        "kissat_executions": 0,
        "notes": [
            "All native Kissat calls were replaced by SearchAttempt; no solver ran.",
            "A corrupt receipt exception is nonterminal but not a clean OPEN/INVALID_CACHE return.",
            "Default mode records the baseline; --require-contract enforces the oracle terminal semantics.",
        ],
        "summary": {
            "cases": len(results),
            "false_cached_terminal_cases": false_closure,
            "lost_valid_terminal_cases": lost_valid_terminal,
            "valid_cached_state_mismatches": valid_state_mismatch,
            "terminal_mismatches": sum(not r["terminal_semantics_match"] for r in results),
            "contract_mismatches": contract_mismatch,
            "native_exceptions_or_search_attempts": [r["name"] for r in results
                                                       if r["native_outcome"] != "RETURN"],
        },
        "results": results,
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    print(f"wrote {args.out}")
    if args.require_contract and contract_mismatch:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
