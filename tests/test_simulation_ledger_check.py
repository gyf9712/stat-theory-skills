"""
Stdlib unittest for simulation_ledger_check.py.

Run from repo root:
    python -m unittest tests.test_simulation_ledger_check

This is the mechanical half of the theory-simulation acceptance test: it verifies the
checker itself catches the failure modes it is supposed to catch, so that when the
checker later passes a real skill run, the pass means something.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "stat-shared-references" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import simulation_ledger_check as chk  # noqa: E402

FIX = ROOT / "tests" / "fixtures" / "simulation_ledger"
SKILL = ROOT / "skills" / "theory-simulation" / "SKILL.md"


def run(report, mode="audit", expect=None):
    argv = ["--report", str(FIX / report), "--mode", mode]
    if expect:
        argv += ["--expect", str(FIX / expect)]
    return chk.main(argv + ["--json-out", str(FIX / "_out.json")])


class GoodAuditTest(unittest.TestCase):
    def test_parses_all_claims(self):
        rows = chk.parse_ledger((FIX / "good_audit.md").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 4, msg=[r["claim"] for r in rows])

    def test_states_recognised(self):
        rows = chk.parse_ledger((FIX / "good_audit.md").read_text(encoding="utf-8"))
        states = {r["state"] for r in rows}
        self.assertIn("YES[strong]", states)
        self.assertIn("NO", states)
        self.assertTrue(any(s.startswith("PARTIAL[") for s in states))

    def test_passes_clean(self):
        self.assertEqual(run("good_audit.md", "audit"), 0)

    def test_passes_against_expect(self):
        self.assertEqual(run("good_audit.md", "audit", "EXPECT_good_audit.md"), 0)


class FailureModeTest(unittest.TestCase):
    def test_third_vocabulary_caught(self):
        self.assertEqual(run("bad_third_vocab.md", "audit"), 1)
        text = (FIX / "bad_third_vocab.md").read_text(encoding="utf-8")
        ids = [f.id for f in chk.check_vocabulary(text)]
        self.assertIn("third_vocabulary", ids)      # "OPEN HYPOTHESIS"
        self.assertIn("adhoc_claim_state", ids)     # a claim row stating "VERIFIED"

    def test_criterion_level_pass_fail_is_not_flagged(self):
        """PASS / FAIL inside a per-criterion audit table are correct, not violations.

        A live acceptance run exposed this as a false positive in the first version of
        the checker: the skill's own contract asks for "| Criterion | Status |" rows.
        """
        extra = "\n".join([
            "",
            "## Per-experiment audit",
            "| Criterion | Status | Issue |",
            "|---|---|---|",
            "| MCSE reported | PASS | bars present |",
            "| Stress tests | FAIL | none run |",
        ])
        text = (FIX / "good_audit.md").read_text(encoding="utf-8") + extra
        ids = [f.id for f in chk.check_vocabulary(text)]
        self.assertNotIn("third_vocabulary", ids)
        self.assertNotIn("adhoc_claim_state", ids)

    def test_criterion_row_mentioning_a_claim_is_not_flagged(self):
        """A criterion row whose prose mentions a claim id is not a claim row.

        Second false positive found by a live acceptance run: the row
        "| Loss object matches the theorem | PASS | ...right object for C3 |" was
        flagged because the claim-id search scanned the whole row instead of the
        claim column.
        """
        extra = "\n".join([
            "",
            "| Criterion | Status | Issue |",
            "|---|---|---|",
            "| Loss object matches the theorem | PASS | the right object for C3. |",
        ])
        text = (FIX / "good_audit.md").read_text(encoding="utf-8") + extra
        ids = [f.id for f in chk.check_vocabulary(text)]
        self.assertNotIn("adhoc_claim_state", ids)

    def test_design_missing_dimensions_caught(self):
        self.assertEqual(run("bad_design_gaps.md", "design"), 1)
        text = (FIX / "bad_design_gaps.md").read_text(encoding="utf-8")
        missing = {f.evidence.get("dimension") for f in chk.check_dimensions(text, "design")}
        # The fixture mentions no truth source, selection discipline, tuning, or timing.
        self.assertIn("truth", missing)
        self.assertIn("tuning", missing)

    def test_contradiction_without_triage_caught(self):
        self.assertEqual(run("bad_contradiction.md", "audit"), 1)
        text = (FIX / "bad_contradiction.md").read_text(encoding="utf-8")
        rows = chk.parse_ledger(text)
        ids = [f.id for f in chk.check_contradiction_triage(text, rows)]
        self.assertIn("contradiction_without_triage", ids)

    def test_review_items_never_fail_the_run(self):
        # The advisory human-judgment item must not affect exit code on a clean report.
        self.assertEqual(run("good_audit.md", "audit"), 0)


class SelfLintTest(unittest.TestCase):
    """The lint that guards the skill file itself."""

    def test_skill_has_no_control_characters(self):
        findings = chk.self_lint(SKILL)
        ctrl = [f for f in findings if f.id == "control_character"]
        self.assertEqual(ctrl, [], msg=[f.evidence for f in ctrl])

    def test_skill_defines_every_state(self):
        findings = chk.self_lint(SKILL)
        undef = [f.evidence.get("state") for f in findings if f.id == "state_undefined_in_skill"]
        self.assertEqual(undef, [], msg=undef)

    def test_self_lint_exit_zero(self):
        self.assertEqual(chk.main(["--self-lint", str(SKILL),
                                   "--json-out", str(FIX / "_lint.json")]), 0)


if __name__ == "__main__":
    unittest.main()
