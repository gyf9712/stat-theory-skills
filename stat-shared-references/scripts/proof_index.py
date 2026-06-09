"""
proof_index.py — mechanical proof-architecture indexer for statistics papers.

Replaces the bash/grep indexing prose in proofcheck Step 1 (Bootstrap) and
Pass 0 (Indexing). Purely mechanical: it builds the inventory and the
dependency graph that the human/model then reasons over. It makes no
judgment about proof correctness.

What it produces
----------------
- Reference-mode detection (single-file vs two-file submission).
- Theorem-like-environment inventory (theorem, lemma, proposition,
  corollary, definition, assumption, remark) with label and line number.
- Dependency edges: for each environment's proof block, the \\ref targets
  it cites that resolve to another indexed environment.
- Topological layers (Kahn's algorithm) giving a valid check order, with
  cycle detection.
- Cross-reference integrity: \\ref targets with no \\label, and the
  cross-file leak case under separate-self-contained submission.

What it does NOT do
-------------------
- It does not verify any proof.
- It does not classify proof strategy (that is judgment).
- It does not decide severity.

All findings are mechanical. There are no heuristic findings in v1, so the
exit code is purely structural:

    0 : indexed cleanly, no structural FAIL (no cycle, no undefined ref)
    1 : at least one structural FAIL (dependency cycle or undefined ref)
    2 : invocation or runtime error

Usage
-----
    python proof_index.py --main paper.tex \\
        --supplement supplement.tex \\
        --supplement-mode separate-self-contained \\
        --json-out audit/proof_index.json \\
        --md-out audit/PROOF_INDEX.md
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
import proof_index_rules as rules  # noqa: E402

SCRIPT_VERSION = "1.0.0"

_COMMENT_RE = re.compile(r"(?<!\\)%.*?$", re.MULTILINE)
_INPUT_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")


# ---------------------------------------------------------------------------
# Source reading (follows \input / \include)
# ---------------------------------------------------------------------------

def read_tex_source(path: Path, _seen: Optional[set] = None) -> str:
    if _seen is None:
        _seen = set()
    if not path.exists():
        return ""
    resolved = path.resolve()
    if resolved in _seen:
        return ""
    _seen.add(resolved)
    text = _COMMENT_RE.sub("", path.read_text(encoding="utf-8", errors="replace"))

    def _resolve(m: re.Match) -> str:
        name = m.group(1).strip()
        cands = [path.parent / name]
        if not name.endswith(".tex"):
            cands.append(path.parent / (name + ".tex"))
        for c in cands:
            if c.exists():
                return "\n" + read_tex_source(c, _seen) + "\n"
        return ""

    return _INPUT_RE.sub(_resolve, text)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ProofUnit:
    env_type: str          # theorem, lemma, ...
    label: Optional[str]   # \label{...} inside the environment, if any
    line: int
    summary: str           # first ~80 chars of the statement
    depends_on: list = field(default_factory=list)  # labels this unit's proof \ref's


@dataclass
class Finding:
    id: str
    kind: str       # always "mechanical" in v1
    status: str     # PASS | FAIL | WARN | INFO
    severity: str   # CRITICAL | HIGH | MEDIUM | LOW
    message: str
    evidence: dict = field(default_factory=dict)
    fix_hint: Optional[str] = None


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def detect_reference_mode(main_path: Path, supplement_path: Optional[Path]) -> str:
    if supplement_path is not None and supplement_path.exists():
        return "two-file"
    # Heuristic: sibling supplement-like files present.
    sibs = list(main_path.parent.glob("*.tex"))
    supp_like = [s for s in sibs if re.search(r"(supp|supplement|appendix|^SI)", s.stem, re.I)]
    return "two-file" if supp_like else "single-file"


def index_environments(source: str, source_name: str) -> list[ProofUnit]:
    """Find theorem-like environments and their labels, line numbers, summaries."""
    units = []
    env_alt = "|".join(rules.THEOREM_ENVIRONMENTS)
    begin_re = re.compile(r"\\begin\{(" + env_alt + r")\}(.*?)\\end\{\1\}", re.DOTALL)
    for m in begin_re.finditer(source):
        env_type = m.group(1)
        body = m.group(2)
        line = source[: m.start()].count("\n") + 1
        label_m = re.search(r"\\label\{([^}]+)\}", body)
        label = label_m.group(1) if label_m else None
        # Summary: strip the label and leading whitespace, take first 80 chars.
        summary_src = re.sub(r"\\label\{[^}]+\}", "", body).strip()
        summary_src = re.sub(r"\s+", " ", summary_src)
        summary = summary_src[:80]
        units.append(ProofUnit(env_type=env_type, label=label, line=line, summary=summary))
    return units


def all_labels(source: str) -> set[str]:
    return {m.group(1) for m in re.finditer(r"\\label\{([^}]+)\}", source)}


def proof_block_dependencies(source: str, known_labels: set[str]) -> dict[int, list[str]]:
    """Map the start line of each proof block to the indexed labels it \\ref's.

    A 'proof block' is a \\begin{proof}...\\end{proof}. We attribute its
    \\ref targets to the nearest preceding theorem-like environment via line
    proximity in the caller.
    """
    out = {}
    proof_re = re.compile(r"\\begin\{proof\}(.*?)\\end\{proof\}", re.DOTALL)
    for m in proof_re.finditer(source):
        block = m.group(1)
        line = source[: m.start()].count("\n") + 1
        refs = []
        for rm in re.finditer(r"\\(?:eq|c|C|auto|name)?ref\{([^}]+)\}", block):
            for key in rm.group(1).split(","):
                key = key.strip()
                if key in known_labels:
                    refs.append(key)
        out[line] = sorted(set(refs))
    return out


def attribute_dependencies(units: list[ProofUnit], proof_deps: dict[int, list[str]]) -> None:
    """Attach each proof block's deps to the nearest preceding indexed unit.

    Mutates units in place. A proof block at line L belongs to the unit with
    the greatest start line <= L (the theorem it proves usually precedes its
    proof).
    """
    unit_lines = sorted((u.line, idx) for idx, u in enumerate(units))
    for proof_line, deps in proof_deps.items():
        owner_idx = None
        for uline, idx in unit_lines:
            if uline <= proof_line:
                owner_idx = idx
            else:
                break
        if owner_idx is not None:
            # Do not let a unit depend on itself.
            own_label = units[owner_idx].label
            units[owner_idx].depends_on = sorted(
                set(units[owner_idx].depends_on) | {d for d in deps if d != own_label}
            )


# ---------------------------------------------------------------------------
# Topological layering (Kahn) with cycle detection
# ---------------------------------------------------------------------------

def topological_layers(units: list[ProofUnit]) -> tuple[list[list[str]], list[str]]:
    """Return (layers, cycle_labels).

    layers[k] is the list of labels whose dependencies are all in layers < k.
    cycle_labels is non-empty if a dependency cycle is detected.
    Only labels that are themselves indexed units participate.
    """
    label_to_deps = {}
    for u in units:
        if u.label:
            label_to_deps[u.label] = [d for d in u.depends_on if d != u.label]
    # Restrict deps to labels that are indexed units (ignore refs to equations etc.).
    indexed = set(label_to_deps.keys())
    for lab in label_to_deps:
        label_to_deps[lab] = [d for d in label_to_deps[lab] if d in indexed]

    remaining = dict(label_to_deps)
    layers = []
    placed: set[str] = set()
    while remaining:
        ready = [lab for lab, deps in remaining.items() if all(d in placed for d in deps)]
        if not ready:
            # Cycle: whatever remains is involved in or downstream of a cycle.
            return layers, sorted(remaining.keys())
        ready.sort()
        layers.append(ready)
        for lab in ready:
            placed.add(lab)
            del remaining[lab]
    return layers, []


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_undefined_refs(
    main_source: str,
    supplement_source: str,
    supplement_mode: str,
) -> list[Finding]:
    findings = []
    main_labels = all_labels(main_source)
    supp_labels = all_labels(supplement_source) if supplement_source else set()

    def _scan(src: str, src_name: str, own_labels: set[str], other_labels: set[str]):
        for m in re.finditer(r"\\(?:eq|c|C|auto|name)?ref\{([^}]+)\}", src):
            target = m.group(1)
            if "," in target:
                continue
            line = src[: m.start()].count("\n") + 1
            if target in own_labels:
                continue
            if target in other_labels:
                if supplement_mode == "separate-self-contained":
                    findings.append(Finding(
                        id="cross_file_ref_leak",
                        kind="mechanical", status="FAIL", severity="HIGH",
                        message=(f"{src_name} \\ref{{{target}}} resolves only via the other "
                                 f"file; under separate-self-contained this is '??' on "
                                 f"standalone compile."),
                        evidence={"file": src_name, "line": line, "target": target},
                        fix_hint="Use a textual reference (e.g., 'Theorem 1 of the main paper').",
                    ))
                continue
            findings.append(Finding(
                id="undefined_ref",
                kind="mechanical", status="FAIL", severity="HIGH",
                message=f"{src_name} \\ref{{{target}}} has no matching \\label.",
                evidence={"file": src_name, "line": line, "target": target},
                fix_hint="Add the \\label or correct the \\ref key.",
            ))

    _scan(main_source, "main", main_labels, supp_labels)
    if supplement_source:
        _scan(supplement_source, "supplement", supp_labels, main_labels)
    return findings


def check_cycle(cycle_labels: list[str]) -> list[Finding]:
    if not cycle_labels:
        return []
    return [Finding(
        id="dependency_cycle",
        kind="mechanical", status="FAIL", severity="CRITICAL",
        message=("A dependency cycle was detected among proof units; the proof "
                 "order is not well-founded."),
        evidence={"units_in_or_below_cycle": cycle_labels},
        fix_hint="Break the circular dependency; one of these proofs must not rely on another.",
    )]


def check_unlabeled_units(units: list[ProofUnit]) -> list[Finding]:
    findings = []
    for u in units:
        if u.label is None:
            findings.append(Finding(
                id="unlabeled_environment",
                kind="mechanical", status="WARN", severity="LOW",
                message=f"{u.env_type} at line {u.line} has no \\label; it cannot be a dependency target.",
                evidence={"env_type": u.env_type, "line": u.line, "summary": u.summary},
                fix_hint="Add a \\label if other results cite this one.",
            ))
    return findings


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def render_json(units, layers, findings, context) -> str:
    return json.dumps({
        "provenance": context,
        "reference_mode": context["reference_mode"],
        "inventory": [asdict(u) for u in units],
        "topological_layers": layers,
        "findings": [asdict(f) for f in findings],
        "summary": _summarize(findings),
    }, indent=2)


def render_markdown(units, layers, findings, context) -> str:
    lines = ["# Proof Index", ""]
    lines.append(f"- Script version: `{context['script_version']}`")
    lines.append(f"- Rules version: `{context['rules_version']}`")
    lines.append(f"- Rules digest: `{context['rules_digest']}`")
    lines.append(f"- Reference mode: `{context['reference_mode']}`")
    lines.append(f"- Supplement mode: `{context['supplement_mode']}`")
    lines.append("")
    s = _summarize(findings)
    lines.append("## Summary")
    lines.append(f"- Indexed units: {len(units)}")
    lines.append(f"- Mechanical FAIL: {s['FAIL']}")
    lines.append(f"- Mechanical WARN: {s['WARN']}")
    lines.append(f"- Topological layers: {len(layers)}")
    lines.append("")
    lines.append("## Proof Unit Inventory")
    lines.append("")
    lines.append("| Type | Label | Line | Depends on | Summary |")
    lines.append("|---|---|---|---|---|")
    for u in units:
        deps = ", ".join(u.depends_on) if u.depends_on else "—"
        label = u.label or "(unlabeled)"
        lines.append(f"| {u.env_type} | `{label}` | {u.line} | {deps} | {u.summary} |")
    lines.append("")
    lines.append("## Suggested Check Order (topological layers)")
    lines.append("")
    if layers:
        for k, layer in enumerate(layers):
            lines.append(f"- Layer {k}: {', '.join('`'+l+'`' for l in layer)}")
    else:
        lines.append("- (no labeled inter-unit dependencies found)")
    lines.append("")
    if findings:
        lines.append("## Findings")
        lines.append("")
        for f in findings:
            lines.append(f"### `{f.id}` [{f.status} / {f.severity}]")
            lines.append("")
            lines.append(f.message)
            if f.evidence:
                lines.append("")
                for k, v in f.evidence.items():
                    lines.append(f"- `{k}`: `{v}`")
            if f.fix_hint:
                lines.append("")
                lines.append(f"Fix: {f.fix_hint}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _summarize(findings) -> dict:
    out = {"PASS": 0, "FAIL": 0, "WARN": 0, "INFO": 0}
    for f in findings:
        out[f.status] = out.get(f.status, 0) + 1
    return out


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

def compute_rules_digest() -> str:
    p = HERE / "proof_index_rules.py"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "unknown"


def run_index(args) -> tuple[list, list, list, dict]:
    main_path = Path(args.main).resolve()
    if not main_path.exists():
        raise FileNotFoundError(f"Main file not found: {main_path}")
    main_source = read_tex_source(main_path)
    supplement_path = Path(args.supplement).resolve() if args.supplement else None
    supplement_source = read_tex_source(supplement_path) if supplement_path else ""

    ref_mode = detect_reference_mode(main_path, supplement_path)

    units = index_environments(main_source, "main")
    if supplement_source:
        units += index_environments(supplement_source, "supplement")

    combined = main_source + "\n" + supplement_source
    known = all_labels(combined)
    proof_deps = proof_block_dependencies(combined, known)
    attribute_dependencies(units, proof_deps)

    layers, cycle = topological_layers(units)

    findings = []
    findings += check_undefined_refs(main_source, supplement_source, args.supplement_mode)
    findings += check_cycle(cycle)
    findings += check_unlabeled_units(units)

    context = {
        "script_version": SCRIPT_VERSION,
        "rules_version": rules.RULES_VERSION,
        "rules_digest": compute_rules_digest(),
        "reference_mode": ref_mode,
        "supplement_mode": args.supplement_mode,
        "main": str(main_path),
        "supplement": str(supplement_path) if supplement_path else None,
    }
    return units, layers, findings, context


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Mechanical proof-architecture indexer.")
    p.add_argument("--main", required=True)
    p.add_argument("--supplement", default=None)
    p.add_argument("--supplement-mode",
                   choices=["separate-self-contained", "linked-appendix", "none"],
                   default="none")
    p.add_argument("--json-out", default=None)
    p.add_argument("--md-out", default=None)
    args = p.parse_args(argv)

    try:
        units, layers, findings, context = run_index(args)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"ERROR: unexpected: {e}", file=sys.stderr)
        return 2

    json_payload = render_json(units, layers, findings, context)
    md_payload = render_markdown(units, layers, findings, context)

    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json_payload, encoding="utf-8")
    if args.md_out:
        Path(args.md_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.md_out).write_text(md_payload, encoding="utf-8")
    if not args.json_out and not args.md_out:
        print(json_payload)

    return 1 if any(f.status == "FAIL" for f in findings) else 0


if __name__ == "__main__":
    sys.exit(main())
