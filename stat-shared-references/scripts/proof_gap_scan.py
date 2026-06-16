"""
proof_gap_scan.py — structural completeness linter for a proof-writer PROOF_PACKAGE.md.

It checks that the package is CLOSED, not that the mathematics is CORRECT. It
parses the Obligation Ledger and the surrounding sections and flags the cases
where the package structurally cannot support its claimed status.

Two tiers of findings:

  STRUCTURAL-INCOMPLETE  mechanical and decidable; affects the exit code. These
                         are the cases where the package contradicts itself:
                         a BLOCKED obligation under PROVABLE AS STATED, a missing
                         closure field, a weaker-with-bridge fit with no bridge,
                         an obligation that is never typed, a dependency-map
                         reference to an undefined obligation, an unverified-source
                         citation under a "Verified" package, or empty Verification
                         Checks under a provable status.

  CANDIDATE              advisory only; never affects the exit code. Heuristic
                         hedge-phrase hits in the proof body. The model reviews
                         and either discharges or justifies each.

What it deliberately does NOT do
--------------------------------
- It does not judge whether any bound, inequality, or limit is mathematically right.
- It does not verify that a cited theorem actually says what the proof claims.
- A clean lint is NOT a certificate of correctness; it certifies closure only.
  PASS-as-correctness is exactly the false authority this tool avoids.

Exit codes
----------
    0 : no STRUCTURAL-INCOMPLETE findings (package is structurally closed)
    1 : at least one STRUCTURAL-INCOMPLETE finding
    2 : invocation or runtime error

Usage
-----
    python proof_gap_scan.py --proof PROOF_PACKAGE.md \\
        --json-out audit/proof_gap_scan.json \\
        --md-out audit/PROOF_GAP_SCAN.md
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import proof_gap_scan_rules as rules  # noqa: E402

SCRIPT_VERSION = "1.0.0"

_HEADER_RE = re.compile(r"^##\s+(.*?)\s*$", re.MULTILINE)
_OBLIG_HEADER_RE = re.compile(r"^-\s*(" + rules.ID_OBLIGATION + r")\b(.*)$")
_SUBFIELD_RE = re.compile(r"^\s+-\s*([A-Za-z][\w /-]*?)\s*:\s*(.*)$")


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class Obligation:
    oid: str
    state: Optional[str]               # one of rules.CLOSURE_STATES, or None if untyped
    header: str                        # text after the id on the header line
    fields: dict = field(default_factory=dict)   # sub-field name (lower) -> value


@dataclass
class Finding:
    id: str
    status: str        # STRUCTURAL-INCOMPLETE | CANDIDATE | INFO
    message: str
    evidence: dict = field(default_factory=dict)
    fix_hint: Optional[str] = None


# ---------------------------------------------------------------------------
# Section splitting
# ---------------------------------------------------------------------------

def split_sections(text: str) -> dict:
    """Map each `## Heading` to its body text (until the next `## ` or EOF)."""
    sections = {}
    matches = list(_HEADER_RE.finditer(text))
    for i, m in enumerate(matches):
        name = m.group(1).strip().lower()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections[name] = text[start:end].strip("\n")
    return sections


def _find_section(sections: dict, *needles: str) -> Optional[str]:
    """First section whose heading contains all needles (lowercased)."""
    for name, body in sections.items():
        if all(n in name for n in needles):
            return body
    return None


def _proof_body(sections: dict) -> str:
    """The Proof section, never the 'Proof Strategy' section (a prefix collision)."""
    if "proof" in sections:
        return sections["proof"]
    for name, body in sections.items():
        if name.startswith("proof") and "strateg" not in name:
            return body
    return ""


# ---------------------------------------------------------------------------
# Parsing the package
# ---------------------------------------------------------------------------

def parse_status(sections: dict) -> tuple[Optional[str], Optional[str]]:
    body = _find_section(sections, "status")
    if body is None:
        return None, None
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    status = None
    verification = None
    for ln in lines:
        if ln.lower().startswith("verification"):
            val = ln.split(":", 1)[1].strip() if ":" in ln else ""
            # Check the longer compound labels first: "Verified" is a substring of
            # "Conditionally verified".
            for v in (rules.VERIFICATION_CONDITIONAL, rules.VERIFICATION_GAP,
                      rules.VERIFICATION_VERIFIED):
                if v.lower() in val.lower():
                    verification = v
                    break
        elif status is None:
            # Resolve the chosen STATUS from the first non-verification line.
            if rules.STATUS_NOT_JUSTIFIED in ln:
                status = rules.STATUS_NOT_JUSTIFIED
            elif rules.STATUS_WEAKEN in ln:
                status = rules.STATUS_WEAKEN
            elif rules.STATUS_PROVABLE in ln:
                status = rules.STATUS_PROVABLE
    return status, verification


def parse_obligations(sections: dict) -> tuple[list[Obligation], bool]:
    """Return (obligations, ledger_present)."""
    body = _find_section(sections, "obligation", "ledger")
    if body is None:
        return [], False
    obligations: list[Obligation] = []
    current: Optional[Obligation] = None
    for line in body.splitlines():
        m = _OBLIG_HEADER_RE.match(line)
        if m:
            header = m.group(2)
            state = next((s for s in rules.CLOSURE_STATES if s in header), None)
            current = Obligation(oid=m.group(1), state=state, header=header.strip())
            # A "closed at" pointer may sit inline on the header for CLOSED-LOCAL.
            inline = re.search(r"closed at\s*:", header, re.I)
            if inline:
                current.fields["closed at"] = header[inline.end():].strip()
            obligations.append(current)
            continue
        sm = _SUBFIELD_RE.match(line)
        if sm and current is not None:
            current.fields[sm.group(1).strip().lower()] = sm.group(2).strip()
    return obligations, True


# ---------------------------------------------------------------------------
# Checks (STRUCTURAL-INCOMPLETE = hard, CANDIDATE = advisory)
# ---------------------------------------------------------------------------

def _struct(fid, message, evidence=None, fix=None) -> Finding:
    return Finding(fid, "STRUCTURAL-INCOMPLETE", message, evidence or {}, fix)


def check_obligations(obligations, status) -> list[Finding]:
    findings = []
    provable = status in (rules.STATUS_PROVABLE, rules.STATUS_WEAKEN)
    for ob in obligations:
        # Untyped obligation: never terminated.
        if ob.state is None:
            findings.append(_struct(
                "obligation_untyped",
                f"Obligation {ob.oid} is listed but never terminated in a typed state "
                f"({'/'.join(rules.CLOSURE_STATES)}).",
                {"obligation": ob.oid, "header": ob.header},
                "Close it as CLOSED-LOCAL or CLOSED-CITED, or mark it BLOCKED with an attack record.",
            ))
            continue
        # BLOCKED under a provable status: contradiction.
        if ob.state == "BLOCKED" and status == rules.STATUS_PROVABLE:
            findings.append(_struct(
                "blocked_under_provable",
                f"Obligation {ob.oid} is BLOCKED but the package claims {rules.STATUS_PROVABLE}.",
                {"obligation": ob.oid},
                "Downgrade to PROVABLE AFTER WEAKENING or NOT CURRENTLY JUSTIFIED, or close the obligation.",
            ))
        # Missing required closure fields.
        for fld in rules.REQUIRED_FIELDS.get(ob.state, []):
            if fld not in ob.fields or not ob.fields[fld]:
                findings.append(_struct(
                    "missing_closure_field",
                    f"Obligation {ob.oid} ({ob.state}) is missing required field '{fld}'.",
                    {"obligation": ob.oid, "state": ob.state, "missing_field": fld},
                    f"Add the '{fld}' field; a typed closure is not valid without it.",
                ))
        # weaker-with-bridge requires a named bridge.
        if ob.state == "CLOSED-CITED":
            fit = ob.fields.get("conclusion fit", "")
            if rules.FIT_REQUIRING_BRIDGE in fit:
                bref = ob.fields.get("bridge ref", "")
                if not re.search(rules.ID_BRIDGE, bref):
                    findings.append(_struct(
                        "bridge_missing",
                        f"Obligation {ob.oid} has conclusion fit '{rules.FIT_REQUIRING_BRIDGE}' "
                        f"but names no bridge (B-id) in 'bridge ref'.",
                        {"obligation": ob.oid, "bridge ref": bref},
                        "Name the bridge derivation (e.g. B1) and define it in the Proof.",
                    ))
    return findings


def check_bridges_defined(obligations, sections) -> list[Finding]:
    """Every bridge referenced by a weaker-with-bridge obligation must appear in the Proof."""
    proof_body = _proof_body(sections)
    defined = set(re.findall(rules.ID_BRIDGE, proof_body))
    findings = []
    for ob in obligations:
        if ob.state == "CLOSED-CITED" and rules.FIT_REQUIRING_BRIDGE in ob.fields.get("conclusion fit", ""):
            for bid in re.findall(rules.ID_BRIDGE, ob.fields.get("bridge ref", "")):
                if bid not in defined:
                    findings.append(_struct(
                        "bridge_undefined",
                        f"Obligation {ob.oid} references bridge {bid}, but {bid} is never "
                        f"defined in the Proof.",
                        {"obligation": ob.oid, "bridge": bid},
                        f"Define {bid} in the Proof body or correct the bridge ref.",
                    ))
    return findings


def check_dependency_refs(obligations, sections) -> list[Finding]:
    """O-ids referenced in the Dependency Map must be defined in the ledger."""
    dep_body = _find_section(sections, "dependency", "map")
    if dep_body is None:
        return []
    defined = {ob.oid for ob in obligations}
    referenced = set(re.findall(rules.ID_OBLIGATION, dep_body))
    findings = []
    for oid in sorted(referenced - defined, key=lambda s: int(s[1:])):
        findings.append(_struct(
            "undefined_obligation_ref",
            f"The Dependency Map references {oid}, but no such obligation is defined "
            f"in the Obligation Ledger.",
            {"obligation": oid},
            f"Add {oid} to the ledger or fix the reference.",
        ))
    return findings


def check_status_verification(obligations, status, verification, sections) -> list[Finding]:
    findings = []
    provable = status in (rules.STATUS_PROVABLE, rules.STATUS_WEAKEN)
    # Unverified-source citation must not coexist with a "Verified" package.
    has_unverified = any(
        ob.state == "CLOSED-CITED"
        and rules.SOURCE_STATUS_UNVERIFIED in ob.fields.get("source-status", "")
        for ob in obligations
    )
    if has_unverified and verification == rules.VERIFICATION_VERIFIED:
        findings.append(_struct(
            "verification_overclaim",
            "A load-bearing CLOSED-CITED obligation carries source-status "
            "'unverified-source', so the package cannot be 'Verified'.",
            {"required_verification": rules.VERIFICATION_CONDITIONAL},
            "Set Verification to 'Conditionally verified' until proofcheck/proof-repair inspects the source.",
        ))
    # Provable packages must carry non-empty Verification Checks.
    if status == rules.STATUS_PROVABLE:
        checks = _find_section(sections, "verification", "checks")
        if not checks or not checks.strip():
            findings.append(_struct(
                "verification_checks_blank",
                "Status is PROVABLE AS STATED but the Verification Checks section is missing or empty.",
                {},
                "Record one pass/NA line per Trap Catalogue item.",
            ))
    return findings


def check_ledger_present(ledger_present, obligations, status) -> list[Finding]:
    findings = []
    if status in (rules.STATUS_PROVABLE, rules.STATUS_WEAKEN):
        if not ledger_present:
            findings.append(_struct(
                "ledger_missing",
                "A provable package has no Obligation Ledger section.",
                {},
                "Add the Obligation Ledger; every nontrivial step must be a typed obligation.",
            ))
        elif not obligations:
            findings.append(Finding(
                "ledger_empty", "CANDIDATE",
                "The Obligation Ledger is present but lists no obligations. Confirm the "
                "proof genuinely raises no nontrivial obligation.",
                {}, "If the proof leans on any inequality, mode conversion, or import, list it.",
            ))
    return findings


def check_hedges(sections) -> list[Finding]:
    """Advisory: hedge phrases in the proof body."""
    proof_body = _proof_body(sections)
    if not proof_body:
        return []
    findings = []
    low = proof_body.lower()
    for phrase in rules.HEDGE_PHRASES:
        idx = low.find(phrase)
        if idx != -1:
            snippet = proof_body[max(0, idx - 30): idx + len(phrase) + 30].replace("\n", " ")
            findings.append(Finding(
                "hedge_phrase", "CANDIDATE",
                f"Possible gap-hiding phrase in the Proof: '{phrase}'.",
                {"phrase": phrase, "context": snippet.strip()},
                "Replace with an explicit derivation, a CLOSED-CITED obligation, or remove.",
            ))
    return findings


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def compute_rules_digest() -> str:
    p = HERE / "proof_gap_scan_rules.py"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "unknown"


def run_scan(args) -> tuple[list[Finding], dict]:
    proof_path = Path(args.proof).resolve()
    if not proof_path.exists():
        raise FileNotFoundError(f"Proof package not found: {proof_path}")
    text = proof_path.read_text(encoding="utf-8", errors="replace")
    sections = split_sections(text)

    status, verification = parse_status(sections)
    obligations, ledger_present = parse_obligations(sections)

    findings: list[Finding] = []
    findings += check_ledger_present(ledger_present, obligations, status)
    findings += check_obligations(obligations, status)
    findings += check_bridges_defined(obligations, sections)
    findings += check_dependency_refs(obligations, sections)
    findings += check_status_verification(obligations, status, verification, sections)
    findings += check_hedges(sections)

    context = {
        "script_version": SCRIPT_VERSION,
        "rules_version": rules.RULES_VERSION,
        "rules_digest": compute_rules_digest(),
        "status": status or "(unparsed)",
        "verification": verification or "(unparsed)",
        "obligation_count": len(obligations),
        "blocked_count": sum(1 for o in obligations if o.state == "BLOCKED"),
    }
    return findings, context


def _summarize(findings) -> dict:
    out = {"STRUCTURAL-INCOMPLETE": 0, "CANDIDATE": 0, "INFO": 0}
    for f in findings:
        out[f.status] = out.get(f.status, 0) + 1
    return out


def render_json(findings, context) -> str:
    return json.dumps({
        "provenance": context,
        "findings": [asdict(f) for f in findings],
        "summary": _summarize(findings),
    }, indent=2)


def render_markdown(findings, context) -> str:
    s = _summarize(findings)
    lines = ["# Proof Gap Scan", ""]
    lines.append(f"- Script version: `{context['script_version']}`")
    lines.append(f"- Rules version: `{context['rules_version']}`")
    lines.append(f"- Rules digest: `{context['rules_digest']}`")
    lines.append(f"- Parsed status: `{context['status']}` / verification `{context['verification']}`")
    lines.append(f"- Obligations: {context['obligation_count']} (BLOCKED: {context['blocked_count']})")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- STRUCTURAL-INCOMPLETE (blocks provable status): {s['STRUCTURAL-INCOMPLETE']}")
    lines.append(f"- CANDIDATE (advisory, review): {s['CANDIDATE']}")
    lines.append("")
    lines.append("> This linter checks closure, not correctness. A clean scan does not "
                 "certify the mathematics.")
    lines.append("")
    if findings:
        lines.append("## Findings")
        lines.append("")
        for f in findings:
            lines.append(f"### `{f.id}` [{f.status}]")
            lines.append("")
            lines.append(f.message)
            if f.evidence:
                lines.append("")
                for k, v in f.evidence.items():
                    lines.append(f"- `{k}`: {v}")
            if f.fix_hint:
                lines.append("")
                lines.append(f"Fix: {f.fix_hint}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Structural completeness linter for a PROOF_PACKAGE.md.")
    parser.add_argument("--proof", required=True, help="Path to the proof package markdown.")
    parser.add_argument("--json-out", default=None)
    parser.add_argument("--md-out", default=None)
    args = parser.parse_args(argv)

    try:
        findings, context = run_scan(args)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    md = render_markdown(findings, context)
    if args.md_out:
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md_out).write_text(md, encoding="utf-8")
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(render_json(findings, context), encoding="utf-8")
    if not args.md_out and not args.json_out:
        print(md)

    structural = sum(1 for f in findings if f.status == "STRUCTURAL-INCOMPLETE")
    return 1 if structural else 0


if __name__ == "__main__":
    sys.exit(main())
