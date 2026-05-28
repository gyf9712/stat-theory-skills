---
artifact: shared_reference
scope: applicability_axes
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills applicability axes protocol, Codex round 2 threadId 019e70c3-1844-7181-b6a1-0b4041c657df
---

# Applicability Axes and Namespaced Assumption Families

Companion to `literature-cache-protocol.md` (router) and `citation-purpose-protocol.md` (purposes and gates). This file defines the eight applicability axes that the cache uses to determine whether a cited result actually applies to a target problem, the namespaced assumption families on each axis, and the five compatibility verdicts.

## When to Read

- When constructing or updating an `applicability_contract` block on a cache entry.
- When checking compatibility at citation time for `load_bearing`, `benchmark_claim`, `comparative` purposes (the three purposes that exercise the axis check).
- When extending the family vocabulary for a new domain.

This file does NOT need to be loaded for `lineage_positioning`, `technique_inheritance`, `standard_tool`, or `background_motivation` citations — those purposes do not run the axis check.

## The Eight Axes

Every cache entry's `applicability_contract` declares values on these axes. Skills constructing a `target_contract` from their current problem use the same axes.

### 1. `data_structure`

| Value | Meaning |
|---|---|
| `iid` | independent, identically distributed |
| `exchangeable` | finitely or infinitely exchangeable; weaker than iid |
| `mixing` | weakly-dependent; α-mixing / β-mixing / φ-mixing |
| `markov` | finite or general state-space Markov chain; geometric / polynomial ergodicity |
| `time_series` | structured-dependent time series; ARMA / VAR / state-space |
| `panel` | cross-sectional units observed over time |
| `spatial` | spatially-indexed observations; lattice / point process / continuous-space |
| `network` | network-indexed observations; node / edge / dyadic |
| `sequential` | sequentially-generated; martingale-difference; online; streaming |

### 2. `modeling_framework`

| Value | Meaning |
|---|---|
| `parametric` | finite-dimensional parameter; well-specified or misspecified |
| `parametric_misspecified` | finite-dimensional model assumed but possibly wrong |
| `semiparametric` | finite-dimensional parameter of interest plus infinite-dimensional nuisance |
| `semiparametric_efficient` | semi-parametric with efficient influence function |
| `semiparametric_doubly_robust` | semi-parametric with double-robustness property |
| `nonparametric` | infinite-dimensional target |
| `nonparametric_smooth` | nonparametric with smoothness constraint (Sobolev / Hölder / Besov) |
| `nonparametric_density` | density estimation |
| `nonparametric_regression` | regression function estimation |
| `nonparametric_functional` | function-valued observations or targets |

### 3. `asymptotic_regime`

| Value | Meaning |
|---|---|
| `classical` | fixed $p$, $n \to \infty$ |
| `proportional` | $p/n \to \gamma \in (0, \infty)$ |
| `high_d_sparse` | $\log p / n \to 0$ with sparsity $s$ |
| `high_d_dense` | $p / n \to \infty$ without sparsity assumption |
| `ultra_high_d` | $\log p$ comparable to or larger than $n$ |
| `non_asymptotic` | finite-sample bounds with explicit constants |
| `online` | streaming / online learning |
| `streaming` | data arriving as a stream; cannot store past |
| `large_population` | super-population framework |
| `super_consistent` | $n^{1+\alpha}$-rate for $\alpha > 0$ |

### 4. `tail_condition`

| Value | Meaning |
|---|---|
| `bounded` | almost surely bounded |
| `sub_gaussian` | $\mathbb{E}[\exp(\lambda X)] \le \exp(\lambda^2 \sigma^2 / 2)$ |
| `sub_exponential` | $\mathbb{P}(|X| > t) \le 2 \exp(-t/\sigma)$ for large $t$ |
| `polynomial_p_moment` | $\mathbb{E}[|X|^p] < \infty$ for specified $p$ |
| `bounded_variance` | $\mathbb{E}[X^2] < \infty$ only |
| `heavy_tail` | regularly-varying tail; $\alpha$-stable; not all moments exist |
| `regularly_varying` | tail satisfies $\mathbb{P}(X > t) = t^{-\alpha} L(t)$ for slowly-varying $L$ |
| `compactly_supported` | support contained in a known compact set |
| `mgf_finite_neighborhood` | MGF exists in a neighborhood of zero |

### 5. `norm`

| Value | Meaning |
|---|---|
| `spectral` | operator norm of a matrix |
| `frobenius` | Frobenius norm |
| `operator` | general operator norm in functional setting |
| `l2` | Euclidean $\ell_2$ |
| `linf` | $\ell_\infty$ |
| `l1` | $\ell_1$ |
| `lp` | general $\ell_p$ |
| `Linf` | $L^\infty$ functional |
| `L2` | $L^2$ functional |
| `Lp` | $L^p$ functional |
| `wasserstein_p` | Wasserstein distance order $p$ |
| `total_variation` | TV distance |
| `KL` | Kullback-Leibler divergence |
| `hellinger` | Hellinger distance |
| `bregman` | Bregman divergence |
| `dual_norm` | Lagrangian dual of an underlying norm |

### 6. `probability_mode`

| Value | Meaning |
|---|---|
| `with_high_probability` | bound holds with probability $1 - \delta$ for specified $\delta$ |
| `in_probability` | convergence in probability |
| `almost_sure` | almost sure convergence |
| `Lp_convergence` | convergence in $L^p$ for specified $p$ |
| `quenched` | conditional on the data path / configuration |
| `annealed` | average over data path / configuration |
| `uniform_over_class` | bound is uniform over an indexing class |
| `uniform_in_parameter` | uniform over parameter space |
| `pointwise` | for each fixed parameter / function |
| `expectation_only` | a statement about expectation, not on path |

### 7. `dimensions`

Free-text describing the asymptotic path. Example values:

- `p, n -> infinity; log p / n -> 0; p >= n permitted`
- `p, n, s -> infinity; s log(p/s) / n -> 0`
- `n -> infinity; p fixed`
- `n -> infinity; p/n -> gamma in (0, 1)`
- `non-asymptotic; n >= 1 valid`
- `p, n -> infinity; p / sqrt{n} -> infinity (ultra-high-d)`

Free-text rather than enum because the asymptotic path is problem-specific.

### 8. `sparsity_class` / smoothness class / structural class

| Value | Meaning |
|---|---|
| `l0_sparse` | exact sparsity by $\ell_0$ norm |
| `lp_ball_sparse` | $\ell_p$-ball for $p \in (0, 1]$ |
| `approximately_sparse` | compressible: $j$-th coefficient decays as $j^{-\alpha}$ |
| `block_sparse` | non-overlapping block structure |
| `group_sparse` | overlapping groups |
| `tree_sparse` | tree-structured sparsity (wavelet) |
| `hierarchical_sparse` | hierarchical structure (lasso variants) |
| `bandable` | covariance / kernel decays with distance from diagonal |
| `toeplitz` | Toeplitz structure |
| `circulant` | circulant structure |
| `low_rank` | $r$-dimensional column / row space |
| `sobolev` | Sobolev smoothness class $W^{s,p}$ |
| `holder` | Hölder smoothness class $C^{s,\alpha}$ |
| `besov` | Besov smoothness class $B^{s}_{p,q}$ |
| `lipschitz` | Lipschitz continuity |
| `convex_lipschitz` | convex Lipschitz functions |
| `monotone` | monotone (shape constraint) |
| `unimodal` | unimodal (shape constraint) |
| `none` | no structural constraint |

## Namespaced Assumption Families

The `same_family` compatibility verdict invokes assumption families. Per Codex's round 2 verdict, families must be **namespaced by domain** to prevent rot: "moment-based tail control" means different things in high-dimensional covariance, empirical process theory, robust mean estimation, and random matrix work.

Family identifiers use the syntax: `<domain>.<axis>:<family>`. Examples: `highdim.tail_condition:moment_based`, `empirical_process.complexity:vc`.

### Domain registry

The following domains are recognized. New domains may be introduced by `/lit-cache verify` with explicit rationale.

- `highdim` — high-dimensional statistics (lasso, covariance, mean, regression)
- `empirical_process` — empirical process theory (Donsker, Glivenko-Cantelli, chaining)
- `concentration` — concentration inequality theory (Talagrand, McDiarmid, Bernstein-style)
- `random_matrix` — random matrix theory (Marchenko-Pastur, BBP, Tracy-Widom)
- `m_estimation` — M-estimation and Z-estimation theory
- `semiparametric` — semiparametric efficiency, double robustness, influence functions
- `bayesian_asymptotics` — posterior contraction, BvM, prior elicitation
- `nonparametric` — nonparametric estimation rates (regression, density, functional)
- `causal_inference` — identification, IPW, double machine learning, sensitivity
- `survival` — survival analysis, hazard, censored data
- `time_series` — stationary and non-stationary time series
- `multiple_testing` — FDR, FWER, dependent tests
- `online_learning` — regret, online convex optimization
- `robust_statistics` — heavy-tail, contamination, median-of-means
- `minimax_lower_bounds` — Fano, Le Cam, Assouad, packing arguments

### Families per axis (per domain)

The same axis name carries different families across domains. Selected examples (extensible):

#### `tail_condition`

| Domain | Family ID | Members |
|---|---|---|
| `highdim` | `highdim.tail_condition:moment_based` | sub_gaussian, sub_exponential, polynomial_p_moment, bounded_variance |
| `highdim` | `highdim.tail_condition:bounded` | bounded, compactly_supported |
| `highdim` | `highdim.tail_condition:heavy_tail` | heavy_tail, regularly_varying |
| `empirical_process` | `empirical_process.tail_condition:envelope_p_moment` | envelope-function with $p$-th moment for specified $p$ |
| `empirical_process` | `empirical_process.tail_condition:envelope_bounded` | uniformly bounded envelope |
| `random_matrix` | `random_matrix.tail_condition:concentration_quad` | sub-Gaussian quadratic forms, Hanson-Wright applicable |
| `random_matrix` | `random_matrix.tail_condition:moments_4plus` | uniformly bounded 4-th and higher moments |
| `robust_statistics` | `robust_statistics.tail_condition:contamination` | $\epsilon$-contamination model; Huber contamination |
| `robust_statistics` | `robust_statistics.tail_condition:p_moment_only` | only $p$-th moment ($p \in (1, 2]$) is finite |

#### `data_structure`

| Domain | Family ID | Members |
|---|---|---|
| `highdim` | `highdim.data_structure:independence` | iid, exchangeable |
| `time_series` | `time_series.data_structure:short_memory` | α-mixing with exponential rate; β-mixing with polynomial rate $> 2$ |
| `time_series` | `time_series.data_structure:long_memory` | regularly-varying autocorrelation; $d \in (0, 1/2)$ memory parameter |
| `time_series` | `time_series.data_structure:non_stationary` | difference-stationary, trend-stationary, locally stationary |
| `causal_inference` | `causal_inference.data_structure:cross_sectional_iid` | cross-sectional iid units |
| `causal_inference` | `causal_inference.data_structure:panel_with_treatment` | repeated measures with intervention |
| `survival` | `survival.data_structure:right_censored_iid` | right-censored iid |
| `survival` | `survival.data_structure:competing_risks` | competing risks structure |

#### `sparsity_class`

| Domain | Family ID | Members |
|---|---|---|
| `highdim` | `highdim.sparsity_class:exact_or_compressible` | l0_sparse, lp_ball_sparse, approximately_sparse |
| `highdim` | `highdim.sparsity_class:structured` | block_sparse, group_sparse, tree_sparse, hierarchical_sparse |
| `highdim` | `highdim.sparsity_class:matrix_structure` | bandable, toeplitz, circulant, low_rank |
| `nonparametric` | `nonparametric.sparsity_class:smoothness` | sobolev, holder, besov, lipschitz |
| `nonparametric` | `nonparametric.sparsity_class:shape_constraint` | monotone, unimodal, convex |

#### `asymptotic_regime`

| Domain | Family ID | Members |
|---|---|---|
| `highdim` | `highdim.asymptotic_regime:high_dim_sparse` | high_d_sparse, ultra_high_d |
| `highdim` | `highdim.asymptotic_regime:proportional` | proportional |
| `random_matrix` | `random_matrix.asymptotic_regime:bulk` | $p/n \to \gamma \in (0, 1)$; bulk Marchenko-Pastur |
| `random_matrix` | `random_matrix.asymptotic_regime:edge` | edge / Tracy-Widom regime |
| `non_asymptotic` (cross-domain) | `<domain>.asymptotic_regime:non_asymptotic` | non_asymptotic with explicit constants |

(Other axis families: extensible — `applicability-axes.md` is intended to grow as new domains are added. Each new family is introduced by `/lit-cache verify` with documented rationale; the verifier checks the family is genuinely a methodological cluster, not a renaming.)

## The Five Compatibility Verdicts

The citing skill compares its `target_contract` against the cache entry's `applicability_contract` on each axis. The verdict on each axis is one of:

| Verdict | Meaning | Example |
|---|---|---|
| `match` | exact equality on the axis | target = `iid`, cache = `iid` |
| `compatible` | cache is at least as general as target | target = `iid`, cache = `exchangeable_or_iid` |
| `same_family` | values differ but belong to the same namespaced family | target = `sub_exponential`, cache = `sub_gaussian`, both in `highdim.tail_condition:moment_based` |
| `partial` | difference present, not in same family, but possibly bridgeable | target = `iid`, cache = `mixing`; reachable via dependence-aware variant + bridge |
| `mismatch` | cache result does not cover the target and no family relation | target = `heavy_tail`, cache = `sub_gaussian` in domain where these are different families |

The aggregate per-citation decision uses these verdicts as inputs; the rule depends on the citation purpose (see `citation-purpose-protocol.md`).

## Compatibility Check Algorithm

Given a `target_contract` and a cache entry's `applicability_contract`, compute one verdict per axis:

```
for axis in [data_structure, modeling_framework, asymptotic_regime,
             tail_condition, norm, probability_mode, dimensions, sparsity_class]:
    target_value = target_contract[axis]
    cache_value  = cache_contract[axis]

    if target_value == cache_value:
        verdicts[axis] = match
    elif cache_value is a generalization of target_value (cache supports superset):
        verdicts[axis] = compatible
    elif both belong to the same namespaced family <domain>.<axis>:<family>:
        verdicts[axis] = same_family
        record_family_membership(target_value, cache_value, family_id)
    elif there exists a documented bridge (in the project's repair plan or a cached lemma) connecting target_value to cache_value:
        verdicts[axis] = partial
        record_bridge(axis, target_value, cache_value, bridge_artifact_ref)
    else:
        verdicts[axis] = mismatch
        record_mismatch(axis, target_value, cache_value)
```

The set of axis verdicts is returned to the citation-purpose gate (see `citation-purpose-protocol.md` decision algorithm).

## Honest Limits

- **Family membership is judgment.** The `same_family` verdict relies on the family registry; the registry is curated by `/lit-cache verify`, not by the citing skill. Disagreements about family membership are recorded in the entry's `verification_log`.
- **Bridges are assertions, not proofs.** Recording a `partial` bridge in `cited_results.lock.md` does not by itself certify the bridge is mathematically valid. The bridge artifact (Lemma A.4, PATCHES.md Patch-7, etc.) must be verified separately by `/proofcheck` or `/proof-repair`.
- **Free-text axes (dimensions) cannot be axis-checked mechanically.** The `dimensions` axis is free-text; compatibility on this axis is human-judged at `/lit-cache verify`.

## Extending the Axes or Families

To add a new domain to the family registry:

1. Propose the domain identifier (lower-case, underscore-separated, no overlap with existing domains).
2. For each axis where the new domain's families differ from existing domains, propose the new family IDs with their members.
3. `/lit-cache verify` accepts or rejects the addition with rationale.
4. The new domain becomes available for `applicability_contract` declarations.

To add a new axis (rare):

1. Propose the axis name and value vocabulary.
2. Justify why existing axes do not cover the distinction.
3. `/lit-cache verify` accepts; existing entries default to `not_specified` on the new axis until updated.

## Cross-Reference

- `literature-cache-protocol.md` (router)
- `citation-purpose-protocol.md` (purposes and gates that consume axis verdicts)
- `cache-verification-states.md` (verification flow that updates `applicability_contract`)
