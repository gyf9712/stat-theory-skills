"""
Stdlib unittest for proof_gap_scan.py. No external dependencies.

Run from repo root:
    python -m unittest tests.test_proof_gap_scan

Verifies the two-tier finding model: a clean provable package produces no
STRUCTURAL-INCOMPLETE findings (exit 0); a package with each structural defect
produces the expected hard-fail findings (exit 1) plus advisory CANDIDATE hits.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "stat-shared-references" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import proof_gap_scan  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proof_gap_scan"


def _args(path):
    import argparse
    ns = argparse.Namespace()
    ns.proof = str(path)
    ns.json_out = None
    ns.md_out = None
    return ns


def _scan(name):
    findings, context = proof_gap_scan.run_scan(_args(FIXTURE / name))
    ids = [f.id for f in findings]
    structural = [f for f in findings if f.status == "STRUCTURAL-INCOMPLETE"]
    candidates = [f for f in findings if f.status == "CANDIDATE"]
    return findings, context, ids, structural, candidates


class CleanProvableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings, cls.context, cls.ids, cls.structural, cls.candidates = _scan("clean_provable.md")

    def test_parsed_status(self):
        self.assertEqual(self.context["status"], proof_gap_scan.rules.STATUS_PROVABLE)
        self.assertEqual(self.context["verification"], proof_gap_scan.rules.VERIFICATION_CONDITIONAL)

    def test_obligations_counted(self):
        self.assertEqual(self.context["obligation_count"], 3)
        self.assertEqual(self.context["blocked_count"], 0)

    def test_no_structural_findings(self):
        self.assertEqual(self.structural, [], msg=[f.id for f in self.structural])

    def test_no_hedges(self):
        self.assertEqual(self.candidates, [], msg=[f.id for f in self.candidates])

    def test_exit_code_clean(self):
        self.assertEqual(proof_gap_scan.main(["--proof", str(FIXTURE / "clean_provable.md")]), 0)


class IncompletePackageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.findings, cls.context, cls.ids, cls.structural, cls.candidates = _scan("incomplete.md")

    def test_blocked_under_provable(self):
        self.assertIn("blocked_under_provable", self.ids)

    def test_missing_closure_field(self):
        # O4 (CLOSED-CITED) omits source-status.
        missing = [f for f in self.findings if f.id == "missing_closure_field"]
        self.assertTrue(missing)
        fields = {f.evidence.get("missing_field") for f in missing}
        self.assertIn("source-status", fields)

    def test_bridge_undefined(self):
        # O2 names bridge B9, never defined in the Proof.
        self.assertIn("bridge_undefined", self.ids)
        b = [f for f in self.findings if f.id == "bridge_undefined"][0]
        self.assertEqual(b.evidence.get("bridge"), "B9")

    def test_undefined_obligation_ref(self):
        # Dependency Map references O9, absent from the ledger.
        self.assertIn("undefined_obligation_ref", self.ids)
        refs = [f.evidence.get("obligation") for f in self.findings if f.id == "undefined_obligation_ref"]
        self.assertIn("O9", refs)

    def test_verification_overclaim(self):
        # Verified status with an unverified-source citation.
        self.assertIn("verification_overclaim", self.ids)

    def test_verification_checks_blank(self):
        self.assertIn("verification_checks_blank", self.ids)

    def test_obligation_untyped(self):
        # O6 has no closure state.
        self.assertIn("obligation_untyped", self.ids)

    def test_hedge_is_advisory_only(self):
        # "Clearly" in the proof is a CANDIDATE, never STRUCTURAL-INCOMPLETE.
        self.assertIn("hedge_phrase", [f.id for f in self.candidates])
        self.assertNotIn("hedge_phrase", [f.id for f in self.structural])

    def test_exit_code_fail(self):
        self.assertEqual(proof_gap_scan.main(["--proof", str(FIXTURE / "incomplete.md")]), 1)


if __name__ == "__main__":
    unittest.main()
