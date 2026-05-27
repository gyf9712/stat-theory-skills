---
name: theory-design
description: >-
  Design a coherent theoretical framework for a new statistics / ML theory
  research topic, paper-type aware. Three modes — Theory paper (explain phenomena
  or provide new theoretical tools), Methodology paper (propose a new method with
  theoretical guarantees), Application paper (apply existing methods to scientific
  data with assumption verification). Each mode walks a different logical order:
  the centerpiece of a theory paper is the theorem itself, of a methodology paper
  the estimator, of an application paper the empirical findings. Mandatory literature
  anchoring step (recent top-venue papers) identifies the field's theoretical
  inertia and positioning options BEFORE any phase decision, then constrains every
  subsequent decision. Produces FRAMEWORK_DESIGN.md + LITERATURE_ANCHOR.md that
  downstream skills (proof-writer, theory-simulation, proofcheck) consume. Use when
  user says "design theory framework", "理论框架设计", "新课题怎么开始", "新方向
  design", "from scratch theory", "构建理论框架", "start a new topic", or asks for
  the logical order to build a statistics paper's theoretical content from a blank
  page.
argument-hint: [topic-or-rough-idea]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, WebSearch, WebFetch
model: opus
---

# Theory-Design — Paper-Type-Aware Theoretical Framework Design

> 🔬 **Model Recommendation**: Run this skill on **Claude Opus** for best results.
> Framework design requires deep reasoning across mathematical and methodological
> dimensions. If your session is not on Opus, run `/model opus`.

Goes from "I have a new research topic" to a structured **FRAMEWORK_DESIGN.md**
that downstream skills can consume. The skill's central insight: **the logical
order of theoretical-framework design depends on what kind of paper you're writing.**

## Context: $ARGUMENTS

---

## Pipeline Position

```
research-refine  →  /theory-design  →  /proof-writer  →  /theory-simulation  →  /proofcheck  →  /theory-sharpen  →  /proof-repair
(rough idea)        (framework)        (theorems)        (verify)              (audit)         (improve)           (fix)
```

This skill is the **planning layer** — chooses the framework, declares assumptions,
sets target results — before any theorem is written or experiment run.

---

## Step 0: Declare paper type (MANDATORY first decision)

Statistics papers come in three types with **fundamentally different logical
orders**. The skill REFUSES to proceed until the user declares type. If unsure,
the skill helps classify based on the topic description.

### The three paper types

| Type | Contribution | Theory's role | Estimator | Lower bound | Simulation | Real data |
|------|-------------|---------------|-----------|-------------|-----------|-----------|
| **THEORY** | New theoretical tool, explanation of phenomenon, impossibility result | The contribution itself | Often none/abstract | Often equally important to upper bound | Illustrative | Rarely |
| **METHODOLOGY** | A new method (estimator/test/algorithm) | Guarantees statistical correctness of method | The centerpiece | Sometimes | Validating | Usually demonstrating |
| **APPLICATION** | New empirical insight on scientific data | Supports / justifies method choice | Uses existing | Almost never | Almost never | The main event |

### Decision aid (if user is unsure)

Ask in order:

1. **Is your contribution primarily**:
   - a new mathematical insight / theorem / theoretical tool → THEORY
   - a new procedure / algorithm / estimator → METHODOLOGY
   - a new finding from analyzing real data → APPLICATION

2. **What would the "main result" section show?**
   - A theorem (rate, distribution, lower bound, characterization) → THEORY
   - Properties of a procedure (consistency, rate, coverage of the procedure) → METHODOLOGY
   - Tables/figures of empirical estimates and p-values from real data → APPLICATION

3. **What does the reviewer most care about?**
   - Mathematical novelty and proof rigor → THEORY
   - Whether the method works better than competitors + has theoretical backing → METHODOLOGY
   - Substantive scientific conclusion + valid inference → APPLICATION

If still unclear: the topic might be a hybrid; force a choice and revisit.

### Mode routing

Based on declared type, the skill runs ONE of three workflows:
- **Theory mode** → Step T1-T7
- **Methodology mode** → Step M1-M7
- **Application mode** → Step A1-A7

But FIRST, regardless of mode, run Step 0.5.

---

## Step 0.5: MANDATORY Literature Anchoring

**This step is NON-NEGOTIABLE.** A theoretical framework designed without
literature context is almost certainly either:
- Reinventing what's already done
- Deviating from field conventions for no reason
- Missing the "theoretical inertia" — how the community frames this problem
- Unpositioned — making it hard to assess the contribution

Build the literature anchor BEFORE any phase decision. Every subsequent phase
must reference back to this anchor when making a choice.

### 0.5A: Topic signature for search

Build a structured topic signature for the search queries:

```
Topic signature:
- Primary subject:     [1-3 word phrase, e.g., "treatment effect estimation"]
- Method/technique:    [e.g., "doubly robust", "Poisson equation", "lasso", "M-estimation"]
- Data structure:      [iid / TS / mixing / Markov / panel / spatial / sequential / network]
- Modeling framework:  [parametric / semiparametric / nonparametric]
- Regime:              [classical / proportional / high-d / non-asymptotic / online]
- Application area (if applicable): [causal inference / genomics / finance / etc.]
```

### 0.5B: Multi-source T1 literature search (parallel)

Run in parallel — use Agent tool for each search agent:

**Agent 1: T1 statistics journals (last 5 years preferred)**
```
Search Semantic Scholar API:
  query = [topic signature components]
  year = current_year - 5 .. current_year
  venue ∈ {Annals of Statistics, JASA T&M, JASA ACS, AOAS, JRSS-B, Biometrika,
            Bernoulli, EJS, Statistica Sinica, Biostatistics, JCGS}
  fields = title, authors, year, abstract, venue, citationCount, externalIds

Apply filters:
  - Sort by recency; prefer last 3 years
  - Drop low-citation older papers
  - Keep top 10-15 most-relevant
```

**Agent 2: T1 ML/AI conferences (last 5 years preferred)**
```
WebSearch + Semantic Scholar:
  query = [topic signature components]
  venue ∈ {NeurIPS, ICML, ICLR, COLT, AISTATS, JMLR, UAI}
  
Same filtering rules.
```

**Agent 3: T1 econometrics journals (if applicable)**
```
Search:
  venue ∈ {Econometrica, Journal of Econometrics (JOE), Review of Economic Studies,
            Quantitative Economics, JBES, Econometric Theory, RFS, JF}
```

**Agent 4: Highly-cited "consensus" papers (last 10 years)**
```
Search:
  query = broader topic signature
  sort = citationCount desc
  year = current_year - 10 .. current_year
  limit = 10

Purpose: identify what the field considers CANONICAL recent work
(papers that define the current framework).
```

### 0.5C: Extract from each found paper

For each paper, extract structured information:

```markdown
## [Paper N] Author (Year, Venue, citations)

### Problem framing
- How is the problem stated?
- What gap does it address?
- One-sentence contribution

### Theoretical anchor
- Data structure used
- Modeling framework
- Asymptotic regime
- Target estimand/object

### Assumption profile
- Key assumptions (≤5)
- Anything unusual or contested

### Result type
- Rate / asymptotic distribution / coverage / lower bound / structural recovery?

### Proof technique
- Main tool used

### Position in literature
- Direct predecessor it extends
- Alternative approach it competes with
```

Compile into `papers/<paper-name>/design/LITERATURE_ANCHOR.md`.

### 0.5D: Identify the "theoretical inertia"

From the extracted papers, identify the **current consensus framework**:

```markdown
## Theoretical Inertia of the Field

### Default data structure: [most common across recent T1 papers]
Example: "Most recent CATE papers use i.i.d. observations even when
applications are clustered."

### Default modeling framework: [most common]
Example: "Semiparametric framework with infinite-dim nuisance is dominant
for treatment effect since Robins-Rotnitzky-Zhao (1994); pure parametric
is now rare."

### Default asymptotic regime: [most common]
Example: "Non-asymptotic high-d bounds with sparsity have become standard
in the last 5 years; classical asymptotic n→∞ with d fixed is now seen
as a special case to confirm."

### Default proof technique: [most common]
Example: "Cross-fitting + orthogonal scores is now the dominant proof
technique in this subfield (Chernozhukov et al. 2018)."

### Default contribution shape
Example: "Recent papers tend to: (a) propose a new method, (b) prove
n^{-1/2} rate under semiparametric assumptions, (c) demonstrate finite-sample
performance via simulation."
```

This is the **inertia** — the path of least resistance for the field. You can
either follow it (lower friction in review) or deviate from it (higher reward
but must justify the deviation).

### 0.5E: Identify positioning options

For your contribution, where does it sit relative to the inertia?

```markdown
## Positioning Options

### Option 1: INCREMENTAL — refine within the inertia
- Adopts default data structure, framework, regime
- Provides a sharper rate, weaker assumption, OR new estimator in the standard frame
- Easier to review and publish (referees see a familiar landscape)
- Lower-novelty perception unless the refinement is technically substantial

### Option 2: LATERAL — same problem, different angle
- Same problem, but pick an alternative framework or regime
- Example: most CATE papers use cross-fitting; you might use posterior contraction
- Must justify why your angle reveals something the standard angle misses
- Higher review difficulty (referee needs to be familiar with your alternative)

### Option 3: DISRUPTIVE — challenges the inertia
- Argues the standard framework is wrong / suboptimal / mis-applied here
- Requires either (a) a counterexample showing standard framework fails, or
  (b) a new framework that supersedes the standard
- Highest reward, highest risk; usually requires a paper-length argument for the
  reframing itself
```

For each option, also identify:
- Which T1 venues are most receptive
- Which 3-5 reference papers should be cited for positioning

### 0.5F: Anchor → design constraints

The literature anchor feeds into every subsequent phase as constraints:

```markdown
## Constraints derived from anchor

For Step 1 (problem framing):
- The motivation must distinguish from [list 3 most similar papers]
- The gap must be precisely articulated; vague gaps will be attacked

For Step 2-3 (model/framework choice):
- If you adopt the inertia: cite [canonical papers]
- If you deviate: justify deviation with [specific reasoning]

For Step 5-6 (target results / proof):
- Your rate must beat / match / explicitly differ from [best known: list]
- Your proof technique should either use [dominant tool] or justify why not

For Step 7 (downstream connections):
- Specify which existing papers your work supersedes or complements
```

### 0.5G: Mandatory user confirmation

Present the LITERATURE_ANCHOR.md to the user. Force confirmation:

```
"Here is the literature anchor for your topic.

  - X recent T1 papers identified
  - Theoretical inertia: [summary]
  - Recommended positioning: [option]

Do you confirm this anchor before proceeding to framework design?"
```

User can: confirm / correct misreadings / add papers / change positioning.

Without explicit confirmation, the skill REFUSES to proceed to Step T1/M1/A1.

---

## THEORY MODE (T1-T7)

Centerpiece: the theorem itself. Estimator often degenerate or absent.

### T1: Phenomenon / object identification

```
Q1.1: What mathematical phenomenon, object, or impossibility are you trying to
      characterize, explain, or formalize?
      (Examples: BBP transition in high-dim regression; new concentration
       inequality for dependent data; minimax lower bound for a new class)

Q1.2: Is this an explanation of an observed effect, the introduction of a new
      abstraction, or both?

Q1.3: Why is the current theoretical toolkit insufficient?
      State precisely the technical step that cannot be handled by existing tools.
```

### T2: Mathematical landscape mapping

```
Q2.1: What existing theoretical frameworks are most relevant?
      (Empirical process / RKHS / random matrix / convex analysis / information
       theory / Markov chains / ...)

Q2.2: Which tools from each framework can be reused?
      Which need extension or replacement?

Q2.3: Are there sibling results in adjacent fields (probability, optimization,
      info theory) that solved analogous structures?

Q2.4: Do a quick T1 literature scan for related results in the last 5 years.
      Save findings to FRAMEWORK_DESIGN.md as the "landscape" section.
```

### T3: Conceptual framework & notation

```
Q3.1: At what level of abstraction does the theory live?
      (Pointwise theorem / parameter class / function class / operator level)

Q3.2: What is the right notation system?
      Compatible with which existing literature?
      Where to introduce new notation? (do so sparingly)

Q3.3: What is the underlying probability space / σ-algebra / filtration setup
      if dependence or sequential structure is involved?
```

### T4: Formal problem setup

```
Q4.1: Define the spaces, parameter classes Θ, function classes F, etc.
      Be explicit about: domain, range, topology, measure.

Q4.2: Regularity on the PROBLEM (not on methods):
      - Smoothness of underlying object?
      - Identifiability conditions?
      - Boundedness / tail behavior?

Q4.3: Asymptotic regime (which path is taken to ∞?)
      Same axes as theory-sharpen: classical / proportional / sparse / non-asymptotic / online.
```

### T5: Target theorems (conjectures + impossibility)

This is where theory papers differ most from methodology: **both upper and lower
bounds are equally first-class citizens.**

```
Q5.1: Upper-bound conjecture: what positive result do you AIM to prove?
      Write a placeholder theorem statement.

Q5.2: Lower-bound conjecture: what impossibility result is needed to certify the
      rate / characterization is sharp?
      (Minimax via Fano / Le Cam / Assouad; or worst-case lower bound)

Q5.3: Are upper and lower bounds going to match? (If not, the gap is itself a
      contribution or a future-work problem.)

Q5.4: Auxiliary theorems: are there secondary results (consistency, structural
      characterization, phase transitions) that strengthen the paper?

Q5.5: For each target theorem: sketch the regime / parameter range where it should hold.
```

### T6: Proof strategy & lemma scaffold

```
Q6.1: High-level path: direct / contradiction / induction / coupling /
      reduction / construction / variational?

Q6.2: Major decomposition (if any): e.g., bias + variance, oracle + remainder,
      martingale + drift, signal + noise, low-rank + sparse.

Q6.3: Key tools needed: chaining / localization / Bernstein / Poisson equation /
      decoupling / spike-and-slab / random matrix concentration / etc.

Q6.4: Anticipated hardest step: where do you expect the proof to fight back?
      Have related papers handled similar difficulties?

Q6.5: Lemma scaffold: list 3-8 auxiliary lemmas you anticipate needing.
      (proof-writer can later be invoked to draft each)

Q6.6: Sketch a proof outline (≤ 1 page) BEFORE detailed proving.
```

### T7: Connections (open to downstream)

```
Q7.1: What method designs does this theory enable / inform?
      (Theory paper authors should NOT design the method here; they should
       enumerate what becomes possible.)

Q7.2: Who will cite this paper? (theorists / methodologists / applied users)
      What is the chain of impact?

Q7.3: Open problems your theory raises but doesn't solve.
      These go in the Discussion section and seed future papers.
```

After T1-T7, FRAMEWORK_DESIGN.md is complete. Hand off:
- T5 conjectures → `/proof-writer` to draft theorem statements
- T6 lemma scaffold → `/proof-writer` to draft each lemma
- Optional simulation illustration → `/theory-simulation` (lightweight DESIGN mode)
- After proofs drafted → `/proofcheck`

---

## METHODOLOGY MODE (M1-M7)

Centerpiece: a new method. Theory exists to guarantee the method.

### M1: Practical problem & method gap

```
Q1.1: What practical statistical problem motivates the new method?
      (Examples: causal inference under unmeasured confounding; high-dim variable
       selection with grouped sparsity; nonparametric test for monotonicity)

Q1.2: What can existing methods NOT do, or do poorly?
      Be precise: name the existing methods and the specific gap.

Q1.3: Who needs the new method? (Sub-discipline / data modality / problem class)
```

### M2: Method design (CENTERPIECE — differs most from theory papers)

```
Q2.1: Define the estimator / algorithm / procedure precisely.
      Pseudo-code or formula.

Q2.2: Tuning parameters: list each (λ, h, K, ...).
      How will each be chosen in practice? (CV, plug-in, BIC, oracle?)

Q2.3: Computational considerations:
      - Closed-form vs iterative?
      - Complexity in n, d?
      - Scalability claim — paper will need /theory-simulation computational audit
        if claimed.

Q2.4: Does the method use cross-fitting / sample splitting / debiasing?

Q2.5: Sanity checks: can the method be a wrong choice?
      Are there degenerate inputs where it fails?
```

### M3: Model setup for analysis

```
Q3.1: Under what DGP / model class will you ANALYZE the method?
      (Should be realistic enough to be useful, not so general that proofs become
       impossible.)

Q3.2: Data structure (i.i.d. / mixing / Markov / panel / spatial / sequential)?

Q3.3: Asymptotic regime to target (n→∞, d→∞, sparsity, ...)?

Q3.4: Pre-declare which assumptions will likely show up in analysis (without
      committing yet — this is the rough plan).
```

### M4: Identification

```
Q4.1: Is the target estimand identified under your model?
      What conditions are needed?

Q4.2: Can identification fail for plausible data configurations?
      Address weak / partial / no identification explicitly.

Q4.3: Are identification conditions VERIFIABLE in data, or only theoretical?
      (E.g., positivity in causal inference is verifiable; no-unobserved-confounding
       is not.)
```

### M5: Theoretical guarantees needed

```
Q5.1: Required guarantees (in order of necessity):
      - Consistency? (almost always required)
      - Rate of convergence? (required for parametric / nonparametric / high-dim)
      - Asymptotic distribution / CLT? (required for inference)
      - Coverage of CIs? (if paper claims inference)
      - Uniformity over Θ? (if claimed; otherwise weaker pointwise suffices)
      - Structural recovery? (if claimed)

Q5.2: Robustness guarantees:
      - To misspecification?
      - To contamination / outliers?
      - To dependence violations?

Q5.3: What's the MINIMAL assumption set that gives the guarantees?
      Iterate this — start broad, narrow down.

Q5.4: Computational guarantees if relevant:
      - Convergence of iterative procedure?
      - Step size conditions?
      - Local-vs-global optimum?
```

### M6: Simulation + real-data validation plan

(Methodology papers REQUIRE both. Application is mostly demonstration.)

```
Q6.1: Simulation plan: hand off to /theory-simulation DESIGN mode
      - rate verification along asymptotic path
      - inference diagnostics (coverage, size, power, EmpSE/ModSE)
      - stress tests on each critical assumption
      - paired comparison against ≥1 competitor

Q6.2: Real data application:
      - Which dataset? Why is it the right test case?
      - Is the application demonstrating practicality, not proving anything new?
      - What assumption-checking will be done on the data?
```

### M7: Proof strategy

```
Q7.1: Proof approach: M-estimation framework / influence function expansion /
      empirical process / regularization theory / etc.

Q7.2: Decomposition: typically bias + variance, or oracle + remainder for
      cross-fitting.

Q7.3: Key technical lemmas (often more "technical labor" than in theory papers):
      list 3-10 lemmas needed.

Q7.4: Are you proving NEW theory, or using EXISTING theory?
      For methodology papers, the proof is usually technical labor applying
      existing theory to your specific method. State this honestly.
```

After M1-M7, hand off:
- M2 method definition → can be implemented in code
- M5 target guarantees → `/proof-writer` to write theorem statements
- M6 validation plan → `/theory-simulation` (DESIGN mode)
- M7 proof strategy → `/proof-writer` for each guarantee
- After proofs → `/proofcheck`

---

## APPLICATION MODE (A1-A7)

Centerpiece: the empirical insight. Method is chosen, not invented.

### A1: Scientific question & data

```
Q1.1: What scientific / economic / medical question motivates this paper?
      Articulate as a sharp hypothesis or estimation target.

Q1.2: What data answers this question?
      - Source, size, structure
      - Strengths and weaknesses
      - Why this data and not other data?

Q1.3: Who is the audience? (Domain experts? Statisticians?)
      Tone and depth of statistical detail varies.

Q1.4: What is the substantive prior? (Effect direction, magnitude, mechanism?)
```

### A2: Existing-method selection

```
Q2.1: Which existing methods match (data structure, question)?
      List 2-3 candidates with pros/cons.

Q2.2: Why this specific method?
      State the trade-off and justify.

Q2.3: Is any method modification needed?
      If yes — this might be METHODOLOGY mode, not APPLICATION; reconsider.

Q2.4: What recent methodological developments could improve this analysis?
      (Don't necessarily use them — but show awareness.)
```

### A3: Assumption verification on THIS dataset (distinguishes APP from METH)

This is the central technical content of application papers.

```
Q3.1: For each assumption of the chosen method, ask:
      - Is it VERIFIABLE in the data? How?
      - If verifiable: what is the test/diagnostic? What's the result?
      - If not: what plausibility argument substitutes for verification?

Q3.2: Standard checks for common methods:
      - Causal inference: positivity (verifiable), no-unmeasured-confounding (sensitivity)
      - Regression: linearity (residual plots), homoskedasticity (Breusch-Pagan), normality (QQ)
      - Time series: stationarity (KPSS), mixing structure
      - High-dim: sparsity heuristics, RE condition (approximate check)

Q3.3: For untestable assumptions: design sensitivity analyses (Rosenbaum-style,
      E-value, partial identification bounds, etc.)
```

### A4: Empirical findings (the main result)

```
Q4.1: Primary estimand and its estimate; effect size, direction.

Q4.2: Comparison: does this estimate confirm, refine, or contradict prior literature?

Q4.3: Subgroup / heterogeneity analyses: preregistered or exploratory?
      Multiplicity correction if exploratory.

Q4.4: Reporting standards for the field (CONSORT, STROBE, REMARK, etc.)
```

### A5: Inference & uncertainty quantification

```
Q5.1: What standard error / confidence interval procedure is used?
      Does the chosen method's theoretical assumptions for inference hold here?

Q5.2: Bootstrap, asymptotic, or finite-sample?
      Validity check: does the inference procedure have theoretical backing in
      the regime of this data (n, d, structure)?

Q5.3: Multiple testing strategy if applicable.

Q5.4: Coverage / size diagnostics on simulated data calibrated to the real data
      (optional but strengthens the paper).
```

### A6: Sensitivity analyses

```
Q6.1: To untestable assumptions:
      - Causal: unmeasured confounding (Rosenbaum sensitivity, E-value)
      - Missing data: NMAR scenarios
      - Model: alternative specifications

Q6.2: To outliers / influential observations:
      - Influence diagnostics
      - Trimmed / robust estimators as comparison

Q6.3: To pre-processing decisions:
      - Variable transformations
      - Sample inclusion / exclusion

Q6.4: Pre-specify which sensitivity results would CHANGE the conclusion.
```

### A7: Connection to literature & implications

```
Q7.1: How do findings update the scientific literature?
      Specific claims that this paper supports, modifies, or refutes.

Q7.2: Policy / clinical / scientific implications.
      Be honest about external validity.

Q7.3: Open questions and future-work directions.
```

After A1-A7, hand off:
- A3 verification → coded diagnostics
- A4-A5 main analysis → coded analysis pipeline
- A6 sensitivity → coded sensitivity analyses
- Optional methodology gap notes → could spawn a METHODOLOGY paper later

---

## Step X: Cross-type quality checks (run for ALL modes)

After the type-specific workflow, run these universal checks:

### X1: Internal consistency

```
- Does the model in Step 3/4 (depending on mode) match what the assumptions reference?
- Does the target result (T5 / M5 / A4) align with what the proof / method / data
  can actually deliver?
- Is the asymptotic regime consistent throughout?
```

### X2: Novelty / contribution audit (literature-anchored)

```
- Is the contribution clearly stated in 1-2 sentences?
- Does it match the paper-type's expected contribution kind?
- Cross-reference against LITERATURE_ANCHOR.md:
  * Is the contribution genuinely distinct from the 10-15 recent T1 papers?
  * Is there a "kill shot" risk — a recent paper that scoops 80% of this?
  * Is the contribution magnitude appropriate for the positioning chosen
    (incremental / lateral / disruptive)?
- For DISRUPTIVE positioning: does the framework actually justify the deviation?
- For INCREMENTAL positioning: is the refinement substantial enough to publish?
```

Cross-check with `/novelty-check` or `/research-lit` if available.

### X2.5: Positioning audit (literature-anchored)

Re-examine the positioning from Step 0.5E against the now-detailed framework:

```markdown
## Positioning Verification

### Chosen positioning: [INCREMENTAL / LATERAL / DISRUPTIVE]

### Coherence check
- Does each phase decision match the positioning?
  * INCREMENTAL: Did you adopt the inertia's defaults except where you refine?
  * LATERAL: Did you justify the angle change?
  * DISRUPTIVE: Did you build the case for the new framework?

### Drift check
- During T1-T7 / M1-M7 / A1-A7, did the framework drift from the chosen positioning?
  Example: started INCREMENTAL but ended up using a non-standard regime — should
  either re-route to LATERAL or revert.

### Citation strategy alignment
- Which 5-10 papers from LITERATURE_ANCHOR.md will be cited prominently?
- Citation structure: predecessors → competitors → adjacent → applications
- For each, what role do they play?
  * "Our paper extends [predecessor] by..."
  * "Unlike [competitor], we..."
  * "[Adjacent] uses similar tools in a different setting..."
  * "[Application] motivates the practical need..."
```

If positioning has drifted, decide: revert framework to match original positioning,
or update positioning to match what framework evolved into. Either is fine; the
mismatch is the problem.

### X3: Reviewer hot-button check

What will a top-stat-journal referee almost certainly ask?

- For THEORY: matching lower bound? Adaptive version? Connections to known frameworks?
- For METHODOLOGY: tuning robustness? Computational feasibility? Realistic assumptions?
- For APPLICATION: assumption verifiability? Sensitivity? Pre-registration?

Pre-empt these in the framework.

### X4: Codex independent review — DISCUSSION not acceptance

Follow the repo's `CODEX_PROTOCOL.md` (Codex Discussion Protocol) — Codex is an
**adversarial reviewer to discuss with, not an oracle to defer to.** Every
Codex finding requires explicit ACCEPT / PUSH BACK / REQUEST CLARIFICATION.

#### Round 2 — Send framework to Codex for adversarial review

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are an adversarial senior referee for a top stat journal
    (AoS / JASA / JRSS-B / Biometrika / Econometrica).
    Be harsh — find real weaknesses. Do not be polite.

    A statistics researcher has drafted a framework for a new [paper_type] paper.
    The framework includes a mandatory literature anchor (Step 0.5).

    LITERATURE_ANCHOR.md:
    [paste]

    FRAMEWORK_DESIGN.md:
    [paste]

    Adversarial review tasks:
    1. Is the paper-type declaration coherent with the framework's actual focus?
       (e.g., user said THEORY but the centerpiece is an estimator → METHODOLOGY)
    2. Is the literature anchor adequate? Did the search miss obvious recent T1 work?
    3. Is the positioning (INCREMENTAL/LATERAL/DISRUPTIVE) realistic given the
       anchor? Is the contribution magnitude believable for the chosen positioning?
    4. Are there logical jumps between phases? (e.g., model setup that doesn't
       support the target results)
    5. Is the asymptotic regime / model choice sensible for the contribution?
    6. What's the most likely reviewer attack on this design?
    7. What's missing? Be specific: name the missing piece + cite an example
       of how recent T1 papers handle it.

    Output: numbered findings with severity (CRITICAL / MAJOR / MINOR / NIT).
    For each, propose a concrete fix.
```

#### Round 3 — Claude evaluates each finding (mandatory)

For EACH Codex finding, decide explicitly:

```markdown
## Per-finding evaluation

| # | Codex finding | Decision | Reasoning |
|---|--------------|----------|-----------|
| 1 | [...] | ACCEPT | [why correct, what to change] |
| 2 | [...] | PUSH BACK | [substantive counter-argument] |
| 3 | [...] | REQUEST CLARIFICATION | [what is ambiguous] |
```

**Forbidden behaviors** (from CODEX_PROTOCOL.md):
- Silent wholesale acceptance to avoid friction
- Silent rejection to defend prior work
- ACCEPT without recording why the finding was correct
- PUSH BACK without a substantive argument

#### Round 4 — Send push-back / clarifications back to Codex

Use `mcp__codex__codex-reply` on the same threadId. Codex can concede, refine,
or hold firm. Capture each.

#### Round 5+ — Iterate until convergence OR escalation

Continue until one of:
- Convergence: both agree on final findings — apply changes
- Persistent disagreement on specific points — escalate to user with both arguments
- >3 rounds without progress — stop and escalate

#### Final: Write `papers/<paper-name>/design/codex_discussion.md`

Required structure (from CODEX_PROTOCOL.md):
```markdown
# Codex Discussion Log — theory-design for [topic]

## Round 1: Claude's initial framework
[link to FRAMEWORK_DESIGN.md]

## Round 2: Codex review (N findings)
[table]

## Round 3: Per-finding evaluation
[table]

## Round 4+: Iterations
[per round]

## Final state
[what changed; what disagreements remain]

## Escalations to user (if any)
[both positions stated]
```

This log goes alongside FRAMEWORK_DESIGN.md and LITERATURE_ANCHOR.md.

**Why the protocol matters here**: framework design is precisely where reflexive
acceptance of Codex would be most harmful — the framework determines the entire
downstream paper. A framework shaped by whichever LLM is louder, rather than by
substantive deliberation, will fail review for reasons neither LLM anticipated.

---

## Output: FRAMEWORK_DESIGN.md

Final structure of the document this skill produces:

```markdown
# Framework Design: [Topic]

## Paper type: [THEORY / METHODOLOGY / APPLICATION]
## Justification: [why this type]

## Phase 1: [paper-type-specific phase 1 — Phenomenon / Practical-problem / Scientific-question]
...

## Phase 2: [...]
...

## Phase 7: [...]

## Cross-type checks
- Internal consistency: ...
- Novelty audit: ...
- Reviewer hot-button: ...
- Codex review: ... (if run)

## Handoff plan
- [downstream skill] receives [artifact] for [purpose]
- ...
```

---

## Quick start (single command)

```
/theory-design "doubly robust estimator for treatment effect under unmeasured confounding"
```

Skill will:
1. Help classify (likely METHODOLOGY)
2. Walk M1-M7 with interactive Q&A
3. Run cross-type checks
4. Output FRAMEWORK_DESIGN.md
5. Recommend next skill (most likely /proof-writer for the consistency theorem)

---

## Output Summary

```
Framework design complete for [Topic].

Paper type: [TYPE]
Phases completed: 7 + cross-type checks
Codex review: [done / skipped]

Key decisions made:
- [decision 1]
- [decision 2]
- ...

Files created:
- FRAMEWORK_DESIGN.md — the design document
- (optional) NOVELTY_NOTES.md — what's new vs literature
- (optional) codex_review.md — independent assessment

Next steps:
- Run /proof-writer for target theorem T5/M5
- Run /theory-simulation DESIGN mode for validation plan (if methodology)
- Run /proofcheck after first draft of proofs
- Run /theory-sharpen periodically to assess sharpenability
```
