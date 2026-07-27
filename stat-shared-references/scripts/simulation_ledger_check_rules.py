"""
Rule data for simulation_ledger_check.py. Data only.

Encodes the acceptance contract for theory-simulation's Claim Evidence Ledger,
per the Codex acceptance-test design (threadId 019fa456-c827-7103-9bcc-0a2af1803240).

Bump RULES_VERSION when the vocabulary or the dimension list changes.
"""

import re

RULES_VERSION = "1.0.0"

# The ONLY admissible ledger states. A state outside this set is a "third
# vocabulary" regression — the exact failure this ledger was unified to prevent.
STATES = [
    "PLANNED",
    "YES[strong]",
    "YES[weak]",
    "PARTIAL",          # carries reason codes: PARTIAL[grid,precision]
    "NO",
    "CONTRADICTED",     # carries a code: CONTRADICTED[metric]
    "HYPOTHESIS-ONLY",
]

# NOTE: a trailing \b must NOT be applied after "]" — "]" is a non-word character, so
# \b there requires a following word character and the bracketed states never match.
# Word-boundary anchoring is applied per-alternative instead.
STATE_RE = re.compile(
    r"\b(PLANNED\b|YES\[(?:strong|weak)\]|PARTIAL\[[^\]]*\]"
    r"|CONTRADICTED\[[^\]]*\]|HYPOTHESIS-ONLY\b|NO\b)"
)

# The historical pre-unification vocabulary for CLAIM STATUS. Unambiguous as a
# status label, so it is flagged anywhere in the document.
BANNED_VOCAB = [
    r"\bOPEN HYPOTHESIS\b",
    r"\bHYPOTHESIS CONFIRMED\b",
]

# Tokens that are legitimate words in general (a per-criterion verdict inside an
# audit table is SUPPOSED to say PASS / FAIL) but are NOT admissible as a claim's
# ledger state. These are only flagged inside a ledger row — i.e. a table row that
# names a claim but carries no approved state. Flagging them document-wide is a
# false positive: it fires on the skill's own "| Criterion | Status |" contract.
BANNED_AS_STATE = [
    "PASS", "FAIL", "VERIFIED", "CONFIRMED", "COVERED", "UNCOVERED",
    "OK", "GOOD", "BAD", "WEAK", "STRONG",
]

# The five adequacy dimensions, mode-neutral. DESIGN must state a position on all
# applicable ones; AUDIT must support any YES[*] with them.
DIMENSIONS = {
    "truth":         [r"truth[- ]source", r"\btruth\b", r"estimand"],
    "selection":     [r"selection", r"omitted", r"selective report"],
    "tuning":        [r"tuning", r"oracle", r"data-driven"],
    "computational": [r"computational", r"runtime", r"memory", r"scaling"],
    "reuse":         [r"reuse", r"replicate-level", r"RNG stream"],
}

# Reuse legitimacy only applies when existing runs are reused (AUDIT/HYBRID).
DIMENSIONS_DESIGN_REQUIRED = ["truth", "selection", "tuning", "computational"]

PRIORITIES = ["PRIMARY", "SECONDARY", "PERIPHERAL"]

# A claim row must name a claim id and a state.
CLAIM_ID_RE = re.compile(r"\b((?:Thm|Theorem|Lem|Lemma|Prop|Proposition|Cor|Corollary|C)\s?\.?\s?\d+[a-z]?)\b", re.I)

# Reason codes admissible inside PARTIAL[...] / CONTRADICTED[...]
REASON_CODES = [
    "path", "metric", "precision", "grid", "comparator",
    "reporting", "stress-coverage", "identification-mismatch",
]

# CONTRADICTED must be accompanied by evidence that triage ran before any
# theorem-failure conclusion.
TRIAGE_MARKERS = [r"replicat", r"seed", r"triage", r"rerun", r"implementation", r"bug"]
THEOREM_FAILURE_MARKERS = [r"theorem is (?:wrong|false)", r"theorem fails", r"result is wrong"]
