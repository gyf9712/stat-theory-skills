# Codex Dialogue: proof-writer strategy improvements

**Date:** 2026-05-28
**threadId:** `019e6fe3-9a34-70e2-942b-ab8343e491d4`
**Model:** gpt-5.4 at `model_reasoning_effort: xhigh`
**Topic:** how proof-writer finds proof strategies

## Background

The proof-writer skill enforces honesty (no sketches, no hand-waving, no fabrication) but Step 4 says "choose a strategy" with a flat menu (direct, contradiction, induction, construction, reduction, coupling, optimization inequality chaining). The skill does not say HOW to choose. Most of the strategy-finding work was implicitly delegated to the underlying model.

The goal of this dialogue was to make the strategy-finding step explicit and statistics-specific, mirroring the senior-statistician move of "choose the battlefield before doing algebra."

## What converged

Three rounds, mostly converged after round 3. The key changes:

### 1. New step 3.5: Locate the Verification Target and Bottleneck

Inserted between Feasibility Triage (Step 3) and the Dependency Map (Step 4). The output is a three-line artifact in the proof package:

- **Verification target**: the precise intermediate statement whose verification closes the claim under the chosen reduction (theorem-specific, not a slogan)
- **Bottleneck**: the first unresolved leaf (specific inequality, localization claim, entropy bound, invertibility step, prerequisite of a cited theorem)
- **Resolution path**: how to break the bottleneck

Codex initially called this a "proof certificate" but agreed to drop the term after I pushed back: "certificate" has specific meanings in optimization (Farkas) and complexity theory (polynomial-time verifier) that do not match how senior statisticians talk. The replacement term `verification target` is plain English and matches actual usage.

### 2. Dependency Map: backward-first, forward-verified

Codex's improvement on my draft. Build the map by:
- Backward chaining from the claim until leaves are assumptions, verified prerequisites of cited theorems, or isolated new lemmas
- Forward pass from the leaves to verify they actually support what they claim to

A purely backward map can produce subgoals that look plausible but do not hold; the forward pass catches that.

### 3. Anchor disclosure with three flavors

Three relations of a proof to the literature, each with its own discipline:

- **Template adaptation**: identify 1-3 closest anchors, name their proof spine, separate borrowed from new
- **Standard-result invocation**: name the theorem, list its prerequisites, verify each
- **Self-contained**: requires explicit Implicit Machinery Disclosure (most claimed self-contained proofs are actually using mature machinery the author has internalized)

Codex agreed (after my pushback) that "self-contained" without disclosure is too lenient. The distinction *paper-self-contained* (only enumerated graduate-core facts) vs *locally self-contained* (no prior paper imported wholesale, but mature machinery used implicitly) is now in the shared reference.

### 4. Trap Catalogue with diagnostic tests

Seven named middle-regime traps, each with a one-line ctrl-F-able diagnostic:

1. Localization-before-expansion
2. Wrong norm / wrong mode
3. Good-event bookkeeping
4. Rate leakage
5. Quantifier inflation
6. Imported-theorem prerequisite drift
7. Boundary / singularity

Codex initially gave names without tests; I pushed back that naming alone is not a defense. The current version has both, with the diagnostic phrased mechanically (search for X, check Y).

### 5. Shared reference file

`stat-shared-references/proof-strategy.md` (new). Contains:

- Claim Families → Verification Targets (the canonical map)
- Anchor Selection and Comparison
- Implicit Machinery Disclosure
- Assumption Budget and Propagation
- Norm / Mode / Quantifier Checklist
- Localization and Good-Event Bookkeeping
- Imported Theorem Prerequisite Audit
- Trap Catalogue with Diagnostic Tests
- High-Dimensional Regularization Patterns
- Asymptotic Linearity / M-Estimation Patterns
- Empirical Process / Concentration / Chaining Patterns
- Lower Bounds and Bayesian Asymptotics

Shared between `proof-writer` (consults at write time) and `proof-repair` (consults at repair time). Codex agreed to share via reference rather than duplicating content in two skill bodies.

## Where I pushed back on Codex

### Push 1: "Proof certificate" terminology — Codex withdrew

Codex initially used "proof certificate" as core terminology. I noted that the term has specific meanings in optimization (Farkas certificate) and complexity theory (polynomial-time-verifiable witness) that do not match statistics usage, and asked for two worked examples to prove the term generalizes.

Codex withdrew the term: "`Proof certificate` is not standard statistics language. I would not put that term into the skill." Replaced with `verification target`. The two examples (Bickel-Ritov-Tsybakov LASSO cone + RE, M-estimator asymptotic linear representation) work cleanly with the replacement term.

### Push 2: Trap catalogue needs diagnostics, not just names

Codex's first version listed seven traps by name and description. I pushed back: "Naming alone is not a defense. Each trap needs a one-line diagnostic test, not just a description, so the polisher can mechanically check."

Codex agreed and produced ctrl-F-able diagnostics for each trap. The current version is mechanical enough for a PhD student to apply.

### Push 3: Self-contained claims need defense

Codex initially said "if no close anchor exists, say so explicitly." I said this was too lenient — most "self-contained" proofs are actually using machinery the author has internalized and stopped citing.

Codex agreed and proposed the *paper-self-contained vs locally self-contained* distinction, plus the Implicit Machinery Disclosure block requiring authors to enumerate the mature machinery, the background a strong PhD student would need, and what is re-proved here.

## Where I held the line

### Citation accountability

Codex's second reply cited three sources: Bickel-Ritov-Tsybakov (AoS 2009), Basu-Ghosh (JASA 1980), Hall et al. (arXiv 1202.5183).

Bickel-Ritov-Tsybakov AoS 2009 is the canonical LASSO + RE paper and matches what it was sourcing. The other two were unclear — I could not tell what they were sourcing, and the format looked like padding.

I called this out in round 3: "Per our dialogue discipline, when you cite a specific paper, theorem, or constant, the burden is on the citation to be checkable. Drop unclear citations rather than padding the list."

Codex agreed: "In my previous reply, only Bickel-Ritov-Tsybakov was doing real work. Ignore the other two."

This is a clean instance of the dialogue principle from `stat-codex-dialogue.md`: Codex is reliably right on patterns, less reliable on specific citations. Verify what is verifiable, drop what is not.

## Outstanding items (not resolved in this dialogue, deferred to roadmap)

- Whether the new step 3.5 should be a separate slash command (`/locate-verification-target`) that proof-writer calls, or remain inline. Codex did not have a strong view.
- Whether `proof-repair` should also gain a Verification Target section in `REPAIR_PLAN.md`, mirroring the proof-writer step. Probably yes; deferred.
- Whether the trap-catalogue diagnostics should be exposed as a standalone `/trap-audit` command for use on existing proofs. Deferred.

## Final architecture

```
proof-writer workflow (updated):
  Step 1: Gather Proof Context
  Step 2: Normalize the Claim
  Step 3: Feasibility Triage
  Step 3.5: Locate the Verification Target and Bottleneck  ← NEW
  Step 4: Build a Dependency Map (backward-first, forward-verified)
  Step 5: Write the Proof Document
  Step 6: Final Verification (now includes 7 trap diagnostics)

Proof package structure (updated):
  ## Claim
  ## Status
  ## Assumptions
  ## Notation
  ## Verification Target and Bottleneck   ← NEW
  ## Anchors and Borrowing                  ← NEW
  ## Implicit Machinery Disclosure          ← NEW (if self-contained)
  ## Proof Strategy
  ## Dependency Map
  ## Proof
  ## Corrections or Missing Assumptions
  ## Open Risks (with trap-catalogue results)

Shared with proof-repair:
  stat-shared-references/proof-strategy.md  ← NEW
```

The Codex thread remains open for resumption at `019e6fe3-9a34-70e2-942b-ab8343e491d4` if these items need to be re-engaged.
