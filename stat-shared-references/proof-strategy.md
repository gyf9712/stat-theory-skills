# Proof Strategy Reference

Use this reference whenever `proof-writer` is finding a proof strategy or whenever `proof-repair` is choosing a repair. It encodes the senior-statistician heuristics that the skills' flat menus do not capture by themselves.

Two principles run through the file.

**Choose the battlefield before doing algebra.** Strong PhD students push forward from assumptions and end up in an algebraic thicket. Senior statisticians work backward to the right verification target, decide the norm, localization radius, and good event, and only then do algebra on a deterministic skeleton.

**Use existing machinery; isolate the genuinely new step.** Most of any proof is borrowed scaffolding from a closest published anchor. The novelty lives in one or two specific steps. The skill's job is to identify what is borrowed, name what is new, and prove only the new part with full rigor.

## Contents

- [Claim Families → Verification Targets](#claim-families--verification-targets)
- [Anchor Selection and Comparison](#anchor-selection-and-comparison)
- [Implicit Machinery Disclosure](#implicit-machinery-disclosure)
- [Assumption Budget and Propagation](#assumption-budget-and-propagation)
- [Norm / Mode / Quantifier Checklist](#norm--mode--quantifier-checklist)
- [Localization and Good-Event Bookkeeping](#localization-and-good-event-bookkeeping)
- [Imported Theorem Prerequisite Audit](#imported-theorem-prerequisite-audit)
- [Trap Catalogue with Diagnostic Tests](#trap-catalogue-with-diagnostic-tests)
- [High-Dimensional Regularization Patterns](#high-dimensional-regularization-patterns)
- [Asymptotic Linearity / M-Estimation Patterns](#asymptotic-linearity--m-estimation-patterns)
- [Empirical Process / Concentration / Chaining Patterns](#empirical-process--concentration--chaining-patterns)
- [Lower Bounds and Bayesian Asymptotics](#lower-bounds-and-bayesian-asymptotics)

## Claim Families → Verification Targets

A verification target is the precise intermediate statement or theorem-hypothesis package whose verification would close the claim under a chosen reduction. It is more specific than a strategy name; it tells you what would actually finish the proof.

| Claim family | Verification target (theorem-specific) | Closing argument |
|---|---|---|
| ℓ_2 estimation rate for a sparse high-dimensional regression | Cone condition on the error plus a quadratic basic inequality, then a restricted eigenvalue (RE) or compatibility lower bound | RE closes the rate; Bickel, Ritov, and Tsybakov (AoS 2009) is the canonical anchor |
| Prediction rate for a sparse high-dimensional regression | Basic inequality on the in-sample fitted error; RE not always required | Direct concentration of $\langle X, \varepsilon \rangle / n$ via maximal inequality |
| Asymptotic normality of an M-estimator | Asymptotic linear representation $\sqrt{n}(\hat\theta-\theta_0) = -A^{-1}(1/\sqrt{n})\sum \psi(Z_i, \theta_0) + o_p(1)$ with $A = \mathbb{E}\dot\psi$ | CLT on the score sum plus Slutsky; invertibility of $A$ required |
| Asymptotic normality of a partial sum under dependence | Martingale difference decomposition with Lindeberg condition, or mixing-based covariance summation | Martingale CLT or Lindeberg-Feller |
| Minimax lower bound for a function class | Comparison family $\{f_0, \ldots, f_M\}$ in the class with pairwise loss separation $\delta_n$ and KL overlap satisfying the chosen lower-bound theorem's hypothesis | Fano (entropy-driven), Le Cam (two-point), or Assouad (hypercube), each with its own hypothesis package |
| Concentration of an empirical process | Symmetrization, then Bernstein or Talagrand on the symmetrized process, plus entropy or chaining control of the function class | Maximal inequality with localization radius |
| Posterior contraction at rate $\varepsilon_n$ | Three Ghosal-Ghosh-van der Vaart conditions: sieve with controlled entropy, prior mass on a KL neighborhood, existence of tests separating $d(f, f_0) \gtrsim \varepsilon_n$ from $f_0$ | The theorem closes the proof if all three hold |
| Coverage of a confidence interval | Asymptotic pivotality of the studentized statistic, or consistency of the bootstrap distribution at the right resolution | CLT plus consistent variance estimation; or Edgeworth expansion to higher order |
| Uniform consistency of an estimator over a class | Bracketing entropy or covering number of the loss class is finite under the relevant integrability | Glivenko-Cantelli or uniform LLN |
| Power of a hypothesis test against a contiguous alternative | Local asymptotic normality of the likelihood, then computation of the score-test power | Le Cam third lemma or direct contiguity calculation |

The right pattern when starting a proof is to (i) pick the claim family, (ii) write the verification target as a precise intermediate statement, (iii) name the theorem that closes the proof once the target is verified.

If a proof has two co-equal hard centers (no dominant reduction), declare one primary verification target for the main claim and secondary targets for each genuinely independent hard lemma.

## Anchor Selection and Comparison

Most published proofs in statistics are adaptations. Before writing, identify the anchors.

**Step 1: Classify the proof's relation to the literature.**

- **Template adaptation**: the proof closely follows a published proof structure with one or two specific changes (different assumption, different setting, weakened condition). Identify 1-3 closest anchors.
- **Standard-result invocation**: the proof reduces to applying a named theorem after verifying its prerequisites. Identify the theorem, the prerequisites, and the verification.
- **Self-contained**: no prior paper is imported wholesale, and the proof relies only on graduate-core facts. *This must be defended explicitly* — see Implicit Machinery Disclosure below.

**Step 2: For each anchor, extract:**

- The anchor's verification target
- The anchor's proof spine (3-5 main steps)
- What the new proof borrows from the spine (often most of it)
- What is genuinely new (the one or two steps where the assumption change or extension lives)

**Step 3: Write the result in the proof package.** A typical anchor block:

```
## Anchors and Borrowing

- Anchor 1: Bickel, Ritov, and Tsybakov (AoS 2009), Theorem 7.2.
  Verification target: cone condition + quadratic basic inequality + RE.
  Borrowed: cone derivation, basic inequality structure, rate closure.
  New: the basic inequality is derived under finite fourth-moment noise
  rather than sub-Gaussian; the concentration step uses a Bernstein-type
  bound with polynomial tails (Lemma 2 below).

- Anchor 2: van de Geer (AoS 2008), Corollary 9.2.
  Borrowed: nothing structural; cited for the maximal-inequality form.
```

A proof claiming to be self-contained without this disclosure is suspect. Most self-contained proofs are using machinery the author has internalized and stopped citing.

## Implicit Machinery Disclosure

A senior statistician who claims a proof is self-contained must defend the claim. The skill enforces this with an explicit disclosure block.

**Two flavors:**

- **Paper-self-contained**: no external theorem is used beyond explicitly enumerated graduate-core facts (e.g., the CLT, Markov, Cauchy-Schwarz, dominated convergence, Slutsky, the Borel-Cantelli lemmas, basic results in van der Vaart and Wellner that are stated in standard textbooks).
- **Locally self-contained**: no prior paper is imported wholesale, but the proof relies on undeclared mature machinery (e.g., the bracketing entropy is invoked without citing the theorem; the Talagrand inequality is used as a one-liner; the contraction principle is applied without statement).

Most alleged self-contained proofs are the second kind. The skill requires the author to disclose which:

```
## Implicit Machinery (if proof labeled self-contained)

- Mature machinery used implicitly: [list]
- Background needed by a strong PhD student to verify the proof unaided: [list]
- Pieces re-proved here rather than imported: [list]
```

If the author cannot fill these honestly, the proof is not self-contained and an anchor walk is required.

## Assumption Budget and Propagation

Every proof spends its assumptions like a budget. Track which step consumes which.

- **List assumptions explicitly at the top** of the proof package, labeled (A1), (A2), etc.
- **For each nontrivial step**, name which assumptions it uses.
- **Watch for silent strengthening**: a step that quietly assumes more than (A1)-(An) is a hidden assumption and must be declared.
- **Watch for headline-claim degradation**: if relaxing an assumption forces the rate or claim to weaken, the headline statement must reflect the weaker claim, not the stronger one the original sketch had.

Common silent strengthenings to flag:

- Using boundedness when only finite moments are assumed
- Using sub-Gaussian when only sub-exponential is assumed
- Using independence when only weak dependence (mixing) is assumed
- Using strict positivity when only non-negativity is assumed
- Using differentiability at a boundary point where the model is singular

## Norm / Mode / Quantifier Checklist

A proof that controls the wrong object proves nothing. Before any algebra:

| Underline in the claim | Common confusion |
|---|---|
| The norm of the conclusion | $\ell_2$ vs $\ell_\infty$ vs prediction norm vs Mahalanobis |
| The convergence mode | $\to_p$ vs $\to_d$ vs $\to_{a.s.}$ vs $L^p$ convergence vs uniform |
| The quantifier | Pointwise vs uniform over a class; existence vs simultaneously |
| The probability model | Fixed design vs random design; iid vs dependent |
| The parameter regime | Asymptotic ($n \to \infty$) vs nonasymptotic (finite $n, p$ with explicit constants) |

After underlining, check that the last bound before the conclusion controls the same norm and mode. Any silent switch is a trap.

## Localization and Good-Event Bookkeeping

Two pieces of disciplined bookkeeping that proofs frequently get wrong.

**Localization before expansion.** Many proofs Taylor-expand or linearize the estimating equation around $\theta_0$. This step is valid only when $\hat\theta$ is already in a neighborhood of $\theta_0$. The proof must contain an explicit localization step: "On an event of probability at least $1 - \delta$, $\|\hat\theta - \theta_0\| \leq r_n$ for some $r_n \to 0$." This step is *prior to* the Taylor expansion, not derived from it.

**Good-event accounting.** Many proofs condition on a high-probability event $E_n$ (e.g., RE condition holds; supremum of empirical process is below a threshold; design matrix is well-conditioned). The proof must explicitly track the probability of the complement:

- Define $E_n$ precisely
- Bound $\mathbb{P}(E_n^c) \leq \delta_n$ explicitly with a concentration argument
- Carry the $\delta_n$ through to the final probability statement

Forgetting to pay the complement probability is one of the most common errors in published statistics proofs. A proof that says "with high probability" without ever bounding the complement is a flag.

## Imported Theorem Prerequisite Audit

Every "by Theorem X of [author]" needs an audit. For each imported result, the proof must show that its prerequisites are satisfied in the current setting.

Prerequisite audit checklist for an imported theorem:

| Prerequisite type | What to check |
|---|---|
| Probability mode | iid, mixing strength, exchangeability, stationarity |
| Tail / moment assumption | sub-Gaussian, sub-exponential, finite moment of order $q$, bounded |
| Envelope | a function dominating the class, with the required integrability |
| Measurability | the class is suitably measurable (often automatic; sometimes not for uncountable suprema) |
| Smoothness / regularity | continuity, differentiability, Lipschitz, Sobolev or Hölder smoothness |
| Identifiability | uniqueness of the population parameter |
| Invertibility | Hessian or design matrix is invertible (and the inverse is bounded if needed) |
| Boundary | the parameter is in the interior of the parameter space, not on the boundary |
| Donsker / Glivenko-Cantelli | the class satisfies the relevant entropy bound |

A frequent failure mode: a proof transplants a result across different dependence / design / smoothness regimes without auditing the prerequisites. The transplanted theorem may not apply, and the proof silently breaks.

### Citation Identity vs Applicability

Citation precision in statistics theory is two-layered, and both layers fail independently.

**Layer 1: Citation identity / version consistency.** Did the proof identify the right source, version, theorem number, and exact clause? LLMs habitually misattribute theorems, swap theorem numbers between papers, confidently state "Theorem X.Y says Z" when it actually says Z' (close but different), or confuse versions across arXiv preprints, journal papers, and errata.

**Layer 2: Imported-result applicability.** Given that the identity is correct, do the source assumptions actually hold in the current setting, and is the source conclusion exactly what the local proof step needs?

Both layers must be passed. A proof that confidently verifies prerequisites of the wrong theorem is wrong; a proof that identifies the right theorem but uses it under different conditions is also wrong. The trap catalogue items #6 (citation identity / version drift) and #7 (imported-result applicability drift) target these layers separately.

### Scope: which citations need a statement-level audit

A statement-level audit is required for **proof-dispositive imported results**: results invoked as black-box steps that discharge a specific point of the proof. Not every citation. Four classes:

| Class | Audit requirement |
|---|---|
| Background / positioning citation | No audit; the citation does not feed into the proof |
| Anchor / template citation | No audit unless a specific result is imported as a black box |
| Named theorem schema used without specific paper citation (e.g., "by symmetrization", "by Slutsky") | Applicability audit (theorem-schema level); no bibliographic theorem-number audit |
| Specific external result with theorem / lemma / proposition / corollary / equation number used to discharge a proof step | Full statement-level audit (both layers) |

Primitive inequalities and analysis tools (Markov, Cauchy-Schwarz, Hölder, Minkowski, Jensen, Fubini, Tonelli, dominated convergence, Fatou, Taylor, conditional-expectation identities, eigenvalue inequalities, Woodbury) are pattern-level checks. They are not whitelist citations; they require verification that the pattern is applied to the right object, but not a bibliographic audit.

### Graduate-core citation-exempt schemas (closed, narrow list)

Treat the following as citation-exempt named schemas only when invoked in their canonical basic forms and with local applicability verified:

- Borel-Cantelli I and II (II only with independence checked locally)
- Weak law of large numbers and classical CLT for iid finite-dimensional observations under their standard finite-moment assumptions
- Continuous mapping theorem
- Slutsky's theorem
- Portmanteau in its basic bounded-continuous / closed-set forms
- The basic finite-dimensional delta method
- Glivenko-Cantelli for the empirical CDF of iid real-valued data
- Hoeffding and Bernstein for independent scalar sums in their standard basic forms
- Doob's $L^p$ inequality in its basic submartingale form

Everything outside this list requires statement-level audit if imported:

- Skorohod representation
- LLN / CLT under dependence or triangular arrays
- Functional or semiparametric delta methods
- Generic Glivenko-Cantelli / Donsker / VC / bracketing-entropy results
- Talagrand / chaining / maximal inequalities
- Fano / Le Cam / Assouad with constants
- argmax or Z-estimator consistency theorems beyond the basic finite-dimensional case
- Asymptotic linearity with nuisance
- Bernstein-von Mises
- Any author / title / theorem-number citation

The whitelist is intentionally narrow. If a result feels routine but is not on this list, it still needs the audit.

### Access states for cited sources

Each proof-dispositive imported result has a direct-inspection status. Four levels, only the first two pass for proof-dispositive use:

- `checked-now-source-of-record`: the source-of-record (journal version, latest preprint, book edition) was directly inspected during this proof. **Passes.**
- `checked-now-alternate-source`: an equivalent statement in an alternate source (different paper, different edition) was directly inspected; the version / numbering crosswalk is filled in. **Passes** with the crosswalk recorded.
- `previously-checked-no-current-access`: the author read the source previously but does not currently have access. **Admissible only as an open risk for P1 or P2 items.** For a P0 proof-dispositive item, this status blocks `PROVABLE AS STATED`; the step must be reproved locally or the source must be retrieved (via `/proof-repair`).
- `never-checked`: the citation was added without direct inspection. **Inadmissible.** Obtain, replace, or prove locally.

For paywalled papers the author has not read: not admissible as a proof-dispositive citation. For "standard textbook results" not on the graduate-core whitelist: if cited with a specific theorem number, the number must be verified. Do not cite theorem numbers from memory. For unpublished or personal communication: not acceptable as a black-box proof step in an archival theory paper; restate and prove locally.

## Trap Catalogue with Diagnostic Tests

Seven common middle-regime traps. Each has a one-line diagnostic test the polisher can apply mechanically.

**1. Localization-before-expansion trap.** A Taylor expansion or linearization is used before localization is proved.

> Diagnostic: find the first Taylor expansion or linearization step; before it, look for an explicit high-probability statement like $\|\hat\theta - \theta_0\| \leq r_n$ or $\hat\theta \in \mathcal{N}(\theta_0)$. If absent, flag.

**2. Wrong norm / wrong mode trap.** The proof controls one norm or convergence mode, but the claim needs another.

> Diagnostic: underline the norm and convergence mode in the claim, then check that the last bound before the conclusion uses the same norm and mode. Any silent switch is a flag.

**3. Good-event bookkeeping trap.** The argument is correct on a high-probability event, but the complement probability is never paid for.

> Diagnostic: every "on the event $E_n$" or "with high probability" must be paired with a bound on $\mathbb{P}(E_n^c)$. If an event appears and its complement is never bounded, flag.

**4. Rate leakage trap.** An extra $\log n$, entropy term, nuisance-rate term, or conditioning constant silently worsens the final rate.

> Diagnostic: list every rate factor introduced in displayed bounds. If the final rate drops a factor like $\log n$, $s$, entropy, or nuisance-rate terms without an explicit cancellation step, flag.

**5. Quantifier inflation trap.** A pointwise argument is sold as uniform, or an existence statement is sold as simultaneous.

> Diagnostic: search for "uniformly", "for all", "sup", or "simultaneously". If the cited or input result is pointwise and no upgrade argument is shown, flag.

**6. Citation identity / version drift.** A theorem is cited, but the proof never pins down exactly which source, version, numbering, or clause is being used.

> Diagnostic: search for `by Theorem`, `by Lemma`, `by Proposition`, `by Corollary`, or `by Eq.` together with an author name, citation key, or bibliographic label. Each proof-dispositive citation must have a matching row in `## Cited Results Audit` with: (i) full source identity, (ii) theorem/lemma/equation number as cited in the proof, (iii) source-of-record, (iv) direct-inspection status, (v) page or equation pointer, and (vi) version / errata note. If a citation has no matching row, or the row omits any of these fields, flag. If the inspection status is `checked-now-alternate-source`, the version / numbering crosswalk field must be filled; otherwise flag.

**7. Imported-result applicability drift.** The cited result is identified, but its hypotheses or conclusion do not actually match the local use.

> Diagnostic: for each row in `## Cited Results Audit`, write down every source assumption and check that each is mapped to a local item `(A_k)`, a previously proved lemma, or a verified prerequisite. Then check that the local proof step closed by the citation is named explicitly, and that the `Conclusion fit` field is one of: `exact`, `stronger than needed`, or `weaker than needed with explicit bridge`. Any unmapped assumption, missing local step, `weaker than needed` without a bridge, `ambiguous-mismatch`, or proof-dispositive row with direct-inspection status `previously-checked-no-current-access` or `never-checked` is a flag.

**8. Boundary / singularity trap.** The proof uses inverses, divisions, argmax differentiability, support recovery, or Hessian inversion at a point where the model is singular or on the boundary.

> Diagnostic: search for inverses, divisions, argmax differentiability, support recovery, or Hessian inversion. If the proof never explicitly excludes zero denominators, singular matrices, boundary parameters, or ties, flag.

## High-Dimensional Regularization Patterns

For LASSO, Dantzig selector, group LASSO, and related ℓ_1-regularized estimators, the proof spine is canonical:

1. KKT conditions or basic inequality from the optimization
2. Cone condition on the error: $\|\Delta_{S^c}\|_1 \leq c \|\Delta_S\|_1$
3. Restricted eigenvalue (RE) or compatibility condition on the design
4. Sparsity support splitting and rate closure
5. Concentration of the noise inner product $\langle X^\top \varepsilon \rangle / n$

Typical failure points:

- The cone derivation breaks under non-standard loss functions
- RE is asserted without proof for the specific design (e.g., correlated or heavy-tailed)
- The basic inequality uses sub-Gaussian when the problem is heavy-tailed
- The tuning parameter $\lambda$ is chosen at a rate that does not match the noise concentration

Canonical anchor: Bickel, Ritov, and Tsybakov, "Simultaneous analysis of Lasso and Dantzig selector," *Annals of Statistics* 37 (2009): 1705-1732.

## Asymptotic Linearity / M-Estimation Patterns

For M-estimators, the proof spine is:

1. Consistency of $\hat\theta$ (separation argument or compactness)
2. Localization: $\|\hat\theta - \theta_0\| \leq r_n$ on a high-probability event
3. Linearization of the estimating equation $\Psi_n(\hat\theta) = 0$
4. Remainder control: the higher-order Taylor terms are $o_p(n^{-1/2})$
5. Invertibility of $A = \mathbb{E}\dot\psi(Z_i, \theta_0)$
6. CLT applied to the score sum $(1/\sqrt{n})\sum \psi(Z_i, \theta_0)$
7. Slutsky to assemble the asymptotic normality conclusion

Typical failure points:

- Skipping step 1 or 2 and going straight to step 3 (localization-before-expansion trap)
- Remainder control is hand-waved; the actual bound on $\sup_{\theta \in \mathcal{N}(\theta_0)} \|\dot\Psi_n(\theta) - \dot\Psi_n(\theta_0)\|$ is not given
- Invertibility of $A$ is assumed but not verified
- Influence function form is correct but variance estimation is left implicit (consistency of the sandwich estimator)

For semiparametric M-estimators with nuisance, see van der Vaart and Wellner (1996) for the empirical-process framework, plus orthogonality / double robustness considerations.

## Empirical Process / Concentration / Chaining Patterns

For uniform laws of large numbers, supremum bounds, and rate-of-convergence proofs that pass through an empirical process, the spine is:

1. Symmetrization to a Rademacher process (or Gaussian process via comparison)
2. Concentration on the symmetrized process: Bernstein, Talagrand, or Hoeffding depending on the tail assumption
3. Entropy or chaining control of the function class
4. Localization to a shrinking neighborhood (for rate-of-convergence proofs)
5. Peeling or layered cake argument across scales

Typical failure points:

- Symmetrization is applied to a non-iid or biased process
- Talagrand is invoked but the envelope condition is not verified
- The entropy integral diverges because the class is too rich
- Localization radius is not balanced against the entropy

Canonical references: van der Vaart and Wellner, *Weak Convergence and Empirical Processes* (1996); Talagrand, *The Generic Chaining* (2005).

## Lower Bounds and Bayesian Asymptotics

For minimax lower bounds:

1. Choose the lower-bound theorem (Fano, Le Cam, Assouad)
2. Construct a finite comparison family in the function class
3. Verify the separation condition (pairwise loss $\geq \delta_n$)
4. Verify the information condition (KL or chi-square overlap small enough)
5. Apply the chosen theorem to extract the lower bound

Common failure points:

- The comparison family is not actually in the function class (e.g., violates the smoothness or sparsity constraint)
- The separation is at the wrong scale
- The information condition is hand-waved
- The theorem's exact hypothesis is not matched (Fano's information ≤ $n\beta + \log 2$, Assouad's edge separation, Le Cam's two-point Hellinger condition)

For posterior contraction (Bayesian asymptotics):

1. Define the sieve $\mathcal{F}_n$ with controlled entropy
2. Lower bound the prior mass in a KL neighborhood of $f_0$
3. Construct tests separating $d(f, f_0) \gtrsim \varepsilon_n$ from $f_0$, with exponentially small Type I and Type II errors
4. Verify the Ghosal-Ghosh-van der Vaart (or Shen-Wasserman) contraction theorem's hypothesis with these three pieces

Common failure points:

- The sieve's entropy bound is not actually computed
- Prior mass on the KL neighborhood is asserted but not derived
- Tests are claimed to exist but not constructed
- The contraction theorem's exact hypothesis is not matched

For Bernstein-von Mises (BvM), the contraction rate must reach parametric ($\varepsilon_n = n^{-1/2}$) and the prior must be sufficiently smooth at $\theta_0$. BvM frequently fails in nonregular models (boundary, change-point, support recovery); a proof claiming BvM in such a setting needs extra scrutiny.

## How proof-writer and proof-repair use this file

`proof-writer` consults this reference in Step 3.5 (Verification Target and Bottleneck) and Step 4 (Dependency Map). The senior-statistician move is to consult Claim Families → Verification Targets first, then Anchor Selection and Comparison, then the relevant pattern section, then the Trap Catalogue at the end of writing.

`proof-repair` consults this reference when proposing repairs. The Anchor Selection and Imported Theorem Prerequisite Audit sections feed directly into the literature support discipline. The Trap Catalogue feeds into the closure verification at re-audit.
