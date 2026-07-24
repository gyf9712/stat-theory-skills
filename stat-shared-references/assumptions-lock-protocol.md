# `assumptions.lock.md` Ownership Protocol

Schema and update discipline for a project's **shared assumption system** — one
canonical, ID-addressable store so the whole theoretical framework draws from a single
namespace instead of each theorem package re-declaring its own assumptions. The
submission-side analogue of `cited-results-lock-protocol.md` (citations) and
`CLAIM_SUPPORT_MAP.md` (claims): assumptions are now a cross-package address space, so
they get one thin lock artifact rather than schema duplicated into every skill.

This is a **convention + tiny protocol**, not a governance layer. There is no
`/lock-assumptions` skill. `theory-design` initializes the file; `proof-writer` and
`proof-repair` append under the rules below; `proofcheck`, `assumption-loadbearing-audit.md`,
and `stat-mock-review` consume and audit it.

## When to Read

- `theory-design` — before writing the framework's assumption profile (initializes the file).
- `proof-writer` — before declaring any theorem's assumptions (invoke by ID, do not restate).
- `proofcheck` — Pass 2A (resolve invoked IDs) and Pass 3 (consistency triage).
- `proof-repair` — when a repair adds an assumption (L4 Add-Assumption appends a registry row).

## The Schema

`assumptions.lock.md` holds **two** tables. Keep them separate — the registry is
append-only and immutable per entry; usage evolves and lives in the matrix.

```markdown
# Assumption Lock — <project>

## Assumption Registry
| ID | Short name | Verbatim statement | Constrained objects | Applicability axis | Strength/regime class | Relation to other IDs | Rationale (where needed) | Introduced by | Status |
|----|-----------|--------------------|--------------------|--------------------|-----------------------|-----------------------|--------------------------|--------------|--------|

## Theorem Invocation Matrix
| Theorem ID | Invoked assumption IDs | Proof package | Version | Supersedes |
|-----------|------------------------|---------------|---------|------------|
```

- **ID**: `A1, A2, …`. Stable and permanent once assigned. `A_k` is reserved for registry
  assumptions **only** (see Namespace Hygiene).
- **Applicability axis**: from `applicability-axes.md` (e.g. `tail_condition`,
  `dependence`, `dimension_regime`). Ties the audit vocabulary together.
- **Relation to other IDs**: `base` / `strengthens A3 on <axis>` / `variant-of A2` /
  `incompatible-with A5`. The relation is how variants enter without silent restatement.
- **Introduced by**: `theory-design` / `proof-writer:<theorem>` / `proof-repair:<issue>`.
- **Status**: `active` / `retired` (retired rows stay for provenance; never deleted).
- **used-by is NOT a registry column** — it is derived from the Invocation Matrix.

## Update Discipline

- **Read before write.** Before adding an assumption, search the registry for one that
  already says it (possibly under a different short name). If it exists, invoke that ID.
- **Registry is append-only.** A new assumption is a new row with a new ID. A *variant* of
  an existing assumption is also a new row, with an explicit `Relation to other IDs`
  (`strengthens A3 on tail_condition`), never an edit of the base row.
- **Matrix is mutable.** A theorem's invoked set can change across revisions; record the
  change with `Version` and `Supersedes`.

## Namespace Hygiene (resolves the promotion question)

One namespace for every **real** assumption; proof-internal devices stay local but must
**not** be labeled `A_k`.

- **Registry `A_k`** — anything that restricts a theorem, lemma, corollary, imported-theorem
  prerequisite, model class, estimator, tuning regime, or asymptotic path.
- **Local devices** — good events `E_k`, temporary hypotheses inside a conditional argument
  `H_k`, bridge lemmas `B_k`, obligation states `O_k`, notation conveniences. These stay in
  the package and must be **discharged from registry assumptions**, not assumed.

A terminal `PROOF_PACKAGE.md` carries **no local `A_k` declarations**. It states
`Invoked assumptions: A1, A3, A7 from assumptions.lock.md`. A hidden assumption that
survives as a premise is either promoted to the registry or the package is not
`PROVABLE AS STATED`.

## No Automatic Inheritance (anti-inflation)

The registry is a store, **not** a global premise. A theorem does **not** inherit `A1..AK`
because they exist — it lists the subset it actually uses. Optional **profiles** are
allowed only as aliases, e.g. `P-base = {A1, A2, A3}`; `proofcheck` **expands** the profile
and runs invoked-but-unused on the expanded IDs. This prevents one bloated maximal
assumption set from over-restricting individual theorems, and keeps the store aligned with
`assumption-loadbearing-audit.md`'s goal of minimal load-bearing assumptions.

## Consistency Triage (proofcheck Pass 3 — NOT satisfiability certification)

Do **not** ask whether the union of all registry assumptions has a common model. A framework
may deliberately contain mutually exclusive regimes (a sub-Gaussian upper bound and a
heavy-tail robustness variant; fixed-design and random-design corollaries); the full
registry need not be jointly satisfiable. Instead, per invoked subset and per declared
profile:

- flag **direct contradictions** within a single theorem's invoked set;
- ensure no theorem co-invokes IDs marked `incompatible-with` each other or `variant-of` the
  same base;
- ask for a witness model only when it is natural and low-cost.

Emit one of: `PASS: no direct contradiction found` / `FLAG: axis tension` /
`FAIL: direct contradiction` / `UNKNOWN: common model not certified`. **Never** claim
satisfiability certification for a nonparametric or infinite-dimensional framework — that is
a false-authority trap, the same class as certifying proof correctness from a clean lint.

## Integration with proof-repair

An L4 `Add-Assumption` repair appends a registry row (`Introduced by: proof-repair:<issue>`,
`Relation` set to the base it strengthens) **and** records the existing Assumption-Extension
Change Log in `proof-closure-machinery.md`. The two mechanisms merge: the change log is the
justification (natural weaker variant considered, why it fails), the registry row is the
canonical entry the rest of the framework now references.

## Cross-Reference

- `applicability-axes.md` — axis vocabulary for the `Applicability axis` column.
- `assumption-loadbearing-audit.md` — reports its T1–T4 findings by registry ID.
- `proof-closure-machinery.md` — repair-side Assumption-Extension Change Log (justification).
- `cited-results-lock-protocol.md` — the sibling canonical store this parallels.

## Honest Limits

A clean invocation matrix certifies that the framework shares one assumption namespace and
has no *directly* contradictory invoked subsets. It does not certify that the assumptions are
*true*, *minimal*, or *jointly satisfiable* in general. Minimality is pushed toward the
invoked-but-unused check and the load-bearing audit; truth stays with the proofs.
