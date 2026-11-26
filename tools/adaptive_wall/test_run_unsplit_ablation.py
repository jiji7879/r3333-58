import tempfile
import unittest
from pathlib import Path

from run_unsplit_ablation import require_empty_case_directory, require_observed_native_call


class FreshObservationTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parent / ".scratch"
        scratch.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_empty_real_directory_is_accepted(self):
        case = self.root / "case"
        case.mkdir()
        require_empty_case_directory(case)

    def test_primary_and_query_suffixed_receipts_are_rejected(self):
        for name in ("r-guided-40000.json", "r-guided-40000-0123456789ab.json"):
            case = self.root / name
            case.mkdir()
            (case / name).write_text("{}")
            with self.assertRaisesRegex(ValueError, "fresh empty"):
                require_empty_case_directory(case)

    def test_arbitrary_entry_and_symlink_are_rejected(self):
        case = self.root / "nonempty"
        case.mkdir()
        (case / "unrelated").write_text("do not overwrite")
        with self.assertRaisesRegex(ValueError, "fresh empty"):
            require_empty_case_directory(case)
        empty = self.root / "empty"
        empty.mkdir()
        link = self.root / "link"
        link.symlink_to(empty, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "fresh empty"):
            require_empty_case_directory(link)

    def test_zero_native_invocations_cannot_claim_fresh_execution(self):
        with self.assertRaisesRegex(ValueError, "no Kissat invocation"):
            require_observed_native_call([])
        require_observed_native_call([{"sequence": 1, "cap": 40000}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
