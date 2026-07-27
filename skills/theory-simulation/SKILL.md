---
name: theory-simulation
description: >-
  Bridge between theoretical results and Monte Carlo simulation, built to
  top-stat-journal standards (AoS, JASA, JRSS-B, Biometrika, Bernoulli). Two modes:
  (1) DESIGN mode — for each theoretical claim, design new simulations that verify
  rates, coverage, stress-test assumptions, and reveal theory-improvement opportunities;
  (2) AUDIT mode — when the paper already has simulations, evaluate whether they
  actually verify the theorems, identify claim-coverage gaps and adequacy flaws,
  and propose targeted improvements (extend / add / reformat) rather than full
  redesign. Produces publication-grade figures (no titles, content in caption,
  color-blind safe) and feeds findings back to refine theory. Use when user says
  "simulation plan", "Monte Carlo", "验证理论", "审查 simulation", "audit simulation",
  "模拟实验", "已有 simulation 检查", "stress test theory", "bridge simulation",
  "rate verification", or wants reproducible stat-journal simulations tied to theorems.
argument-hint: [path-to-paper.tex or paper-dir]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent
model: opus
---

# Theory-Simulation — Bridge Theory and Monte Carlo for Statistics Papers

> 🔬 **Model Recommendation**: Run this skill on **Claude Opus** for best results.
> Designing rate-verifying experiments and reconciling theory with empirical results
> requires deep reasoning. If your session is not on Opus, run `/model opus`.

Bridges theoretical results and simulation experiments, two-way:

```
Theory ←————— stress tests, rate slopes ——————→ Simulation
       ←————— sharper bounds, weakened —————→
              assumptions discovered from sim
```

Built to **top statistics journal standards**: clearly stated DGPs, multiple sample
sizes, Monte Carlo replications, rate verification via log-log slopes, stress tests
on every assumption, finite-sample vs asymptotic comparisons, and publication-grade
figures conforming to AoS / JASA / Biometrika / JRSS-B style.

## Context: $ARGUMENTS

---

## Pipeline Position

```
/proofcheck → /proof-repair → /theory-sharpen → /theory-simulation → /proof-writer
   Correct?     Fix issues       Strengthen theory      Verify + stress         Write proofs
                                                        (this skill)
```

This skill can also run standalone if user has theorems and wants Monte Carlo
verification without a full pipeline.

---

## Core Philosophy

A theoretical result is taken seriously by reviewers when simulation:
1. **Confirms** the predicted rate/coverage/bias under stated assumptions
2. **Breaks** in the predicted way when assumptions are violated
3. **Quantifies** the finite-sample regime where asymptotics kick in
4. **Reveals** improvements (sharper rates, weaker assumptions) for theory iteration

A simulation is taken seriously by reviewers when it has:
- **Reproducible DGPs** with hierarchical RNG streams (not just a single seed)
- **Multiple cells along the asymptotic path** the theory uses
  (e.g., `s log d / n` fixed, NOT just "multiple n and d")
- **MCSE-driven replication count** for each metric (NOT a fixed B threshold)
- **Honest stress tests**, including least-favorable DGPs matched to the theorem
- **Inference diagnostics beyond rate**: size, local power, interval length,
  EmpSE vs ModSE calibration
- **Publication-grade figures** with MC uncertainty shown
- **Paired-replicate baseline comparison** (all methods on the same synthetic data)
- **Failure handling**: nonconvergence, singular Hessian, optimizer stalls all
  logged and reported per cell

References for stat-journal simulation standards: Morris, White & Crowther
(2019, *Stat in Medicine*); Koehler, Brown & Haneuse (2009, *Am. Stat.*); JASA
Reproducibility Editorial (2024).

---

## The Claim Evidence Ledger (the spine)

Everything this skill does is one object: a ledger mapping each theoretical claim to
the evidence that does or does not support it. AUDIT mode and DESIGN mode are two entry
routes into the same ledger — AUDIT populates it from experiments that already exist,
DESIGN populates it as `PLANNED` and then runs them — and Step 5 reads it. There is one
vocabulary, used everywhere in this skill.

Each claim carries a **priority**: `PRIMARY` (the paper is built on it), `SECONDARY`
(supporting), `PERIPHERAL` (decorative). Audit severity is a function of priority and
state, not of state alone.

Each claim terminates in exactly one **state**:

| State | Meaning |
|---|---|
| `PLANNED` | an experiment is designed for this claim but has not been run (DESIGN mode only) |
| `YES[strong]` | an experiment exists and is adequate on every dimension; the claim is genuinely verified |
| `YES[weak]` | adequate by a minimum margin; supported but easily attacked by a referee |
| `PARTIAL[codes]` | an experiment exists but fails on one or more dimensions; the codes say which |
| `NO` | no experiment addresses this claim |
| `CONTRADICTED[code]` | the result conflicts with the prediction — a red flag, follow the CONTRADICTED protocol |
| `HYPOTHESIS-ONLY` | simulation suggests a theory improvement that is not yet proved; it stays a hypothesis until it is (Step 5) |

**Two axes, not one.** *Coverage* asks whether any experiment aims at the claim.
*Evidentiary strength* asks whether that experiment can actually identify the claim at
top-journal standards. Coverage without strength is the most common failure, so a claim
covered by an inadequate experiment is `PARTIAL[...]`, never `YES`.

Reason codes for `PARTIAL` / `CONTRADICTED` (multiple allowed, e.g.
`PARTIAL[grid,precision]`):

| Code | Failure |
|---|---|
| `path` | the asymptotic path the theorem uses is not held (e.g. $n$ varies but $s\log d/n$ is not fixed) |
| `metric` | the measured quantity is not what the theorem bounds |
| `precision` | too few replications; MCSE too large to identify the claim |
| `grid` | too few cells (three sample sizes cannot fit a rate slope) |
| `comparator` | the required baseline is missing or wrong |
| `reporting` | the numbers or figure do not permit verification |
| `stress-coverage` | a robustness claim tested against only one violation type |
| `identification-mismatch` | the setup cannot identify the claim (a single-$\theta$ test for a uniform-over-$\Theta$ claim) |

**Severity.** `PRIMARY` + (`NO` or `CONTRADICTED[*]`) is CRITICAL. `SECONDARY` +
`PARTIAL[reporting]` is MINOR. Everything else falls between; judge by how much the
paper's central story leans on the claim.

**Terminal rule.** A ledger with any `PRIMARY` claim left at `NO`, `CONTRADICTED[*]`, or
`PLANNED` is not a finished simulation study, whichever mode produced it.

---

## Adequacy Dimensions (both modes)

A simulation is adequate when it holds on five dimensions. AUDIT scores existing
experiments against them; DESIGN builds experiments to satisfy them. One contract, two
questions — this is what stops the skill from auditing other people's simulations more
rigorously than it designs its own.

| Dimension | Pass condition | Failure maps to |
|---|---|---|
| **Truth source** | the truth ($\theta^*$, $f^*$, estimand) is the quantity the theorem targets, and its own error is far below the metric's MCSE | `metric` |
| **Selection discipline** | every cell, method, regime, and DGP that was run is reported, or its omission is explained | `reporting` |
| **Tuning protocol** | tuning is described and reproducible, and any claimed advantage holds under data-driven tuning, not only oracle tuning | `comparator` |
| **Computational adequacy** | any practicality claim is backed by runtime, memory, failure rate, and scaling against the baseline | `reporting` |
| **Reuse legitimacy** | reusing an existing run requires replicate-level outputs, recorded RNG streams, paired sharing, logged failures, the correct truth, and tuning held fixed within a cell | rerun required |

**DESIGN**: a planned experiment that has not stated its position on all five is not
finished being designed. Design against the reason codes, not merely toward "an
experiment exists".

**AUDIT**: a claim cannot reach `YES[*]` while any applicable dimension fails. The
failing dimension supplies the reason code.

Reuse legitimacy applies only when existing runs are being reused; the other four
apply in both modes.

---

## Step 0: Ingest Theory + Existing Code

### 0A: Locate inputs

Parse `$ARGUMENTS`:
- A `.tex` file → read paper, extract theoretical statements
- A paper directory → read paper.tex + any existing simulation code
- A directory with `theorems/` or `claims/` → read those

### 0B: Extract simulation-relevant items from theory

Build the **Theory-to-Simulation Mapping Table**:

```markdown
| Theory ID | Statement | Quantities to verify | Assumptions to stress |
|-----------|-----------|---------------------|----------------------|
| Thm 1 | √n-consistency under A1-A3 | bias, variance, MSE rate | break A1: i.i.d., A3: tail |
| Thm 2 | Asymptotic normality | coverage of 95% CI | sample size threshold |
| Thm 3 | Rate O(n^{-2/(2+d)}) | log-log slope ≈ -2/(2+d) | d growth, smoothness |
| Cor 1 | Uniform over Θ | sup-norm error vs θ | hardest θ in Θ |
```

### 0C: Detect framework axes (from theory-sharpen if available)

Use the 3-axis classification (Data / Framework / Regime) to tailor simulation:
- **i.i.d. + parametric + classical** → standard n→∞ MC with fixed d
- **mixing TS + semiparametric** → autoregressive DGP, blocked replications
- **i.i.d. + nonparametric + classical** → curves at multiple n, smoothness parameter sweep
- **i.i.d. + parametric + high-d** → vary n and d jointly, sparsity regimes
- **online/sequential** → cumulative regret, anytime guarantees

### 0D: Mode detection — DESIGN vs AUDIT

The skill operates in two modes depending on what already exists in the paper:

| Mode | Trigger | What this skill does |
|------|---------|---------------------|
| **DESIGN** | Paper has theorems but no simulation section, OR user explicitly requests new sims | Steps 1-7 below: design plan → code → run → figures → reconcile |
| **AUDIT** | Paper has BOTH theorems AND an existing simulation section | Step A0-A4 below: parse existing sims → assess adequacy → identify gaps → propose targeted improvements |
| **HYBRID** | Existing sims partially cover theory; user wants gap-filling | Run AUDIT first to identify gaps; then DESIGN mode for only the missing experiments |

**Auto-detection rules**:
- Search the paper for sections matching: "Simulation", "Numerical Experiments",
  "Monte Carlo", "Empirical Studies", "Numerical Studies", "Numerical Illustration"
- Search for figures with captions mentioning "simulation", "Monte Carlo", "replications", "MSE", "coverage"
- Search for tables containing simulation results (typical header keywords: bias, SE, MSE, coverage, B=, n=)
- If any of the above found → likely AUDIT or HYBRID mode

**Ask the user to confirm mode** before proceeding. Default to AUDIT when simulation
content is detected.

---

## AUDIT MODE — Assess existing simulation results

When the paper already has simulation experiments, evaluate them BEFORE designing
new ones. This is the standard situation during paper revision or peer review.

### Step A0: Parse the existing simulation section

Extract systematically:

| Item | What to record |
|------|---------------|
| **Experiments** | Each Experiment / Setting / Scenario name + section reference |
| **DGPs** | Data generating processes used (with stated parameters) |
| **Sample sizes** | n values; if multiple, the full grid |
| **Other parameters** | d, sparsity s, signal strength, smoothness — anything varied |
| **Methods** | Proposed method + all comparator baselines |
| **Metrics reported** | Bias, SE, RMSE, MSE, coverage, length, runtime, etc. |
| **B (replications)** | Stated number of Monte Carlo replications per cell |
| **Figures/tables** | What is shown and the caption claims |
| **Stated conclusions** | What the paper claims the simulations demonstrate |

Build `papers/<paper-name>/simulation_audit/EXISTING_SIMS.md` with the parsed
inventory.

### Step A1: Map existing sims → theoretical claims (TWO-AXIS Coverage Matrix)

Build a matrix on TWO axes (split per Codex review). A claim can be "covered" by
an experiment that doesn't actually identify it — coverage ≠ credibility.

**Step A1.0: Claim priority ranking** (do this before matrix)

Rank every theoretical claim:
- **PRIMARY**: central result the paper is built on (main rate, asymptotic distribution, identification)
- **SECONDARY**: supporting result (consistency, conditions, auxiliary lemma)
- **PERIPHERAL**: decorative corollary not needed for the main story

Audit severity scales with priority: a gap on a PRIMARY claim is critical; the
same gap on a PERIPHERAL one is minor.

**Step A1.1: Populate the Claim Evidence Ledger**

Fill one ledger row per theoretical claim, using the typed states and reason codes
defined in the Claim Evidence Ledger section above. Coverage and evidentiary strength
are scored on separate axes: an experiment can exist and still fail to identify the
claim, which is why `PARTIAL[...]` carries reason codes rather than a bare verdict.

A filled example ledger and a worked per-experiment audit:
`../stat-shared-references/examples/simulation-audit-example.md`.

### Step A2: Audit each existing experiment against top-journal standards

For each existing experiment, score against the standards from Steps 1-4:

```markdown
## Audit: Experiment {k} ({section ref}, "{name}")

### What the experiment does
[DGP with parameters; sample sizes; methods; metric; B; what is reported]

### Audit against standards
| Criterion | Status | Issue |
[asymptotic path declared; loss object matches the theorem; >=6 cells along the path;
MCSE reported; paired replicates; failure rates reported; comparator adequate]

### Ledger effect
Claim {id}: {typed state with reason codes}
```

A filled example: `../stat-shared-references/examples/simulation-audit-example.md`.

### Step A2.5: CONTRADICTED protocol (REQUIRED when a claim is tagged CONTRADICTED)

When existing simulation conflicts with theoretical prediction, do NOT just flag
"investigate". Run this 7-step structured triage in order:

```
Step 1. Replication check
  - Rerun the exact cell with the saved seed (if available)
  - Verify the reported numbers reproduce
  - If they don't → reporting / archival error; correct and proceed

Step 2. Metric check
  - Verify the plotted/measured quantity matches the theorem's target
  - Theorem on ‖θ̂ − θ*‖? Paper measures MSE? Compute the correct quantity
  - If contradiction disappears → MISTAKEN COMPARISON, not theorem failure

Step 3. DGP check
  - Verify the DGP actually satisfies the theorem's assumptions
  - Verify the asymptotic path was implemented correctly
  - If contradiction disappears under correct DGP → ASSUMPTION VIOLATED IN SIM, not theorem failure

Step 4. Computation check
  - Inspect convergence failures, optimizer tolerances, numerical issues
  - Inspect tuning behavior (oracle vs data-driven)
  - Look for silent failures dropped from aggregation
  - If contradiction disappears under correct computation → IMPLEMENTATION BUG, not theorem failure

Step 5. MC precision check
  - Compute MCSE for the contradicting quantity
  - Is |empirical − theoretical| > 2 × MCSE?
  - If not → APPARENT CONTRADICTION IS WITHIN MC NOISE; not real

Step 6. Localization
  - Does the contradiction occur in ALL cells, or only specific regimes?
  - Pre-asymptotic only (small n)? → finite-sample effect; theory still valid asymptotically
  - All n? → genuine asymptotic contradiction
  - Off-assumption only? → robustness limit, not theorem failure

Step 7. Escalation routing
  - Implementation / reporting issue (Steps 1, 2, 3, 4) → fix and rerun
  - Within MC noise (Step 5) → not a contradiction; update conclusion to "consistent within MC error"
  - Pre-asymptotic only (Step 6) → reframe as finite-sample regime; consult /proof-repair for FS theorem
  - Off-assumption only (Step 6) → reclassify as robustness failure, NOT theorem failure
  - Survives all 6 checks → GENUINE CONTRADICTION:
      → trigger /proofcheck for proof audit
      → trigger /theory-sharpen for theory revisit
      → flag to user as a major issue requiring author response
```

Record the triage in `simulation_audit/CONTRADICTED_<claim_id>.md` for each
CONTRADICTED claim. Without this discipline, "contradicted" becomes a dramatic
label with no rigor behind it.

### Step A2.6: Score every experiment against the adequacy dimensions

For each existing experiment, take a position on all five dimensions from the
Adequacy Dimensions section above. A dimension failure maps to its reason code and
caps the claim at `PARTIAL[...]`; a claim reaches `YES[*]` only when every applicable
dimension passes.

Three failures get their own flag in the gap analysis because they routinely sink a
submission on their own:

- `SELECTION_RISK` — evidence of selective reporting (omitted cells, methods, regimes,
  DGPs, or failures; a single illustrative seed).
- `TUNING_GAP` — a method advantage shown only under oracle tuning, with no
  data-driven version.
- `COMP_GAP` — a paper marketing practicality ("fast", "scalable", "works for large
  $n$") without runtime, memory, failure-rate, and scaling diagnostics.

Signal-by-signal forensic tables (what to look for, and what each finding implies):
`../stat-shared-references/simulation-adequacy-audit.md`.

### Step A3: Gap analysis — what's missing

Compile gaps in three categories:

**A3.1: Claims with NO experimental evidence** (most serious)
```markdown
| Claim | Why it matters | Required new experiment |
|-------|---------------|-----------------------|
| Theorem 3 rate n^{-2/(2+d)} | Main rate result | Design rate-verification along (n,d) grid; ≥6 cells |
| Cor 1 uniformity over Θ | Strengthens Thm 2 from pointwise to uniform | Sup-error experiment over a θ-grid |
| Computational scalability claim | Stated in abstract | Runtime/memory vs n |
```

**A3.2: Experiments with adequacy problems** (medium serious)
```markdown
| Existing experiment | Flaw | Fix |
|---------------------|------|-----|
| Exp 1 MSE vs n | 3 cells, no slope CI | Extend to 6-8 n values; report weighted slope + 95% CI |
| Exp 1 figure | No MC uncertainty | Add MCSE error bars |
| Exp 2 coverage | Single n | Extend to 4-6 n values to show convergence to nominal |
| Exp 3 stress test | Only t_3 | Add t_5 (intermediate), AR(1) (dependence), misspec |
```

**A3.3: Reporting / discipline issues** (revision quality)
```markdown
| Issue | Where | Fix |
|-------|-------|-----|
| No B justification | Throughout | State MCSE target and how B was chosen |
| No paired comparison | Tables | Report paired loss differences method-vs-method |
| Captions lack DGP detail | All figures | Rewrite captions: DGP, n, B, theoretical prediction explicit |
| No failure rates | All cells | Add failure-rate column |
| Missing baselines | Exp 1-2 | Add at least one published competitor + oracle |
| Single θ value | Exp 1-3 | Vary θ at least 3 values, or argue why one is representative |
```

**A3.4: Selection-bias risks** (from A2.8)
```markdown
| Signal | Evidence | Required action |
|--------|----------|----------------|
| SELECTION_RISK: omitted cells | Paper says "additional simulations available on request" | Force inclusion of all cells or explicit exclusion rationale |
| SELECTION_RISK: omitted DGPs | Stress menu has 1 entry | Expand stress menu per theorem-matched least-favorable design |
| SELECTION_RISK: omitted failures | No failure-rate column | Reanalyze raw outputs and report failure rates |
```

**A3.5: Tuning / procedure gaps** (from A2.9)
```markdown
| Gap | Method | Required action |
|-----|--------|----------------|
| TUNING_GAP | Proposed method shown only under oracle λ | Add data-driven λ (CV) and report performance gap |
| TUNING_GAP | CV variability not reported | Add variability over CV folds / random init |
```

**A3.6: Computational adequacy gaps** (from A2.10)
```markdown
| Gap | Where claimed | Required action |
|-----|---------------|----------------|
| COMP_GAP: no runtime | Abstract says "scalable" | Add runtime + memory vs n,d |
| COMP_GAP: no failure rate | Method uses iterative optimization | Add convergence statistics |
```

### Step A4: Targeted improvement plan

Based on the gap analysis, produce a **minimal targeted plan** — only what's needed
to close gaps, not a full redesign:

```markdown
# Targeted Improvement Plan

## Priority 1: Close critical claim-gaps (NEW experiments)
- E_new1: Verify Theorem 3 rate (along asymptotic path s log d / n = 0.5)
- E_new2: Computational scalability (runtime + peak memory vs n)
- E_new3: Uniformity over Θ for Corollary 1

## Priority 2: Extend / strengthen existing experiments
- Extend Exp 1 to n ∈ {50, 100, 200, 500, 1000, 2000, 5000} with MCSE bars
- Extend Exp 2 coverage to multiple n; add Wilson CIs
- Add t_5 and AR(1) to Exp 3 stress tests

## Priority 3: Reporting + discipline fixes (NO new runs needed)
- Recompute slope estimates with weighted regression + CI
- Rewrite all captions to be content-bearing
- Add paired-difference reporting where possible
- Report B-selection rationale (target MCSE per metric)

## What CAN be reused from existing runs
- Exp 1 raw results: extend rather than rerun if seed/code recoverable
- Exp 2 raw results: extend coverage to new n
- Exp 3 raw results: reuse t_3 cell; add t_5 + AR(1) as new cells

## What MUST be rerun
- If existing code is lost / seeds not stored, baseline experiments must be redone
  with STRICT-tier reproducibility before extension
```

Write to `papers/<paper-name>/simulation_audit/IMPROVEMENT_PLAN.md`.

### Step A5: Codex cross-audit (if Codex MCP available)

After completing the audit, send it to Codex for independent verification, following
`../stat-shared-references/codex-protocol.md`. Ask specifically whether any claim the
audit marked `YES[*]` is actually only `PARTIAL[...]`, and whether any gap was missed —
the failure mode here is an audit that is too generous to the paper it is auditing.

Reconcile findings explicitly (ACCEPT / PUSH BACK / REQUEST CLARIFICATION with
reasoning); a Codex objection is not automatically correct. Record the exchange, and
never downgrade or upgrade a ledger state silently to match Codex.

Prompt text: `../stat-shared-references/examples/simulation-codex-review-prompts.md`.

## Step 1: Design the Simulation Plan (ADEMP-style, claim-based)

Write `papers/<paper-name>/simulation/SIMULATION_PLAN.md`.

**This is the DESIGN entry route into the Claim Evidence Ledger.** Open a ledger row
for every claim before designing anything, each starting at `PLANNED`, with its
priority set. The design target for a row is the evidence that would move it to
`YES[strong]` — not merely to "an experiment exists", which is what produces
`PARTIAL[...]` rows in audits of other people's papers. Design against the reason
codes: pick the grid that defeats `[grid]`, the metric that defeats `[metric]`, the
replication count that defeats `[precision]`.

**Design by CLAIM, not by theorem.** A single theorem typically implies multiple
empirical claims (rate, limiting distribution, variance consistency, tuning
sensitivity, failure behavior). Each gets its own block. Follow the ADEMP framework
(Morris, White & Crowther 2019):

- **A**ims of the experiment (which specific empirical claim is being tested)
- **D**ata-generating mechanism (DGP, with explicit asymptotic path)
- **E**stimators / methods compared (including baselines)
- **M**ethods of analysis (metrics, MCSE formulas, summary plots)
- **P**erformance measures (with target MCSE precision)

### 1A: For each CLAIM, design a verification experiment

```markdown
## Experiment E{k} — Verify {claim} ({theorem ref})

### Theoretical prediction
[the exact quantity the theorem bounds, with its rate and the assumptions in force]

### Asymptotic path
[which quantities move together, e.g. s log d / n held fixed — not merely "n varies"]

### DGP
[generating mechanism with explicit parameters, and why it is the right difficulty]

### Methods
[proposed estimator + the baselines a referee will expect, run on paired replicates]

### Metrics and MCSE
[the measured quantity, matched to what the theorem bounds; MCSE formula per metric;
target precision that makes the claim identifiable]

### Grid and replication count
[>= 6 cells along the path for a rate claim; B chosen from the target MCSE, not a
round number]

### Adequacy dimensions (all four required; a design missing any is unfinished)
- Truth source: [how theta*/f*/the estimand is defined, and why its own error is far
  below the metric's MCSE]
- Selection discipline: [what will be reported — every cell, method, and regime run,
  including the unflattering ones; state up front that nothing is reported selectively]
- Tuning protocol: [how tuning is chosen, and the data-driven version that must
  accompany any oracle-tuned comparison]
- Computational adequacy: [runtime, memory, failure rate, scaling vs baseline — required
  whenever the paper claims practicality]

### Ledger row
Claim {id} — priority {PRIMARY/SECONDARY/PERIPHERAL} — state PLANNED
```

A filled example: `../stat-shared-references/examples/simulation-design-example.md`.

### 1B: Stress tests — two-layer design (diagnostic + robustness-claim)

A stress test serves one of two distinct purposes:

**Layer 1: Diagnostic (one-at-a-time)**.
For each assumption that is theoretically critical, violate ONLY that assumption.
This isolates which assumption matters — a referee needs this to attribute failure.

**Layer 2: Robustness-claim (factorial / crossed stress)**.
If the paper *claims* robustness to multiple violations simultaneously
(e.g., heavy tails AND weak signal, misspecification AND dependence), one-at-a-time
is NOT sufficient. A method can survive each violation alone yet fail when they
co-occur. Run a targeted crossed design — usually a 2×2 or 2×3 factorial of the
critical-pair violations, not a full factorial.

**Diagnostic stress: candidate menu (NOT a prescription)**.

These are *starting candidates*. **You must select stressors matched to your
theorem's specific assumptions** and add theorem-specific least-favorable DGPs.

| Generic stress | Candidate DGP | ⚠ Mismatch warning |
|--------|----------------|---------------------|
| Heavy tails | t₃, Pareto, log-normal | t₃ still has finite variance; for "no variance" results use Cauchy / stable α<2 |
| Dependence | AR(1), MA(q), block-bootstrap | AR(1) is short-memory parametric; long-memory / cluster / spatial / endogenous dependence need separate DGPs |
| Misspecification | fit wrong parametric family | Choose the misspecification the theory actually targets (e.g., omitted nonlinearity vs wrong link function) |
| Boundary | θ on ∂Θ | Be specific about which boundary (e.g., positive-definiteness boundary vs box boundary) |
| Identifiability | near-singular Hessian | For weak-ID papers, use weak-instrument-style local-to-unidentified sequences (Andrews & Cheng 2012) |
| Growing dim | d/n → γ | Specify γ value; spike/no-spike regime; covariance structure |
| Outliers | ε-fraction Huber contamination | Specify contamination distribution (point mass, heavy-tail, adversarial) |
| Small sample | n ∈ {20, 30, 50} | Often more relevant than large-n stress |
| Weak signal | r_n → 0 in detectability sense | Critical for detection theorems; pair with heavy tails for robustness claims |

**Required**: replace each generic stressor with a **theorem-matched** version.
Example for an M-estimation theorem assuming sub-Gaussian X and bounded influence:

```markdown
## S1 (diagnostic): violate sub-Gaussian → bounded 4th moment
DGP: X_i ~ t_5 (finite variance + 4th moment ✓, sub-G ✗)
Theoretical prediction: theorem still holds with weaker rate

## S2 (diagnostic): violate sub-Gaussian → infinite variance heavy tail
DGP: X_i ~ t_{1.5} (4th moment fails)
Theoretical prediction: theorem fails

## S3 (least-favorable diagnostic): adversarial contamination at influence point
DGP: clean X_i with prob 1-ε, plus mass at the worst-case point
Theoretical prediction: tests the boundary of the influence-function bound

## S4 (robustness claim): heavy-tailed AND weak signal
DGP: X_i ~ t_5 + ‖θ*‖ shrinks at rate n^{-1/4}
Theoretical prediction: paper's "robustness" claim requires this to hold
```

### 1C: Rate verification protocol (mathematically precise)

**Step 1: Identify the loss object the theorem bounds.**

The slope target depends on WHICH quantity the theorem claims to control:

| Theorem claim | Loss to compute | Expected log-log slope |
|---------------|-----------------|----------------------|
| `‖θ̂ − θ*‖ = O_P(n^{-a})` | RMSE = √mean‖θ̂ − θ*‖² | `−a` |
| `E‖θ̂ − θ*‖² = O(n^{-2a})` | MSE = mean‖θ̂ − θ*‖² | `−2a` |
| `‖θ̂ − θ*‖₂² ≤ C r(n,d,s)` | MSE; varies r(·) | depends on path (see below) |
| High-prob bound with prob ≥ 1−δ | empirical quantile of error | depends on quantile |

**Force the user to declare the loss object before running.** A single skill that
defaults to "slope = −2a always" is wrong.

**Step 2: Declare the asymptotic path.**

If the theorem uses any path parameter (e.g., `s log d / n → 0`, `d/n → γ`,
`nh^β → ∞`, signal strength `r_n`), simulate along that path holding the
control parameter fixed. Examples:

```
Theorem 1: ‖θ̂ − θ*‖² = O_P(s log d / n)
Path: keep s log d / n = 0.5 fixed; vary (n,d,s) so the ratio is preserved
Example grid: (n=200, d=50, s=5), (n=400, d=200, s=10), (n=800, d=800, s=20)
```

This is the only way to make a slope plot interpretable for high-dim / nuisance theory.

**Step 3: Run at ≥6 cells along the path.**

- Each cell needs B replications determined by MCSE target (Step 1D below).
- Compute empirical loss at each cell with metric-appropriate MCSE.

**Step 4: Multiple slope diagnostics (do NOT rely on a single OLS slope).**

(a) **Weighted regression** of log(empirical loss) on log(n) using inverse MCSE²
    as weights. Report slope estimate + 95% CI from delta method or bootstrap.
(b) **Local slopes**: compute the slope between each adjacent pair of cells;
    if these vary systematically with n, asymptotics has not kicked in.
(c) **Normalized loss plot**: plot `n^a · empirical loss` (or `n^{2a} · MSE`)
    versus n. If the rate is correct, this should level off; if it drifts, the
    rate is wrong or finite-sample bias dominates.

The normalized-loss leveling-off plot is more diagnostic than a single slope number.

**Step 5: Pass criteria.**

- Weighted slope's 95% CI contains the theoretical value
- Local slopes converge to the theoretical value as n grows
- Normalized loss plot levels off (within a band of ±2× MCSE of its plateau)

If any of these fails, do NOT call the rate "confirmed"; investigate.

### 1D: Inference diagnostics (REQUIRED for any paper with CIs/tests)

Coverage ALONE is not enough for a top-stat-journal inference paper. A referee
will demand at minimum:

| Diagnostic | Why | How |
|-----------|-----|-----|
| **Empirical coverage** | Direct check of 1−α claim | Fraction of CIs containing θ*; Wilson or Jeffreys CI on the coverage itself |
| **Empirical size** | Validity of tests under null | Reject rate at level α under H₀ |
| **Local power** | Detection ability under H₁ | Reject rate at θ* + h_n/√n for h_n ∈ grid |
| **Interval length** | Efficiency of CI procedure | Mean / median CI width and its MCSE |
| **EmpSE vs ModSE** | SE calibration | EmpSE = empirical SD of θ̂; ModSE = mean of model-based SE estimates; ratio should be ≈ 1 |
| **Bias-eliminated coverage** | Disentangle SE error from bias | Re-center CI at empirical mean; if coverage now hits nominal, undercoverage was bias-driven |

**MCSE for coverage** (Wilson / Jeffreys interval — not `sd/√B`):
- For B replications and observed coverage p̂: MCSE = √(p̂(1−p̂)/B)
- 95% MC interval for coverage: Wilson interval based on (p̂, B)

**MCSE for size** (same binomial logic):
- For size α (e.g., 0.05) with B reps: MCSE = √(α(1−α)/B)
- B=1000 → MCSE ≈ 0.0069 for size at 0.05 — non-trivial precision needed

**B from MCSE target, NOT from a fixed threshold**:
- Choose target MCSE per metric (e.g., MCSE ≤ 0.005 for coverage near 0.95 → B ≥ 1900)
- If a cell shows MCSE too high after initial B, extend with more replicates (preserve seed determinism)
- Document each metric's chosen target MCSE in the plan

References: Morris, White & Crowther (2019); Koehler, Brown & Haneuse (2009);
Brown, Cai & DasGupta (2001, *Statistical Science*).

### 1D′: Metric-specific MCSE formulas (DO NOT use `sd/√B` for everything)

| Metric | MCSE formula |
|--------|-------------|
| Mean of per-rep scalar | `sd / √B` |
| Coverage / rejection rate (binomial) | `√(p̂(1−p̂)/B)` |
| RMSE | Delta method or jackknife |
| Relative efficiency (ratio of MSEs) | Delta method or paired bootstrap |
| Median / quantile | Bootstrap or jackknife |
| Fitted slope of log(MSE) on log(n) | Weighted regression standard error using cell-level MCSEs |
| Paired loss difference | `sd_diff / √B` where `sd_diff` is paired SD |

### 1E: Method comparison — REQUIRED to be paired across replicates

Always include ≥1 of:
- Competing method from the literature (e.g., MLE vs proposed estimator)
- Oracle (knows nuisance) — should bound your method's loss
- Naive baseline (e.g., empirical mean)

**Paired-replicate rule (NOT optional)**: all methods compared in a cell must
evaluate on the SAME replicate datasets (same RNG stream per replicate). Compare
via paired loss differences:

```
for each cell:
  for each rep:
    data = generate(rng[cell, rep], n, d, dgp)
    for each method:
       loss[method, cell, rep] = evaluate(method, data, truth)
  # Method comparisons within cell are PAIRED across rep
  diff[A vs B, cell] = mean(loss[A, cell, :] - loss[B, cell, :])
  MCSE_diff = sd_paired / sqrt(B)
```

This is a free variance reduction and is the standard for top-stat-journal method
comparisons. Report paired differences with MCSE, not just per-method means.

### 1F: Conditional diagnostics — REQUIRED when the corresponding claim exists

| If the paper claims... | You MUST run this experiment |
|---------------------|------------------------------|
| Method requires tuning (λ, h, K, ...) | Compare **oracle tuning** (knows ground truth) vs **data-driven tuning** (CV, BIC, plug-in). Report the gap. |
| Method uses CV / sample splitting / random init | Report **variability over tuning randomness** with multiple seeds at the tuning layer |
| Method has computational advantage / scalability | Report **runtime and peak memory** along the asymptotic path; not just metric values |
| Method has theoretical robustness to misspecification | Layer-2 factorial stress (multiple violations co-occurring) |
| Inference is asymptotic | Report **size + local power + interval length + EmpSE/ModSE ratio** (already required in 1D) |

These are conditional but mandatory once their trigger exists. Top-stat-journal
referees will demand them. Skipping = inviting major revision.

### 1G: Anti-cherry-picking discipline (preregister the headline)

Before running, preregister:

| Item | Why |
|------|-----|
| **Primary cells**: which cells are headline results | Prevents picking favorable cells post-hoc |
| **Primary summaries**: which metric × cell × method combinations report in the abstract | One paper-level claim per primary summary |
| **Deviation threshold**: what counts as a "meaningful" deviation from theoretical prediction | Use MCSE-relative thresholds (e.g., 2× MCSE) |
| **Anti-narration rule**: do NOT narrate one-off cell results as general conclusions | "in cell X" wording, not "in general" |

Record these in `SIMULATION_PLAN.md` BEFORE running anything. If the data later
contradict the predesignated headline, REPORT the contradiction — do not silently
swap the headline to a more flattering cell.

This is not formal multiplicity correction; it is the discipline that distinguishes
"simulation supports my method" from "simulation found cherry-picked cells that
support my method." Top-journal referees can spot this from a mile away.

---

## Step 2: Write the Simulation Code

Full operational detail — language choice, code structure, reproducibility tiers,
manifest-driven immutable cells, storage format, and edge cases — is in
`../stat-shared-references/simulation-execution-protocol.md`.

Hard gates for this step:

- **STRICT reproducibility is the default** for top-stat-journal work: hierarchical
  RNG streams (not a single global seed), the reproducibility tier declared
  explicitly, and every cell re-runnable in isolation.
- **Manifest-driven, immutable cells.** A cell's inputs are fixed once written; a
  changed design is a new cell, never an edited one. This is what makes partial
  reruns trustworthy.
- **Failure handling is required, not optional.** Nonconvergence, singular Hessians,
  and optimizer stalls are caught, logged per cell, and reported. A silently dropped
  failure is a referee magnet and biases every metric in that cell.
- **Paired replicates.** All methods run on the same synthetic data within a
  replicate, so comparisons are paired rather than independent.

## Step 3: Run + Collect Results

### 3A: Run order

1. **Pilots**: small B (50), small n grid, all experiments — catch coding bugs
2. **Baseline experiments**: full B for the main rate-verification figures
3. **Stress tests**: full B for the assumption-violation figures
4. **Sensitivity**: vary nuisance params (smoothness, signal strength, etc.)

### 3B: Result aggregation per cell

For each (n, d, DGP) cell, aggregate B replications into:
- mean, sd, median, IQR of the metric
- Monte Carlo standard error: sd / sqrt(B)
- 95% empirical CI of the metric

Write aggregated to `results/aggregated.csv` for plotting.

### 3C: Reproducibility check

Re-run one experiment with the same seed → verify exact match.
Document this in `README.md`.

---

## Step 4: Publication-Grade Figures

General figure conventions — no plot titles, content-bearing captions, legend
placement, colour-blind-safe palettes, redundant encoding, multi-panel labelling,
vector output, per-venue rules — are owned by `stat-figure-design.md` (writing repo;
resolves in the shared install). Follow it; do not restate it here.

Simulation-specific requirements this skill adds:

- **Monte Carlo uncertainty is mandatory.** Every plotted point carries an MCSE error
  bar or a shaded band. A point-estimate plot without uncertainty is not publishable,
  and this is a hard gate, not a preference.
- **Theory reference lines.** Show the predicted rate slope (dashed black) and any
  nominal level such as 0.95 coverage (dashed grey), so the reader can see prediction
  against evidence in one glance.
- **Failure rates are reported**, per cell, whenever any cell exceeds 5% nonconvergence.

Figure choice follows the simulation claim:

| Claim | Display |
|---|---|
| Rate of convergence | Log-log error vs $n$ with theory slope and MC bands; add a normalized-loss plot as a sanity check |
| Limiting distribution | QQ plot of the studentized pivot vs $N(0,1)$, plus density or ECDF |
| CI coverage | Empirical coverage vs $n$ with Wilson intervals and the nominal line; add interval length |
| Test size and power | Size vs $n$; power vs local alternative, referenced at nominal $lpha$ |
| EmpSE vs ModSE calibration | Ratio or scatter against target ratio 1, one point per cell |
| Paired method comparison | Paired-difference plot with MC CIs (more informative than overlaid lines beyond three methods) |
| Two-parameter sweep | Heatmap on viridis/cividis, never jet |
| Failure rates | Bar or heatmap of nonconvergence per cell |

Runnable matplotlib template and the full convention detail:
`../stat-shared-references/examples/simulation-figure-template.md`.

## Step 4F: Codex Adversarial Review of Simulation Design

Follow `../stat-shared-references/codex-protocol.md`. Codex is an adversarial
reviewer to discuss with iteratively, not an oracle: every finding gets an explicit
ACCEPT / PUSH BACK / REQUEST CLARIFICATION with reasoning. This matters more here
than elsewhere, because reflexively accepting a Codex objection can trigger CPU-days
of needless reruns.

Two passes: **pre-run** on the plan (claim coverage, DGP difficulty, n-grid range,
replication count per metric, baseline choice, rate-identification protocol) and
**post-run** on the findings (does the evidence actually support each claim).

Emit `simulation/codex_discussion.md` with the round-by-round record and
`simulation/codex_design_review.md` with the per-finding reconciliation (issue,
severity, Codex position, action taken).

**Hard rule:** when Codex flags a claim OVERCLAIMED or a result SUSPICIOUS, never
silently edit `RECONCILIATION.md` to match. Surface the disagreement to the user and
record both positions.

Prompt text and reconciliation-table shape:
`../stat-shared-references/examples/simulation-codex-review-prompts.md`.

## Step 5: Theory ↔ Simulation Reconciliation (HYPOTHESIS GENERATION ONLY)

**CRITICAL DISCIPLINE**: Simulation findings can SUGGEST hypotheses for theory
extension. They CANNOT validate theorem-weakening. A finite grid of DGPs is not
a proof; "method survived t_5" is NOT evidence that the sub-Gaussian assumption
can be dropped — the worst-case DGP may be elsewhere in the space.

Use simulation feedback to **generate hypotheses for analytic follow-up**, not
to declare theory upgrades. Every such finding enters the Claim Evidence Ledger as
`HYPOTHESIS-ONLY` and stays there until a proof lands — it is never promoted to
`YES[*]` by more simulation, however favourable.

| Simulation finding | Valid interpretation | INVALID interpretation |
|--------------------|---------------------|----------------------|
| Method works at t_5 too | "Worth investigating whether sub-G can be relaxed to bounded 4th moment" | "Sub-G can be relaxed" (overclaim — t_5 is only one point) |
| Slope sharper than predicted | "Suggests rate may be improvable; needs proof" | "Rate is improvable" |
| No coverage drop near boundary | "Theory's boundary caveat may be conservative" | "Boundary is fine" |
| Method fails at t_3 | "Some moment condition matters; t_3 is in failure region" | (this one is OK as evidence FOR keeping the assumption) |

Asymmetry: simulation can produce evidence FOR keeping an assumption
(by showing a failure mode), but NOT evidence FOR dropping it
(absence of failure in a finite grid ≠ proof of universal robustness).

To upgrade a "hypothesis" to a "theory revision claim", you must:
1. Expand the least-favorable search (more DGPs, adversarial directions, smaller h_n)
2. Identify what proof technique would handle the relaxation
3. Get the analytic follow-up done by `/proof-writer` or human

Without these, the finding stays in the "OPEN HYPOTHESIS" column, not "CONFIRMED".

After running simulations, do the final, most important step: feed findings back.

Write `papers/<paper-name>/simulation/RECONCILIATION.md`:

```markdown
## Reconciliation: Theory vs Simulation

### Verified predictions
| Theorem | Predicted | Observed | Status |
|---------|-----------|----------|--------|
| Thm 1 rate | n^{-1/2} | slope −0.51 (95% CI) | ✅ Confirmed |
| Thm 2 coverage | 95% | 94.2% at n=500, 95.1% at n=2000 | ✅ Confirmed |
| Thm 3 rate | n^{-2/(2+d)} | slope matches for d=2, deviates for d=10 | 🟡 Partial |

### Open hypotheses (NOT confirmed theory revisions)
| Finding | Cells tested | What more is needed before a theory claim |
|---------|-------------|------------------------------------------|
| Method works at t_5 (sub-G violated, 4th moment ✓) | 6 cells along path | Test t_4, t_3.1; least-favorable contamination; analytic check whether proof technique extends |
| Slope appears sharper than n^{-1/2} for bounded support | (n,d) grid | Verify whether bounded support is what's responsible (vary support); analytic upper-bound derivation |
| Coverage degrades for n<50 | small-n grid | Verify across more DGPs; locate finite-sample correction in literature |

### Findings that DO support keeping/strengthening an assumption
| Finding | Cells tested | What this evidence supports |
|---------|-------------|----------------------------|
| Method fails at t_3 | 4 cells, multiple θ values | Some moment condition strictly stronger than 2nd moment is required |
| Coverage breaks at boundary | boundary stress | Boundary caveat in Theorem 2 is necessary, not artifact |

### Recommendations (routing to other skills)
- **/theory-sharpen**: Investigate whether sub-G can be relaxed to bounded 4th moment;
  simulation suggests it but does NOT prove it
- **/proof-writer**: If theory-sharpen's literature check finds support, draft the
  relaxed-assumption theorem and re-verify
- **Open**: Why does coverage overshoot for n > 2000? Suggests higher-order expansion
  term; analytical investigation needed

### Next steps
- Send "Relax A3" finding to /theory-sharpen for literature confirmation
- Send "Strengthen for bounded designs" to /proof-writer for new theorem draft
- Add additional stress test: lognormal X to test bounded vs unbounded boundary
```

### How findings feed back into the pipeline (hypothesis vs evidence)

| Discovery type | Strength | Feed to | Action |
|---------------|---------|---------|--------|
| Slope is steeper than predicted at every cell along the path | HYPOTHESIS only | `/theory-sharpen` | Investigate sharper rate; do NOT claim until proof updated |
| Slope is shallower than predicted | EVIDENCE of problem | `/proofcheck` | Re-audit proof; possible error |
| Assumption violated in finitely many cells, method still works | HYPOTHESIS only | `/theory-sharpen` | Investigate relaxation; expand stress search; analytic follow-up |
| Assumption violated, method FAILS | EVIDENCE for keeping assumption | `/proof-writer` | Strengthen / refine assumption statement |
| Coverage degrades at small n | EVIDENCE for finite-sample regime | `/proof-repair` or `/theory-sharpen` | Add finite-sample theorem version |

**Key distinction**:
- "EVIDENCE" findings can directly update the paper.
- "HYPOTHESIS" findings require literature search + analytic follow-up before
  the paper is updated. Stage them in an OPEN HYPOTHESES list, not the main paper.

---

## Step 6: Write Simulation Section for the Paper

Final deliverable: a complete simulation section drop-in.

Write `papers/<paper-name>/simulation/SIMULATION_SECTION.tex`:

```latex
\section{Simulation Studies}\label{sec:simulation}

We conduct three experiments to verify the theoretical results and stress-test
the assumptions of Theorems~\ref{thm:1}--\ref{thm:3}. Implementation details and
seeds are provided in Section~S.5 of the supplementary material. Each cell uses
$B=500$ Monte Carlo replications unless noted otherwise.

\subsection{Rate verification (Experiment~E1)}
% Caption describes DGP, baselines, what figure shows
[Description tied to figure]

\subsection{Coverage of confidence intervals (Experiment~E2)}
% Coverage details

\subsection{Stress tests (Experiments~S1-S3)}
% Each stress described, results referenced

\subsection{Summary of empirical findings}
% Reconciliation results that go into the paper
% Findings that lead to theoretical extensions go in Discussion, not here
```

Notes:
- Section structure: rate verification → coverage → stress tests → summary
- Each subsection has 1-2 figures, max
- Defer ALL implementation detail to a supplement section
- Reference theoretical predictions explicitly in captions
- Use the Reference Mode from `/proof-repair` (Mode A vs Mode B) to handle
  cross-file references to theorems

---

## Quick Mode

For a single theorem's quick verification:

```
/theory-simulation papers/my-paper/ --thm "Theorem 1" --quick
```

Runs E1 (rate verification) only, B=200, fewer sample sizes, single figure.

---

## Output Summary

When complete, report to user:

```
Simulation study complete for [Paper].

Experiments run:
├── Baseline (rate verification): E1, E2, ... — X experiments
├── Stress tests: S1-S{K} — assumption violation tests
├── Sensitivity: nuisance parameter sweeps
└── Total CPU time: H hours

Findings:
├── Confirmed predictions: A/N theorems
├── Discrepancies: B issues (see RECONCILIATION.md)
├── Theory-relaxation opportunities: K (forward to /theory-sharpen)
├── Theory-strengthening opportunities: M (forward to /proof-writer)
└── Open questions: J

Files:
├── simulation/SIMULATION_PLAN.md
├── simulation/RECONCILIATION.md
├── simulation/SIMULATION_SECTION.tex
├── simulation/src/ — reusable code
├── simulation/results/*.csv — raw + aggregated data
└── simulation/figures/*.pdf — publication-grade figures (no titles, captions ready)

Next steps:
  - Review RECONCILIATION.md for theory iteration ideas
  - Feed relaxation hints to /theory-sharpen
  - Drop SIMULATION_SECTION.tex into your paper
  - Verify all figures render correctly when compiled into the paper
```
