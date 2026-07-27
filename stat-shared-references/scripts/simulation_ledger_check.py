"""
simulation_ledger_check.py — acceptance checker for theory-simulation output.

A prose skill has no unit tests, so this is the mechanical half of the acceptance
test: given a produced simulation report (a Claim Evidence Ledger plus supporting
prose), it verifies the assertions that are actually decidable, and reports the
rest as REVIEW items for a human.

Designed with Codex (threadId 019fa456-c827-7103-9bcc-0a2af1803240). The workflow is:
build a fixture, write its EXPECT.md, run the skill in a fresh session N times, then
run this checker on each output. Pass = 2/3 runs satisfy every hard assertion with no
forbidden failure.

Hard assertions (affect exit code)
----------------------------------
- Only the approved state vocabulary appears (no "third vocabulary" regression).
- Every claim has exactly one ledger row.
- DESIGN mode: every planned experiment states a position on the four
  design-applicable adequacy dimensions.
- AUDIT mode: no claim reaches YES[*] without dimension-level support.
- CONTRADICTED is never used without triage evidence preceding a theorem-failure
  conclusion.
- If an EXPECT.md is supplied, the observed route and per-claim states match it.

REVIEW items (never affect exit code)
-------------------------------------
Judgment calls a script cannot make: whether an audit recommended full redesign when
targeted repair would do, whether a dimension position is substantively adequate.

    0 : all hard assertions hold
    1 : at least one hard assertion failed
    2 : invocation or runtime error

Usage
-----
    python simulation_ledger_check.py --report OUT.md --mode design
    python simulation_ledger_check.py --report OUT.md --expect EXPECT.md
    python simulation_ledger_check.py --self-lint ../../skills/theory-simulation/SKILL.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import simulation_ledger_check_rules as rules  # noqa: E402

SCRIPT_VERSION = "1.0.0"


@dataclass
class Finding:
    id: str
    status: str        # FAIL (hard) | REVIEW (advisory) | INFO
    message: str
    evidence: dict = field(default_factory=dict)


def _fail(i, m, e=None): return Finding(i, "FAIL", m, e or {})
def _review(i, m, e=None): return Finding(i, "REVIEW", m, e or {})


def parse_ledger(text: str) -> list[dict]:
    """Extract (claim_id, priority, state) triples from ledger-shaped table rows."""
    rows = []
    for line in text.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2:
            continue
        joined = " ".join(cells)
        st = rules.STATE_RE.search(joined)
        cid = rules.CLAIM_ID_RE.search(cells[0])
        if st and cid:
            prio = next((p for p in rules.PRIORITIES if p in joined), None)
            rows.append({"claim": cid.group(1), "state": st.group(1),
                         "priority": prio, "line": line.strip()})
    return rows


def check_vocabulary(text: str) -> list[Finding]:
    """Detect a third vocabulary for CLAIM STATUS.

    Deliberately narrow. Words like PASS / FAIL are correct as per-criterion verdicts
    inside an audit table — the skill's own contract asks for them — so they are only a
    failure when used as a claim's ledger state. Flagging them document-wide was a
    false positive caught by the first live acceptance run.
    """
    out = []
    for pat in rules.BANNED_VOCAB:
        m = re.search(pat, text)
        if m:
            ctx = text[max(0, m.start()-45):m.end()+45].replace("\n", " ")
            out.append(_fail("third_vocabulary",
                f"Pre-unification status vocabulary {m.group(0)!r} appears; the ledger "
                f"admits only {', '.join(rules.STATES)}.",
                {"match": m.group(0), "context": ctx.strip()}))

    # A table row that names a claim must carry an approved state, not an ad-hoc one.
    # The claim id must be in the FIRST cell (the claim column), matching parse_ledger.
    # Searching the whole row misfires on a criterion row whose prose mentions a claim
    # ("...the right object for C3") — a second false positive caught by a live run.
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if len(cells) < 2 or all(set(c) <= {"-", ":", " "} for c in cells):
            continue
        if rules.CLAIM_ID_RE.search(cells[0]) is None:
            continue
        if rules.STATE_RE.search(" ".join(cells)):
            continue                      # has an approved state — fine
        adhoc = [t for t in rules.BANNED_AS_STATE
                 if any(re.fullmatch(rf"\**{t}\**", c, re.I) for c in cells)]
        if adhoc:
            out.append(_fail("adhoc_claim_state",
                f"A claim row uses {adhoc[0]!r} as its state instead of the approved "
                f"ledger vocabulary.", {"row": s[:110], "token": adhoc[0]}))
    return out


def check_one_row_per_claim(rows: list[dict]) -> list[Finding]:
    out, seen = [], {}
    for r in rows:
        seen.setdefault(r["claim"].replace(" ", ""), []).append(r["state"])
    for claim, states in seen.items():
        if len(states) > 1:
            out.append(_fail("duplicate_ledger_row",
                f"Claim {claim} has {len(states)} ledger rows ({', '.join(states)}); "
                f"exactly one is required.", {"claim": claim, "states": states}))
    if not rows:
        out.append(_fail("no_ledger", "No Claim Evidence Ledger rows found in the report.", {}))
    return out


def check_reason_codes(rows: list[dict]) -> list[Finding]:
    out = []
    for r in rows:
        m = re.match(r"(PARTIAL|CONTRADICTED)\[([^\]]*)\]", r["state"])
        if not m:
            continue
        codes = [c.strip() for c in m.group(2).split(",") if c.strip()]
        if not codes:
            out.append(_fail("missing_reason_code",
                f"{r['claim']} is {m.group(1)}[] with no reason code.", {"claim": r["claim"]}))
        for c in codes:
            if c not in rules.REASON_CODES:
                out.append(_fail("unknown_reason_code",
                    f"{r['claim']} uses reason code {c!r}, which is not in the approved set.",
                    {"claim": r["claim"], "code": c}))
    return out


def check_dimensions(text: str, mode: str) -> list[Finding]:
    out = []
    if mode not in ("design", "hybrid"):
        return out
    low = text.lower()
    for dim in rules.DIMENSIONS_DESIGN_REQUIRED:
        if not any(re.search(p, low) for p in rules.DIMENSIONS[dim]):
            out.append(_fail("design_missing_dimension",
                f"DESIGN output states no position on the '{dim}' adequacy dimension.",
                {"dimension": dim}))
    return out


def check_audit_support(text: str, rows: list[dict], mode: str) -> list[Finding]:
    out = []
    if mode not in ("audit", "hybrid"):
        return out
    low = text.lower()
    covered = [d for d in rules.DIMENSIONS
               if any(re.search(p, low) for p in rules.DIMENSIONS[d])]
    for r in rows:
        if r["state"].startswith("YES") and len(covered) < 3:
            out.append(_fail("yes_without_dimension_support",
                f"{r['claim']} is {r['state']} but the report discusses only "
                f"{len(covered)} adequacy dimension(s); YES requires dimension-level support.",
                {"claim": r["claim"], "dimensions_discussed": covered}))
    return out


def check_contradiction_triage(text: str, rows: list[dict]) -> list[Finding]:
    out = []
    if not any(r["state"].startswith("CONTRADICTED") for r in rows):
        return out
    low = text.lower()
    if not any(re.search(p, low) for p in rules.TRIAGE_MARKERS):
        out.append(_fail("contradiction_without_triage",
            "A claim is CONTRADICTED but the report shows no triage (replication check, "
            "seed rerun, implementation check) before that conclusion.", {}))
    if any(re.search(p, low) for p in rules.THEOREM_FAILURE_MARKERS) and \
       not any(re.search(p, low) for p in rules.TRIAGE_MARKERS):
        out.append(_fail("premature_theorem_failure",
            "The report concludes the theorem is wrong without documented triage.", {}))
    return out


def check_expect(rows: list[dict], expect_path: Path) -> list[Finding]:
    """Compare observed route/states against a fixture's EXPECT.md."""
    out = []
    text = expect_path.read_text(encoding="utf-8", errors="replace")
    want_route = re.search(r"expected[_ ]route\s*:\s*(\w+)", text, re.I)
    if want_route:
        out.append(Finding("expected_route", "INFO",
            f"Fixture expects route {want_route.group(1).upper()}.",
            {"route": want_route.group(1).upper()}))
    observed = {r["claim"].replace(" ", ""): r["state"] for r in rows}
    for m in re.finditer(r"^\s*[-*]\s*([\w. ]+?)\s*(?:->|:)\s*(\S+)\s*$", text, re.M):
        claim, want = m.group(1).strip().replace(" ", ""), m.group(2).strip()
        if not rules.STATE_RE.fullmatch(want):
            continue
        got = observed.get(claim)
        if got is None:
            out.append(_fail("expected_claim_absent",
                f"EXPECT names claim {claim} but the report has no ledger row for it.",
                {"claim": claim, "expected": want}))
        elif got.split("[")[0] != want.split("[")[0]:
            out.append(_fail("state_mismatch",
                f"Claim {claim}: expected {want}, got {got}.",
                {"claim": claim, "expected": want, "got": got}))
    return out


def self_lint(skill_path: Path) -> list[Finding]:
    """Lint the SKILL.md itself: control characters and vocabulary consistency."""
    out = []
    raw = skill_path.read_text(encoding="utf-8", errors="replace")
    for ch, name in (("\t", "TAB"), ("\x08", "BACKSPACE"), ("\x0c", "FORMFEED")):
        for i, line in enumerate(raw.splitlines(), 1):
            if ch in line:
                out.append(_fail("control_character",
                    f"{name} character at line {i} — usually a mangled LaTeX escape "
                    f"(\\t in \\theta) introduced by a non-raw string edit.",
                    {"line": i, "text": line.strip()[:90]}))
    # The spine must define every state.
    for s in rules.STATES:
        token = s.split("[")[0]
        if token not in raw:
            out.append(_fail("state_undefined_in_skill",
                f"Skill does not mention ledger state {s}.", {"state": s}))
    return out


def compute_rules_digest() -> str:
    p = HERE / "simulation_ledger_check_rules.py"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "unknown"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Acceptance checker for theory-simulation output.")
    ap.add_argument("--report", help="Path to the produced simulation report / ledger.")
    ap.add_argument("--mode", choices=["design", "audit", "hybrid"], default="audit")
    ap.add_argument("--expect", default=None, help="Fixture EXPECT.md to compare against.")
    ap.add_argument("--self-lint", dest="self_lint", default=None,
                    help="Lint a SKILL.md instead of checking a report.")
    ap.add_argument("--json-out", default=None)
    args = ap.parse_args(argv)

    try:
        findings: list[Finding] = []
        if args.self_lint:
            findings += self_lint(Path(args.self_lint).resolve())
            context = {"target": args.self_lint, "check": "self-lint"}
        else:
            if not args.report:
                print("ERROR: --report or --self-lint is required", file=sys.stderr)
                return 2
            rp = Path(args.report).resolve()
            text = rp.read_text(encoding="utf-8", errors="replace")
            rows = parse_ledger(text)
            findings += check_vocabulary(text)
            findings += check_one_row_per_claim(rows)
            findings += check_reason_codes(rows)
            findings += check_dimensions(text, args.mode)
            findings += check_audit_support(text, rows, args.mode)
            findings += check_contradiction_triage(text, rows)
            if args.expect:
                findings += check_expect(rows, Path(args.expect).resolve())
            findings.append(_review("human_judgment",
                "A script cannot judge whether an audit demanded full redesign where "
                "targeted repair would do, nor whether a dimension position is "
                "substantively adequate. Review both by hand.", {}))
            context = {"target": str(rp), "mode": args.mode, "claims": len(rows)}
        context.update({"script_version": SCRIPT_VERSION,
                        "rules_version": rules.RULES_VERSION,
                        "rules_digest": compute_rules_digest()})
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    hard = [f for f in findings if f.status == "FAIL"]
    payload = {"provenance": context,
               "findings": [asdict(f) for f in findings],
               "summary": {"FAIL": len(hard),
                           "REVIEW": sum(1 for f in findings if f.status == "REVIEW")}}
    out = json.dumps(payload, indent=2)
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(out, encoding="utf-8")
    else:
        print(out)
    return 1 if hard else 0


if __name__ == "__main__":
    sys.exit(main())
