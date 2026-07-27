---
artifact: shared_reference
scope: simulation_execution
generator: extracted from theory-simulation Step 2 per Codex threadId 019fa42e-217f-7171-b94f-99b95177aab8 (execution manual out of the hot body)
---

# Simulation Execution Protocol

Language choice, code structure, reproducibility tiers, manifest-driven cell
architecture, failure handling, storage format, and edge cases for Monte Carlo
studies. Consumed by `theory-simulation` Step 2. The skill keeps only the hard
gates; everything operational lives here.

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
