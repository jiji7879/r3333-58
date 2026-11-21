"""Tests for ledger.py. Run: python -m unittest discover -s skills/siege-workflow/scripts -p 'test_*.py'"""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().with_name("ledger.py")


class Ledger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.d = self.root / "research" / "p"
        (self.d / "checks").mkdir(parents=True)
        (self.d / "problem.md").write_text("Statement.\n")
        (self.d / "notes.md").write_text("1. A step.\n2. Another step.\n")

    def tearDown(self):
        self.tmp.cleanup()

    def run_ledger(self, *args, ok=True):
        r = subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.root,
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0 if ok else 1, r.stdout + r.stderr)
        return r.stdout.strip()

    def add(self, *args, ok=True):
        return self.run_ledger("add", "research/p", *args, ok=ok)

    def gate(self):
        return self.run_ledger("gate", "research/p").splitlines()[0]

    def test_goal_proved_and_checked_by_a_model(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.add("PROVED", "the goal", "--on", "1", "--at", "notes.md#2")
        self.assertEqual(self.gate(), "NOT YET: #2 has no check: check it (references/check.md)")
        self.add("CHECK", "PASS: every step read", "--on", "2", "--kind", "model", "--at", "notes.md")
        self.assertEqual(self.gate(), "PROVED #2. The argument was checked by: model.")

    def test_gate_wording_by_check_kind(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.add("PROVED", "the goal", "--on", "1", "--at", "notes.md")
        self.add("CHECK", "PASS: values recomputed", "--on", "2", "--kind", "compute", "--at", "notes.md")
        self.assertIn("not read; only its computations", self.gate())
        self.add("CHECK", "PASS: read", "--on", "2", "--kind", "self", "--at", "notes.md")
        self.assertIn("read only by the model that wrote it", self.gate())

    def test_goal_resting_on_an_open_entry_is_refused(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.add("OPEN", "lemma B")
        self.add("PROVED", "the goal, by #2", "--on", "1", "--at", "notes.md")
        self.add("CHECK", "PASS: read", "--on", "3", "--kind", "model", "--at", "notes.md")
        self.assertEqual(self.gate(), "NOT YET: #3 rests on #2, still OPEN")
        self.add("PROVED", "lemma B", "--on", "2", "--at", "notes.md#1")
        self.assertEqual(self.gate(), "PROVED #3. The argument was checked by: model.")

    def test_retracting_the_proof_of_a_cited_lemma(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.add("OPEN", "lemma B")
        self.add("PROVED", "lemma B", "--on", "2", "--at", "notes.md")
        self.add("PROVED", "the goal, by #2", "--on", "1", "--at", "notes.md")
        self.add("CHECK", "PASS: read", "--on", "4", "--kind", "model", "--at", "notes.md")
        out = self.add("RETRACT", "lemma B's proof is wrong", "--on", "3")
        self.assertIn("resting on #3 or #2: #4", out)
        self.assertEqual(self.gate(), "NOT YET: #4 rests on #2, still OPEN")

    def test_goal_resting_on_a_refuted_entry_is_refused(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.add("OPEN", "lemma B")
        self.add("REFUTED", "lemma B fails at n = 3", "--on", "2", "--at", "notes.md")
        self.add("PROVED", "the goal, by #2", "--on", "1", "--at", "notes.md")
        self.add("CHECK", "PASS: read", "--on", "4", "--kind", "model", "--at", "notes.md")
        self.assertEqual(self.gate(), "NOT YET: #4 rests on #2, which was refuted")

    def test_brought_proof_of_a_false_statement(self):
        self.add("OPEN", "the statement", "--goal", "--at", "problem.md")
        self.add("PROVED", "the statement, as claimed", "--on", "1", "--at", "notes.md")
        self.add("CHECK", "GAP: step 4 fails at n = 40", "--on", "2", "--kind", "model", "--at", "notes.md")
        self.assertEqual(self.gate(), "NOT YET: unresolved GAP on #2")
        self.add("RETRACT", "step 4 fails", "--on", "2")
        self.add("REFUTED", "n = 40 is a counterexample", "--on", "1", "--at", "notes.md")
        self.assertEqual(self.gate(), "NOT YET: #5 has no check: check it (references/check.md)")
        self.add("CHECK", "PASS: 40^2+40+41 = 41^2", "--on", "5", "--kind", "compute", "--at", "notes.md")
        self.assertTrue(self.gate().startswith("REFUTED #5."))

    def test_a_case_does_not_settle_the_goal(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        out = self.add("PROVED", "the goal for n < 10", "--on", "1", "--case", "--at", "notes.md", ok=False)
        self.assertIn("a case does not settle the goal", out)

    def test_hand_edit_blocks_add_and_gate_until_undone(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        ledger = self.d / "ledger.md"
        before = ledger.read_text()
        ledger.write_text(before + "2. CHECK #1 [model]: PASS: invented — notes.md\n")
        self.assertIn("edited by hand", self.add("OPEN", "lemma", ok=False))
        self.assertIn("edited by hand", self.gate())
        ledger.write_text(before)
        self.add("OPEN", "lemma")

    def test_bad_input_is_refused(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.assertIn("TEXT comes right after STATUS", self.add("OPEN", "--goal", "x", ok=False))
        self.assertIn("does not exist", self.add("PROVED", "x", "--at", "/etc/hosts", ok=False))
        self.assertIn("no step 9", self.add("PROVED", "x", "--at", "notes.md#9", ok=False))
        self.assertIn("is a status, not a command", self.run_ledger("PROVED", "research/p", ok=False))

    def test_checkpoint_counts_stalls(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.assertTrue(self.run_ledger("checkpoint", "research/p").startswith("STALLED 1"))
        self.assertTrue(self.run_ledger("checkpoint", "research/p").startswith("STALLED 2"))
        self.add("PROVED", "a lemma", "--at", "notes.md")
        self.assertTrue(self.run_ledger("checkpoint", "research/p").startswith("PROGRESS"))

    def test_refuting_goal_may_mention_goal_number(self):
        self.add("OPEN", "the goal", "--goal", "--at", "problem.md")
        self.add("REFUTED", "n = 40 refutes #1", "--on", "1", "--at", "notes.md")
        self.add("CHECK", "PASS: checked at n = 40", "--on", "2", "--kind", "compute", "--at", "notes.md")
        self.assertTrue(self.gate().startswith("REFUTED #2."))


if __name__ == "__main__":
    unittest.main()
