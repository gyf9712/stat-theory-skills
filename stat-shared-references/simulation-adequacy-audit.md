---
artifact: shared_reference
scope: simulation_adequacy_forensics
generator: extracted from theory-simulation A2.6-A2.10 per Codex threadId 019fa456-c827-7103-9bcc-0a2af1803240
---

# Simulation Adequacy — Forensic Audit Tables

The mode-neutral adequacy CONTRACT (five dimensions, pass conditions, reason-code
mapping) lives inline in `theory-simulation`, because a design mode that has to open a
reference to remember the dimensions will forget them. This file holds only the
forensic detail: the signal-by-signal tables for auditing someone else's finished
simulation section, which design-from-scratch does not need.

### Step A2.6: Reuse legitimacy audit

Before recommending that existing runs be REUSED (rather than rerun), verify
the reuse is statistically legitimate:

| Check | Why | If fails |
|-------|-----|----------|
| Replicate-level outputs saved | Reuse requires per-rep data, not just aggregates | Must rerun |
| RNG streams recorded per replicate | To verify independence and chunking | Must rerun |
| Methods used paired-replicate sharing | Required for valid paired comparisons | Reuse for non-paired metrics only |
| Failures logged, not silently dropped | Silent drops bias aggregates | Audit raw outputs; if not recoverable, rerun |
| Truth target matches the theorem | Sim may have compared to wrong ground truth | Recompute against correct truth or rerun |
| Tuning was held fixed across reps within cell | If tuning varied, the variability is a noise floor | Refer to A2.7 |

Reuse without this audit is a referee magnet. Only bless reuse after all checks pass.

### Step A2.7: Truth-source audit

How was the "truth" (θ*, f*, target estimand) defined in each existing experiment?

| Truth source | Audit needed |
|-------------|--------------|
| Analytic / closed-form | Verify formula correctness; trust if correct |
| Plug-in oracle (knows nuisance) | Verify this matches the theorem's target, not a different one |
| Approximate numerical (e.g., quadrature) | Verify tolerance is much smaller than MCSE of metrics |
| Estimated from a high-B benchmark run | Verify that benchmark's MCSE is reported and small enough |
| Asymptotic limit treated as truth | Often hides bias of order 1/n; flag if rate verification depends on this |

Many papers quietly use the wrong truth. Document the truth-source for each
experiment and flag any that conflate "estimand under model assumption" with
"empirical population quantity".

### Step A2.8: Selection-bias audit

Existing simulation sections often show only the good cells. Look for signals
of selective reporting:

| Signal | What to check |
|--------|--------------|
| **Omitted cells** | Does the paper mention a wider grid than what is shown? Are "additional results" in supp / not shown? |
| **Omitted methods** | Are some baselines mentioned in text but absent from figures? |
| **Omitted regimes** | Does the n / d grid look tailored (e.g., starts at the smallest n where the method beats baseline)? |
| **Omitted DGPs** | Is the stress test menu suspiciously short? |
| **Omitted failures** | Is the failure rate reported? Are convergence diagnostics shown? |
| **Cherry-picked seed** | Is only one Monte Carlo replication / random seed shown for illustration? |

Flag any signal as `SELECTION_RISK` in the gap analysis. Even when not a fatal
flaw, force a rewrite to either show the omitted cells or explain why they were
excluded.

### Step A2.9: Tuning / procedure audit

For each method in the existing simulations, audit how tuning parameters were chosen:

| Tuning regime | Audit |
|--------------|-------|
| Oracle (knows true λ, h, K, ...) | Acceptable for "best case" benchmark; must also report data-driven version |
| Data-driven (CV, BIC, plug-in) | Verify the procedure is described and reproducible |
| Single tuning value mentioned in text | Why this value? Sensitivity check? |
| Tuning varies but variability not reported | Hidden variance source; demand variability over tuning randomness |
| CV / sample splitting with random folds | Is the CV randomness within or across reps? Both have implications |

If the paper claims a method advantage, it must show the advantage holds under
PRACTICAL tuning, not just oracle. If only oracle results are shown, flag as
`TUNING_GAP` and require data-driven version.

### Step A2.10: Computational adequacy audit

If the paper makes ANY of:
- "fast", "scalable", "tractable", "practical"
- "easy to implement"
- "comparable to baseline X in runtime"
- "works for large n / large d"

…then computational diagnostics are mandatory. Audit:

| Item | Should be reported |
|------|-------------------|
| Runtime per replicate (mean, median, max) | Yes, vs n and d |
| Peak memory | Yes, if memory is a constraint |
| Failure rate (nonconvergence, timeout) | Yes, per cell |
| Scaling exponent | Empirical runtime should track theoretical complexity |
| Comparison to baseline runtime | Required if speed advantage is claimed |

Missing computational diagnostics in a paper that markets practicality is a
common referee complaint. Flag as `COMP_GAP` in gap analysis.

