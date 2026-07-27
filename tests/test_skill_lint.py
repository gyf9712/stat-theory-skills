"""
Stdlib unittest for skill_lint.py.

Run from repo root:
    python -m unittest tests.test_skill_lint

Guards the defect class that has bitten this project three times: a file reference in a
SKILL.md that does not resolve once the skill is installed. Each case below corresponds
to a real bug that shipped.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "stat-shared-references" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import skill_lint  # noqa: E402


# References that legitimately live in the sibling stat-writing-skills repo. Both repos
# install into one shared directory, so these resolve at runtime but not from this repo
# alone. Anything OUTSIDE this set is a real defect.
KNOWN_CROSS_REPO = {"../stat-shared-references/stat-theory-writing.md"}


class RealRepoTest(unittest.TestCase):
    """The live repo must stay clean apart from the known cross-repo references."""

    def _findings(self):
        shared = ROOT / "stat-shared-references"
        names = {p.name for p in shared.rglob("*") if p.is_file()}
        out = []
        for s in sorted((ROOT / "skills").glob("*/SKILL.md")):
            out += skill_lint.lint_skill(s, names, None, "stat-shared-references", shared)
        return out

    def test_no_unexpected_failures(self):
        bad = [f for f in self._findings()
               if f.status == "FAIL" and f.evidence.get("ref") not in KNOWN_CROSS_REPO]
        self.assertEqual(bad, [], msg=[f.evidence for f in bad])

    def test_no_control_characters_anywhere(self):
        ctrl = [f for f in self._findings() if f.id == "control_character"]
        self.assertEqual(ctrl, [], msg=[f.evidence for f in ctrl])

    def test_cross_repo_refs_resolve_when_install_root_given(self):
        """With both repos installed side by side, even the cross-repo refs resolve."""
        live = Path.home() / ".claude" / "skills"
        if not (live / "stat-shared-references" / "stat-theory-writing.md").exists():
            self.skipTest("live install not present")
        code = skill_lint.main([
            "--skills-dir", str(ROOT / "skills"),
            "--shared-dir", str(ROOT / "stat-shared-references"),
            "--install-root", str(live),
            "--json-out", str(ROOT / "tests" / "fixtures" / "_lint.json"),
        ])
        self.assertEqual(code, 0)


class SyntheticTest(unittest.TestCase):
    """Each case is a bug that actually shipped."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.shared = root / "stat-shared-references"
        (self.shared / "scripts").mkdir(parents=True)
        (self.shared / "real-protocol.md").write_text("x", encoding="utf-8")
        (self.shared / "scripts" / "tool.py").write_text("x", encoding="utf-8")
        self.skills = root / "skills"
        (self.skills / "demo").mkdir(parents=True)
        self.skill = self.skills / "demo" / "SKILL.md"

    def tearDown(self):
        self.tmp.cleanup()

    def _lint(self, body: str):
        self.skill.write_text(body, encoding="utf-8")
        names = {p.name for p in self.shared.rglob("*") if p.is_file()}
        return skill_lint.lint_skill(self.skill, names, None,
                                     "stat-shared-references", self.shared)

    def test_correct_reference_is_clean(self):
        f = self._lint("See `../stat-shared-references/real-protocol.md` for the schema.")
        self.assertEqual([x.id for x in f], [])

    def test_missing_parent_prefix_is_a_failure(self):
        """The 15-path bug: a directory path without '../' resolves nowhere."""
        f = self._lint("See `stat-shared-references/real-protocol.md`.")
        ids = [x.id for x in f]
        self.assertIn("missing_parent_prefix", ids)
        sug = [x.evidence["suggested"] for x in f if x.id == "missing_parent_prefix"][0]
        self.assertEqual(sug, "../stat-shared-references/real-protocol.md")

    def test_scripts_path_without_prefix_is_a_failure(self):
        """The proof-repair bug introduced during compression."""
        f = self._lint("Run `scripts/tool.py` on the paper.")
        self.assertIn("missing_parent_prefix", [x.id for x in f])

    def test_nonexistent_target_is_a_failure(self):
        """The CODEX_PROTOCOL bug: a well-formed path to a file that is not installed."""
        f = self._lint("Follow `../stat-shared-references/does-not-exist.md`.")
        self.assertIn("unresolvable_reference", [x.id for x in f])

    def test_output_artifacts_are_not_flagged(self):
        """Files the skill CREATES are not references; absence is expected."""
        f = self._lint("Write `REPAIR_PLAN.md` and `audit/06_reports/issue_log.md`, "
                       "then `06_reports/FINAL_REPORT.md`.")
        self.assertEqual([x.id for x in f if x.status == "FAIL"], [])

    def test_bare_shared_filename_is_advisory_only(self):
        """A prose mention by bare name is a WARN, never a build failure."""
        f = self._lint("The schema in `real-protocol.md` governs this.")
        self.assertEqual([x.id for x in f], ["bare_shared_filename"])
        self.assertEqual(f[0].status, "WARN")

    def test_control_character_caught(self):
        """Writing \\theta in a non-raw Python string leaves a TAB behind."""
        f = self._lint("A single-$\theta$ test is not enough.")
        self.assertIn("control_character", [x.id for x in f])

    def test_count_in_heading_is_advisory(self):
        """A count in a heading drifts as the list grows.

        Shipped as "## 19 Common Failure Patterns" over a list of 29. Advisory rather
        than a failure, since a correct count is not itself wrong.
        """
        f = self._lint("## 19 Common Failure Patterns\n\n- a\n- b\n")
        hits = [x for x in f if x.id == "count_in_heading"]
        self.assertTrue(hits)
        self.assertEqual(hits[0].status, "WARN")
        self.assertEqual(hits[0].evidence["count"], "19")

    def test_ordinary_heading_not_flagged(self):
        f = self._lint("## Common Failure Patterns\n\n## Step 2: Do the thing\n")
        self.assertEqual([x.id for x in f if x.id == "count_in_heading"], [])


if __name__ == "__main__":
    unittest.main()
