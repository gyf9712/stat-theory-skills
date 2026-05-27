# Changelog

## v1.5.1 — Detection-MUST-trigger-completion (sketch handling hardened)

User observation: v1.5.0 added sketch detection and an Expand-Sketch-to-Proof
repair class, but it was still possible for the system to flag a sketch and
move on without expanding it. v1.5.1 closes that loophole.

### Hard rules added (across 3 skills)

**proofcheck**: A detected sketch MUST be expanded before the audit can be
marked complete.
- New mandatory field `Expansion status: REQUIRED / IN-PROGRESS / COMPLETED`
  on every flagged unit
- Audit refuses to advance to Pass 5 (Final Report) while any sketch remains
  in REQUIRED or IN-PROGRESS state
- Final Report's executive summary REQUIRES a line accounting for every
  detected sketch (must end as EXPANDED or BLOCKAGE — no partial states)

**proof-repair**: Expand-Sketch-to-Proof becomes **P0 priority unconditionally**
- Cannot be deferred to "future revision"
- REPAIR_PLAN.md now has a mandatory Sketch Expansion Tracker section
  showing every flagged sketch and its terminal state
- Plan refuses to mark complete with "Outstanding sketches > 0"
- Reclassified failure modes still must expand: Replace-Technique → expand the
  alternative proof; Add-Assumption → expand under new assumption

**proof-writer**: New HARD COMPLETION RULE when invoked to expand sketches
- Output MUST be exactly one of two terminal states:
  - COMPLETE PROOF (every step rigorously derived)
  - BLOCKAGE REPORT (explicit NOT-CURRENTLY-JUSTIFIED with what's missing)
- Explicitly FORBIDDEN: second sketch, partial expansion, weaker claim
  without relabeling, silent assumption injection
- Refuses requests to "just expand this a bit" — forces full expansion
  or blockage report

### Why this matters

The most common failure mode when LLMs are asked to "expand a proof sketch" is
producing another sketch with slightly more words. v1.5.0 detected sketches
but did not enforce that detection lead to terminal expansion. v1.5.1 makes
"sketch detected and not expanded" an impossible terminal state of the pipeline.

## v1.5.0 — Sketch vs Complete Proof discipline (3 skills)

User observation: many papers present "proof sketches" that are actually research
outlines, not verifications. The skills must distinguish, classify, and act
on this — proof-writer must refuse to produce one, proofcheck must classify
existing proofs, proof-repair must expand sketches into full proofs.

### proofcheck — New Sketch-vs-Complete Classification

New mandatory sub-step in Pass 1 (Step 3), runs before step-by-step verification.

Three-class classification per unit:
- **COMPLETE**: rigorous step-by-step derivation; all transitions justified
- **PARTIAL-SKETCH**: rigorous in parts but with substantial gaps ("rest follows
  by similar arguments"; entire technical lemma deferred; main step is one
  paragraph for a 1-page claim) — each gap recorded as S1 issue
- **SKETCH-ONLY**: high-level outline without rigorous derivation. Title labeled
  "Proof Sketch", or purely verbal narrative, or single-paragraph "proof" for a
  substantive theorem — STATUS forced to "SKETCH-ONLY — NO PROOF PROVIDED"

8 sketch indicators listed (explicit labels, verbal-only body, "we omit details",
disproportionate length, etc.). Supplement proofs that are also sketches inherit
the same classification.

Reviewer-facing rule: a sketch in main text is NOT verification; if paper relies
on it, theorem is at best CONDITIONALLY VERIFIED pending full proof.

### proof-repair — New repair class: Expand-Sketch-to-Proof

When proofcheck flags SKETCH-ONLY / PARTIAL-SKETCH, the repair is to write
the ENTIRE proof, not just fix steps. Distinct from Fill-Skipped-Steps (which
fills isolated gaps inside an otherwise rigorous proof).

Workflow:
1. Extract intended outline from the sketch
2. For each intended step: verify cited technique applies + write actual derivation
3. Trigger /proof-writer (which refuses to produce another sketch)
4. Verify expanded proof concludes the original claim exactly
5. Cite canonical references for invoked techniques

Common failure modes documented:
- Sketch hides genuine unprovability → downgrade to NOT CURRENTLY JUSTIFIED
- Cited technique doesn't apply → reclassify as Replace-Technique
- Expansion reveals missing assumption → reclassify as Add-Assumption

### proof-writer — New ANTI-SKETCH DISCIPLINE

The skill now explicitly REFUSES to produce a sketch in place of a proof.

Distinguishes:
- Proof outline / research plan: fine (delegate to /theory-design)
- Proof sketch placed as "proof": REFUSED
- Complete proof: what this skill always produces

When user asks for a sketch:
- Refuse the disguised-as-proof version
- Offer: complete proof / explicit research outline (labeled, not proof) /
  proof of weaker verifiable claim + research outline for stronger

When the only completable thing is a sketch:
- Downgrade to NOT CURRENTLY JUSTIFIED + blockage report
- Do NOT silently substitute a sketch for a proof

New length heuristic: a substantive theorem (rate, distribution, coverage)
typically needs ≥ 1 page of dense derivation. ≤ 10 lines for a paragraph-long
theorem triggers a sketch-suspicion check.

Strengthened forbidden phrases now include: "the rest is similar", "we omit
the details", "details are routine", and pointing-at-paper-without-adaptation.

## v1.4.0 — Shared Codex Discussion Protocol (NOT wholesale acceptance)

User observation: across all skills using Codex, the implicit risk was that Claude
would "全盘接受" Codex findings rather than discussing them. This release codifies
the discipline.

### New file: `CODEX_PROTOCOL.md` (repo root)

A shared, explicit protocol for how Claude skills invoke Codex:

- **Core principle**: Codex is an adversarial reviewer to discuss with, NOT an
  oracle to defer to
- **5-round protocol**: Claude output → Codex review → Claude per-finding
  evaluation (ACCEPT / PUSH BACK / REQUEST CLARIFICATION) → Codex response →
  iterate until convergence or escalate
- **Forbidden behaviors**: silent wholesale acceptance, silent rejection,
  acceptance without recorded reasoning, push-back without substantive argument
- **Documentation requirement**: every Codex-using skill emits `codex_discussion.md`
  showing the full round-by-round dialogue
- **When to escalate**: persistent disagreement, >3 rounds without progress,
  or taste/philosophy/venue-preference disagreements (let user pick)

### Updated skills (all 5 now reference CODEX_PROTOCOL.md)

- `proofcheck` (Pass 4): adversarial cross-review uses discussion protocol
- `proof-repair` (Step 5C): stress-test repairs via discussion
- `theory-sharpen` (Step 5B): independent assessment via discussion;
  especially critical to prevent OVERCLAIM of theory relaxation
- `theory-simulation` (Step 4F): pre-run + post-run review via discussion;
  critical because reruns are expensive
- `theory-design` (Step X4): NEW — adversarial framework review via discussion;
  critical because framework shapes the whole paper

Each skill explicitly calls out the forbidden behaviors and the requirement to
emit a `codex_discussion.md` documenting the dialogue.

### Why this matters

LLM-to-LLM review has two failure modes:
- **Capitulation**: Claude accepts every Codex finding to avoid disagreement
  → output shaped by whichever model is louder
- **Defensiveness**: Claude dismisses Codex findings to defend prior work
  → loses the value of independent review

Both produce worse outputs than a single careful Claude pass. The protocol
forces structured deliberation that exploits both models without inheriting
either's blind spots.

### Documented examples

CHANGELOG entries v1.1.1, v1.2.0 already documented real instances of the
protocol working (Codex raised 20 findings; 13 accepted, 6 push-backs of which
5 produced refinements and 1 was conceded by Claude). v1.4.0 makes this pattern
explicit and uniform across all skills.

## v1.3.1 — theory-design: Mandatory literature anchoring

Designing a theoretical framework without first reading recent top-venue
literature is unsafe — you risk reinventing existing work, deviating from
field conventions for no reason, or being unable to position the contribution.
The skill now enforces literature anchoring BEFORE any phase decision.

### New Step 0.5: Mandatory Literature Anchoring

**0.5A Topic signature**: structured search keywords (subject + technique + data
structure + framework + regime + application area).

**0.5B Multi-source T1 search** (4 parallel agents):
- T1 statistics journals (AoS, JASA T&M/ACS, AOAS, JRSS-B, Biometrika,
  Bernoulli, EJS, Statistica Sinica, Biostatistics, JCGS)
- T1 ML/AI conferences (NeurIPS, ICML, ICLR, COLT, AISTATS, JMLR, UAI)
- T1 econometrics journals (Econometrica, JOE, REStud, QE, JBES, ET)
- Highly-cited consensus papers (last 10 years, citation-sorted)

Prefers last 3 years, hard cap at last 5 years. Citation gates calibrated by recency.

**0.5C Per-paper structured extraction**:
problem framing, theoretical anchor, assumption profile, result type, proof
technique, position in literature.

**0.5D Theoretical inertia identification**:
What is the current consensus on data structure, modeling framework, asymptotic
regime, proof technique, contribution shape? This is the "default path" the
field expects.

**0.5E Positioning options** (3 choices, each with trade-offs):
- INCREMENTAL: refine within the inertia (lower friction, lower novelty)
- LATERAL: same problem, different angle (justifies the angle change)
- DISRUPTIVE: challenges the inertia (highest reward, must build the case)

**0.5F Anchor → design constraints**:
Every subsequent phase must reference the anchor when making decisions:
"You're adopting the inertia here — cite [canonical papers]"
"You're deviating here — justify with [specific reasoning]"

**0.5G Mandatory user confirmation**:
Skill REFUSES to proceed to Step T1/M1/A1 until user confirms the anchor.

### New Step X2.5: Positioning audit

After framework design, verify:
- Did each phase decision match the chosen positioning?
- Did the framework drift from positioning during T1-T7 / M1-M7 / A1-A7?
- Citation strategy alignment: which 5-10 papers cited prominently, in what role?

If positioning drifted, decide: revert framework to match original positioning,
OR update positioning to match what framework evolved into. Either is fine;
the mismatch is the problem.

### Output addition
- New artifact: `papers/<paper-name>/design/LITERATURE_ANCHOR.md`
- Consumed by all downstream skills (proof-writer, theory-simulation, proofcheck)
  for context

## v1.3.0 — New skill: theory-design (paper-type-aware framework planning)

Adds a 6th skill that handles the **planning phase** — from "I have a new
research topic" to a structured FRAMEWORK_DESIGN.md.

### Key insight
Statistics papers come in three types with FUNDAMENTALLY different logical
orders for theoretical-framework design:

| Type | Centerpiece | Theory's role |
|------|-------------|---------------|
| THEORY paper | The theorem itself | The contribution |
| METHODOLOGY paper | The estimator/method | Guarantees method correctness |
| APPLICATION paper | Empirical findings | Justifies method choice + verifies assumptions |

Previous version of this skill family conflated these three. The new skill
forces a paper-type declaration first, then walks a type-specific 7-phase
logical order:

**THEORY mode (T1-T7)**:
T1: Phenomenon / mathematical-object identification
T2: Mathematical landscape mapping (existing toolkit gap)
T3: Conceptual framework & notation
T4: Formal problem setup (spaces, parameter classes, regimes)
T5: Target theorems — upper AND lower bounds equally first-class
T6: Proof strategy & lemma scaffold
T7: Connections to downstream (what methods this enables)

**METHODOLOGY mode (M1-M7)**:
M1: Practical problem & method gap
M2: Method design (CENTERPIECE)
M3: Model setup for analysis
M4: Identification
M5: Theoretical guarantees needed (consistency / rate / inference / etc.)
M6: Simulation + real-data validation plan
M7: Proof strategy (technical labor supporting the method)

**APPLICATION mode (A1-A7)**:
A1: Scientific question & data
A2: Existing-method selection
A3: Assumption verification on THIS dataset (distinguishes APP from METHO)
A4: Empirical findings
A5: Inference & uncertainty quantification
A6: Sensitivity analyses
A7: Connection to literature & implications

**Cross-type checks (X1-X4)** run for all modes:
- Internal consistency
- Novelty / contribution audit
- Reviewer hot-button preemption
- Codex independent framework review

### Pipeline placement
```
research-refine → /theory-design → /proof-writer → /theory-simulation → /proofcheck → /theory-sharpen → /proof-repair
(rough idea)      (framework)      (theorems)      (verify)              (audit)         (improve)         (fix)
```

theory-design is the planning layer BEFORE any theorem is written or experiment
run. It hands off:
- Theorem statements (T5/M5) → /proof-writer
- Validation plan (M6/A4-A5) → /theory-simulation
- Pre-paper checks → /proofcheck (after proofs drafted)

## v1.2.0 — theory-simulation: AUDIT MODE for existing simulations

Adds a second operating mode to theory-simulation, after a third round of Codex
adversarial review focused on the new audit functionality.

### New AUDIT MODE
When a paper already has a simulation section, the skill now evaluates whether
those existing simulations actually verify the theorems, identifies gaps,
and proposes targeted improvements (rather than full redesign).

**A0 — Parse existing sims**: extract experiments, DGPs, n grids, methods, metrics,
B values, figures, tables, stated conclusions.

**A1 — Two-axis Coverage Matrix** (per Codex's split):
- Axis 1: **Coverage** — does any experiment aim at this claim?
- Axis 2: **Evidentiary strength** — does the experiment actually identify the claim?
- Claim priority ranking: PRIMARY / SECONDARY / PERIPHERAL
- Final tags with structured reason codes:
  - `YES[strong]` / `YES[weak]`
  - `PARTIAL[path | metric | precision | grid | comparator | reporting | stress-coverage | identification-mismatch]`
  - `NO`
  - `CONTRADICTED[*]`

**A2 — Per-experiment adequacy audit** scoring on 12 criteria.

**A2.5 — CONTRADICTED 7-step protocol** (Codex insisted on this):
1. Replication check (rerun with saved seed)
2. Metric check (does paper measure what theorem bounds?)
3. DGP check (do assumptions actually hold in sim?)
4. Computation check (failures, tuning, numerics)
5. MC precision check (is contradiction > 2 × MCSE?)
6. Localization (all cells / pre-asymptotic / off-assumption?)
7. Escalation routing (implementation fix / not real / reframe / genuine — invoke /proofcheck)

**A2.6 — Reuse legitimacy audit**: verifies existing runs can be statistically
reused (replicate-level data saved, RNG streams recorded, no silent failures,
correct truth, etc.) before blessing reuse.

**A2.7 — Truth-source audit**: how was ground truth defined?
Analytic / oracle / numerical / high-B estimate / asymptotic limit — each needs verification.

**A2.8 — Selection-bias audit**: omitted cells, methods, regimes, DGPs, failures,
cherry-picked seeds.

**A2.9 — Tuning / procedure audit**: oracle vs data-driven; CV variability; sensitivity.

**A2.10 — Computational adequacy audit**: mandatory when paper claims "fast",
"scalable", "practical".

**A3 — Gap analysis** in 6 buckets now (was 3):
1. Claims with NO experimental evidence
2. Experiments with adequacy problems
3. Reporting / discipline issues
4. Selection-bias risks (`SELECTION_RISK`)
5. Tuning / procedure gaps (`TUNING_GAP`)
6. Computational adequacy gaps (`COMP_GAP`)

**A4 — Targeted improvement plan**: priorities ordered, distinguishing what can
be reused from existing runs vs what must be rerun.

**A5 — Codex cross-audit** (optional): independent second opinion on the audit itself.

### Result
Skill went 1001 → 1435 lines. Three Codex review rounds, all 23 + 4 + 4 findings
addressed. Skill now handles both new-from-scratch design AND audit of existing
simulations.

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
