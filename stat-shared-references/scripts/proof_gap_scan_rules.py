"""
Rule data for proof_gap_scan.py. Data only, no logic.

Bump RULES_VERSION when any value here changes. proof_gap_scan.py stamps the
sha256 of this file into every report for provenance.
"""

RULES_VERSION = "1.0.0"

# --- Status vocabulary (must match proof-writer SKILL.md and proof-closure-machinery.md) ---

STATUS_PROVABLE = "PROVABLE AS STATED"
STATUS_WEAKEN = "AFTER WEAKENING"          # substring of "PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION"
STATUS_NOT_JUSTIFIED = "NOT CURRENTLY JUSTIFIED"

VERIFICATION_VERIFIED = "Verified"
VERIFICATION_CONDITIONAL = "Conditionally verified"
VERIFICATION_GAP = "Gap found"

# --- Obligation closure typing ---

# The three typed states an obligation may terminate in.
CLOSURE_STATES = ["CLOSED-LOCAL", "CLOSED-CITED", "BLOCKED"]

# Required sub-fields per state. Missing any is STRUCTURAL-INCOMPLETE.
# (CLOSED-LOCAL's "closed at" may sit inline on the header line; the others are sub-bullets.)
REQUIRED_FIELDS = {
    "CLOSED-LOCAL": ["closed at"],
    "CLOSED-CITED": ["clause used", "assumption map", "conclusion fit", "source-status"],
    "BLOCKED": ["statement", "bridge attempted", "failure reason", "alternative considered"],
}

# Allowed values for the typed fields.
CONCLUSION_FITS = ["exact", "stronger than needed", "weaker-with-bridge"]
SOURCE_STATUSES = ["checked-now", "local-excerpt", "unverified-source"]

# The conclusion-fit value that obligates a bridge derivation.
FIT_REQUIRING_BRIDGE = "weaker-with-bridge"

# source-status value that downgrades a provable package to Conditionally verified.
SOURCE_STATUS_UNVERIFIED = "unverified-source"

# --- Advisory only (CANDIDATE; never affects exit code, brittle by nature) ---

# Gap-hiding tells. A hit in the Proof body is advisory: it may be a legitimate use
# or live inside a quotation, so it never hard-fails.
HEDGE_PHRASES = [
    "clearly",
    "obviously",
    "it can be shown",
    "it can easily be shown",
    "by standard arguments",
    "by a standard argument",
    "the rest is similar",
    "the rest is routine",
    "we omit the details",
    "details are routine",
    "it is easy to see",
    "it follows immediately",
    "trivially",
]

# Canonical ID patterns. Obligations are defined in the ledger, bridges in the proof.
ID_OBLIGATION = r"O\d+"
ID_BRIDGE = r"B\d+"
ID_LEMMA = r"L\d+"
