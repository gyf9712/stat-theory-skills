"""
venue_tiers.py — venue credibility tiers. Data only, no logic.

Single source of truth for venue tiering, extracted from proof-repair Step 4B so the
same lists serve proof-repair, theory-sharpen, and the writing repo instead of drifting
across three inline copies.

Interpretation and the scoring rules live in
`../repair-literature-protocol.md`. This module holds only the lists.

Bump RULES_VERSION when any list changes.
"""

RULES_VERSION = "1.0.0"

# Tier 1 — gold standard. A single T1 citation can anchor a repair.
TIER_1 = {
    "statistics": [
        "Annals of Statistics", "AoS",
        "Journal of the American Statistical Association", "JASA",
        "Journal of the Royal Statistical Society Series B", "JRSS-B",
        "Biometrika",
    ],
    "probability": [
        "Annals of Probability",
        "Probability Theory and Related Fields",
        "Stochastic Processes and their Applications",
    ],
    "mathematics": [
        "Annals of Mathematics", "Inventiones Mathematicae",
        "Acta Mathematica", "Communications on Pure and Applied Mathematics",
    ],
    "ml_conferences": ["NeurIPS", "ICML", "ICLR", "COLT", "ALT", "AISTATS"],
    "ml_journals": ["Journal of Machine Learning Research", "JMLR", "Machine Learning"],
    "econometrics": [
        "Econometrica", "Journal of Econometrics",
        "Review of Economic Studies",
        "Journal of Business & Economic Statistics", "JBES",
    ],
    "optimization": [
        "Mathematical Programming",
        "SIAM Journal on Optimization",
        "Mathematics of Operations Research",
    ],
    "applied_numerical": [
        "SIAM Review",
        "SIAM Journal on Numerical Analysis",
        "Mathematics of Computation",
    ],
    "textbook_series": [
        "Springer Graduate Texts in Mathematics",
        "Springer Lecture Notes",
        "Cambridge Tracts",
        "Princeton Series in Applied Mathematics",
    ],
}

# Tier 2 — strong; acceptable, especially alongside a T1 reference.
TIER_2 = {
    "statistics": [
        "Electronic Journal of Statistics", "EJS", "Bernoulli",
        "Statistica Sinica", "Scandinavian Journal of Statistics",
    ],
    "ml_ai": ["AAAI", "IJCAI", "UAI", "KDD", "JAIR"],
    "mathematics": [
        "Transactions of the American Mathematical Society",
        "Journal of Functional Analysis", "Advances in Mathematics",
    ],
    "econometrics": [
        "Econometric Theory", "Journal of Applied Econometrics", "Econometric Reviews",
    ],
    "applied": [
        "IEEE Transactions on Information Theory",
        "IEEE Transactions on Signal Processing",
    ],
}

# Tier 3 — supplementary. Use only when T1/T2 unavailable; flag as lower confidence.
TIER_3 = [
    "arXiv preprint (no published version)",
    "workshop paper",
    "technical report / working paper",
    "conference outside the top tier",
]

# Tier 4 — avoid. Do not cite unless no alternative exists.
TIER_4 = [
    "unpublished manuscript with no arXiv ID",
    "blog post, lecture slides, StackExchange",
    "retracted paper",
    "predatory journal",
]

# Citation-count thresholds used by the credibility scoring table.
T1_GOLD_MIN_CITATIONS = 50
T1_STRONG_MIN_CITATIONS = 10
T3_CONDITIONAL_MIN_CITATIONS = 20
