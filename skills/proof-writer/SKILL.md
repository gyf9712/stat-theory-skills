---
name: proof-writer
description: Writes rigorous mathematical proofs for ML/AI theory. Use when asked to prove a theorem, lemma, proposition, or corollary, fill in missing proof steps, formalize a proof sketch, 补全证明, 写证明, 证明某个命题, or determine whether a claimed proof can actually be completed under the stated assumptions.
argument-hint: [theorem-statement-and-assumptions]
allowed-tools: Read, Write, Edit, Grep, Glob
model: opus
---

# Proof Write: Rigorous Theorem / Lemma Drafting

> 🔬 **Model Recommendation**: Run this skill on **Claude Opus** for best results.
> Writing rigorous mathematical proofs requires deep reasoning. If your session is
> not on Opus, run `/model opus` before invoking.

Write a mathematically honest proof package, not a polished fake proof.

## Constants

- DEFAULT_PROOF_DOC = `PROOF_PACKAGE.md` in project root
- STATUS = `PROVABLE AS STATED | PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION | NOT CURRENTLY JUSTIFIED`

## Context: $ARGUMENTS

## Goal

Produce exactly one of:
1. a complete proof of the original claim
2. a corrected claim plus a proof of the corrected claim
3. a blockage report explaining why the claim is not currently justified

## Inputs

Extract and normalize:
- exact theorem / lemma / proposition / corollary statement
- explicit assumptions
- notation and definitions
- any user-provided proof sketch, partial proof, or intended strategy
- nearby lemmas or claims in local notes, appendix files, or theorem drafts if the request points to them
- desired output style if specified: concise, appendix-ready, or full-detail

If notation or assumptions are ambiguous, state the exact interpretation you are using before proving anything.

## Workflow

### Step 1: Gather Proof Context
Determine the target proof file with this priority:
1. a file path explicitly specified by the user
2. a proof draft already referenced in local notes or theorem files
3. `PROOF_PACKAGE.md` in project root as the default target

Read the relevant local context:
- the chosen target proof file, if it already exists
- theorem notes, appendix drafts, or files explicitly mentioned by the user

Extract:
- exact claim
- assumptions
- notation
- proof sketch or partial proof
- nearby lemmas that the draft may depend on

### Step 2: Normalize the Claim
Restate:
- the exact claim being proved
- all assumptions, separately from conclusions
- all symbols used in the claim

Identify:
- hidden assumptions
- undefined notation
- scope ambiguities
- whether the available sketch proves the full claim or only a weaker variant

Preserve the user's original theorem statement unless a change is explicitly required.
If you use a stronger normalization or cleaner internal formulation only to make the proof easier, keep that as an internal proof device rather than silently replacing the original claim.

### Step 3: Feasibility Triage
Before writing a proof, classify the claim into exactly one status:
- `PROVABLE AS STATED`
- `PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION`
- `NOT CURRENTLY JUSTIFIED`

Check explicitly:
- does the conclusion actually follow from the listed assumptions?
- is any cited theorem being used outside its conditions?
- is the claim stronger than what the available argument supports?
- is there an obvious counterexample, boundary case, or quantifier failure?

If the claim is not provable as stated, do NOT fabricate a proof.
Do NOT silently strengthen assumptions or narrow the theorem's scope just to make the proof work.

### Step 3.5: Locate the Verification Target and Bottleneck

Before building the dependency map, locate the proof's strategic center. This is the senior-statistician move that distinguishes battlefield selection from blind algebra. Strong PhD students push forward from assumptions; senior statisticians work backward to the right verification target first.

Read `../stat-shared-references/proof-strategy.md`, especially the *Claim Families → Verification Targets* table, the *Anchor Selection and Comparison* section, and the *Trap Catalogue with Diagnostic Tests*.

Decide three things and write them into the proof package as a section titled `## Verification Target and Bottleneck`.

**(a) Verification target.** The precise intermediate statement whose verification would close the claim under your chosen reduction.

Examples:
- For LASSO ℓ_2 error: "Cone condition $\|\Delta_{S^c}\|_1 \leq 3\|\Delta_S\|_1$ plus quadratic basic inequality $\|X\Delta\|_2^2/n \lesssim \lambda \sqrt{s}\|\Delta_S\|_2$; then RE closes the rate."
- For M-estimator asymptotic normality: "Asymptotic linear representation $\sqrt{n}(\hat\theta - \theta_0) = -A^{-1} (1/\sqrt{n})\sum \psi(Z_i, \theta_0) + o_p(1)$; then CLT plus Slutsky."
- For a Sobolev-ball minimax lower bound via Fano: "Comparison family of size $M$ in $W^{s,2}(L)$ with pairwise loss separation $\delta_n$ and pairwise KL $\leq \beta$, satisfying Fano's hypothesis $\log M \geq 2n\beta + \log 2$."

The target must be theorem-specific. "Use Fano" is a slogan; "construct a comparison family satisfying Fano's separation and information conditions at scale $\delta_n$" is a target.

**(b) Bottleneck.** The first unresolved leaf: the specific inequality, localization claim, entropy bound, invertibility step, or prerequisite of a cited theorem that currently lacks a verification. Express as a statement, not as prose.

**(c) Resolution path.** How you intend to break the bottleneck: prove a new lemma, verify prerequisites of a cited theorem, weaken the claim, or downgrade status if no path exists.

If the proof has two co-equal hard centers, declare one primary verification target for the main claim and secondary targets for each genuinely independent hard lemma.

**Declare the proof's relation to the literature** per *Anchor Selection and Comparison* in the shared reference:

- **Template adaptation**: identify 1-3 closest anchors, their proof spine, what is borrowed, what is genuinely new.
- **Standard-result invocation**: name the theorem and list the prerequisites you will verify.
- **Self-contained**: this requires explicit defense via the *Implicit Machinery Disclosure* block. Most claims of self-containment are false; if you cannot honestly fill the disclosure, the proof is not self-contained and an anchor walk is required.

`proof-writer` does not have its own web tools. Anchor identification draws on the model's training, the user's narrative, and any local notes referenced in Step 1. If the closest anchor is unclear, say so explicitly rather than fabricating a citation. If the proof is genuinely new and self-contained, defend that.

### Step 4: Build a Dependency Map (backward-first, forward-verified)

With the verification target in hand, build the dependency map.

**Backward pass.** Start from the claim. For each unresolved subgoal, ask: what would imply this? Continue backward until the leaves are one of:
- an explicit assumption (A1), (A2), ...
- a verified prerequisite of a cited theorem
- an isolated new lemma that you will prove separately

**Forward pass.** From the leaves, verify by forward reasoning that the assumptions actually support each leaf claim. A backward decomposition can produce subgoals that look plausible but do not actually hold; the forward pass catches this.

If the forward pass fails on a leaf, either:
- change strategy (try a different verification target or anchor)
- isolate that leaf as a lemma and find a different proof for it
- downgrade the status of the main claim

The dependency map is then a structured inventory:
- main claim
- the verification target (from Step 3.5)
- required intermediate lemmas
- named theorems or inequalities to cite
- which assumptions each nontrivial step depends on
- boundary cases that must be handled separately

Choose a proof strategy from the menu only after the verification target and bottleneck are clear:
- direct
- contradiction
- induction
- construction
- reduction to a known result
- coupling / probabilistic argument
- optimization inequality chaining

A strategy chosen before locating the verification target is a label, not a proof method. If one step is substantial, isolate it as a lemma instead of burying it in one sentence.

### Step 5: Write the Proof Document
Write to the chosen target proof file.

If the target proof file already exists:
- read it first
- update the relevant claim section
- do not blindly duplicate prior content

If the user does not specify a target, default to `PROOF_PACKAGE.md` in project root.

Do NOT write directly into paper sections or appendix `.tex` files unless the user explicitly asks for that target.

The proof package must include:
- exact claim
- explicit assumptions
- proof status
- announced strategy
- dependency map
- numbered major steps
- justification for every nontrivial implication

## ANTI-SKETCH DISCIPLINE (mandatory — refuses sketch output)

This skill must NEVER produce a proof sketch labeled or used as a proof. A
"sketch" is a research-planning device, not a verification.

**Distinction**:
- **Proof outline / proof plan**: high-level strategy used during research design
  (this is fine and useful; see /theory-design for that purpose)
- **Proof sketch**: a short summary placed in lieu of a proof, intended to
  convince a reader (this is what this skill refuses)
- **Complete proof**: rigorous step-by-step derivation that any qualified reader
  could verify — what this skill always produces

**Sketch indicators to REFUSE**:
- Title or section labeled "Proof Sketch", "Sketch of Proof", "Outline of Proof"
  when output is meant as the actual proof
- Verbal-only narrative without equation derivations for a quantitative claim
- "By similar arguments to [paper Z]" without showing the adaptation
- "The rest follows from standard techniques" without specifying which technique
  and how it applies
- "We omit the details" / "Details are routine"
- A single paragraph + citation as a "proof" for a substantive theorem

**Behavior when asked for a sketch**:
If the user explicitly asks for a sketch:
1. Refuse to produce one disguised as a proof
2. Offer alternatives:
   (a) Complete proof (this skill's purpose)
   (b) Explicit "Research outline — NOT a proof" document (labeled clearly,
       no implication of verification) — but redirect to /theory-design
   (c) Proof of a strictly weaker but completely verifiable claim, plus a
       clearly-labeled research outline for the stronger conjecture

Behavior when asked for "a proof" but the only completable thing is a sketch:
Downgrade status to `NOT CURRENTLY JUSTIFIED` and write a blockage report.
Do NOT silently produce a sketch in place of a proof.

Mathematical rigor requirements:
- never use "clearly", "obviously", "it can be shown", "by standard arguments", or "similarly" to hide a gap
- never use "the rest is similar" / "we omit the details" / "details are routine"
- when invoking a result from another paper, write the adaptation explicitly —
  do not just point at the paper
- define every constant and symbol before use
- check quantifier order carefully
- handle degenerate and boundary cases explicitly, or state why they are excluded
- if invoking a standard fact, state its name and why its assumptions are satisfied here
- use `$...$` for inline math and `$$...$$` for display equations
- never write math in plain text

**Length test** (a heuristic, not a hard rule):
For a substantive theorem (e.g., a rate of convergence, asymptotic distribution,
or coverage claim), a complete proof is typically ≥ 1 page of dense derivation
unless the proof genuinely reduces to a single named result + verification of
its prerequisites. If your proof is ≤ 10 lines for a theorem that's a paragraph
to state, suspect it's actually a sketch.

## HARD COMPLETION RULE (when invoked to expand a sketch)

When proof-writer is invoked by /proof-repair (Expand-Sketch-to-Proof workflow)
or by the user directly to expand an existing sketch, the output MUST be one
of exactly two terminal states:

1. **COMPLETE PROOF**: every step rigorously derived, no remaining sketch
   indicators, length appropriate to claim complexity. Output a proof package
   with status `PROVABLE AS STATED` or `PROVABLE AFTER WEAKENING`.

2. **BLOCKAGE REPORT**: explicit `NOT CURRENTLY JUSTIFIED` status with:
   - The specific step that cannot be expanded and why
   - What additional assumption, lemma, or technique would be needed
   - Whether a weaker claim is provable (if so, prove that weaker claim
     completely)

The skill is **forbidden** from producing:
- A second sketch (even one labeled differently)
- A "partial expansion" that fills some steps but leaves others sketched
- A proof of a strictly weaker claim without clearly relabeling the claim
- An expansion that introduces silent assumptions to make the proof work

If the user invokes proof-writer with the intent of "just expand this a bit",
refuse and explain: either FULL expansion (with all hidden assumptions surfaced)
or BLOCKAGE REPORT. There is no middle ground.

This rule prevents the failure mode where a sketch is "expanded" into another
sketch with slightly more words, which is the most common silent failure when
asking LLMs to expand proofs.
- if the proof uses an equivalent normalization that is stronger in appearance than the user's original theorem statement, label it explicitly as a proof device and keep the original claim separate

### Step 6: Final Verification
Before finishing the target proof file, verify:
- the theorem statement exactly matches what was actually shown
- every assumption used is stated
- every nontrivial implication is justified
- every inequality direction is correct
- every cited result is applicable under the stated assumptions
- edge cases are handled or explicitly excluded
- no hidden dependence on an unproved lemma remains
- the verification target stated in Step 3.5 is actually reached by the proof
- the anchor disclosure honestly reflects what was borrowed
- the implicit machinery disclosure (if any) is filled in honestly

Then apply each of the seven diagnostic tests from the *Trap Catalogue* in `../stat-shared-references/proof-strategy.md`:

1. **Localization-before-expansion**: find the first Taylor / linearization step; verify a high-probability localization statement precedes it.
2. **Wrong norm / wrong mode**: underline the norm and convergence mode in the claim; verify the last bound before the conclusion uses the same norm and mode.
3. **Good-event bookkeeping**: every "on the event $E_n$" or "with high probability" must be paired with a bound on $\mathbb{P}(E_n^c)$.
4. **Rate leakage**: list every rate factor introduced; verify the final rate accounts for each one or shows an explicit cancellation.
5. **Quantifier inflation**: every "uniformly", "for all", "sup", "simultaneously" must be supported by an upgrade argument if the input result is pointwise.
6. **Citation identity / version drift**: for each "by Theorem / Lemma / Proposition / Corollary / Eq. X", verify a matching row exists in `## Cited Results Audit` with full source identity, locator, source-of-record, direct-inspection status, page or equation pointer, and version / errata note. If inspection status is `checked-now-alternate-source`, the version crosswalk must be filled.
7. **Imported-result applicability drift**: for each row in `## Cited Results Audit`, verify every source assumption is mapped to a local item; the local step closed is named; the conclusion fit is `exact`, `stronger than needed`, or `weaker than needed with explicit bridge`. Any unmapped assumption, missing local step, `weaker than needed` without bridge, `ambiguous-mismatch`, or proof-dispositive row marked `previously-checked-no-current-access` or `never-checked` is a flag.
8. **Boundary / singularity**: every inverse, division, argmax differentiability, support recovery, or Hessian inversion is paired with an explicit exclusion of the singular case.

Record the result of each test in the `Open Risks` section. Any FAIL must be fixed or the status downgraded.

If a key step still cannot be justified, downgrade the status and write a blockage report instead of forcing a proof.

## Required File Structure

Write the target proof file using this structure:

```md
# Proof Package

## Claim
[exact statement]

## Status
PROVABLE AS STATED / PROVABLE AFTER WEAKENING / NOT CURRENTLY JUSTIFIED

## Assumptions
- ...

## Notation
- ...

## Verification Target and Bottleneck
- Verification target: If [precise intermediate statement] holds, then the claim follows by [named final argument].
- Bottleneck: The first unresolved leaf is [specific inequality, localization claim, entropy bound, invertibility step, or citation prerequisite].
- Resolution path: [prove a new lemma / verify prerequisites of a cited theorem / weaken the claim].

## Anchors and Borrowing
- Relation to literature: [template adaptation / standard-result invocation / self-contained]
- Anchor 1: [reference], [theorem number]. Verification target: [...]. Borrowed: [...]. New: [...].
- Anchor 2 (if any): ...
- If self-contained: see Implicit Machinery Disclosure below.

## Implicit Machinery Disclosure (if proof labeled self-contained)
- Mature machinery used implicitly: [list]
- Background needed by a strong PhD student to verify the proof unaided: [list]
- Pieces re-proved here rather than imported: [list]
- Paper-self-contained or locally self-contained: [one of these labels]

## Cited Results Audit

Use one block per imported result that is either proof-dispositive, or cited by specific theorem / lemma / proposition / corollary / equation number.

Do not create rows for background or positioning citations (those are handled by the project's `cited_results.lock.md` lock manifest, schema in `../stat-shared-references/citation-purpose-protocol.md`). Do not use this section to hide primitive techniques such as Cauchy-Schwarz or Fubini; those belong in the local proof verification, not here. For graduate-core citation-exempt schemas (see `../stat-shared-references/proof-strategy.md`), a single schema-applicability note suffices instead of a full row.

Each row's locator and source-of-record fields should resolve to a literature cache entry. Cache reference format: `paper:<bibkey>#<result_id>`. The cache protocol lives in `../stat-shared-references/literature-cache-protocol.md` (router with Minimum Load Map); proof-writer's Cited Results Audit typically consumes `cache-verification-states.md` (to enforce `Direct inspection status: checked-now-source-of-record` matches the cache's verification state) and `citation-purpose-protocol.md` (for the `Role class` field, which maps to citation purpose).

**Lock manifest update** (per `../stat-shared-references/cited-results-lock-protocol.md`): for every row added to `## Cited Results Audit`, ensure a matching row exists in the project's `papers/<project>/cited_results.lock.md`. Citation purpose is typically `load_bearing` for proof-dispositive citations (`P0`), `standard_tool` for schema-exempt invocations recorded explicitly, and `lineage_positioning` for anchor citations. If the cache entry's verification state is below `independently_checked` and the audit row is `P0`, the lock manifest row records the current state but the audit emits a verification request per `cache-verification-states.md`.

Rows with `never-checked` are inadmissible. Rows with `previously-checked-no-current-access` may remain only as open risks for `P1` or `P2` items. If such a row is `P0` proof-dispositive, it blocks `PROVABLE AS STATED` unless the step is reproved locally or `/proof-repair` retrieves the source. Cache entries below `source_checked` cannot satisfy `Direct inspection status: checked-now-source-of-record`; the audit emits a verification request per `cache-verification-states.md`.

### CR1. [Short label]

- Role class: [proof-dispositive / schema-level / anchor-specific]
- Audit priority: [P0 essential / P1 supportive / P2 optional]
- Local proof location: [Step number, equation transition, lemma use, or sentence closed by this citation]
- Full source identity: [authors, year, title, venue / book]
- Cited locator in proof: [Theorem / Lemma / Proposition / Corollary / Equation number exactly as written]
- Source of record: [journal version / book edition / arXiv vN / erratum-corrected source]
- Version / numbering crosswalk: [required if numbering differs across versions, or if alternate source inspected]
- Errata status: [checked / none known / unknown]
- Direct inspection status: [checked-now-source-of-record / checked-now-alternate-source / previously-checked-no-current-access / never-checked]
- Inspection note: [what was inspected, or when / where it was last checked]
- Page / equation pointer: [page(s), theorem page, equation number]
- Exact used clause: [the exact clause actually consumed; quote only the needed clause]
- Source assumptions:
  - (S1) ...
  - (S2) ...
- Local verification map:
  - (S1) ← [A_k / Lemma m / verified prerequisite / local derivation]
  - (S2) ← [...]
- Local step closed by the citation: [exact step this result is supposed to justify]
- Conclusion needed locally: [exact statement needed at that step]
- Conclusion fit: [exact / stronger than needed / weaker than needed with explicit bridge / ambiguous-mismatch]
- Bridge argument if not exact: [required when `Conclusion fit` is `weaker than needed with explicit bridge`]
- Audit verdict: [PASS / OPEN RISK / FAIL]
- Failure or risk reason: [one sentence]

### Literature-Retrieval Handoff

List only rows that are not cleanly verified. `proof-writer` itself does not have web tools and cannot retrieve sources; this table is the prioritized handoff to `/proof-repair` or to the author.

| Priority | Audit row | Why retrieval is needed | If retrieval fails | Effect on proof status |
|---|---|---|---|---|
| P0 | CR_ | Proof-dispositive citation not directly inspected | Reprove locally or downgrade claim | Cannot remain `PROVABLE AS STATED` |
| P1 | CR_ | Supporting citation checked only via memory / alternate source | Replace with accessible source or keep as explicit open risk | Proof may survive with disclosed risk |
| P2 | CR_ | Nonessential citation precision issue | Drop or replace citation | No effect on core proof |

## Proof Strategy
[chosen approach and why; should follow from the verification target above]

## Dependency Map
1. Main claim depends on the verification target above.
2. Verification target depends on ...
3. Lemma A depends on ...
4. Step k uses ...
[Built backward from the claim, then forward-verified that leaves are supported.]

## Proof
Step 1. ...
Step 2. ...
...
Therefore the claim follows. ∎

## Corrections or Missing Assumptions
- [only if needed]

## Open Risks
- [remaining fragile points, if any]
- Cross-check against the *Trap Catalogue* in `../stat-shared-references/proof-strategy.md`:
  - Localization-before-expansion: [pass / fail / not applicable]
  - Wrong norm / wrong mode: [pass / fail / NA]
  - Good-event bookkeeping: [pass / fail / NA]
  - Rate leakage: [pass / fail / NA]
  - Quantifier inflation: [pass / fail / NA]
  - Citation identity / version drift: [pass / fail / NA]
  - Imported-result applicability drift: [pass / fail / NA]
  - Boundary / singularity: [pass / fail / NA]
```

## Output Modes

### If the claim is provable as stated
Write the full file structure above with a complete proof.

### If the original claim is too strong
Write:
- why the original statement is not justified
- the corrected claim
- the minimal extra assumption if one exists
- a proof of the corrected claim

### If the proof cannot be completed honestly
Write:
- `Status: NOT CURRENTLY JUSTIFIED`
- the exact blocker: missing lemma, invalid implication, hidden assumption, or counterexample direction
- what extra assumption, lemma, or derivation would be needed to finish the proof
- a corrected weaker statement if one is available

## Chat Response

After writing the target proof file, respond briefly with:
- status
- whether the original claim survived unchanged
- what file was updated

## Key Rules

- Never fabricate a missing proof step.
- Prefer weakening the claim over overclaiming.
- Separate assumptions, derived facts, heuristics, and conjectures.
- Preserve the user's original theorem statement unless you explicitly mark a corrected claim or an internal normalization.
- If the statement is false as written, say so explicitly and give a counterexample or repaired statement.
- If uncertainty remains, mark it explicitly in `Open Risks`; do not hide it inside polished prose.
- Correctness matters more than brevity.
