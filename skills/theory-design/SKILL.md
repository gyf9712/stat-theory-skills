---
name: theory-design
description: >-
  Design a coherent theoretical framework for a new statistics / ML theory
  research topic, paper-type aware. Three modes — Theory paper (explain phenomena
  or provide new theoretical tools), Methodology paper (propose a new method with
  theoretical guarantees), Application paper (apply existing methods to scientific
  data with assumption verification). Each mode walks a different logical order:
  the centerpiece of a theory paper is the theorem itself, of a methodology paper
  the estimator, of an application paper the empirical findings. The skill forces
  the user to declare paper type first, then asks paper-type-appropriate questions
  in the correct order, and produces a FRAMEWORK_DESIGN.md that downstream skills
  (proof-writer, theory-simulation, proofcheck) consume. Use when user says
  "design theory framework", "理论框架设计", "新课题怎么开始", "新方向 design",
  "from scratch theory", "构建理论框架", "start a new topic", or asks for the
  logical order to build a statistics paper's theoretical content from a blank
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

### X2: Novelty / contribution audit

```
- Is the contribution clearly stated in 1-2 sentences?
- Does it match the paper-type's expected contribution kind?
- Is there a "kill shot" risk — a recent paper that scoops 80% of this?
```

Cross-check with `/novelty-check` or `/research-lit` if available.

### X3: Reviewer hot-button check

What will a top-stat-journal referee almost certainly ask?

- For THEORY: matching lower bound? Adaptive version? Connections to known frameworks?
- For METHODOLOGY: tuning robustness? Computational feasibility? Realistic assumptions?
- For APPLICATION: assumption verifiability? Sensitivity? Pre-registration?

Pre-empt these in the framework.

### X4: Codex independent review (if Codex MCP available)

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    A statistics researcher has drafted a framework for a new [paper_type] paper.
    Below is FRAMEWORK_DESIGN.md.

    [paste content]

    As a senior referee for a top stat journal (AoS / JASA / JRSS-B / Biometrika /
    Econometrica), assess:
    1. Is the contribution well-defined and matched to paper type?
    2. Are there logical jumps between steps?
    3. Is the asymptotic regime / model choice sensible for the contribution?
    4. What's the most likely reviewer attack on this design?
    5. What's missing for a top-journal-quality framework?

    Be specific and adversarial.
```

Reconcile Codex findings with the framework. Document disagreements.

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
