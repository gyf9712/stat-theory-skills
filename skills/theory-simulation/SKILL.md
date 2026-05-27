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
- Reproducible DGPs with seeds
- Multiple n, d (and other regime parameters)
- ≥500 Monte Carlo replications for asymptotic claims; ≥1000 for tails/coverage
- Honest stress tests, not just easy cases
- Publication-grade figures (described below)
- Comparison with at least one competing method or theoretical baseline

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

## Step 1: Design the Simulation Plan

Write `papers/<paper-name>/simulation/SIMULATION_PLAN.md`.

### 1A: For each theorem, design a verification experiment

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

### 1B: Stress tests (violate one assumption at a time)

For EACH assumption that is theoretically critical, design a stress test that
violates ONLY that assumption.

```markdown
## Experiment S1.1 — Stress: violate sub-Gaussian assumption

### What is changed from baseline (E1)
Replace P_θ* with a heavy-tailed distribution (e.g., t_3) that violates A3 only.
Keep A1, A2 intact.

### Theoretical prediction
- Rate should degrade. If theory predicts breakdown: confirm.
- If theory predicts robustness: confirm (and consider strengthening).

### What we expect to see
- Slower than n^{-1/2} (e.g., n^{-1/4})
- Or large finite-sample bias
- Or no convergence at all

### Pass/fail
- Confirms theory's predicted boundary
- OR reveals theory is too pessimistic (assumption can be relaxed)
- OR reveals theory is too optimistic (assumption is genuinely needed)
```

Common stress tests for statistics papers:

| Stress | What to violate | Expected outcome |
|--------|----------------|------------------|
| Heavy tails | Replace sub-G with t_3 / Pareto | Rate degrades |
| Dependence | Replace i.i.d. with AR(1), MA(q) | Variance inflated, CLT may fail |
| Misspecification | Fit wrong parametric family | Bias persists, pseudo-true target |
| Boundary | θ on ∂Θ | Asymmetric CI, slower rate |
| Identifiability | Near-singular Hessian | Variance blows up |
| Growing dim | d/n → γ ∈ (0,1) | Rate changes |
| Outliers | Add ε-fraction contamination | Method-dependent breakdown |
| Small sample | n = 20, 30 | Asymptotic approximation fails |

### 1C: Rate verification protocol

For any claimed rate r(n) = n^{-a}:
- Run at ≥6 sample sizes spanning ≥1.5 decades (e.g., 50 to 2000)
- Compute empirical MSE at each n with ≥500 reps
- Regress log(MSE) on log(n) → slope should be ≈ −2a
- Report slope estimate + 95% CI

### 1D: Coverage verification (if theory gives CIs)

For nominal coverage 1−α:
- Construct CI on each of B replications
- Coverage = fraction that contains θ*
- Report coverage at several n, with Wilson 95% CI for the coverage itself
- Target band: [1−α − 0.02, 1−α + 0.02] for B = 1000

### 1E: Method comparison (baselines)

Always include ≥1 of:
- Competing method from the literature (e.g., MLE vs proposed estimator)
- Oracle (knows nuisance) — should bound your method's loss
- Naive baseline (e.g., empirical mean)

This protects against the "your method works because every method works here" critique.

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

### 2C: Required code conventions

For reviewer trust:
- **Seeds**: set a master seed + derive per-cell seeds deterministically
  (e.g., `seed = master_seed * 10000 + n_idx * 100 + rep`)
- **Parallel**: use `joblib.Parallel` (Python) or `future_map` (R) — record
  the parallel backend and number of workers
- **Versioning**: dump `requirements.txt` / `sessionInfo()` to results dir
- **Sanity asserts**: every result row has the expected columns + types
- **Progress**: log every 10% of replications
- **Atomic writes**: write results to `.tmp` then rename, so partial runs don't
  corrupt the CSV

### 2D: Make replications cheap

For deep stress tests, MC cost can balloon. Tactics:
- Vectorize over replications when DGP is i.i.d. (`np.random` with shape `(B, n, d)`)
- Use closed-form estimators where possible
- Cache intermediate quantities that don't change across reps within a cell
- Use small B (≤200) for quick pilots; scale to B=500-1000 for final

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

### 4A: Figure conventions (strict — top stat journal style)

**RULES** (these differ from default matplotlib/ggplot defaults):

1. **NO `title`** on plots
   - All title information goes into the **LaTeX caption** of the figure
   - Plots are referenced as "Figure X" with content described in caption text
2. **Captions are content-bearing**:
   - State the DGP, the n range, B, the metric, what the curves are
   - State the theoretical prediction explicitly (e.g., "dashed line is slope −1")
3. **Axis labels**: short but precise
   - `Sample size n` not `n`
   - `Empirical MSE` not `mse`
   - Include units if any
4. **Legend**:
   - Concise method/condition names
   - Place where it does NOT overlap data (use `loc='best'` then verify; if it
     overlaps, move to outside the axes via `bbox_to_anchor`)
   - For >4 entries, use 2-column legend
5. **Color & marker scheme** (color-blind safe):
   - Default palette: Okabe-Ito (8 distinct colors safe for deuteranopia/protanopia)
   - Each method gets a (color, marker, linestyle) triple — redundant encoding
   - Avoid red+green pairs
6. **Reference lines**:
   - Theoretical rate lines as dashed black with explicit slope in caption
   - Nominal coverage line (e.g., 0.95) as dashed grey
7. **Multi-panel**:
   - Use `sharex` / `sharey` when comparing across panels
   - Panel labels (a), (b), (c) in top-left corner inside each panel
   - **No** "Panel A" / "Panel B" titles
8. **Font sizes**:
   - Axis tick labels: 9-10pt
   - Axis labels: 11-12pt
   - Legend: 9-10pt
   - All consistent across figures in the paper
9. **Format**:
   - PDF or EPS for vector graphics — NEVER PNG/JPG for line plots
   - Embedded fonts: `pdf.fonttype = 42` (matplotlib) to make text searchable/editable
   - Bounding box tight: `bbox_inches='tight'`
10. **Overlap prevention**:
    - Use `tight_layout()` or `constrained_layout=True`
    - For dense legends: check no points are hidden
    - For multi-panel: verify x-axis labels not cropped
    - Manual `plt.subplots_adjust()` if needed

### 4B: Required figure types

**Type 1: Rate verification (log-log)**
- x: log(n), y: log(empirical MSE)
- Each method one line
- Reference dashed line with theoretical slope
- Caption states "Slope estimate: −1.02 (95% CI: −1.08, −0.97), consistent with the
  theoretical rate −1 of Theorem 1."

**Type 2: Coverage**
- x: n, y: empirical coverage
- Horizontal dashed at nominal level (0.95)
- Wilson CI bars around each point
- Caption states nominal level, B, deviation tolerance

**Type 3: Stress test comparison**
- Multi-panel: one panel per stress condition
- Same axes within panels for direct comparison
- Caption clearly states which assumption is violated in each panel

**Type 4: Boxplot of distribution of estimator**
- x: n (categorical), y: θ̂ − θ*
- Shows bias + variance + skewness
- Reference line at 0

**Type 5: Heatmap (for two-parameter sweeps)**
- Color = metric, x = n, y = d (or another parameter)
- Colorbar with caption explanation
- Use perceptually uniform colormap (viridis, cividis — NEVER jet/rainbow)

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

## Step 5: Theory ↔ Simulation Reconciliation

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

### Discrepancies discovered
| Finding | Implication for theory |
|---------|----------------------|
| Sub-G assumption (A3) not necessary; t_5 gives same rate | Can RELAX A3 to bounded 4th moment; revisit proof |
| Coverage degrades for n < 50 even though theory says √n | Add finite-sample correction; cite Cattaneo et al. for similar |
| Rate sharper than predicted when X_i has bounded support | Theorem can be STRENGTHENED for bounded designs |

### Recommendations (feedback to theory)
1. **Relax**: Assumption A3 sub-Gaussian → bounded 4th moment (sim supports)
2. **Strengthen**: Theorem 1 can give a faster rate under bounded design (sim shows)
3. **Refine**: Add explicit finite-sample threshold; sim suggests n ≥ 50
4. **Open**: Why does coverage overshoot for n > 2000? Possible
   higher-order term in expansion.

### Next steps
- Send "Relax A3" finding to /theory-sharpen for literature confirmation
- Send "Strengthen for bounded designs" to /proof-writer for new theorem draft
- Add additional stress test: lognormal X to test bounded vs unbounded boundary
```

### How findings feed back into the pipeline

| Discovery type | Feed to | Action |
|---------------|---------|--------|
| Theory under-claims (rate sharper than predicted) | `/theory-sharpen` Step 2B | Add as rate-sharpening direction |
| Theory over-claims (rate slower than predicted) | `/proofcheck` | Re-audit; possible proof error |
| Assumption is unnecessary (sim works without it) | `/theory-sharpen` Step 1 | Add as relaxation candidate |
| Assumption is genuinely needed (sim breaks without it) | `/proof-writer` for new proof | Strengthen assumption statement |
| Finite-sample regime needed | `/proof-repair` or `/theory-sharpen` | New theorem statement |

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
