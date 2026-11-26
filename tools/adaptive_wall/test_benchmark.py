#!/usr/bin/env python3
import csv
import gzip
import hashlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile

from benchmark_audit import LEDGER, RECEIPT_PREFIX, audit_archive
from split_policy import child_closure, compare_pair, next_split_decision

KEYS = [
    "0122d0de168c7733374d5055af2a37e9c745a42a1e9da3fc6617dd098d530a3b",
    "22ef20e32f2312a575f6faa39dacd77d63910e4d76b030516ca1419ba7f070dc",
    "8deca0bc678e42df2156c42c1459c1f6c0c1efb29c9d23217444cb2ec42a867c",
    "a0a6e050d688a4639ee7b052865dea5301fc5d199f53d439ef39c85597afddec",
    "db5750181e8cbf3ebab6cfa0490d632ed791816144ceb22f42ef3dfc3c4b1ba8",
    "f5eb36508251fefb6d82102310fc23a5509d191f7ed3a3b4416c052c7e897c7a",
]
UNSAT_PER_CASE = [8, 2, 1, 8, 2, 1]
PROOF = b"synthetic DRAT bytes; not presented as a proof\n"


def make_archive(path: Path, *, missing_proof=False, premature_open=False) -> None:
    ledger_fields = [
        "row_id", "profile", "direction", "earlier_H", "certified_H", "derived_from"
    ]
    ledger_rows = []
    with ZipFile(path, "w") as zf:
        for case_index, (key, unsat_count) in enumerate(zip(KEYS, UNSAT_PER_CASE)):
            cutoff = 2 if case_index in {0, 2, 3} else 3
            digest = hashlib.sha256(PROOF).hexdigest()
            for part in range(8):
                status = "UNSAT" if part < unsat_count else "OPEN"
                slug = f"cap-45000-part-{part}-of-8"
                base = f"{RECEIPT_PREFIX}{key}/{slug}"
                receipt = {
                    "key": key, "exterior_vertices": 27, "n": 58, "q": 0,
                    "cutoff": cutoff, "cap": 45000, "map_representatives": 16,
                    "query_sha256": f"query-{case_index}-{part}",
                    "status": status,
                    "conflicts": (10 if status == "UNSAT" else (1 if premature_open else 45000)),
                    "partition": [part, 8],
                }
                if status == "UNSAT":
                    receipt["proof_sha256"] = digest
                zf.writestr(base + "/receipt.json", json.dumps(receipt))
                if status == "UNSAT" and not (missing_proof and case_index == part == 0):
                    zf.writestr(base + "/proof.drat.gz", gzip.compress(PROOF))
            direct = {
                "key": key, "exterior_vertices": 27, "n": 58, "q": 0,
                "cutoff": cutoff, "cap": 65000, "map_representatives": 16,
                "query_sha256": f"direct-{case_index}", "status": "OPEN",
                "conflicts": 65000,
            }
            zf.writestr(
                f"{RECEIPT_PREFIX}{key}/cap-65000/receipt.json", json.dumps(direct)
            )
            if unsat_count == 8:
                derived = f"all 16 map representatives at H <= {cutoff}, 27 exterior vertices, {key}"
                ledger_rows.append({
                    "row_id": f"physical-{case_index}", "profile": "p", "direction": "forward",
                    "earlier_H": str(cutoff), "certified_H": str(cutoff + 1),
                    "derived_from": derived,
                })
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=ledger_fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(ledger_rows)
        zf.writestr(LEDGER, out.getvalue())


class ArchiveAccountingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent)
        self.zip = Path(self.temp.name) / "tiny.zip"
        make_archive(self.zip)

    def tearDown(self):
        self.temp.cleanup()

    def test_recomputed_counts_and_no_proof_claim(self):
        report = audit_archive(self.zip)
        self.assertEqual(report["split_children"], 48)
        self.assertEqual(report["split_status_counts"], {"OPEN": 26, "UNSAT": 22})
        self.assertEqual(report["receipt_complete_cutoffs"], 2)
        self.assertEqual(report["archived_direct_closed"], 0)
        self.assertEqual(report["proof_integrity"]["unsat_proofs_checked"], 22)
        self.assertFalse(report["proof_integrity"]["drat_replayed"])
        self.assertTrue(all(c["unrestricted_row_verdict"] == "NOT_EVALUATED" for c in report["cases"]))

    def test_missing_proof_is_rejected(self):
        make_archive(self.zip, missing_proof=True)
        with self.assertRaisesRegex(ValueError, "missing proof"):
            audit_archive(self.zip)

    def test_duplicate_partition_cannot_fake_coverage(self):
        duplicate = f"{RECEIPT_PREFIX}{KEYS[0]}/cap-45000-part-0-of-8/receipt.json"
        with ZipFile(self.zip, "a") as zf:
            receipt = json.loads(zf.read(duplicate))
            zf.writestr(duplicate, json.dumps(receipt))
        with self.assertRaisesRegex(ValueError, "duplicate archive member"):
            audit_archive(self.zip)

    def test_premature_open_is_rejected(self):
        make_archive(self.zip, premature_open=True)
        with self.assertRaisesRegex(ValueError, "premature OPEN"):
            audit_archive(self.zip)

    @unittest.skipUnless(os.environ.get("K58_937_ZIP"), "set K58_937_ZIP for original-archive integration test")
    def test_original_archive(self):
        report = audit_archive(Path(os.environ["K58_937_ZIP"]))
        self.assertEqual(report["source_zip_sha256"], "0478f72e0204de7b6e845a66aab4741046180ab3e5e9a726583e04b06e9d6527")
        self.assertEqual(report["manifest_members_verified"], 76)
        self.assertEqual(report["split_status_counts"], {"OPEN": 26, "UNSAT": 22})
        self.assertEqual(report["split_total_conflicts_including_open"], 1697996)
        self.assertEqual(report["receipt_complete_cutoffs"], 2)
        self.assertEqual(report["archived_direct_closed"], 0)
        self.assertTrue(report["proof_integrity"]["all_uncompressed_digests_match"])
        by_key = {c["case_key"]: c for c in report["cases"]}
        reverse = by_key["8deca0bc678e42df2156c42c1459c1f6c0c1efb29c9d23217444cb2ec42a867c"]["regenerated_projection_bindings"]
        self.assertEqual(reverse, [{"row_id": "c5eff016e42fd29b0689ba43ebece4fe372218208173e96e1b7dd97013a56c1d", "direction": "reverse"}])
        self.assertEqual(sum(len(c["regenerated_projection_bindings"]) for c in report["cases"]), 6)


class PolicyTests(unittest.TestCase):
    def test_timeout_and_unknown_stay_open(self):
        for statuses in (["UNSAT"] * 7 + ["TIMEOUT"], ["UNSAT"] * 7 + ["UNKNOWN"], ["SAT"] * 8):
            self.assertEqual(child_closure(list(statuses), coverage_verified=True, all_unsat_proofs_replayed=True), "OPEN")

    def test_unsat_labels_do_not_repair_missing_obligations(self):
        for coverage, replay, parent in ((False, True, True), (True, False, True), (True, True, False)):
            self.assertEqual(child_closure(["UNSAT"] * 8, coverage_verified=coverage, all_unsat_proofs_replayed=replay, intended_parent=parent), "OPEN")
        self.assertEqual(child_closure(["UNSAT"] * 8, coverage_verified=True, all_unsat_proofs_replayed=True), "CLOSED_CUTOFF")

    @staticmethod
    def pair(split_closed=False, direct_closed=False, split_work=100, direct_work=100, split_cap=100, direct_cap=100):
        return {
            "case_id": "same-case", "scope": "same signed H cutoff",
            "budget_relation": "EQUAL_TOTAL_CONFLICT_ALLOCATION",
            "split": {"closed": split_closed, "conflicts": split_work, "budget_conflicts": split_cap},
            "direct": {"closed": direct_closed, "conflicts": direct_work, "budget_conflicts": direct_cap},
        }

    def test_unequal_historical_caps_cannot_be_called_matched(self):
        pair = self.pair(split_closed=True, split_cap=150000, direct_cap=65000)
        pair["budget_relation"] = "ARCHIVED_UNMATCHED_RUNS"
        answer = compare_pair(pair)
        self.assertEqual(answer["outcome"], "INCOMPARABLE_BUDGETS")
        self.assertFalse(answer["may_split_on_this_evidence"])
        self.assertFalse(answer["general_speedup_claim"])

    def test_equal_allocation_outcomes_and_negative_control(self):
        split = compare_pair(self.pair(split_closed=True, direct_closed=False))
        self.assertEqual(split["outcome"], "ONLY_SPLIT_CLOSED_WITHIN_EQUAL_ALLOCATION")
        self.assertTrue(split["may_split_on_this_evidence"])
        both = compare_pair(self.pair(split_closed=True, direct_closed=True, split_work=70, direct_work=80))
        self.assertEqual(both["outcome"], "SPLIT_FEWER_TOTAL_CONFLICTS")
        direct = compare_pair(self.pair(split_closed=True, direct_closed=True, split_work=90, direct_work=80))
        self.assertEqual(direct["outcome"], "DIRECT_FEWER_TOTAL_CONFLICTS")
        self.assertFalse(direct["may_split_on_this_evidence"])
        inconclusive = compare_pair(self.pair())
        self.assertEqual(inconclusive["outcome"], "BOTH_OPEN_INCONCLUSIVE")
        self.assertFalse(inconclusive["may_split_on_this_evidence"])

    def test_stop_split_is_bounded_and_not_recursive(self):
        supported = compare_pair(self.pair(split_closed=True))
        self.assertEqual(next_split_decision(supported, coverage_verified=True, total_budget_exhausted=False, already_split=False)["action"], "SPLIT_ONCE_WITH_SHARED_TOTAL_CAP")
        self.assertEqual(next_split_decision(supported, coverage_verified=False, total_budget_exhausted=False, already_split=False)["action"], "HOLD_OPEN")
        self.assertEqual(next_split_decision(supported, coverage_verified=True, total_budget_exhausted=True, already_split=False)["action"], "STOP_OPEN")
        self.assertEqual(next_split_decision(supported, coverage_verified=True, total_budget_exhausted=False, already_split=True)["action"], "HOLD_OPEN")

    def test_bounded_pilot_is_measurement_not_speedup(self):
        inconclusive = compare_pair(self.pair())
        action = next_split_decision(
            inconclusive, coverage_verified=True, total_budget_exhausted=False,
            already_split=False, direct_pilot_open=True,
            split_measurement_budget_reserved=True,
        )
        self.assertEqual(action["action"], "MEASURE_ONE_BOUNDED_SPLIT")
        self.assertFalse(action["new_solver_herd"])
        self.assertEqual(action["reason"], "DIRECT_OPEN_PILOT_NOT_SPEEDUP_EVIDENCE")
        no_reserve = next_split_decision(
            inconclusive, coverage_verified=True, total_budget_exhausted=False,
            already_split=False, direct_pilot_open=True,
        )
        self.assertEqual(no_reserve["action"], "HOLD_OPEN_OR_DIRECT_WITHIN_CAP")

    def test_string_false_is_not_a_closure_flag(self):
        pair = self.pair()
        pair["split"]["closed"] = "false"
        self.assertEqual(compare_pair(pair)["outcome"], "INVALID_BOOLEAN_STATUS")


if __name__ == "__main__":
    unittest.main()
