---
artifact: shared_reference
scope: equivalence_ledger_protocol
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills equivalence-ledger protocol for the stat-polishing formal-statement-pass mode, Codex threadId 019e7bc0-56ef-7710-8424-e61b6d58399b
---

# Equivalence Ledger Protocol

Governs the `--formal-statement-pass` mode of `stat-polishing` (in the sibling `stat-writing-skills` repo). That mode rewrites the mathematical FORM of assumptions, definitions, theorem/lemma statements, and displayed conditions into a more formal, more conventional, equivalence-preserving form aligned with the target venue's published register.

The danger this protocol exists to contain: **"rewrite into an equivalent more formal form" is exactly the operation that silently changes meaning.** "Well-conditioned design" → "$\lambda_{\min}(\Sigma) \ge c > 0$" silently adds a uniform lower bound. "Sub-Gaussian errors" → "$\mathbb{E} e^{\lambda\epsilon} \le e^{\lambda^2\sigma^2/2}$" pins a constant that may not be intended. This is the same failure mode as proof-repair's semantic edits, and it gets the same grade of guardrail.

This protocol lives in `stat-theory-skills/stat-shared-references/` because it shares the silent-semantic-change ontology defined here (the axis vocabulary in `applicability-axes.md`, the change-log discipline in `proof-closure-machinery.md`, the diff-ledger dimensions in `proofcheck --post-repair`). `stat-polishing` references it cross-repo, exactly as it already references `literature-cache-protocol.md`.

## When to Read

- Before running `stat-polishing --formal-statement-pass`.
- When `/proofcheck` or `/proofcheck --post-repair` encounters an equivalence ledger and must decide whether a formalized statement needs a dependency check.
- When the author reviews a formal-pass proposal at the per-atomic-claim gate.

## The Standing Refusal Condition

The mode's identity is **as much a refusal engine as a formalization engine**. The governing rule, co-equal with the silent-semantic-change ban:

> Never formalize to increase apparent depth. Apparent depth is only ever a side effect of a genuine precision-or-register gain. The moment a rewrite raises the reading barrier without (a) resolving a referee-checkable ambiguity, (b) matching the target venue's register, or (c) removing notation clutter, refuse it.

Prose-side analog (already in `stat-style-discipline.md`): "mathematical precision over adjectival praise." Math-form analog: **"precision over notational sophistication."**

## Two Kinds of "More Formal"

| | Precision-increasing formalism (apply) | Decoration formalism / theoretical theater (refuse or flag) |
|---|---|---|
| Example | "p large" → "$\log p / n \to 0$ as $n \to \infty$" | measure-theoretic dress on an elementary argument; operator notation for a scalar; empirical-process language for an i.i.d. sum |
| Reading barrier | up a little | up |
| Verifiable information | up more | flat |
| Net | positive | negative |
| Why it looks deeper | because it is genuinely more precise; depth is a side effect | because the notation is heavy; depth is an illusion |

The discriminator (sharpened by Codex; the loose "increases what's verifiable" version is too easy for an LLM to rationalize):

> **The formalized version must answer at least one referee-checkable question the original could not answer unambiguously:** with respect to what limit? uniform over which class? in which norm? with what probability mode? under what conditioning? If no new ambiguity is resolved AND the rewrite does not remove notation clutter, the rewrite is decoration and is refused.

The ambiguity axes (limit / uniformity / norm / probability mode / conditioning) are the same load-bearing dimensions used by `applicability-axes.md` and the `--post-repair` diff ledger. The system carries one ontology of silent semantic change.

## Statement-Formalism vs Notation-Formalism

Both layers have a legitimate and a dangerous mode; the asymmetry is in where the danger concentrates, and both are policed by the same use-test + equivalence-ledger machinery below.

- **Notation formalism** (introducing operators, function spaces, measure-theoretic objects, processes) is legitimate only when the object **already lives in that structure and is used downstream**: stochastic-process convergence, operator norms, function classes, empirical measures, RKHS objects, semiparametric tangent spaces. Otherwise it is decoration. Policed by the **use-test**.
- **Statement formalism** (quantifier order, regime, probability mode, environment packaging) is usually precision-positive, but overclaims badly when it adds a quantifier / regime / bound not in the original: adding "uniformly over $\Theta$"; converting "with high probability" into "$1 - o(1)$" without specifying the regime; replacing heuristic regularity with bounded eigenvalues. Policed by the **equivalence ledger**.

## Anti-Theater: Two Concrete Checks

These are executable, not slogans.

### Use-test

Every symbol, space, operator, topology, or process introduced by a formalization must be used in a theorem, proof, rate statement, or assumption cross-reference. (Literally grep-able: search the manuscript for later uses of the introduced symbol.) If a symbol is introduced only to restate an elementary scalar or vector condition and is never used again, withdraw the formalization.

### Simpler-equivalent challenge

If a simpler conventional statement is equally falsifiable, choose the simpler one. The mode must record, for each formalization it keeps, why a simpler equivalent does not suffice (typically: the simpler form is ambiguous on one of the five ambiguity axes, or the venue's register expects the heavier form).

## The Two-Tier Gate

Formal-pass rewrites split by whether they are semantic (meaning-bearing) or cosmetic (presentation only).

### Cosmetic / packaging rewrites → existing cluster gate

Formatting, labeling, ordering, environment cleanup (e.g., wrapping loose conditions into a numbered `Assumption` environment), bullet-vs-prose presentation, symbol-typeface normalization that does not change meaning. These go through `stat-polishing`'s existing `REVISION_PLAN.md` cluster-approval gate (5-25 changes per cluster, one accept/reject).

### Semantic rewrites → per-atomic-claim gate

Any rewrite that touches one of the **semantic-trigger axes**:

- quantifier (order, scope, pointwise vs uniform)
- probability mode (in probability / a.s. / $L^p$ / with-high-probability / uniform-over-class)
- uniformity (uniform over a class vs pointwise)
- constants (pinning, sign, dependence on dimension / sample size)
- asymptotic regime (the limit being taken)
- conditioning set
- norm or topology
- dependence structure
- parameter space

These get a **per-atomic-claim gate**: one atomic claim, one approval item, with an equivalence-ledger row attached. **Never clustered.** A six-part assumption inside one environment contains up to six independent semantic risks and produces up to six approval items. A single silently-strengthened assumption can sink the paper, so each is approved on its own.

## The Equivalence Ledger

One artifact per project: `papers/<project>/EQUIVALENCE_LEDGER.md`. One row per semantic rewrite. The columns reuse the system's axis ontology so silent semantic change is checked on the identical axis set used by proof-repair's change logs and `--post-repair`'s diff ledger.

```markdown
---
artifact: equivalence_ledger
project: <project-name>
generated: <YYYY-MM-DD>
generator: stat-polishing v1.x.x formal-statement-pass
---

# Equivalence Ledger

| Row | Original text (verbatim) | Proposed text (verbatim) | Touched axis | Equivalence justification | Possible silent strengthening / weakening | Downstream consumers | Approval status | Proofcheck status |
|---|---|---|---|---|---|---|---|---|
| E-01 | "the design is well-conditioned" | "$\lambda_{\min}(\Sigma) \ge c > 0$ for a fixed constant $c$" | conditioning / constants / uniformity | claims the author intended a uniform lower bound on the smallest eigenvalue, confirmed against Section 3 usage | STRENGTHENING risk: a uniform $c$ is stronger than mere invertibility; if the author only needs invertibility per $n$, this overclaims | Lemma 3.2, Theorem 2.1 | PENDING | required (Lemma 3.2 on main chain) |
| E-02 | "errors have finite variance" | "$\mathbb{E}\|\epsilon\|^2 < \infty$" | none beyond notation | direct notational restatement; no axis touched | none | none | APPROVED | not required (notation only) |
```

Column semantics:

- **Touched axis**: one or more of the semantic-trigger axes above, drawn from the same vocabulary as `applicability-axes.md`. If "none beyond notation", the rewrite is borderline cosmetic and may not need the per-atomic gate (author's call).
- **Equivalence justification**: why the proposed form is equivalent to the original (or, if not strictly equivalent, what the author actually intended, confirmed against downstream usage).
- **Possible silent strengthening / weakening**: the honest statement of what could have changed. This is the load-bearing column. "none" is allowed only when the rewrite is genuinely notation-only.
- **Downstream consumers**: every unit (lemma, theorem, corollary, proof step, abstract sentence) that consumes the rewritten property. Populated from the dependency graph if `/proofcheck` has run, else by manual trace.
- **Approval status**: PENDING / APPROVED / REJECTED (per-atomic-claim gate decision).
- **Proofcheck status**: see the depth split below.

## Proofcheck Depth Split

Not every semantic rewrite needs a full re-audit. The default:

- **Semantic rewrite NOT on the main dependency chain** → **targeted dependency check** only. Does any downstream unit consume the changed property? If yes, propagate the change (or flag the consumer). No full re-audit.
- **Semantic rewrite ON the dependency path to a headline theorem, rate theorem, main lemma, or proposition used in the main proof chain** → **full `/proofcheck --post-repair` on the affected sub-DAG**. A silently-changed assumption to a load-bearing lemma is the catastrophic case.
- **Dependency status unclear** → treat as load-bearing (require the heavier check). Conservative default.

Requiring full `/proofcheck` for ALL semantic rewrites is overkill and would incentivize either no useful formalization or under-reporting of semantic edits. The split keeps the heavy machinery where the catastrophic risk is.

The `Proofcheck status` column records: `not required (notation only)` / `targeted dependency check passed` / `required (on main chain) — /proofcheck --post-repair PENDING|CONVERGED|NOT CONVERGED`.

## Venue-Calibrated Formalism Level

No thresholds. Same formalization is a different verdict by venue. The mode asks two exemplar questions for each candidate formalization:

1. "Would this object look normal in two recent accepted or thematically similar papers from the target venue?"
2. "Does the formalism reduce or increase the burden for the venue's modal reader?"

Venue register guidance (reuse `stat-venue-checklists.md` and the "read 2-3 recent venue papers" calibration already in `stat-polishing`'s workflow):

| Venue | Formalism register |
|---|---|
| AoS / Bernoulli / EJS | High formalism tolerated and expected. Measure-theoretic and empirical-process language is native — when the object is actually used downstream. |
| JRSS-B | Middle. Formal where precision demands; not gratuitously heavy. |
| Biometrika | Concise and readable house style. Excess formalism is penalized. Prefer compact assumptions with a verbal interpretation. |
| JASA T&M | Compact assumptions with verbal interpretation; formalism that aids precision, not display. |
| JASA ACS / AOAS | Application-facing. Formalism that hurts readability for the applied audience is wrong. |
| Biostatistics / JCGS | Readable; class-driven; formalism subordinate to the applied narrative. |

Target the venue's actual register, never max formalism.

## Cross-Reference Drift Audit

The first-30-day failure mode (Codex Q7): rewriting a labeled object silently breaks later references. "the boundedness condition", "the compatibility condition", "Assumption 3(ii)" used in prose and proofs may no longer match after a rewrite.

After any rewrite to a labeled object, audit every downstream reference to it. Reuse `stat-notation-audit.md`. A rewrite that changes an assumption's name, number, or verbal handle requires updating every prose and proof reference; unupdated references are flagged as defects (analogous to the Mode B cross-file reference rule in proof-repair).

## Self-Check via the Economy Audit

The formal-pass mode runs `stat-polishing`'s Step 6 Mathematical Expression Economy flags on its own output: object-before-symbol, dormant-symbol-introduction, local-notation-load, display-purpose-clarity, theorem-packaging, interpretive-handoff. Any formalization that trips an economy flag without a precision gain is withdrawn. The economy audit and the formal pass are complementary guardrails: one proposes formalization, the other blocks overload.

## Workflow Summary

1. Identify candidate objects (assumptions, definitions, theorem/lemma statements, displayed conditions) in the body.
2. For each candidate, draft the formalized form.
3. Classify the rewrite: cosmetic or semantic (semantic-trigger axes).
4. Run the discriminator (resolves a referee-checkable ambiguity?) and the use-test (every introduced symbol used downstream?) and the simpler-equivalent challenge. Withdraw decoration.
5. Run the venue-register exemplar check. Withdraw register-mismatched formalism.
6. Cosmetic rewrites → cluster gate. Semantic rewrites → per-atomic-claim gate with an EQUIVALENCE_LEDGER.md row.
7. For each semantic rewrite, fill the ledger row including the honest silent-change column and the downstream consumers.
8. Apply the proofcheck depth split: targeted dependency check, or full `/proofcheck --post-repair` for main-chain rewrites.
9. Run the cross-reference drift audit on every rewritten labeled object.
10. Run the economy self-check.
11. Present per-atomic-claim approvals (semantic) and cluster approval (cosmetic) to the author.

## Honest Limits

- Equivalence is the author's responsibility to confirm; the ledger documents the claim of equivalence and surfaces the silent-change risk, but it does not prove equivalence. The proofcheck depth split is the verification layer for main-chain rewrites.
- The use-test cannot detect a symbol that is used downstream but used vacuously (introduced, referenced once in a trivial way, never load-bearing). That is a softer form of decoration the mode does not catch.
- Venue-register exemplar judgment depends on the model actually reading recent venue papers; stale or hallucinated venue conventions produce wrong calibration. Where possible the exemplar papers should resolve to literature cache entries.

## Cross-Reference

- `proof-closure-machinery.md` — the change-log discipline this ledger parallels; semantic rewrites that feed proofs route into the same closure machinery.
- `applicability-axes.md` — the axis vocabulary the `Touched axis` column draws from.
- `cache-verification-states.md` / `literature-cache-protocol.md` — venue exemplars should resolve to cache entries where possible.
- `stat-notation-audit.md` (stat-writing-skills) — the cross-reference drift audit.
- `stat-theory-writing.md` (stat-writing-skills) — formalization statement patterns and the venue formalism register.
- `stat-venue-checklists.md` (stat-writing-skills) — per-venue register.
- `CODEX_PROTOCOL.md` — `/proofcheck --post-repair` on a main-chain rewrite uses the same dialogue and reasoning-ladder discipline.
