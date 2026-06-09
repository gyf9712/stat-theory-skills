"""
proof_index_rules.py — data for proof_index.py.

Data only. Bump RULES_VERSION (semver) when behavior changes; proof_index.py
emits an automatic rules_digest alongside it to pin provenance.
"""

RULES_VERSION = "1.0.0"

# Theorem-like environments to inventory. Order does not matter; matching is
# by exact environment name. Extend this list to index custom environments,
# but keep it to genuine claim-bearing environments (not "proof", "remark"
# is included because it can carry a label others cite).
THEOREM_ENVIRONMENTS = [
    "theorem",
    "lemma",
    "proposition",
    "corollary",
    "definition",
    "assumption",
    "condition",
    "remark",
    "claim",
    "fact",
]
