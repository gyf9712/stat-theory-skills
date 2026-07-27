"""
skill_lint.py — structural lint for SKILL.md files. Repo-agnostic.

Guards the two defect classes that have actually bitten this project, both of which
are invisible until a skill is run from its INSTALLED location:

1. **Unresolvable file references.** A skill lives at `<skills>/<name>/SKILL.md`, so a
   companion reference must be written `../stat-shared-references/foo.md`. Writing
   `stat-shared-references/foo.md` (no `../`) or naming a repo-root file that the
   installer never copies produces an instruction pointing at nothing. Found twice:
   `CODEX_PROTOCOL.md` referenced by all five theory skills but never installed, and 15
   paths across four skills missing `../`.

2. **Control characters.** Writing `\\theta` inside a non-raw Python string turns it
   into a TAB. Happened twice in one editing session.

Exit codes
----------
    0 : no findings
    1 : at least one finding
    2 : invocation error

Usage
-----
    python skill_lint.py --skills-dir ../../skills
    python skill_lint.py --skills-dir ../../..  --layout flat   # writing repo layout
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

SCRIPT_VERSION = "1.0.0"

# Backticked path-like references to a .md or .py companion file.
REF_RE = re.compile(r"`((?:\.\./)?[A-Za-z0-9_][A-Za-z0-9._/-]*\.(?:md|py))`")

# Artifacts a skill CREATES rather than reads; absence is expected, not a defect.
OUTPUT_ARTIFACT_RE = re.compile(
    r"^(?:[A-Z][A-Z0-9_]*\.md|.*_(?:log|plan|report|matrix|ledger|lock)\.md|"
    r"papers/.*|audit/.*|simulation/.*|\d+_[a-z]+/.*|.*\.lock\.md)$"
)

CONTROL_CHARS = {"\t": "TAB", "\x08": "BACKSPACE", "\x0c": "FORMFEED"}

# A hard-coded count in a HEADING is a maintenance trap: the list grows, the number
# does not, and a stale count is worse than none because the model may read it as a
# completeness target and stop enumerating there. Found as "## 19 Common Failure
# Patterns" over a list that had grown to 29.
COUNT_IN_HEADING_RE = re.compile(r"^#{1,4}\s+(\d+)\s+[A-Z]", re.M)


@dataclass
class Finding:
    id: str
    status: str
    message: str
    evidence: dict = field(default_factory=dict)


def lint_skill(skill_md: Path, shared_names: set[str], install_root: Path | None,
               shared_dir_name: str = "stat-shared-references",
               shared_root: Path | None = None) -> list[Finding]:
    out: list[Finding] = []
    raw = skill_md.read_text(encoding="utf-8", errors="replace")
    skill_dir = skill_md.parent

    for m in COUNT_IN_HEADING_RE.finditer(raw):
        line_no = raw[:m.start()].count("\n") + 1
        out.append(Finding("count_in_heading", "WARN",
            f"{skill_dir.name}:{line_no} hard-codes a count ({m.group(1)}) in a heading. "
            f"Counts drift as the list grows; prefer no number, or verify it.",
            {"skill": skill_dir.name, "line": line_no, "count": m.group(1)}))

    for i, line in enumerate(raw.splitlines(), 1):
        for ch, name in CONTROL_CHARS.items():
            if ch in line:
                out.append(Finding("control_character", "FAIL",
                    f"{name} at {skill_md.parent.name}:{i} — usually a mangled LaTeX "
                    f"escape from a non-raw string edit.",
                    {"skill": skill_dir.name, "line": i, "text": line.strip()[:90]}))

    for m in REF_RE.finditer(raw):
        ref = m.group(1)
        base = ref.split("/")[-1]
        if OUTPUT_ARTIFACT_RE.match(ref) and not ref.startswith("../"):
            continue                              # an artifact the skill writes
        if ref.startswith("../"):
            # Resolve against the INSTALLED layout, where <skill>/ and the shared
            # directory are siblings under ~/.claude/skills/. In the repo they are not
            # siblings (skills/ is its own subdirectory), so resolving against the repo
            # path would reject every correct reference.
            rest = ref[3:]
            prefix = shared_dir_name + "/"
            if shared_root and rest.startswith(prefix) and (shared_root / rest[len(prefix):]).exists():
                continue
            if install_root and (install_root / rest).exists():
                continue
            if (skill_dir / ref).resolve().exists():
                continue
            out.append(Finding("unresolvable_reference", "FAIL",
                f"{skill_dir.name} references {ref!r}, which resolves to nothing in the "
                f"installed layout.", {"skill": skill_dir.name, "ref": ref}))
        elif "/" in ref:
            # A path with a directory component and no '../' is definitively broken:
            # it resolves against the skill's own directory, where nothing lives.
            shared_name = shared_dir_name
            suggested = ("../" + ref if ref.startswith(shared_name + "/")
                         else f"../{shared_name}/{ref}")
            out.append(Finding("missing_parent_prefix", "FAIL",
                f"{skill_dir.name} references {ref!r} without '../'. A skill lives one "
                f"level below the shared directory, so this path does not resolve once "
                f"installed.", {"skill": skill_dir.name, "ref": ref,
                                "suggested": suggested}))
        elif base in shared_names:
            # A bare filename naming a real shared file. Common in prose ("per the
            # schema in `foo.md`") and usually harmless because the full path appears
            # elsewhere in the same skill — advisory, not a failure.
            out.append(Finding("bare_shared_filename", "WARN",
                f"{skill_dir.name} names {ref!r} without a path. Fine in prose if the "
                f"full path appears elsewhere in the skill; otherwise give the path.",
                {"skill": skill_dir.name, "ref": ref}))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Structural lint for SKILL.md files.")
    ap.add_argument("--skills-dir", required=True,
                    help="Directory containing <name>/SKILL.md subdirectories.")
    ap.add_argument("--shared-dir", default=None,
                    help="The stat-shared-references directory (default: sibling of skills-dir).")
    ap.add_argument("--install-root", default=None,
                    help="Optional installed skills root, for cross-repo references.")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    try:
        skills_dir = Path(args.skills_dir).resolve()
        if not skills_dir.is_dir():
            raise FileNotFoundError(f"skills dir not found: {skills_dir}")
        shared = Path(args.shared_dir).resolve() if args.shared_dir else None
        if shared is None:
            for cand in (skills_dir / "stat-shared-references",
                         skills_dir.parent / "stat-shared-references"):
                if cand.is_dir():
                    shared = cand
                    break
        shared_names = set()
        if shared and shared.is_dir():
            shared_names = {p.name for p in shared.rglob("*") if p.is_file()}
        install_root = Path(args.install_root).resolve() if args.install_root else None

        findings: list[Finding] = []
        skills = sorted(skills_dir.glob("*/SKILL.md"))
        for s in skills:
            findings += lint_skill(s, shared_names, install_root,
                                   shared.name if shared else "stat-shared-references",
                                   shared)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    payload = {"provenance": {"script_version": SCRIPT_VERSION,
                              "skills_dir": str(skills_dir),
                              "skills_checked": len(skills)},
               "findings": [asdict(f) for f in findings],
               "summary": {"FAIL": sum(1 for f in findings if f.status == "FAIL"),
                           "WARN": sum(1 for f in findings if f.status == "WARN")}}
    out = json.dumps(payload, indent=2)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 1 if any(f.status == "FAIL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
