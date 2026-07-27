---
name: theory-sharpen
description: >-
  Systematically assess whether a paper's theoretical results can be strengthened:
  relax assumptions, sharpen rates, align theory with model and experiments, and
  benchmark against state-of-the-art literature. Use when user says "sharpen theory",
  "strengthen results", "relax assumptions", "improve rates", "理论提升", "放宽假设",
  "优化rate", "theory alignment", "理论对齐", or wants to go beyond proof correctness
  toward theoretical optimality and practical relevance.
argument-hint: [path-to-paper.tex or paper-dir]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, WebSearch, WebFetch, mcp__codex__codex, mcp__codex__codex-reply
model: opus
---

# Theory-Sharpen — Systematic Theoretical Improvement Assessment

> 🔬 **Model Recommendation**: Run this skill on **Claude Opus** for best results.
> Framework classification, assumption-relaxation analysis, and rate-sharpening all
> require deep mathematical reasoning. If your session is not on Opus, run
> `/model opus` before invoking. Literature search and Codex cross-review will use
> Opus sub-agents.

Go beyond "is the proof correct?" to ask "can the theory be stronger, sharper, and
better aligned with the model, the literature, and the experiments?"

**Pipeline position**:
```
/proofcheck → /proof-repair → /theory-sharpen → /proof-writer
  Correct?      Fix issues       Improve theory     Write new proofs
```

This skill can also run standalone on any paper with theoretical results.

## Context: $ARGUMENTS

---

## Core Philosophy

A good theory paper is evaluated on three axes:

1. **Strength**: Are assumptions as weak as possible? Are rates as sharp as possible?
2. **Alignment**: Does the theory match what the model actually provides and what
   the experiments actually test?
3. **Positioning**: How does the result compare to the best known results in the literature?

This skill systematically audits all three axes and produces an actionable improvement
roadmap.

---

## Step 0: Ingest & Map the Theory-Model-Experiment Triangle

### 0A: Locate Inputs

Parse `$ARGUMENTS`. Accept:
- A `.tex` file path → read directly
- A paper directory → read `paper.tex` + any `/proofcheck` audit if it exists
- If `/proofcheck` audit exists, leverage `assumption_ledger.md`, `theorem_inventory.md`,
  `dependency_graph.md` for a head start

### 0B: Extract the Three Pillars

Read the paper and extract three structured inventories:

**Pillar 1: Theory** — What the theorems claim

| ID | Result | Assumptions used | Rate / bound | Constants | Regime | Location |
|----|--------|-----------------|-------------|-----------|--------|----------|

For each result, record:
- Exact assumptions (named + implicit)
- Convergence rate or bound (e.g., $O(n^{-1/2})$, $O_P(n^{-2/(2+d)})$)
- Whether rate is minimax, near-minimax, or suboptimal (if known)
- Sample size / dimension regime (e.g., $n \gg d$, $n \gg d^2$, fixed $d$)
- Constants: universal, dimension-dependent, problem-parameter-dependent?

**Pillar 2: Model** — What the model actually provides

| Property | Stated in paper? | Actually holds? | Stronger than needed? | Weaker than assumed? |
|----------|-----------------|-----------------|----------------------|---------------------|

Read the model definition (usually Section 2 or "Setup") and inventory:
- What distributions / processes does the model generate?
- What structural properties does the model have? (linearity, sparsity, convexity, Markov, etc.)
- What regularity does the model provide? (smoothness, tail behavior, mixing, etc.)
- Are there properties the model has that the theory does NOT exploit?
- Are there properties the theory assumes that the model does NOT guarantee?

**Pillar 3: Experiments** — What the empirical evaluation actually tests

| Experiment | Setting | Covered by theory? | Gap |
|-----------|---------|-------------------|-----|

Read the experiment section and inventory:
- What data distributions / models are tested?
- What sample sizes and dimensions are used?
- What metrics are reported?
- Which theoretical predictions are actually verified empirically?
- Which theoretical conditions are violated in practice?

### 0C: Build the Alignment Map

Produce a **Theory-Model-Experiment Alignment Matrix**:

```markdown
## Alignment Matrix

| Assumption / Claim | Theory requires | Model provides | Experiments test | Alignment |
|--------------------|----------------|----------------|-----------------|-----------|
| i.i.d. data | Yes (Assumption 1) | Yes (by construction) | Yes | ALIGNED |
| Sub-Gaussian tails | Yes (Assumption 3) | Gaussian (stronger) | Heavy-tailed also tested | THEORY-EXP GAP |
| Dimension fixed | Yes (implicit in rate) | Not restricted | d=50,100,500 tested | THEORY-EXP GAP |
| Strong convexity | Yes (Assumption 2) | Only local convexity | Non-convex also tested | THEORY-MODEL GAP |
| Rate O(n^{-1/2}) | Theorem 1 | — | Matches empirically | ALIGNED |
| Uniform over Θ | Theorem 2 claims | Model has compact Θ | Fixed θ only | THEORY-EXP GAP |

Legend:
  ALIGNED         — theory, model, and experiments all agree
  THEORY-MODEL GAP — theory assumes something the model doesn't guarantee (or vice versa)
  THEORY-EXP GAP  — theory doesn't cover what experiments test (or vice versa)
  MODEL-EXP GAP   — model definition differs from experimental setup
  EXPLOITABLE     — model provides something stronger that theory doesn't use
```

---

## Step 0.5: Framework Classification (MANDATORY — must complete before any relaxation analysis)

Relaxation pathways are framework-dependent. Trying to "relax i.i.d. to mixing" is
meaningless for a paper on cross-sectional regression. Classify the paper on three
axes BEFORE filtering the pathway library.

### Auto-Detection + Literature-Anchored Confirmation

The classification proceeds in three sub-steps:

**0.5A: Paper-internal inference** (agent)
Read paper sections (intro, model setup, assumptions, theorems) and infer a draft
classification on three axes from the paper's own statements.

**0.5B: Literature-anchored validation** (agent — parallel literature search)
Search for RECENT T1-venue papers in the same topic, and check whether the
classification is consistent with how the field currently frames similar problems.

**0.5C: Forced user confirmation** (mandatory)
Present BOTH the paper-internal classification AND the literature evidence to the
user. **Do not proceed until user confirms.**

---

### 0.5B: Literature-Anchored Validation (details)

After drafting the classification in 0.5A, build a **topic signature** and run a
targeted multi-source literature search to validate.

**Topic signature components**:
- Subject domain (e.g., "treatment effect estimation", "stochastic optimization",
  "high-dim regression", "Markov chain Monte Carlo", "online learning")
- Main technique keywords (e.g., "M-estimation", "lasso", "kernel regression",
  "Poisson equation", "doubly robust")
- Data structure (from Axis 1)
- Framework (from Axis 2)
- Regime (from Axis 3)

**Search strategy (parallel agents, T1 priority, recent first)**:

```
Agent 1: Recent T1 journal papers (last 3 years preferred, 5 years max)
  Search: [topic] + [technique] + [framework keyword]
  Venues filter: AoS, Biometrika, JASA, JRSS-B, Econometrica, JOE, JBES, RESS,
                  JMLR, Annals of Probability, Bernoulli, EJS, Stat Sinica
  Source: WebFetch on Semantic Scholar API with venue + year filter
  
Agent 2: Recent T1 conference papers (last 3 years preferred)
  Search: same topic signature
  Venues filter: NeurIPS, ICML, ICLR, COLT, AISTATS, AAAI, KDD, UAI
  Source: WebSearch with site filter + arXiv with venue annotation

Agent 3: Most cited recent papers in this framework (last 5 years, ≥30 citations)
  Search: broader topic
  Source: Semantic Scholar sorted by citation count
  Purpose: identify the "current consensus" framework
```

**For each found paper, extract**:
- Title, authors, year, venue, citation count
- How THEY classified their problem on the three axes (data type, framework, regime)
- What assumptions they use (compare with our paper's assumptions)
- What rates they prove
- What techniques they use

**Build the Literature Anchor Table**:

```markdown
## Recent T1 Papers in This Framework (top 5-10)

| # | Paper | Venue (Year) | Cite | Their Axis 1 | Their Axis 2 | Their Axis 3 | Key technique |
|---|-------|-------------|------|--------------|--------------|--------------|---------------|
| 1 | Chen & Li (2024) | AoS | 25 | mixing TS | SEMI | CLA | Orthogonal scores + HAC |
| 2 | Zhang et al. (2023) | Econometrica | 80 | mixing TS | SEMI | CLA + FS | Cross-fitting + DML |
| 3 | Wang & Park (2024) | JASA | 12 | mixing TS | NONPAR | CLA | Sieve + peeling |
| 4 | Kim (2023) | NeurIPS | 50 | i.i.d. | SEMI | HD | RSC + LASSO |
| 5 | ... |
```

**Classification cross-check**:

If the literature evidence DISAGREES with the paper-internal inference, flag this
explicitly:

```markdown
## Classification Validation Report

### Axis 1 (Data): paper says i.i.d.
Literature check: Of 10 recent papers on the same topic ("dynamic treatment effect 
under adaptive randomization"), 7 frame it as sequential-adaptive, 2 as i.i.d.-with-
conditioning, 1 as Markov.
Verdict: ⚠ MISMATCH — paper's i.i.d. framing may be unconventional for this topic.
Recommendation: Reclassify as `SEQ` and re-examine i.i.d. assumption.

### Axis 2 (Framework): paper says parametric
Literature check: 8/10 recent papers use semiparametric framework with nuisance.
Verdict: ⚠ POSSIBLE MISMATCH — modern treatment may have shifted to SEMI.
Note: If paper genuinely is PAR, this is fine but flag as a positioning issue.

### Axis 3 (Regime): paper says classical asymptotic
Literature check: 6/10 recent papers prove non-asymptotic bounds.
Verdict: 🟡 TREND — field is moving toward finite-sample; classical is acceptable
but consider adding finite-sample version.
```

**Output to user (Step 0.5C — forced confirmation)**:

```markdown
## Draft Framework Classification (please confirm or correct)

### Axis 1: Data Structure
- Paper-internal inference: [class] (confidence: HIGH/MEDIUM/LOW)
- Paper evidence: "Section 2 line 47 defines X_i as i.i.d. samples from P"
- Literature check (last 3-5 years, T1 only): X of N recent papers in this topic
  use the same framing; Y use [alternative]
- Verdict: ✅ CONSISTENT / ⚠ MISMATCH / 🟡 TREND
- Sample recent T1 papers in same framing:
  • Chen & Li (2024, AoS, 25 cites)
  • Zhang et al. (2023, Ectrica, 80 cites)

### Axis 2: Modeling Framework
- Paper-internal inference: [parametric / semiparametric / nonparametric / structured-nonpar]
- Paper evidence: "Parameter θ ∈ R^d with d fixed" / "Target β with nuisance η(·)"
- Literature check: X of N recent T1 papers use [same framework]; trend = [observation]
- Verdict: ✅ / ⚠ / 🟡
- Sample papers: ...

### Axis 3: Asymptotic Regime
- Paper-internal inference: [classical / proportional / high-d sparse / non-asymptotic / online]
- Paper evidence: "Theorem 1 states 'as n→∞' with no d dependence"
- Literature check: X of N recent papers prove [same regime]; field trend = ...
- Verdict: ✅ / ⚠ / 🟡
- Sample papers: ...

### Cross-axis consistency
- Does the (Data, Framework, Regime) triple match common combinations in literature?
- Are there standard "default" choices being deviated from? (e.g., NEMS is usually
  framed as SEMI + finite-sample, but this paper uses PAR + classical)

### Multi-regime papers
If the paper proves results in MULTIPLE regimes (common!), list all that apply.

### Literature-recommended pathway hints (preview)
Based on recent T1 papers in your framework, these relaxation directions are
TRENDING and likely to be reviewer-asked:
- [pathway 1 — supported by N recent T1 papers]
- [pathway 2 — supported by M recent T1 papers]
- [pathway 3 — emerging direction in last 12 months]
```

**User actions after seeing this report**:
1. CONFIRM the classification → proceed to Step 1 with filtered pathways
2. CORRECT one or more axes → agent updates and reruns the filter
3. ASK for more detail on a specific paper from the literature anchor table
4. REQUEST classification under a DIFFERENT venue's framing (e.g., "show me how an
   Econometrica reviewer would classify this vs a NeurIPS reviewer")

### Literature search for classification and pathways

Query templates by framework axis, the recency and venue gating rules (prefer T1 within
the last ~5 years; an older paper needs a reason), and worked pathway-relevance examples:
`../stat-shared-references/theory-search-templates.md`. Venue tiers are rule data in
`../stat-shared-references/scripts/venue_tiers.py`.

Gate: a classification or pathway asserted without literature support is a draft, not a
finding. Confirm the framework classification against recent T1 papers before running any
relaxation analysis on it.

## Step 1: Assumption Relaxation Analysis

For EACH assumption in the theory, systematically assess whether it can be weakened
**within the confirmed framework** from Step 0.5.

### 1A: Assumption Relaxation Table

```markdown
| Assumption | Current form | Relaxation candidate | Feasibility | Literature support | Priority |
|-----------|-------------|---------------------|-------------|-------------------|----------|
| A1: i.i.d. | Samples are i.i.d. | β-mixing with polynomial decay | LIKELY | Doukhan (1994), Rio (2017) | HIGH if time-series app |
| A2: Strong convexity (μ>0) | ∇²f ≽ μI globally | Local strong convexity + growth | POSSIBLE | Mei et al. (2018, AoS) | MEDIUM |
| A3: Sub-Gaussian | ψ₂-norm bounded | Sub-exponential (ψ₁) | LIKELY | Vershynin (2018, Cambridge) | HIGH |
| A3: Sub-Gaussian | ψ₂-norm bounded | Bounded 4th moment only | HARD | Catoni (2012, AoS) — different technique | LOW |
| A4: Compact Θ | Θ is compact | Locally compact + growth at ∞ | POSSIBLE | van der Vaart (1998), Ch. 5 | MEDIUM |
```

### 1B: Relaxation Feasibility Assessment

For each relaxation candidate, answer these questions:

1. **Which proof step breaks?**
   - Trace through the proof: where is the strong assumption actually used?
   - Is it used once (easy to patch) or pervasively (hard to patch)?

2. **What replacement technique exists?**
   - i.i.d. → mixing: blocking technique, coupling, Berbee's lemma
   - Sub-Gaussian → heavy-tailed: truncation, median-of-means, Catoni's estimator
   - Strong convexity → local: restricted strong convexity, local Rademacher complexity
   - Compact → non-compact: localization, peeling, sieve

3. **Does the rate change?**
   - Some relaxations preserve the rate (e.g., i.i.d. → mixing with fast decay)
   - Some worsen the rate (e.g., sub-Gaussian → bounded moment adds log factors)
   - Record the rate change explicitly

4. **Is this aligned with the model and experiments?**
   - If the model is actually Gaussian, relaxing to heavy-tailed is theoretically nice
     but practically unnecessary → PRIORITY: LOW
   - If experiments test heavy-tailed data but theory assumes sub-Gaussian → PRIORITY: HIGH

### 1C: Choose relaxation pathways from the catalogue

For each assumption marked feasible in 1B, select a candidate pathway from
`../stat-shared-references/relaxation-pathways.md`, which tags every standard route by
framework axis (data structure, modelling framework, asymptotic regime).

The selection rule, which matters more than the catalogue: **filter by the Step 0.5
classification first**. A pathway developed for i.i.d. parametric classical-asymptotic
work usually does not transfer to a dependent-data high-dimensional setting, and
proposing it wastes the author's time and signals the analysis did not read the paper's
own regime. A pathway that survives the filter still needs literature support (Step 5)
and a proof sketch before it is called feasible.

If no catalogued pathway survives the filter, say so: "no standard pathway applies in
this framework" is a real finding, and it usually means the relaxation is research-level
rather than a known technique.

## Step 2: Rate Sharpness Analysis

For EACH rate claimed in the paper, assess whether it can be improved.

### 2A: Rate Inventory & Optimality Check

```markdown
| Result | Claimed rate | Best known rate (literature) | Minimax lower bound | Gap | Sharpening possible? |
|--------|-------------|---------------------------|-------------------|-----|---------------------|
| Thm 1: LLN | O(n^{-1/2}) | n^{-1/2} (sharp for CLT) | n^{-1/2} (Cramer-Rao) | None | NO — already optimal |
| Thm 2: Estimation | O(n^{-2/5}) | n^{-2/(2+d)} (Stone 1982) | n^{-2/(2+d)} (Stone) | Yes if d>1 | POSSIBLE — check technique |
| Thm 3: Uniform bound | O(√(d log n / n)) | √(d/n) (no log) | √(d/n) (Rademacher) | log n factor | LIKELY removable |
| Cor 1: Prediction | O(n^{-1/3}) | n^{-1/2} (parametric) | Depends on model | Large gap | CHECK model assumptions |
```

### 2B: Sharpening Directions

For each improvable rate, identify the specific source of suboptimality:

**Common sources of loose rates and their fixes** *(venue-verified with Codex)*:

| Loose rate source | How to identify | Fix | Key references |
|-------------------|----------------|-----|----------------|
| **Unnecessary log factor** | Union bound over an ε-net | Chaining / Dudley integral / generic chaining | Talagrand (2014, Springer); van der Vaart & Wellner (1996, Springer) |
| **Suboptimal covering number** | Metric entropy bound too loose | Tighter entropy / local entropy / local Rademacher | Bartlett, Bousquet & Mendelson (2005, *JMLR*); Koltchinskii (2006, *Annals of Statistics*) |
| **Union bound over finite set** | Discretization then union | Direct empirical-process supremum bound | van der Vaart & Wellner (1996, Springer); Gine & Nickl (2016, Cambridge) |
| **Hoeffding when variance known** | Sub-Gaussian bound ignoring small variance | Bernstein / Bennett / Freedman inequality | Boucheron, Lugosi & Massart (2013, Oxford); Freedman (1975, *Annals of Probability*) |
| **Ambient-dimension factor** | C(d) grows with d hidden in O(·) | Effective-rank / Gaussian-width / localized-geometry | Koltchinskii & Lounici (2017, *Bernoulli*); Vershynin (2018, Cambridge) |
| **Ignoring local structure** | Global bound where local suffices | Localization / peeling / local Rademacher | Bartlett, Bousquet & Mendelson (2005, *JMLR*); Koltchinskii (2006, *Annals of Statistics*) |
| **Suboptimal truncation** | Heavy-tail truncation too conservative | Optimize bias-variance tradeoff | Catoni (2012, *AIHP*); Devroye et al. (2016, *AoS*); Lugosi & Mendelson (2019, *AoS*) |
| **Only slow rate proved** | Fast rate should be possible | Bernstein / margin / low-noise condition | Tsybakov (2004, *Annals of Statistics*); Koltchinskii (2006, *Annals of Statistics*) |
| **Crude bias term** | Bias dominates or left unsharpened | Debiasing / higher-order expansion / robust bias correction | Calonico, Cattaneo & Titiunik (2014, *Econometrica*); Fan & Gijbels (1996, Chapman & Hall) |
| **Nuisance estimation remainder** | Nuisance error dominates target rate | Orthogonalization + cross-fitting (DML) | van de Geer et al. (2014, *Annals of Statistics*); Chernozhukov et al. (2018, *Econometrics J.*) |
| **Non-adaptive step size** | Algorithm analysis with fixed η | Adaptive / diminishing / accelerated analysis | Duchi, Hazan & Singer (2011, *JMLR*); Rakhlin, Shamir & Sridharan (2012, *ICML*) |

### 2C: Minimax Lower Bound Cross-Check

For the main theorem, check if a matching lower bound exists:

1. **Search for minimax lower bounds** in the same problem class
   - Use venue-tier system from `/proof-repair` (T1 priority)
   - Focus: AoS, JRSS-B, JMLR, Econometrica, COLT, information-theoretic bounds

2. **If lower bound matches** → rate is minimax optimal; note this as a strength
3. **If lower bound is better** → gap exists; check if it's:
   - A fundamental gap (technique limitation) → suggest new technique from literature
   - An artifact of loose analysis → suggest tightening specific steps
   - A different model class → clarify which lower bound applies
4. **If no lower bound exists** → consider whether constructing one would
   strengthen the paper (and cite relevant methodology: Fano, Le Cam, Assouad)

### 2D: Rate-Under-Relaxed-Assumptions

Cross-reference with Step 1: if assumptions are relaxed, how do rates change?

```markdown
| Result | Current rate | Under relaxed assumption | Rate change | Worth it? |
|--------|-------------|------------------------|-------------|-----------|
| Thm 1 | n^{-1/2} (i.i.d.) | n^{-1/2} (β-mixing, poly decay) | Same | YES — free generalization |
| Thm 2 | n^{-2/5} (sub-Gaussian) | n^{-2/5} · (log n) (sub-exp) | Extra log | MAYBE — depends on application |
| Thm 3 | √(d/n) (strong convex) | (d/n)^{1/3} (local SC) | Worse | NO — rate degradation too large |
```

---

## Step 2E: Reviewer-Critical Dimensions Audit

*Identified via Codex cross-review. These are dimensions that top-venue reviewers
(AoS, Biometrika, Econometrica, NeurIPS/ICML/COLT) routinely demand but that
assumption-relaxation and rate-sharpening alone do not cover.*

For EACH dimension, check whether the paper addresses it. If not, flag as an
improvement opportunity.

| Dimension | Typical reviewer question | Key technique | T1 references |
|-----------|--------------------------|---------------|---------------|
| **Lower bounds / optimality** | "Are your rates minimax? What shows they can't be improved?" | Le Cam / Fano / Assouad; phase transitions | Donoho & Johnstone (1994, *Biometrika*); Cai & Low (2004, *AoS*); Tsybakov (2009, Springer) |
| **Necessity of assumptions** | "Which assumptions are genuinely needed vs proof artifacts? Counterexample if dropped?" | Counterexamples; impossibility theorems | Low (1997, *AoS*); Cai & Low (2004, *AoS*); Huber (1964, *Annals of Math. Stat.*) |
| **Inference / UQ** | "Can you do valid CIs, tests, bootstrap? Is the estimator asymptotically linear or semiparametrically efficient?" | Debiasing; Gaussian approximation; bootstrap | van de Geer et al. (2014, *AoS*); Chernozhukov, Chetverikov & Kato (2017, *Annals of Probability*); Robinson (1988, *Econometrica*) |
| **Identification** | "Is the target identified? What happens under weak/partial identification?" | Identification analysis; weak-ID robust inference | Staiger & Stock (1997, *Econometrica*); Andrews & Cheng (2012, *Econometrica*); White (1982, *Econometrica*) |
| **Adaptivity / tuning-free** | "Do you need oracle tuning or known smoothness/sparsity? Can the procedure adapt?" | Lepski selection; pivotal tuning; oracle inequalities | Goldenshluger & Lepski (2011, *AoS*); Donoho & Johnstone (1994, *Biometrika*); Belloni, Chernozhukov & Wang (2011, *Biometrika*) |
| **Structural guarantees** | "ℓ₂ rate is fine, but can you recover support/rank/graph/changepoint?" | Support recovery; sign consistency; localization | Zou (2006, *JASA*); Meinshausen & Buhlmann (2006, *AoS*); Wainwright (2009, *IEEE Trans. IT*) |
| **Computational attainability** | "Is the estimator computationally feasible? Nonconvex optimization trustworthy?" | Stat-computation tradeoffs; benign landscape | Agarwal, Negahban & Wainwright (2012, *AoS*); Loh & Wainwright (2015, *JMLR*); Mei, Bai & Montanari (2018, *AoS*) |
| **Robustness to misspecification** | "What if model is wrong, data contaminated, errors heteroskedastic?" | Huber contamination; quasi-MLE; sandwich/HAC | Huber (1964, *Annals of Math. Stat.*); White (1982, *Econometrica*); Newey & West (1987, *Econometrica*) |
| **Uniformity / honesty** | "Is the approximation uniform over the parameter class, or only pointwise? Honest CIs?" | Uniform Gaussian approximation; honest coverage | Low (1997, *AoS*); Cai & Low (2004, *AoS*); Andrews & Cheng (2012, *Econometrica*) |
| **Assumption verifiability** | "Can practitioners actually check whether your assumptions hold in their data, or are they unobservable theoretical conditions?" | Testable conditions; data-driven verification; observable identification | Imbens & Rubin (2015, Cambridge); Crump et al. (2009, *Biometrika*); D'Amour et al. (2021, *J. Econometrics*) |

### Audit template per dimension

For each dimension, produce:

```markdown
| Dimension | Paper addresses it? | How? | Gap? | Improvement suggestion |
|-----------|-------------------|------|------|----------------------|
| Lower bounds | No | — | YES | Prove Fano lower bound for the estimation rate |
| Inference/UQ | Partially (CLT only) | Thm 4 | Partial: no bootstrap validity | Add bootstrap consistency theorem |
| Identification | Yes | Assumption 1 | None | — |
| Adaptivity | No — tuning parameter λ is oracle | — | YES | Lepski-type or cross-validation analysis |
| Computation | No — NP-hard in general | — | YES | Show benign landscape under conditions or use convex relaxation |
```

---

## Step 3: Theory-Model Alignment Audit

Check whether the theoretical framework actually matches the model.

### 3A: Assumption-Model Match

For EACH assumption the theory uses, check:

```markdown
| Assumption | Theory requires | Model provides | Match? | Issue |
|-----------|----------------|----------------|--------|-------|
| A1: i.i.d. | Independent samples | Sequential adaptive design | MISMATCH | Samples depend on past allocations |
| A2: Bounded gradient | ‖∇f‖ ≤ B | Neural net — unbounded | MISMATCH | Needs truncation or clipping argument |
| A3: Lipschitz loss | L-Lipschitz | Logistic loss — yes, L=1 | MATCH | — |
| A4: Sub-Gaussian noise | ψ₂ ≤ σ | Gaussian noise — yes | OVER-SPECIFIED | Model gives Gaussian, only need sub-G |
```

**Match types**:
- **MATCH**: Theory and model agree exactly
- **OVER-SPECIFIED**: Theory assumes more than needed; model gives more than theory uses
  → Opportunity: exploit the extra structure for sharper results
- **MISMATCH**: Theory assumes something the model doesn't provide
  → Problem: theorem may not apply to the paper's own model
- **IMPLICIT**: Assumption is used in the proof but not stated in the model
  → Problem: hidden assumption gap

### 3B: Exploitable Model Properties

When the model provides MORE than the theory uses (OVER-SPECIFIED), list improvements:

```markdown
## Exploitable Properties

| Model property | Theory uses only | Could exploit for | Potential improvement |
|---------------|-----------------|-------------------|---------------------|
| Gaussian noise | Sub-Gaussian bound | Exact Gaussian tail | Remove log factors, exact constants |
| Linear model | Generic Lipschitz | Linear structure | Parametric rate n^{-1/2} instead of nonparametric |
| Sparse signal | Dense estimation | Sparsity + LASSO theory | Rate s·log(d)/n instead of d/n |
| Known covariance | Unknown Σ bounds | Plug-in Σ | Remove condition number dependence |
```

### 3C: Theory-Model Gap Resolution Strategies

For each MISMATCH, propose a resolution:

1. **Weaken the assumption** to match what the model actually provides (→ Step 1)
2. **Strengthen the model description** if the model does satisfy the condition but
   the paper didn't state it explicitly
3. **Add a bridging lemma** that derives the theoretical condition from model properties
4. **Acknowledge the gap** as a limitation and suggest it for future work

---

## Step 4: Theory-Experiment Alignment Audit

Check whether the theoretical predictions are actually testable and tested.

### 4A: Coverage Check

```markdown
| Theoretical result | Experimentally verified? | How? | Discrepancy? |
|-------------------|------------------------|------|-------------|
| Thm 1: √n-consistency | Yes — Fig 3 shows convergence | MSE vs n plot, slope ≈ -1 | ALIGNED |
| Thm 2: Uniform over Θ | No — only fixed θ tested | — | NOT TESTED |
| Thm 3: d can grow with n | Partially — d=50,100,500 but n fixed | Only 3 dimension values | WEAK EVIDENCE |
| Cor 1: Asymptotic normality | No — no QQ plots or coverage | — | NOT TESTED |
| Rate: O(n^{-1/2}) | Contradicted — empirical rate ≈ n^{-1/3} | Log-log regression in Fig 4 | CONTRADICTION ⚠ |
```

### 4B: Experimental Gap Analysis

**Theory predicts but experiments don't test**:
- Missing experiments → suggest what to add
- Untestable predictions → note as limitation

**Experiments show but theory doesn't cover**:
- Empirical success beyond theoretical regime → opportunity to strengthen theory
- Empirical failure where theory predicts success → possible theoretical error

**Theory and experiments contradict**:
- Empirical rate worse than theoretical rate → check:
  - Is sample size large enough for asymptotics to kick in?
  - Is a hidden constant very large?
  - Is there an error in the proof?
- Empirical rate better than theoretical rate → check:
  - Is the theoretical bound loose?
  - Is the model providing extra structure not captured by theory?

### 4C: Regime Relevance Check

Do the theoretical conditions match realistic experimental settings?

```markdown
| Condition | Theory requires | Experiments use | Practice needs | Relevance |
|-----------|----------------|----------------|----------------|-----------|
| n ≥ C·d² | n > d² | n=1000, d=50 (n=0.4d²) | n ≈ d typical | IMPRACTICAL — threshold too high |
| ε ≤ 1/d | vanishing ε | ε = 0.1 | small but fixed ε | POSSIBLY OK |
| T → ∞ | asymptotic | T = 100 iterations | fixed budget | FINITE-SAMPLE NEEDED |
| σ known | known noise level | estimated σ̂ | unknown σ | PLUG-IN ANALYSIS NEEDED |
```

If theoretical conditions are impractical, suggest:
- Finite-sample versions of asymptotic results
- Conditions in terms of observable quantities (not unknown parameters)
- Adaptive procedures that don't require knowing constants

---

## Step 5: Literature Benchmarking

Compare the paper's results against the current state of the art.

### 5.cache: Cache-consult first (mandatory)

Before any web search, consult the durable literature cache. Protocol in `../stat-shared-references/literature-cache-protocol.md`. For Step 5 (benchmarking) the typical loads are:

- `literature-cache-protocol.md` (router).
- `citation-purpose-protocol.md` — benchmarking citations are typically `benchmark_claim` (rate / constant comparison) or `lineage_positioning` (placing the work in a methodological line). `independently_checked` floor for both.
- `applicability-axes.md` — to verify the cached competitor's axes match the paper's setting.

Read the INDEX and the domain shards relevant to the paper's `primary_line` (in the `theoretical_lineage` declared earlier). Cache hits at `independently_checked` cover direct competitors and assumption frontier without a fresh fetch; misses go to the three search agents below.

### 5A: Venue-Tiered Literature Search

Apply the venue credibility tiers from `/proof-repair`:

**T1 Priority**: AoS, JASA, JRSS-B, Biometrika, Econometrica, JOE, NeurIPS, ICML,
ICLR, COLT, JMLR, Math Programming, SIAM Opt

Search strategy (parallel agents):

**Agent 1: Direct Competitors**
```
Search for papers solving the SAME problem with DIFFERENT techniques.
Queries:
- "[problem name] convergence rate" + venue filter
- "[problem name] optimal rate minimax"
- "[model class] estimation [loss function]"
Focus: results from last 5 years in T1 venues
Extract: their assumptions, their rates, their technique
```

**Agent 2: Assumption Frontier**
```
Search for papers solving SIMILAR problems under WEAKER assumptions.
Queries:
- "[problem name] without [strong assumption]"
- "[problem name] heavy-tailed" / "dependent data" / "high-dimensional"
- "[technique name] relaxed conditions"
Focus: which assumptions have been successfully relaxed in related work?
```

**Agent 3: Rate Frontier**
```
Search for the BEST KNOWN rates for this problem class.
Queries:
- "[problem class] minimax rate"
- "[problem class] optimal estimation"
- "[problem class] lower bound information-theoretic"
Focus: minimax lower bounds, matching upper bounds, rate-optimal procedures
```

### 5B: Competitive Positioning Table

```markdown
## Competitive Positioning

| Paper | Venue (Tier) | Year | Assumptions | Rate | Technique | vs. Ours |
|-------|-------------|------|-------------|------|-----------|----------|
| This paper | — | — | A1-A4 | n^{-1/2} | M-estimation + Poisson eq | BASELINE |
| Chen & Li | AoS (T1) | 2022 | A1-A3 (no A4) | n^{-1/2} | Empirical process | WEAKER ASSUMPTIONS, SAME RATE |
| Zhang et al. | NeurIPS (T1) | 2023 | A1-A4 + sparsity | s·log(d)/n | LASSO-type | SHARPER UNDER SPARSITY |
| Wang | JMLR (T1) | 2021 | A1-A2 only | n^{-1/3} | Robust estimation | WEAKER ASSUMPTIONS, WORSE RATE |
| Kim & Park | Econometrica (T1) | 2023 | A1-A4 | n^{-1/2} | GMM | SAME RESULT, DIFFERENT TECHNIQUE |
| Lower bound: Tsybakov | AoS (T1) | 2009 | Nonparametric class | n^{-2/(2+d)} | Le Cam / Fano | OUR RATE IS OPTIMAL IN FIXED-d |

## Key Findings
1. Chen & Li (2022) achieved the same rate without A4 → our A4 may be removable
2. Under sparsity (Zhang 2023), sharper rate is possible → extension opportunity
3. Our rate matches the minimax lower bound → rate is tight (strength to highlight)
4. No competitor handles the adaptive design setting → our contribution is unique here
```

### 5C: Gap-to-Frontier Analysis

For each gap between this paper and the frontier:

```markdown
| Gap | Frontier paper | What they achieved | What we'd need to match | Feasibility | Priority |
|-----|---------------|-------------------|------------------------|-------------|----------|
| A4 removable | Chen & Li (2022) | Same rate without A4 | Replace Lemma C.3 technique | MEDIUM | HIGH |
| Log factor | Zhang (2023) | No log in uniform bound | Use chaining instead of net | LIKELY | HIGH |
| Heavy tails | Lugosi & Mendelson (2019) | Bounded 2nd moment only | Median-of-means wrapper | HARD | MEDIUM |
```

---

## Step 5B: Codex Independent Assessment (if Codex MCP available)

Send the sharpening analysis to Codex per `../stat-shared-references/codex-protocol.md`
for an independent read on three questions: which relaxations are genuinely feasible,
whether the rates are actually sharp, and which theory-practice gaps a referee will
raise first.

Reconcile per finding with an explicit disposition and reasoning. Codex disagreeing
does not make a relaxation infeasible, and Codex agreeing does not make one feasible —
the literature support and the proof sketch decide that. Record both positions where
they differ.

Reconciliation shape and a worked exchange:
`../stat-shared-references/examples/theory-sharpen-codex-example.md`.

## Step 6: Improvement Roadmap

Synthesize all findings (Claude + Codex) into a prioritized improvement plan.

### 6A: Priority Scoring

Score each potential improvement on five dimensions:

| Dimension | Weight | Scale |
|-----------|--------|-------|
| **Impact on main result** | 3× | 1 (cosmetic) – 5 (transforms the paper's contribution) |
| **Feasibility** | 2× | 1 (requires fundamentally new ideas) – 5 (standard technique, literature exists) |
| **Literature support** | 2× | 1 (no known technique) – 5 (textbook result from T1 source) |
| **Alignment payoff** | 1× | 1 (only theoretical elegance) – 5 (resolves theory-experiment contradiction) |
| **Reviewer demand** | 1.5× | 1 (rarely asked) – 5 (routinely demanded at target venue) |

Priority = 3×Impact + 2×Feasibility + 2×Literature + 1×Alignment + 1.5×Reviewer

*The "Reviewer demand" dimension addresses what top-venue reviewers actually ask for
(Step 2E). Weight is 1.5× (intermediate) — not so high that it dominates Impact, but
high enough to push reviewer-targeted improvements up the priority list.*

*Tuning tip: For a paper aimed at a SPECIFIC venue, customize the Reviewer-demand
scoring by reviewer profile:*
- *AoS/Biometrika*: weight lower bounds, inference/UQ, adaptivity higher
- *Econometrica/JOE*: weight identification, robustness, uniformity higher
- *NeurIPS/ICML/COLT*: weight computational attainability, structural guarantees higher

### 6B: Improvement Roadmap Table

```markdown
| Rank | Improvement | Type | Impact | Feas | Lit | Align | Reviewer | Score | Key reference |
|------|------------|------|--------|------|-----|-------|----------|-------|---------------|
| 1 | Remove log factor in Thm 3 | Rate-Sharpen | 4 | 5 | 5 | 3 | 4 | 41.0 | Talagrand (2014) |
| 2 | Remove Assumption A4 | Assumption-Relax | 5 | 3 | 4 | 4 | 5 | 40.5 | Chen & Li (2022, AoS) |
| 3 | Heavy-tail extension | Assumption-Relax | 3 | 3 | 5 | 5 | 4 | 36.0 | Lugosi & Mendelson (2019, AoS) |
| 4 | Finite-sample version of Thm 1 | Regime-Extend | 4 | 4 | 3 | 5 | 3 | 35.5 | — (needs new analysis) |
| 5 | Exploit Gaussian structure | Model-Exploit | 2 | 5 | 5 | 2 | 2 | 31.0 | — (standard) |

Every row carries all five 6A dimensions, including Reviewer demand; a table that drops
a dimension silently changes the ranking the formula produces.
```

### 6C: Per-Improvement Specification

For each top-ranked improvement, write:

```markdown
## Improvement I-1: Remove log factor in Theorem 3

### Current state
Theorem 3 claims ‖θ̂ − θ*‖ = O(√(d log n / n)) uniformly over Θ.
The log n factor comes from a union bound over an ε-net in the proof of Lemma D.4.

### Target state
Replace with ‖θ̂ − θ*‖ = O(√(d / n)), matching the minimax lower bound.

### Technique
Replace ε-net + union bound (Lemma D.4, lines 842-867) with Dudley's entropy
integral or generic chaining (Talagrand 2014).

### Which proof steps change
- Lemma D.4: replace entirely with chaining-based uniform bound
- Theorem 3 proof: update the line citing Lemma D.4's bound
- No other lemmas affected (D.4 is used only by Theorem 3)

### Literature support
| Reference | Venue (Tier) | Credibility | What it provides |
|-----------|-------------|-------------|------------------|
| Talagrand (2014), Upper and Lower Bounds for Stochastic Processes | Springer (T1) | GOLD | Generic chaining removes log factors |
| van der Vaart & Wellner (1996), Weak Convergence, Ch. 2.5 | Springer (T1) | GOLD | Dudley entropy integral |
| Wainwright (2019), High-Dimensional Statistics, Ch. 5 | Cambridge (T1) | GOLD | Localized Rademacher complexity |

### Alignment impact
- Resolves log n discrepancy between theoretical rate and empirical rate in Fig 4
- Makes the bound match the information-theoretic lower bound exactly

### Downstream effects
- Theorem 3 rate improves: this propagates to Corollary 3.1 and Section 5 applications
- No assumptions change → all existing results remain valid

### Estimated effort
MEDIUM — requires rewriting one lemma proof (Lemma D.4) using chaining technique.
The technique is standard in empirical process theory.

### Connection to pipeline
- If accepted: feed to `/proof-repair` as a voluntary improvement (not a bug fix)
- The new Lemma D.4 proof should be written via `/proof-writer` with full rigor
```

---

## Step 7: Write SHARPEN_REPORT.md

Write `papers/<paper-name>/SHARPEN_REPORT.md`:

```markdown
# Theory Sharpening Report: [Paper Title]

## Executive Summary
- Assumptions analyzed: N
- Relaxable assumptions: K (M with T1 literature support)
- Rates analyzed: R
- Sharpenable rates: S
- Theory-model gaps: G_M
- Theory-experiment gaps: G_E
- Top priority improvements: [list top 3]

## Theory-Model-Experiment Alignment Matrix
[From Step 0C]

## Assumption Relaxation Opportunities
### Feasible (T1 literature support)
[table]
### Possible (T2/T3 support or new technique needed)
[table]
### Infeasible (fundamental barriers)
[table]

## Rate Sharpening Opportunities
### Achievable (known techniques)
[table]
### Research-level (requires new ideas)
[table]

## Minimax Optimality Status
| Result | Current rate | Minimax lower bound | Optimal? | Gap source |

## Theory-Model Gaps
[From Step 3A-3C, with resolution strategies]

## Theory-Experiment Gaps
[From Step 4A-4C, including contradictions]

## Competitive Positioning
[From Step 5B — how this paper compares to state of the art]

## Codex Cross-Assessment (independent second opinion)
### Agreement summary
- Findings where Claude + Codex agree: X (HIGH confidence)
- Findings where they disagree: Y (needs human review ⚠)
- Findings only Codex found: Z (added to roadmap)
[From Step 5B Codex reconciliation table]

## Improvement Roadmap (prioritized)
[From Step 6B — ranked improvements with scores, integrating Codex findings]

## Detailed Improvement Specifications
[From Step 6C — one section per top improvement]

## New References
| # | Key | Full citation | Venue (Tier) | Credibility | Supports |
[All references found, venue-tiered]

## Recommended Actions for Authors
### Quick wins (1-2 days each)
1. [improvement]
### Medium effort (1-2 weeks each)
1. [improvement]
### Future work suggestions
1. [improvement]
```

Also write supporting files:
- `papers/<paper-name>/sharpen_references.bib` — BibTeX for all new references
- `papers/<paper-name>/audit/08_sharpen/` — per-improvement detail files

---

## Quick Mode

For a targeted analysis of a SINGLE aspect:

```
/theory-sharpen papers/my-paper/ --assumptions     # Only Step 1
/theory-sharpen papers/my-paper/ --rates           # Only Step 2
/theory-sharpen papers/my-paper/ --alignment       # Only Steps 3-4
/theory-sharpen papers/my-paper/ --benchmark       # Only Step 5
/theory-sharpen papers/my-paper/ --unit "Theorem 3" # Full analysis, single result
```

---

## Output Summary

When complete, report to user:

```
Theory sharpening analysis complete for [Paper].

Alignment status:
├── Theory-Model:      X aligned, Y gaps found
├── Theory-Experiment: X aligned, Y gaps, Z contradictions
└── Literature position: [ahead of / on par with / behind] frontier

Improvement opportunities:
├── Assumption relaxation:  K feasible (M with T1 refs)
├── Rate sharpening:        S achievable
├── Model exploitation:     E unexploited properties
└── Experiment coverage:    G untested predictions

Top 3 priorities:
1. [I-1: description] — Score: 35, T1 refs available
2. [I-2: description] — Score: 33, T1 refs available
3. [I-3: description] — Score: 30, needs new analysis

Files created:
├── SHARPEN_REPORT.md — full analysis
├── sharpen_references.bib — new BibTeX entries
└── audit/08_sharpen/ — per-improvement details

Next steps:
  /proof-repair papers/my-paper/ — to implement chosen improvements
  /proof-writer [specific improved claim] — to write new proofs
```
