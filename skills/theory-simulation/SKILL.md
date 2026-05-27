---
name: theory-simulation
description: >-
  Bridge between theoretical results and Monte Carlo simulation, built to
  top-stat-journal standards (AoS, JASA, JRSS-B, Biometrika, Bernoulli). For each
  theoretical claim, design simulations that (1) verify the result under stated
  assumptions, (2) stress-test by violating assumptions one at a time, (3) confirm
  rates by log-log slopes, (4) check finite-sample vs asymptotic agreement. Produce
  publication-grade figures (NO titles, content in caption, no overlap, color-blind
  safe). Feed simulation findings back to refine theory. Use when user says
  "simulation plan", "Monte Carlo", "验证理论", "模拟实验", "stress test theory",
  "bridge simulation", "rate verification", or wants reproducible stat-journal
  simulations tied to theorems.
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

---

## Step 1: Design the Simulation Plan (ADEMP-style, claim-based)

Write `papers/<paper-name>/simulation/SIMULATION_PLAN.md`.

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
## Experiment E1 — Verify Theorem 1 (√n-consistency)

### Theoretical prediction
Under Assumptions 1-3: ‖θ̂ − θ*‖ = O_P(n^{-1/2})

### Data Generating Process (DGP)
- X_i ~ i.i.d. P_θ* with θ* = [stated value]
- Sample sizes: n ∈ {50, 100, 200, 500, 1000, 2000, 5000}
- Dimensions: d = [fixed value or sweep]
- Reps: B = 500 per (n, d) cell

### Quantities reported per cell
- Bias: mean(θ̂) − θ*
- Variance: var(θ̂)
- MSE: E‖θ̂ − θ*‖²
- Log-log slope of MSE vs n (should be ≈ −1)

### Pass/fail criteria
- Slope within [−1.1, −0.9] (rate confirmed)
- Bias decays to 0 with n
- 95% bootstrap CI for slope contains −1

### Figure target
- Figure E1: log MSE vs log n, with theoretical slope line overlaid
- Table E1: bias, SD, MSE × n at each n (verifies it stays bounded)
```

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

### 2A: Language choice

Decide based on existing project / user preference:
- **Python** (`numpy`, `scipy`, `statsmodels`, `joblib` for parallel) — default
- **R** (`tidyverse`, `parallel`, `future`) — preferred for some stat audiences

Default to Python unless project already has R code. Ask user if unclear.

### 2B: Code structure

Lay out the simulation as a small library, not a monolithic script:

```
papers/<paper-name>/simulation/
  SIMULATION_PLAN.md      # the design doc
  config.py / config.R    # global params, seeds
  src/
    dgp.py                # data generating processes (one per stress test)
    estimators.py         # the proposed estimator + baselines
    metrics.py            # bias, variance, MSE, coverage, slope
    run.py                # one-cell runner: (n, d, dgp, B) → metrics
  scripts/
    run_E1.py             # one script per experiment
    run_S1_1.py
  results/
    E1.csv                # one row per (n, d, rep) cell
    S1_1.csv
  figures/                # output, populated by Step 4
  README.md               # how to reproduce
```

### 2C: Reproducibility — TIERED (STRICT is default for top-stat-journal work)

| Tier | Use case | Required |
|------|----------|----------|
| **BASIC** | PhD prototype, exploratory study | Single seed + `requirements.txt` + git commit hash |
| **STRICT** (DEFAULT) | Paper draft for top-stat-journal submission | All of BASIC + **hierarchical RNG streams** (`np.random.SeedSequence` / `L'Ecuyer-CMRG`) + per-replicate stored seed + thread-count recorded + `pip-compile`/`renv` lockfile + paired-replicate sharing across methods |
| **PUBLICATION** | Replication package for code release | All of STRICT + container or reproducible-environment recipe (Docker/Singularity/Nix) + pinned BLAS/MKL version + replicate-level result archive + reproduce-all script that regenerates every table and figure |

The skill defaults to STRICT. Downgrade to BASIC only with explicit user opt-in
(e.g., for fast prototyping). Always escalate to PUBLICATION before code release.

**Reproducibility target — declare explicitly**:
- **Bitwise identical reruns**: every replicate produces exact same numbers.
  Requires fixed thread counts (`OMP_NUM_THREADS=1` etc.), fixed BLAS/MKL version,
  fixed library versions. Often only achievable inside a container.
- **Statistically equivalent reruns**: aggregate metrics agree to within MCSE
  across reruns; individual replicates may differ due to BLAS / library updates.
  More realistic for long-lived projects.

State the target in `simulation/README.md`. The default for STRICT tier is
statistically equivalent; for PUBLICATION tier, bitwise identical is preferred.

**STRICT-tier conventions**:
- **Hierarchical RNG**: NEVER use `master_seed * 10000 + n_idx * 100 + rep` arithmetic
  — it has collision risk and breaks under parallel chunking. Use:
  ```python
  ss = np.random.SeedSequence(master_seed)
  child_seeds = ss.spawn(n_cells * B)  # one independent stream per (cell, replicate)
  rng_for_cell_rep = np.random.default_rng(child_seeds[cell_idx * B + rep])
  ```
  In R, use `RNGkind("L'Ecuyer-CMRG")` and store the state per replicate.
  RECORD the RNG algorithm + version in result files.
- **Parallel determinism**: joblib/future are SCHEDULERS only. They do not by themselves
  guarantee reproducibility:
  - Each worker must construct its own RNG from the child seed for its replicate
  - Threaded BLAS introduces non-determinism: set `OMP_NUM_THREADS=1`,
    `MKL_NUM_THREADS=1`, `OPENBLAS_NUM_THREADS=1` when bit-reproducibility matters
  - Record actual thread counts + scheduler backend in the result file
- **Atomic writes**: write to `.tmp` then rename (you had this).
- **Versioning**: lockfile (`pip-compile` → `requirements.txt` with hashes, or `renv.lock`)
- **Env record**: thread env vars, thread counts, OS, CPU model, BLAS lib + version,
  Python/R version, git commit, hostname
- **Sanity asserts**: dtype + shape on every result row + invariants
  (e.g., variance ≥ 0, B replicates per cell)

Note: paired replicates across methods is NOT in this list — it lives in Step 1E
as a core design rule, not a tier-conditional reproducibility option.

References: Morris et al. (2019); JASA Reproducibility Editorial (2024).

### 2C′: Code architecture — manifest-driven, immutable cells

The previous "dgp.py / estimators.py / metrics.py" layout works for small studies
but rots fast under paper revisions. For top-journal work use a manifest-driven
architecture:

```
papers/<paper-name>/simulation/
  manifest/
    experiments.yaml      # one entry per experiment: id, DGP, n grid, methods, etc.
    cells.csv             # expanded: one row per (experiment, cell), with cell_id hash
  src/
    dgp.py, estimators.py, metrics.py, run.py   # core code
  results/
    raw/{cell_id}/rep_{rep_id}.json       # immutable replicate-level outputs
    aggregated/{cell_id}.csv               # per-cell summary
  figures/{figure_id}.pdf
  tables/{table_id}.tex
  reproduce.{sh,py}        # rebuilds ALL tables/figures from results/
  tests/test_toy.py        # regression tests on small toy DGPs (catch silent bugs)
  README.md
```

Key properties this enables:
- **Immutable `cell_id`** = hash(manifest entry + code version). Same inputs → same id.
- **Provenance trail**: every figure panel traces back to specific cells, which trace
  to specific reps, which trace to RNG streams + code version
- **Reruns are cheap**: rerunning a cell after a code fix produces a new `cell_id`;
  old results remain comparable
- **Reproduce script**: `reproduce.sh` rebuilds the paper's tables and figures from
  saved `results/` without re-running expensive sims (assumes results exist)
- **Regression tests**: 1-2 small DGPs with known closed-form answers run in
  every CI / pre-commit, catching silent breakage during paper revisions

This is the architecture top-journal authors actually use during 6-month revision
cycles. Without it, "we re-ran simulations after addressing R1's comments" turns
into a multi-week mess.

### 2D: Failure handling (REQUIRED — referee magnet if missing)

Real stats simulations fail. Optimizers don't converge, Hessians become singular,
selected models are empty, variance estimates go negative. PREDECLARE the policy:

- Every replicate logs a `status` field: `success / nonconvergence / singular /
  empty_model / negative_variance / timeout / other`
- Per cell, report:
  - **Failure rate** by status
  - **What is counted in metrics**: success-only? success + recoverable? all?
  - **Policy declaration**: whether failures are excluded, treated as worst-case,
    or treated as separate metric
**Default alert thresholds (interpret in regime context, not as universal laws)**:

| Failure rate | Default alert | Context-dependent interpretation |
|--------------|---------------|----------------------------------|
| >5% | FLAG in reconciliation | In a benign regime: suspicious — investigate. In an intentionally near-singular stress regime: may be expected and even informative. |
| >20% | SUSPECT — cell result questionable | In stress tests near a known breakdown: this IS the scientific finding (report failure rate as the metric). In a baseline regime: cell likely uninterpretable. |

A 6% failure rate in a benign DGP is worse than 20% in an intentionally adversarial
DGP. Interpret thresholds relative to:
- **Regime severity**: is the cell intended to be benign, moderate, or adversarial?
- **Scientific role**: is failure itself part of the claim (a breakdown experiment)
  or an unintended outcome?

The skill should NOT auto-mark cells as bad based on threshold alone. Surface the
failure rate to the user with context and let the user interpret.

Without explicit failure handling, a referee will ask "what happened in the cells
where MSE looks suspiciously clean?" and you have no answer.

### 2E: Make replications cheap

For deep stress tests, MC cost can balloon. Tactics:
- Vectorize over replications when DGP is i.i.d. (`np.random` with shape `(B, n, d)`)
- Use closed-form estimators where possible
- Cache intermediate quantities that don't change across reps within a cell
- Use small B (≤200) for quick pilots; scale to MCSE-target B for final

### 2F: Storage format (CSV by default; Parquet for large studies)

- **CSV** (default): adequate for small-to-moderate studies (<1M rows, <200MB)
- **Parquet / Feather**: switch when ANY of:
  - Total rows > 1M (e.g., many cells × many reps × many metrics)
  - Total file size > 200MB
  - Files re-read repeatedly during analysis / plotting
  - Strict schema preservation matters (dtype fidelity)
- Use immutable replicate-level rows + a separate aggregated file
- Schema columns at minimum:
  `cell_id, dgp, n, d, other_path_params, rep, seed_used, status, metric_name, value, runtime_seconds`

### 2G: Edge cases that need special design

| Edge case | Issue | Required adjustment |
|-----------|-------|---------------------|
| **Rare events / tail risk** | B=1000 gives 50 rare events at p=0.05; too noisy | Use importance sampling or stratified resampling; OR scale B to ≥ 10/p_target |
| **Randomized algorithms** | Method has its own RNG | Use a second hierarchical RNG layer for algorithm randomness; record both seeds per replicate |
| **No closed-form ground truth** | Estimand `θ* = E[g(X)]` is itself unknown | Run a one-time HIGH-B benchmark to estimate θ* with negligible error; treat it as ground truth (note its MCSE in the report) |
| **Long-running estimators** | Each rep takes minutes/hours | Time-budget per cell; checkpoint partial results; cluster jobs |
| **Adaptive/sequential procedures** | State evolves across observations | DGP must support sequential generation; replication keys both the data and any algorithm randomness |

---

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

## Step 4: Publication-Grade Figures (stat-journal style)

### 4A: Figure conventions (split: actual journal rules vs stat house style)

#### Actual journal requirements (CHECK each venue's current guidelines)

| Requirement | Source | Applies to |
|------------|--------|------------|
| Alt text for figures (accessibility) | JRSS-B, Biometrika guidelines | JRSS-B, Biometrika submissions |
| Final-size legibility (camera-ready dimensions) | All top stat journals | All — verify at intended print size |
| Color must encode redundantly (also via line style / marker) for grayscale printing | JRSS-B, Biometrika | All |
| Vector format for line plots | Most | All |

**Always check the venue's current guidelines** before submission. The skill cannot
keep these up to date.

#### Stat-paper house style (strong convention, not always required)

These reflect AoS / JASA / Biometrika / JRSS-B house conventions:

1. **Plot titles are usually OMITTED** — content moves to LaTeX `\caption{}`
   - This is convention, not a hard rule. Compare Nature, where titles are common.
2. **Content-bearing captions**: DGP, n range, B, metric, theoretical prediction
3. **Axis labels**: short but precise ("Sample size n", "Empirical MSE")
4. **Legend placement** does not cover data — verify visually; use `bbox_to_anchor`
   when needed; ≥5 entries → 2-column legend
5. **Color-blind-safe palettes** (emerging expectation): Okabe-Ito for lines,
   viridis/cividis for heatmaps. Avoid jet/rainbow.
6. **Redundant encoding**: each method gets (color, marker, linestyle) — supports
   grayscale + color-blind readers
7. **Reference lines for theoretical predictions** (dashed black for rate, dashed
   grey for nominal coverage)
8. **MC uncertainty shown**: every data point should have an MCSE error bar or
   shaded band — referees expect to see uncertainty
9. **Multi-panel**: in-panel labels (a) (b) (c) (lowercase is common but check
   venue); no panel titles; share axes when comparing
10. **Embedded fonts** (`pdf.fonttype = 42`): best practice for editable PDF,
    not a journal requirement

The previous version of this skill called some of the above "rules" — they are
conventions and best practices, not legal requirements. Verify against each
venue's current guidelines.

### 4B: Figure menu — CONDITIONAL on the empirical claim

Pick figures matched to the claim being supported. Not every paper needs every
figure; some need figures not on this list.

| Claim being supported | Figure type | Notes |
|---------------------|-------------|-------|
| Rate of convergence | Log-log loss vs n, with theory reference slope and MC bands | Add normalized-loss leveling-off plot as a sanity check |
| Limiting distribution | QQ plot of studentized pivot vs N(0,1) | Plus density / ECDF comparison |
| Coverage of CIs | Empirical coverage vs n with Wilson CIs and nominal dashed line | Add interval-length plot |
| Test size and power | Size vs n; power curve vs local alternative | Reference at nominal α |
| Estimator distribution | Boxplots / violins of `θ̂ − θ*` vs n | Reference line at 0 |
| EmpSE vs ModSE calibration | Scatter or ratio plot, target ratio = 1 | One point per cell |
| Method comparison (paired) | Paired-difference plot with MC CIs, or lollipop with bars | More informative than overlaid lines for >3 methods |
| Two-parameter sweeps | Heatmap on viridis/cividis (NEVER jet/rainbow) | Colorbar with units |
| Failure rates per cell | Bar/heatmap of nonconvergence rates | Required if any cell has >5% failures |

Figures must show MC uncertainty (error bars, shaded bands, or visible MCSE).
A point estimate plot without uncertainty is not publishable.

### 4C: Concrete matplotlib template (Python)

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# Stat-journal style setup
mpl.rcParams.update({
    'pdf.fonttype': 42,            # editable text in PDF
    'ps.fonttype': 42,
    'font.family': 'serif',        # matches LaTeX document
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 0,           # we don't use titles — force 0
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.spines.top': False,      # remove top/right spines (Tufte-ish)
    'axes.spines.right': False,
})

# Okabe-Ito palette (color-blind safe)
OKABE_ITO = ['#E69F00','#56B4E9','#009E73','#F0E442',
             '#0072B2','#D55E00','#CC79A7','#000000']

fig, ax = plt.subplots(figsize=(3.5, 2.8))  # single-column-friendly

# Plot data
for i, method in enumerate(methods):
    ax.plot(log_n, log_mse[method],
            color=OKABE_ITO[i], marker='os^DvX'[i], linestyle='-',
            label=method)

# Theoretical slope reference
ax.plot(log_n, theoretical_intercept - 1.0*log_n,
        color='black', linestyle='--', linewidth=1, label='theory: slope $-1$')

# Axis labels — short + precise, NO title
ax.set_xlabel(r'$\log n$')
ax.set_ylabel(r'$\log$ empirical MSE')

# Legend placement
leg = ax.legend(loc='best', frameon=False)
# Verify no overlap; if needed: ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')

fig.tight_layout()
fig.savefig('figures/E1_rate.pdf')
plt.close(fig)
```

### 4D: Caption template (for the LaTeX paper)

```latex
\begin{figure}[t]
  \centering
  \includegraphics{figures/E1_rate.pdf}
  \caption{Empirical MSE versus sample size for the proposed estimator and two
  baselines (oracle and MLE). DGP: $X_i \stackrel{iid}{\sim} N(\theta^*, 1)$ with
  $\theta^* = 0.5$; $d=5$ fixed; $B=500$ Monte Carlo replications per cell.
  The dashed line shows the theoretical rate $n^{-1}$ (slope $-1$) predicted by
  Theorem~1. The fitted slope for the proposed estimator is $-1.02$
  (95\% CI: $[-1.08, -0.97]$), confirming the theoretical rate.}
  \label{fig:E1-rate}
\end{figure}
```

### 4E: Pre-export checklist (run before saving every figure)

- [ ] No `title()` call anywhere
- [ ] Legend does not cover data points (visual check)
- [ ] All axis labels are present and readable
- [ ] Color scheme is color-blind safe (Okabe-Ito or viridis)
- [ ] At least one reference line (theoretical prediction) when applicable
- [ ] Font sizes consistent across all figures in the paper
- [ ] Saved as PDF/EPS with embedded fonts
- [ ] `tight_layout()` applied — no clipping at edges
- [ ] Caption written and stored alongside the figure file
- [ ] Figure has a unique label for cross-referencing

---

## Step 4F: Codex Adversarial Review of Simulation Design (if Codex MCP available)

Before running expensive simulations, send the SIMULATION_PLAN.md to Codex for an
independent design review. Catching design flaws BEFORE running saves CPU hours.
After running, do a second Codex pass on the figures + reconciliation.

### Pass 1: Plan review (before running)

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are a senior referee for a top statistics journal (AoS / JASA / Biometrika / JRSS-B).
    A paper provides the following theoretical claims and proposed Monte Carlo simulation plan.

    THEORETICAL CLAIMS:
    [paste main theorems with assumptions + rates]

    SIMULATION PLAN:
    [paste SIMULATION_PLAN.md]

    Adversarial review tasks (be harsh — assume the simulation IS the test of the theory):
    1. Coverage: does EVERY theoretical claim have a verification experiment?
       Which assumptions are NOT stress-tested? Name them specifically.
    2. DGP quality: are the chosen DGPs the WORST CASES the theory should handle, or
       are they easy cases that any method would pass?
    3. Sample-size grid: is the range wide enough to identify the rate? Is it deep
       enough to see finite-sample breakdown? Suggest specific n values to add.
    4. Replication count: is B large enough for the metrics? (Coverage needs B ≥ 1000
       for ±0.014 SE at nominal 0.95; tail metrics need more.)
    5. Baselines: is the comparator the right one? Is there an obvious competitor missing?
    6. Rate verification: is the slope-regression protocol valid? Is there a known
       bias-variance issue (e.g., bias term dominating at small n)?
    7. Missing stress tests: list any standard violation that should be tested but isn't.

    Output a numbered list of design issues with severity (CRITICAL / MAJOR / MINOR).
    For each, propose a specific fix.
```

### Pass 2: Figure + reconciliation review (after running)

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are reviewing simulation results from a paper aimed at a top stat journal.

    THEORY:
    [paste theorems]

    SIMULATION RESULTS:
    [paste aggregated metrics tables — e.g., bias/SD/MSE × n for each method × DGP]

    RECONCILIATION CLAIM:
    [paste RECONCILIATION.md draft]

    FIGURE CAPTIONS:
    [paste each \caption text]

    Adversarial review tasks:
    1. Do the empirical numbers ACTUALLY support the claimed reconciliation, or is
       the author overclaiming "✅ confirmed" when slope is borderline?
    2. Are any results SUSPICIOUS — e.g., coverage above 0.99 (overcoverage), or
       MSE non-monotone in n? Could these signal a coding bug?
    3. For each "discrepancy" the author flags as theory-relaxation opportunity:
       is the relaxation actually supported, or could the simulation be too easy?
    4. Caption sanity: do captions state the DGP, B, n range, baselines, and the
       theoretical prediction explicitly? Flag any captions missing context.
    5. Figure-level issues: based on the captions alone, is the figure asking the
       right question? Is the dashed reference line the right slope?

    Output: per-finding verdict (CONFIRMED / OVERCLAIMED / UNDERCLAIMED / SUSPICIOUS)
    with specific evidence.
```

### Reconciliation with Claude's findings

Same pattern as the other skills: first-independent-then-reconcile.

```markdown
## Codex Simulation Design Review

### Pass 1 (Pre-run) findings
| Issue | Severity | Codex says | Claude action |
|-------|---------|------------|---------------|
| Stress test for dependence missing | MAJOR | Add AR(1) DGP | Adding to plan |
| B=500 too small for coverage | CRITICAL | Use B=2000 for coverage cells | Adjusting plan |
| No competitor for Thm 3 | MINOR | Add MLE | Noted; addressed |

### Pass 2 (Post-run) findings
| Finding | Codex verdict | Claude original | Final |
|---------|--------------|-----------------|-------|
| Thm 1 rate slope = -0.51 | CONFIRMED | ✅ Confirmed | Agree |
| "Sub-G can be relaxed" | OVERCLAIMED — only tested t_5, didn't test t_3 | Relaxation candidate | Downgrade to "needs more tests" |
| Coverage at n=2000 is 0.991 | SUSPICIOUS — overcoverage suggests CI too wide | ✅ Confirmed | Investigate; may be variance plug-in conservative |
```

Write to `simulation/codex_design_review.md`.

**Critical**: when Codex flags OVERCLAIMED or SUSPICIOUS, DO NOT auto-update
RECONCILIATION.md to silently match. Surface the disagreement to the user.

---

## Step 5: Theory ↔ Simulation Reconciliation (HYPOTHESIS GENERATION ONLY)

**CRITICAL DISCIPLINE**: Simulation findings can SUGGEST hypotheses for theory
extension. They CANNOT validate theorem-weakening. A finite grid of DGPs is not
a proof; "method survived t_5" is NOT evidence that the sub-Gaussian assumption
can be dropped — the worst-case DGP may be elsewhere in the space.

Use simulation feedback to **generate hypotheses for analytic follow-up**, not
to declare theory upgrades.

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
