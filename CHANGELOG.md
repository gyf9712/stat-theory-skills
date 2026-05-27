# Changelog

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
