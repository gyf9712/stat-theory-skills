"""
Stdlib unittest for proof_index.py. No external dependencies.

Run from repo root:
    python -m unittest tests.test_proof_index

Verifies inventory, dependency attribution, topological layering, undefined-ref
detection, unlabeled-environment warning, and a cycle fixture.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "stat-shared-references" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import proof_index  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "proof_index"


def _args(main, supplement=None, mode="none"):
    import argparse
    ns = argparse.Namespace()
    ns.main = str(main)
    ns.supplement = str(supplement) if supplement else None
    ns.supplement_mode = mode
    ns.json_out = None
    ns.md_out = None
    return ns


class ProofIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.units, cls.layers, cls.findings, cls.context = proof_index.run_index(
            _args(FIXTURE / "paper.tex")
        )
        cls.by_label = {u.label: u for u in cls.units if u.label}
        cls.finding_ids = [f.id for f in cls.findings]

    def test_inventory_count(self):
        # 5 labeled (assumption, 2 lemmas, theorem, proposition) + 1 unlabeled lemma = 6.
        self.assertEqual(len(self.units), 6)

    def test_assumption_indexed(self):
        self.assertIn("ass:subgauss", self.by_label)
        self.assertEqual(self.by_label["ass:subgauss"].env_type, "assumption")

    def test_theorem_dependencies(self):
        # thm:rate's proof cites both lemmas and the assumption.
        deps = set(self.by_label["thm:rate"].depends_on)
        self.assertIn("lem:concentration", deps)
        self.assertIn("lem:bias", deps)
        self.assertIn("ass:subgauss", deps)

    def test_no_self_dependency(self):
        # lem:concentration's proof \ref's ass:subgauss twice but not itself.
        self.assertNotIn("lem:concentration", self.by_label["lem:concentration"].depends_on)

    def test_topological_order(self):
        # Flatten layers; assumption and lem:bias should appear before thm:rate;
        # thm:rate before prop:extra.
        order = [lab for layer in self.layers for lab in layer]
        self.assertLess(order.index("ass:subgauss"), order.index("lem:concentration"))
        self.assertLess(order.index("lem:concentration"), order.index("thm:rate"))
        self.assertLess(order.index("lem:bias"), order.index("thm:rate"))
        self.assertLess(order.index("thm:rate"), order.index("prop:extra"))

    def test_undefined_ref_flagged(self):
        self.assertIn("undefined_ref", self.finding_ids)
        # Specifically the nonexistent label.
        undefined = [f for f in self.findings if f.id == "undefined_ref"]
        targets = {f.evidence.get("target") for f in undefined}
        self.assertIn("thm:does_not_exist", targets)

    def test_unlabeled_warning(self):
        self.assertIn("unlabeled_environment", self.finding_ids)

    def test_exit_code_fail(self):
        # The undefined ref is a FAIL, so the CLI exit code must be 1.
        code = proof_index.main(["--main", str(FIXTURE / "paper.tex")])
        self.assertEqual(code, 1)

    def test_provenance(self):
        for key in ["script_version", "rules_version", "rules_digest", "reference_mode"]:
            self.assertIn(key, self.context)
            self.assertTrue(self.context[key])


class CycleTest(unittest.TestCase):
    """A two-unit mutual-dependency fixture must be detected as a cycle."""

    def setUp(self):
        self.tmp = FIXTURE / "_cycle.tex"
        self.tmp.write_text(
            r"""\documentclass{article}
\usepackage{amsthm}
\newtheorem{lemma}{Lemma}
\begin{document}
\begin{lemma}\label{lem:a}A\end{lemma}
\begin{proof}By Lemma~\ref{lem:b}.\end{proof}
\begin{lemma}\label{lem:b}B\end{lemma}
\begin{proof}By Lemma~\ref{lem:a}.\end{proof}
\end{document}
""",
            encoding="utf-8",
        )

    def tearDown(self):
        if self.tmp.exists():
            self.tmp.unlink()

    def test_cycle_detected(self):
        units, layers, findings, context = proof_index.run_index(_args(self.tmp))
        ids = [f.id for f in findings]
        self.assertIn("dependency_cycle", ids)


if __name__ == "__main__":
    unittest.main()
