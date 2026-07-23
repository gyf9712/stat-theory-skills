# Assumption Load-Bearing Audit

Source of truth for one adversarial question the family did not previously ask of a
**submitted** manuscript: *does a load-bearing assumption pre-satisfy the theorem's
verification target, or pre-empt the paper's stated central difficulty?* This is the
classic AE kill-line — "Assumption 3 essentially assumes what Theorem 1 claims," "the
interesting regime is assumed away" — that literal circularity detection alone does not
catch.

Consumed by `proofcheck` (Pass 4, as a proof-severity audit) and by `stat-mock-review`
(Step 3, as a contribution/positioning verdict). The two skills apply the **same tests**
but map them to different consequence scales: `proofcheck` emits `S0`–`S3`;
`stat-mock-review` emits fatal / major / minor editorial consequence. Separate the two —
a correct theorem that assumes away its own selling point is not a proof-theoretic `S0`,
but it can be an AE-fatal concern.

## Framing (read this first)

Do not audit an abstract "distance to the conclusion." That invites pseudo-metrics and
false positives; Big Four referees do not object that an assumption is *close* to a
theorem. They object that the paper **sold** heavy tails, weak identification,
misspecification, high dimension, adaptivity, or nonconvexity, and then **assumed away
exactly that**. The audit is anchored to the paper's own claimed contribution, not to a
metric. So the required inputs are:

- the introduction's **claimed central difficulty** and contribution list (what the paper
  says is hard / new);
- the theorem inventory and assumption ledger (Task 2A of `proofcheck`);
- the dependency graph (which assumption feeds which result, and where it is *consumed*
  in the proof).

Without the claimed-difficulty input this audit cannot run; it is not a local proof check.

## Scope: which assumptions

Run the tests only on **load-bearing** assumptions — those a main theorem's critical
chain actually consumes. Do not run them on every regularity condition. An unused or
purely technical smoothness assumption is a different finding (`unused assumption`,
handled by the existing Pass 4 "Stress assumptions" bullet), not a trivialization.

## The four tests

For each load-bearing assumption A and the main conclusion C it feeds:

### T1 — Conclusion Restatement
Does A literally restate C, imply C by equivalence, or reference the claimed
theorem/conclusion? This is genuine circularity / "assume the conclusion."
- **proofcheck: `S0`.** Merges with the existing circularity gate; route to `proof-repair`.

### T2 — Verification Target Assumed
Does A assume the exact intermediate object the proof is supposed to *establish*?
Canonical cases: assume asymptotic linearity to prove asymptotic normality; assume
stochastic equicontinuity / a Donsker condition to prove a uniform CLT; assume the oracle
support to prove support recovery; assume a global minimizer is attained when finding it
is the hard step.
- **proofcheck: `S1`.** Downgrade only if the paper explicitly labels the result a
  *conditional* corollary and proves or checks the target elsewhere (then it is at most
  `S2`, or no finding).

### T3 — Central Difficulty Pre-emption
Does A exclude the hard regime the abstract/introduction/contribution list claims to
handle? (Selling heavy-tail robustness but assuming sub-Gaussian; selling weak
identification but assuming eigenvalues bounded away from zero; selling misspecification
robustness but assuming correct specification.)
- **proofcheck: `S1`, capped.** Never `S0` *here* — this is a contribution judgment, not a
  proof break. It escalates to `S0` only if it becomes a proof/statement defect: the
  assumptions are inconsistent or vacuous (T5-style), OR the theorem **statement** claims a
  broader regime than its assumptions permit (a scope mismatch — this is the existing
  `OVERSTATED` status; wire it there, do not invent a new severity), OR a downstream result
  silently uses the broader claim.
- **stat-mock-review:** fatal or major, by centrality to the sold contribution.

### T4 — Comparative Axis Reversal
Does the paper claim to relax or generalize prior work on an axis where its assumptions are
actually *stronger* or *narrower*? Reuse the vocabulary in `stat-positioning-and-claims.md`
and `applicability-axes.md`; this is where the audit meets the claim-support map.
- **proofcheck: `S1` if the reversal is on a headline axis; `S2` if local.**

## Severity discipline (avoid reviewer-annoying noise)

- Proof severity (`S0`–`S3`) and AE consequence are **different scales**. Do not report a
  positioning problem as a fabricated `S0`.
- T3 caps at `S1` in `proofcheck` unless it converts to a genuine statement/consistency
  defect per the escalation rule above.
- The absence of a finding is a valid, expected result. Most well-constructed conditional
  theorems (Lasso under a restricted-eigenvalue condition; M-estimator CLT after isolating
  asymptotic linearity; argmax consistency under a separation condition; fast rates under a
  margin condition) are **not** trivializations. Proof *length* is not evidence — a short
  closing proof from a legitimately isolated condition is good mathematics. The defect is
  only present when the paper **claims to solve** the condition it merely assumes.

## Known failure sub-modes (catalogue)

Reviewer-cited instances of "assumption assumes away the contribution." Use as a checklist;
a hit here is a candidate, not an automatic finding — confirm against the four tests.

- **Vacuous / inconsistent assumption class** — assumptions are mutually inconsistent or
  leave only degenerate examples (this one *can* be `S0`).
- **Identifiability assumed** while identification is the claimed contribution.
- **Separation directly assumed** — beta-min, eigengap, margin, irrepresentable /
  incoherence, RE / RIP, or strong-overlap conditions that impose the very separation the
  theorem claims to handle.
- **Oracle assumptions** — known support, known sparsity / smoothness, oracle tuning, known
  nuisance-parameter rates, known global optimizer.
- **Realizability assumed** — well-specification / realizability assumed while selling
  robustness to misspecification.
- **Empirical-process result assumed** — Donsker / entropy / stochastic-equicontinuity
  conditions that are exactly the empirical-process statement the paper claims to prove.
- **Curvature assumed** — global convexity / strong curvature assumed while selling nonconvex
  or weak-curvature theory.
- **Algorithmic attainability assumed** — "let the estimator be a global minimizer" when
  computing it is the hard part.

## Original Assumption Challenge Ledger

Produced only for assumptions that a test flags — not for every assumption (that would
generate "why not weaken everything?" noise). This is the submission-side analogue of the
repair-side Assumption-Extension Change Log in `proof-closure-machinery.md`; keep them
separate — that log is mandatory because a repair *introduced* an assumption, this ledger
challenges an *original* one.

```markdown
## Original Assumption Challenge Ledger

| Assumption | Feeds result | Test hit | Claimed central difficulty affected | Verification target pre-satisfied? | Natural weaker variant | Where current proof needs current form | Scientific-scope impact | Recommended first owner |
|---|---|---|---|---|---|---|---|---|
```

The "Natural weaker variant" + "Where current proof needs current form" pair is the defense:
if an obvious weakening was tried and a concrete step genuinely fails under it, the strong
form is justified and the finding downgrades or clears. If no weaker variant was considered,
the assumption is treated as unjustified over-strengthening.

## Routing (by repair type, not blanket)

Do not send every finding to `theory-sharpen`. Route by what the fix actually is:

| Finding shape | First owner | Why |
|---|---|---|
| Literal circularity / conclusion restatement (T1) | `proof-repair` | It is a proof defect, not a strengthening |
| Mathematically relaxable over-strong assumption (T2/T3/T4, relaxation is the path) | `theory-sharpen` | Relaxation-pathway analysis |
| Correct theorem, oversold contribution | `stat-polishing` / claim-support audit | Soften the verb or restrict scope, not the math |
| Central result becomes uninteresting under its assumptions | `stat-mock-review` | Marks fatal/major, then the rescue plan chooses relax vs reposition |
