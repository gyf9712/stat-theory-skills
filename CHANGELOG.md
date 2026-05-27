# Changelog

## v1.1.1 — theory-simulation: Codex-reviewed rigor pass

Codex GPT acted as an adversarial AoS/JASA/JRSS-B referee on the theory-simulation
skill and identified 20 issues. After discussion, 13 were accepted outright, 6 were
refined via pushback (Codex agreed), and 1 was pushed back (Codex held firm — accepted).
A second round caught 4 remaining MAJOR gaps. All 23 final findings now addressed.

### Major upgrades in theory-simulation (687 → 1001 lines)

**Statistical correctness**
- Rate protocol now declares loss object (norm vs MSE → slope `-a` vs `-2a`)
- Asymptotic path must be declared and held fixed (`s log d / n` etc.)
- Slope verified via weighted regression + local slopes + normalized-loss leveling
- B selected by MCSE target per metric (no fixed thresholds)
- Per-metric MCSE formulas (binomial / delta / bootstrap / paired)

**Inference diagnostics (was missing — biggest hole)**
- Now required: coverage + size + local power + interval length + EmpSE vs ModSE +
  bias-eliminated coverage
- Wilson/Jeffreys intervals for coverage, not arbitrary ±0.02 bands

**Design discipline (ADEMP + claim-based)**
- "One experiment per theorem" replaced with ADEMP block per empirical claim
- Stress tests in two layers: one-at-a-time (diagnostic) + factorial (robustness claim)
- DGP candidates carry mismatch warnings (t_3 finite variance, AR(1) short memory etc.)
- Theorem-matched least-favorable DGPs required
- Paired-replicate method comparison is NOW DEFAULT (was misclassified as STRICT-tier)

**Conditional diagnostics (mandatory if claim exists)**
- Oracle vs data-driven tuning gap
- Variability over tuning randomness (CV folds, random init)
- Runtime/memory scaling along asymptotic path (if scalability claimed)

**Anti-cherry-picking discipline**
- Preregister primary cells + primary summaries before running
- MCSE-relative deviation thresholds
- Anti-narration rule: no general conclusions from one-off cells

**Reproducibility (tiered, target-aware)**
- BASIC / STRICT (default) / PUBLICATION
- Declare reproducibility target: bitwise identical vs statistically equivalent
- Hierarchical RNG (SeedSequence / L'Ecuyer-CMRG), per-rep state stored
- Thread env vars + BLAS lib version recorded
- Code architecture: manifest-driven, immutable cell_id, replicate-level Parquet/JSON,
  reproduce script, regression tests on toy DGPs

**Failure handling (was missing)**
- Per-rep status field (success/nonconvergence/singular/empty/negative_var/timeout)
- Per-cell failure rate reported
- Default alerts >5% / >20% reframed as context-dependent (regime severity)

**Figure rules split**
- Actual journal requirements (alt text, color-redundant encoding, final-size legibility)
- vs stat-paper house style (no title, Okabe-Ito, in-panel labels)
- "NO title" softened to "usually omitted in stat journals" (convention, not rule)
- Figure types CONDITIONAL on claim (rate → log-log, CI → coverage, test → size/power)
- MC uncertainty required on every figure (error bars or bands)

**Reconciliation discipline (no overclaiming)**
- Findings split: EVIDENCE (can update paper) vs HYPOTHESIS (needs analytic follow-up)
- Asymmetry rule: sim can support keeping assumptions (via failure) but cannot prove dropping
- "Worked at t_5" → hypothesis only; needs adversarial expansion + proof before paper claim

**Edge cases**
- Rare events: importance sampling or scale B to ≥10/p_target
- Randomized algorithms: nested RNG layer
- No closed-form truth: HIGH-B benchmark for ground-truth estimate
- Long-running estimators: time budgets, checkpointing
- Adaptive/sequential procedures: data + algorithm randomness both seeded

**Codex cross-review (still optional but improved)**
- Pre-run plan review + post-run figure/reconciliation review
- Catches overclaim, suspicious results, missing context

References cited: Morris, White & Crowther (2019, Stat Med); Koehler, Brown &
Haneuse (2009, Am Stat); Brown, Cai & DasGupta (2001, Stat Sci); JASA
Reproducibility Editorial (2024); Andrews & Cheng (2012, Econometrica).

## v1.1.0 — New skill: theory-simulation

Adds a fifth skill, `theory-simulation`, that bridges theoretical results and
Monte Carlo simulation to top-statistics-journal standards.

### Pipeline now (5 skills)
```
/proofcheck → /proof-repair → /theory-sharpen → /theory-simulation → /proof-writer
```

### theory-simulation skill (583 lines)
- **Theory-to-simulation mapping**: each theorem gets a verification experiment
  with explicit DGP, sample-size grid, reps, metrics, pass/fail criteria
- **Stress-test design**: violate each critical assumption one at a time
  (heavy tails, dependence, misspecification, boundary, identifiability,
  growing dim, outliers, small sample)
- **Rate verification protocol**: ≥6 sample sizes, log-log slope regression
  with 95% CI on the slope
- **Coverage verification**: empirical coverage at multiple n with Wilson CI
- **Method comparison**: required ≥1 baseline (oracle/competitor/naive)
- **Implementation conventions**: seed determinism, parallel runner, atomic
  CSV writes, reproducibility check
- **Stat-journal figure conventions** (different from Nature defaults):
  - **NO titles** on plots — all content in LaTeX `\caption{}`
  - Okabe-Ito palette (color-blind safe) for lines
  - Viridis/cividis for heatmaps; never jet/rainbow
  - Embedded fonts (`pdf.fonttype = 42`) for editable text
  - Reference dashed lines for theoretical rates / nominal coverage
  - Multi-panel with (a),(b),(c) labels in-panel, no panel titles
  - Pre-export checklist (no titles, legend doesn't cover data, etc.)
- **Theory ↔ simulation reconciliation**: feedback loop to upstream skills
  - Confirmed predictions → ready for paper
  - Theory under-claims → forward to `/theory-sharpen`
  - Theory over-claims → forward to `/proofcheck` for re-audit
  - Assumption unnecessary → relaxation candidate
  - Assumption genuinely needed → strengthen statement
- **Drop-in SIMULATION_SECTION.tex** for the paper

## v1.0.3 — Reference Mode Awareness (single-file vs two-file submissions)

Handles the practical reality that JASA / AoS / JRSS-B / Biometrika / Econometrica
submissions split main text and supplement into TWO separately-compiled PDF files,
where LaTeX `\ref{}` does NOT work across files.

### proofcheck additions
- **Reference Mode detection** at Step 0: distinguish Mode A (single-file) from
  Mode B (two-file main+supplement)
- **Mode-aware cross-reference audit** (Pass 0 Task 2B):
  - Mode A: standard `\ref{}` ↔ `\label{}` audit
  - Mode B: per-file audit + flags cross-file `\ref{}` as broken (S1 issue)
  - Mode B: validates "of the supplement" / "of the main text" wording is paired
    with hard-coded numbers
  - Mode B: checks S-prefix numbering consistency in supplement

### proof-repair additions
- **Step 0B: Detect Reference Mode** before any LaTeX patch is written
- LaTeX patches now declare their reference mode and conformance rules:
  - Within-file references → `\ref{}` / `\eqref{}` / `\cref{}` as normal
  - Cross-file references → hard-coded numbers ("Lemma S.3 of the supplement",
    "Assumption 2 of the main text"), NEVER `\ref{}`
- New lemmas inserted in supplement get S-prefixed display numbers, recorded
  for downstream main-text patches to hard-code
- **Pre-patch validation rules** scan each patch to catch leaked cross-file `\ref{}`
- BibTeX `\cite{}` is shared (works in both files) — only mathematical-object
  `\ref{}` is mode-sensitive

## v1.0.2 — Step Completeness Audit

Goes beyond passive anti-fabrication word-flagging to actively detect, reconstruct,
and classify skipped proof steps.

### proofcheck additions
- New mandatory sub-step **Step Completeness Audit** within each unit's check:
  - **Skip-point detection** in 3 categories: verbal phrases ("clearly", "by
    symmetry", "after some algebra"), equation-number jumps, implicit logical jumps
  - **Reconstruction attempt** for each detected skip using only paper's
    assumptions + cited results + named standard facts (anti-fabrication on the
    checker side)
  - **Skip classification**: TRIVIAL / VERIFIABLE / NONTRIVIAL / UNRECONSTRUCTIBLE
  - **Step Completeness Table** per unit recording every skip and verdict
  - **Reconstruction discipline rules** preventing the checker from inventing
    intermediate inequalities or unstated lemmas

### proof-repair additions
- New repair class **Fill-Skipped-Steps** with class-specific workflow:
  - VERIFIABLE (S3): write 2-5 intermediate steps inline, no refs needed
  - NONTRIVIAL (S1): identify the bridging idea, cite or create lemma
  - UNRECONSTRUCTIBLE (S0): no bridge manufacturing — investigate root cause
    (wrong proof, hidden assumption, or wrong technique)

## v1.0.1 — Model recommendation: Opus

- Added `model: opus` to YAML frontmatter of all 4 skills (forward-compatible
  with future Claude Code versions; harmless if not yet honored)
- Added prominent "Model Recommendation" callout at the top of each SKILL.md
- Updated README with required Opus setup section and rationale per skill
- Updated install.sh to print the model reminder after installation

## v1.0.0 — Initial release

### Skills included
- `proofcheck` (528 lines) — multi-pass proof verification methodology (references
  maweiruc/proofcheck-stat-paper for the 6-pass structure), reorganized into a single
  SKILL.md with provability triage and proof-strategy classification
- `proof-repair` (768 lines) — new skill: triage → impact analysis → candidate
  repairs → multi-source T1 literature search → complete proof writing → Codex
  stress-test → master REPAIR_PLAN
- `theory-sharpen` (1120 lines) — new skill: mandatory 3-axis framework
  classification with literature-anchored validation → 22 framework-tagged
  relaxation pathways → rate sharpening → reviewer-critical dimensions audit →
  Codex independent assessment
- `proof-writer` — rigorous proof drafting skill, included for pipeline completeness

### Key design decisions
- **Venue tier system** (T1 Gold → T4 Avoid) applied consistently across
  proof-repair and theory-sharpen
- **Codex MCP cross-review** integrated into three skills using a
  first-independent-then-reconcile pattern
- **Framework Classification** before any relaxation analysis to prevent
  irrelevant pathway suggestions
- **Literature recency + venue gating**: prefer last 3 years, T1 only,
  with citation gates calibrated by recency
- Reference library audited by Codex: 6 venue errors corrected, 7 missing
  pathways added, 9 reviewer-critical dimensions surfaced

### Reference library size
- 22 relaxation pathways across 5 categories with framework tags
- 11 rate-sharpening directions
- 10 reviewer-critical dimensions
- All references venue-verified
