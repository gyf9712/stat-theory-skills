---
name: proof-writer
description: Writes rigorous mathematical proofs for ML/AI theory. Use when asked to prove a theorem, lemma, proposition, or corollary, fill in missing proof steps, formalize a proof sketch, 补全证明, 写证明, 证明某个命题, or determine whether a claimed proof can actually be completed under the stated assumptions.
argument-hint: [theorem-statement-and-assumptions]
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
model: opus
---

# Proof Write: Rigorous Theorem / Lemma Drafting

> 🔬 Run this skill on **Claude Opus**. Writing rigorous proofs needs deep reasoning;
> run `/model opus` first if your session is not on Opus.

Write a mathematically honest proof package, not a polished fake proof.

**The unit of completion is the closed obligation, not prose.** A proof is finished
when every nontrivial obligation it raises is discharged into a typed closure
object, not when it reads smoothly. This single idea drives the whole skill: it is
what stops the model from quitting early (an open obligation is visible and costly)
and from faking (you cannot prose your way into a typed closure).

## Constants

- DEFAULT_PROOF_DOC = `PROOF_PACKAGE.md` in project root
- STATUS = `PROVABLE AS STATED | PROVABLE AFTER WEAKENING / EXTRA ASSUMPTION | NOT CURRENTLY JUSTIFIED`
- VERIFICATION = `Verified | Conditionally verified | Gap found` (defined in `../stat-shared-references/proof-closure-machinery.md`, single source of truth)
- SCRIPT = `../stat-shared-references/scripts/proof_gap_scan.py`

## Context: $ARGUMENTS

## Goal

Produce exactly one of three terminal outputs:
1. a complete proof of the original claim, every obligation closed;
2. a corrected (usually weaker) claim plus a complete proof of it;
3. a blockage record stating precisely why the claim is not currently justified.

There is no fourth option. A sketch, a partial expansion, or a proof with a residual
"open risk" footnote is not a terminal output.

## Workflow

### Step 1: Gather context
Determine the target proof file by priority: (1) a path the user specified, (2) a
proof draft referenced in local notes or theorem files, (3) `PROOF_PACKAGE.md`.
Read the target if it exists, plus theorem notes and any files the user names.
Extract the exact claim, assumptions, notation, any user sketch, and nearby lemmas
the draft depends on. If notation or assumptions are ambiguous, state the exact
interpretation you will use before proving anything.

### Step 2: Normalize the claim
Restate the exact claim, all assumptions separated from conclusions, and every
symbol. Identify hidden assumptions, undefined notation, scope ambiguities, and
whether the available sketch proves the full claim or only a weaker variant.
Preserve the user's original statement. If a stronger internal formulation only
makes the proof easier, keep it as a labeled proof device, not a silent replacement.

### Step 3: Feasibility triage
Classify into exactly one STATUS. Check: does the conclusion follow from the listed
assumptions? Is any cited theorem used outside its conditions? Is the claim stronger
than the available argument supports? Is there an obvious counterexample or
quantifier failure? If not provable as stated, do not fabricate a proof and do not
silently strengthen assumptions to force one.

### Step 4: Locate the verification target and bottleneck
This is the senior-statistician move: work backward to the right verification target
before any forward algebra. Read `../stat-shared-references/proof-strategy.md` —
the *Claim Families → Verification Targets* table, *Anchor Selection and Comparison*,
and the *Trap Catalogue*.

Decide and record three things under `## Verification Target and Bottleneck`:
- **Verification target** — the precise intermediate statement whose verification
  closes the claim under your chosen reduction. It must be theorem-specific: "use
  Fano" is a slogan; "construct a comparison family meeting Fano's separation and
  information conditions at scale $\delta_n$" is a target. Worked examples per claim
  family are in the *Claim Families → Verification Targets* table of the reference.
- **Bottleneck** — the first unresolved leaf, expressed as a statement: the specific
  inequality, localization claim, entropy bound, invertibility step, or citation
  prerequisite that currently lacks a verification.
- **Resolution path** — prove a new lemma, verify a cited theorem's prerequisites,
  weaken the claim, or downgrade if no path exists.

Declare the proof's relation to the literature per *Anchor Selection and Comparison*:
template adaptation (name 1-3 anchors, what is borrowed, what is new),
standard-result invocation (name the theorem, list prerequisites to verify), or
self-contained (defend via the *Implicit Machinery Disclosure* block; most claims of
self-containment are false). proof-writer has no web tools; anchor identification
draws on training and local notes. If the closest anchor is unclear, say so rather
than fabricate a citation.

### Step 5: Build the dependency map and raise obligations
Backward pass: from the claim, ask what would imply each subgoal until the leaves are
explicit assumptions, verified citation prerequisites, or isolated new lemmas.
Forward pass: from the leaves, verify the assumptions actually support each leaf — a
backward decomposition can produce plausible subgoals that do not hold.

Every nontrivial leaf or step becomes a numbered **obligation** `O1..Ok` in the
Obligation Ledger (see below). "Nontrivial" excludes primitive moves (Cauchy-Schwarz,
Fubini, a triangle inequality); it includes every inequality, localization, mode
conversion, invertibility, uniformity upgrade, or imported result that the proof
actually leans on. Give each obligation a canonical ID; give each isolated lemma `L1..`
and each bridge `B1..` an ID too. The linter needs these IDs to check the package.

### Step 6: Construct the proof, closing every obligation
Write the proof to the target file (read and update it first if it exists; do not
duplicate prior content; do not write into paper `.tex` files unless asked). Number
the major steps and justify every nontrivial implication. Each obligation must
terminate in exactly one typed state — `CLOSED-LOCAL`, `CLOSED-CITED`, or `BLOCKED`
— with the fields the Obligation Ledger requires. An obligation left untyped is an
incomplete proof.

### Step 7: Verify and lint
Apply the diagnostic tests from the *Trap Catalogue* in `proof-strategy.md` and
record each result in `## Verification Checks`:
localization-before-expansion, wrong norm/mode, good-event bookkeeping, rate leakage,
quantifier inflation, citation identity, imported-result applicability, negligibility
closure (see also the *Negligibility-Closure Trivial-Pass Tier*), boundary/singularity.
Then run the linter:

```bash
python "$(dirname "$0")/../stat-shared-references/scripts/proof_gap_scan.py" --proof PROOF_PACKAGE.md
```

Resolve every `STRUCTURAL-INCOMPLETE` finding (these are mechanical and block a
`PROVABLE AS STATED` status). Review every `CANDIDATE` finding (advisory hedge-phrase
hits) and either discharge or justify it. The linter checks closure, not correctness;
a clean lint does not certify the mathematics, only that the package is closed.

## Termination Rule (the one invariant)

This skill never emits a sketch, a partial expansion, or a "proof" that defers a step.
A **proof sketch** is a short narrative offered in lieu of verification; this skill
refuses it. A **proof outline** is a research-planning device — fine during design,
redirect to `/theory-design`, never output here as a proof.

Three banned outputs, no exceptions:
- a section labeled or used as "Proof Sketch" / "Outline of Proof" as the actual proof;
- a partial expansion that closes some obligations and leaves others narrated;
- a proof of a strictly weaker claim without relabeling the claim.

The phrases "clearly", "obviously", "it can be shown", "by standard arguments",
"similarly", "the rest is routine", "we omit the details" are gap-hiding tells. When
invoking another paper's result, write the adaptation explicitly. Define every symbol
before use; check quantifier order; handle or explicitly exclude boundary cases; use
`$...$` and `$$...$$`, never plain-text math.

When the only completable thing is a sketch, the output is a **Blockage Record** with
status `NOT CURRENTLY JUSTIFIED`, not a sketch. When asked to "just expand a bit",
refuse the middle ground: full closure of every obligation, or a Blockage Record.

**Length is a symptom, not a target.** A substantive theorem (a rate, a limiting
distribution, a coverage claim) whose proof is ≤ 10 lines is almost always a sketch,
unless it genuinely reduces to one named result plus prerequisite verification.

## The Obligation Ledger (core mechanism)

Every nontrivial obligation terminates in exactly one typed state. This is what makes
finishing cheaper than quitting without making fabrication cheap: closure is a typed
object the linter can check, and `BLOCKED` carries a full attack record.

- **`CLOSED-LOCAL`** — discharged by an explicit local derivation. Field: the step or
  equation transition that closes it.
- **`CLOSED-CITED`** — discharged by a load-bearing imported result. Requires an inline
  **applicability block** (only load-bearing imports get one; background and anchor
  citations do not):
  - `clause used` — the exact clause of the cited result actually consumed;
  - `assumption map` — each source assumption mapped to a local item (`A_k` / `Lm` /
    verified prerequisite / local derivation);
  - `conclusion fit` — `exact` | `stronger than needed` | `weaker-with-bridge`;
  - `bridge ref` — the `Bk` ID of the bridge derivation, required iff fit is
    `weaker-with-bridge`;
  - `source-status` — `checked-now` (source inspected this session) | `local-excerpt`
    (verified against a local excerpt) | `unverified-source` (recalled, not inspected).
    proof-writer has no web tools, so `unverified-source` is honest and common.
- **`BLOCKED`** — could not be closed. Requires an attack record:
  - the exact statement of the obligation;
  - the best bridge attempted;
  - the concrete reason it failed;
  - one alternative reduction considered (and why it also failed or was not pursued).
  Then isolate the obligation as a named conjectural lemma.

**Provability vs verification.** `PROVABLE AS STATED` requires every obligation
`CLOSED-LOCAL` or `CLOSED-CITED` and a clean structural lint. But if any load-bearing
`CLOSED-CITED` obligation carries `source-status: unverified-source`, the package
VERIFICATION is `Conditionally verified`, not silently complete — it is correct *if*
the cited statement is as recalled. proofcheck upgrades source verification;
proof-repair retrieves sources. Any `BLOCKED` obligation forbids `PROVABLE AS STATED`:
the status is `PROVABLE AFTER WEAKENING` (if the weaker claim closes) or
`NOT CURRENTLY JUSTIFIED`.

Full provenance (version crosswalk, errata, lock-manifest, cache verification-states,
retrieval handoff) is **not** proof-writer's job — it lives in
`../stat-shared-references/cited-results-lock-protocol.md` and is operated by
proof-repair and proofcheck. proof-writer keeps only the inline applicability block,
because "cited outside its conditions" is a correctness failure that must be caught
where the proof is written.

## Required File Structure

Proof comes before any audit. The package ends with `Verification Checks` (if
provable) or `Blockage Record` (if not) — there is no `Open Risks` catch-all, because
a residual risk is a `BLOCKED` obligation, not a footnote.

```md
# Proof Package

## Claim
[exact statement]

## Status
PROVABLE AS STATED / PROVABLE AFTER WEAKENING / NOT CURRENTLY JUSTIFIED
Verification: Verified / Conditionally verified / Gap found

## Assumptions
- (A1) ...

## Notation
- ...

## Verification Target and Bottleneck
- Verification target: if [precise intermediate statement] holds, the claim follows by [named argument].
- Bottleneck: the first unresolved leaf is [specific statement].
- Resolution path: [new lemma / verify cited prerequisites / weaken claim].

## Anchors and Borrowing
- Relation to literature: [template adaptation / standard-result invocation / self-contained]
- Anchor 1: [reference], [theorem no.]. Borrowed: [...]. New: [...].
- If self-contained: fill the Implicit Machinery Disclosure (schema in proof-strategy.md).

## Proof Strategy
[chosen approach; follows from the verification target above]

## Dependency Map
1. Main claim depends on the verification target.
2. Verification target depends on O1, O2, ...
[Built backward from the claim, then forward-verified.]

## Obligation Ledger
- O1 [short label] — CLOSED-LOCAL. Closed at: Step 3, eq. (4).
- O2 [short label] — CLOSED-CITED.
  - clause used: ...
  - assumption map: (S1)←(A2); (S2)←L1
  - conclusion fit: weaker-with-bridge
  - bridge ref: B1
  - source-status: unverified-source
- O3 [short label] — BLOCKED.
  - statement: ...
  - bridge attempted: ...
  - failure reason: ...
  - alternative considered: ...
  - isolated as: Conjecture C1.

## Proof
Step 1. ...
Step 2. ...
[Bridge B1: ...]
Therefore the claim follows. ∎

## Corrections or Missing Assumptions
- [only if the claim was weakened or an assumption added]

## Verification Checks   (provable outputs only)
- One pass / NA line per Trap Catalogue item (the nine listed in Step 7). Any fail is
  fixed or the status is downgraded; a fail may not survive here.

## Blockage Record   (non-provable outputs only — replaces everything below Proof)
- Blocked obligation(s): O_k
- Exact blocker: missing lemma / invalid implication / hidden assumption / counterexample direction
- What would be needed to finish: [extra assumption, lemma, or derivation]
- Weaker claim that IS provable (if any), with its own complete proof above.
```

## Chat Response

After writing the file, respond briefly with: status and verification level, whether
the original claim survived unchanged, the count of obligations and how many are
`BLOCKED`, the linter result, and the file updated.

## Key Rules

- Never fabricate a missing step; never close an obligation with prose.
- Prefer weakening the claim over overclaiming.
- An untyped or `BLOCKED` obligation under `PROVABLE AS STATED` is a contradiction the linter will catch.
- Preserve the user's original statement unless you explicitly mark a corrected claim or internal device.
- If the statement is false as written, say so with a counterexample or a repaired statement.
- Correctness matters more than brevity; closure matters more than smoothness.
