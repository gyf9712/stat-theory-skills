---
artifact: shared_reference
scope: proof_closure_machinery
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills proof-closure machinery extracted from proof-repair v1.7.x + proofcheck v1.7.x for compactification per Codex round 2 threadId 019e70c3-1844-7181-b6a1-0b4041c657df
---

# Proof Closure Machinery

Canonical schemas for the shared verification and closure objects used by `proofcheck`, `proof-repair`, `proof-writer`, and `theory-sharpen`. Extracted from individual `SKILL.md` files so each skill loads the schemas once and references them by name, eliminating duplicated inline content.

This file holds: the severity system, verification statuses, provability triage, the Repair Priority Ladder, repair classes, the Repair Closure Matrix schema, the Weaken-Claim and Assumption-Extension Change Log schemas, the Repair Ladder Defense block, the Repair Ladder Summary table, and the Hard-Gate Completion Rule.

## When to Read

- During `proofcheck` Pass 0 (when assigning severities to detected issues).
- During `proof-repair` Step 1 (issue triage and class selection).
- During `proof-repair` Step 3 (Repair Priority Ladder enforcement).
- During `proof-repair` Step 7 (REPAIR_PLAN.md construction).
- During `/proofcheck --post-repair` (when reading the Closure Matrix and Change Logs to verify convergence).
- During `proof-writer` whenever a chosen claim is downgraded (verification status transition).

## Severity System (shared between proofcheck and proof-repair)

| Level | Meaning | Examples |
|-------|---------|---------|
| `S0` | Fatal — main theorem does not follow | Circular dependency, wrong inequality direction in critical chain |
| `S1` | Major — missing assumption or step, likely repairable | Hidden invertibility assumption, missing log factor |
| `S2` | Moderate — local ambiguity, may not affect final result | Unclear quantifier scope, uncited intermediate step |
| `S3` | Minor — typo, notation, reference | Missing label, inconsistent symbol |

## Verification Statuses

Applied to a proof unit at any point in the audit / repair / re-audit cycle.

- `Verified` — all dependencies checked, logic sound
- `Conditionally verified` — correct IF listed dependencies hold
- `Gap found` — specific missing step identified
- `Incorrect` — error found
- `Not checked` — not yet examined

## Provability Triage

Before deep-checking any unit, triage its provability. This prevents wasting effort on units where the claim is fundamentally flawed.

| Status | Meaning | Action |
|--------|---------|--------|
| `PROVABLE AS STATED` | Claim follows from listed assumptions | Proceed with full verification |
| `PROVABLE AFTER WEAKENING` | Needs extra assumption or narrower claim | Record gap, verify the weakened version |
| `NOT CURRENTLY JUSTIFIED` | No clear path to a valid proof | Write blockage report, skip deep-check |

Used by `proofcheck` Pass 0 and by `proof-repair` for every candidate repair (the candidate's feasibility triage).

## Repair Classes

The mechanism used to implement a repair. Each repair file declares one chosen class.

| Class | When to use | Needs literature? |
|-------|-------------|-------------------|
| `Add-Assumption` | Proof uses unstated condition | Yes — find papers with similar assumption or weaker alternative |
| `Weaken-Claim` | Theorem claims more than proved | Maybe — find if stronger result exists elsewhere. **MANDATORY**: produce a Weaken-Claim Change Log entry (see schema below). |
| `Strengthen-Proof` | Gap in reasoning, but claim is likely true | Yes — find technique/lemma to fill the gap |
| `Insert-Lemma` | Missing intermediate step | Yes — may exist as known result in literature |
| `Fill-Skipped-Steps` | Author skipped intermediate steps; proofcheck flagged NONTRIVIAL or UNRECONSTRUCTIBLE jumps | Sometimes — TRIVIAL/VERIFIABLE need no refs, NONTRIVIAL may need a named technique, UNRECONSTRUCTIBLE may need new lemma + refs |
| `Expand-Sketch-to-Proof` | proofcheck flagged the unit as `SKETCH-ONLY` or `PARTIAL-SKETCH` | Often — sketches usually rely on cited techniques that need to be properly invoked with prerequisites verified |
| `Replace-Technique` | Current technique fundamentally flawed | Yes — find alternative proof strategy |
| `Fix-Constants` | Rates, bounds, or constants wrong | Maybe — check if correct constants known |
| `Fix-Quantifiers` | Pointwise↔uniform, ∀∃ order, etc. | Maybe — find uniform versions of cited results |
| `Notation-Fix` | Symbol drift, type mismatch | No |
| `Citation-Fix` | External theorem misapplied | Yes — find correct version or alternative theorem |

`Expand-Sketch-to-Proof` is orthogonal to the ladder: an expanded sketch may land at any ladder level depending on what the full proof actually requires.

## Repair Priority Ladder (Phase A / B / C, L1-L6)

Before generating candidate repairs, classify each candidate by **ladder level** and by **repair class**. The ladder level is how invasive the repair is with respect to the theorem's semantics; the repair class is the mechanism.

The ladder is mandatory and enforced.

### Phase A: Claim-preserving and assumption-preserving repairs only

Exhaust the relevant branches in Phase A before allowing any semantic edit.

- **L1. Internal correction**: fix a local logical error, omitted step, citation misuse, constant slip, quantifier slip, or proof gap without changing the claim, the assumptions, or the proof's dependency scope in any substantive way.
- **L2. Supporting lemma from existing assumptions**: add a helper lemma or intermediate proposition proved entirely from the existing assumption set; the main theorem statement and its assumptions remain unchanged.
- **L3. Alternative proof technique under existing assumptions**: replace the proof route, decomposition, or imported theorem while still proving the same claim from the same assumptions.

There is **no hard order between L2 and L3**. They are sibling branches within Phase A. Consider the **relevant** Phase A branches for the issue at hand; do not mechanically force all branches when some are plainly irrelevant.

### Phase B: Semantic edits, allowed only after documented Phase A exhaustion

A repair may enter Phase B only if the per-issue repair file contains a **Phase A exhaustion record** showing why the relevant claim-preserving branches did not work.

- **L4. Add assumption**: introduce the minimal defensible additional assumption that makes the original claim provable.
- **L5. Weaken claim**: replace the original claim with the strongest claim that the existing assumptions, or the chosen repaired assumption set, honestly support.

There is **no universal order between L4 and L5**. Choose based on mathematical necessity and scientific-scope impact. A stronger assumption that preserves the headline theorem is not automatically preferable to a weaker theorem under the original assumptions. A heavy-tail paper that adds sub-Gaussian to preserve the original rate is often worse than a weaker rate under the original tail assumption.

### Phase C: Terminal failure

- **L6. Blockage / NOT CURRENTLY JUSTIFIED**: no honest repair works.

### Mapping from ladder level to repair class

| Ladder level | Primary repair classes |
|---|---|
| L1 | Strengthen-Proof (inline fix), Fill-Skipped-Steps, Citation-Fix, Fix-Constants, Fix-Quantifiers |
| L2 | Insert-Lemma (or Strengthen-Proof when the helper stays inline) |
| L3 | Replace-Technique (or Strengthen-Proof when the new route is closely related to the old) |
| L4 | Add-Assumption |
| L5 | Weaken-Claim |
| L6 | Blockage report |

### Hard enforcement rule

`proof-repair` may not mark an `L4` or `L5` candidate as the chosen repair unless the per-issue repair file includes:

1. the chosen ladder level,
2. the chosen repair class,
3. whether the claim is preserved,
4. whether the assumptions are preserved,
5. a Phase A exhaustion record for the relevant lower-level branches.

For `L4`, the repair must also include an `Assumption-Extension Change Log` entry. For `L5`, the repair must also include a `Weaken-Claim Change Log` entry. A Phase B repair without these artifacts is invalid and must be demoted to `NOT CURRENTLY JUSTIFIED`.

## Repair Closure Matrix Schema

Canonical record of issue closure. Lives in `REPAIR_PLAN.md`. Each row tracks one original issue from `audit/06_reports/issue_log.md` from issue identification through post-repair verification. `/proofcheck --post-repair` reads this matrix to verify convergence.

```markdown
## Repair Closure Matrix

| Issue ID | Original severity | Unit | Repair class | Patch ID | Touched units | Closure status | Post-repair status | Downstream affected units |
|---|---|---|---|---|---|---|---|---|
| I-01 | S0 | Lemma C.3 | Add-Assumption | Patch 1 | Lemma C.3 + assumption block | DESIGNED | (set by re-audit) | Thm 2.1, Cor 2.2, Sec 5 |
| I-02 | S1 | Thm 3.1 | Weaken-Claim | Patch 5 | Thm 3.1, intro | DESIGNED | (set by re-audit) | Cor 3.2 |
| I-03 | S1 | Prop B.2 | Insert-Lemma | Patch 3 | Prop B.2 + new Lemma B.5 | DESIGNED | (set by re-audit) | Lemma B.4, Thm 4.1 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |
```

**Closure status** (set by `proof-repair` when designing the repair):

- `DESIGNED` — repair strategy specified, patch written, complete proof drafted, Codex per-repair stress-test passed
- `DEFERRED` — repair postponed (user decision); paper carries the unrepaired issue forward
- `BLOCKAGE` — repair impossible; theorem downgraded to NOT CURRENTLY JUSTIFIED with a blockage report

**Post-repair status** (set by `/proofcheck --post-repair`; blank until re-audit runs):

- `CLOSED-VERIFIED` — re-audit confirms the unit now passes verification under the revised claim
- `CLOSED-WEAKENED` — the original claim was unprovable; the patch weakened it, and the weakening is documented in PATCHES.md and propagated to every downstream unit listed in the matrix
- `CLOSED-BLOCKAGE` — the unit could not be repaired; the patched paper downgrades it; all downstream consumers are also downgraded or removed
- `STILL-OPEN` — the patch did not actually close the issue (re-audit failure)
- `WAIVED` — explicitly waived by the user with documented rationale (allowed for S2/S3, almost never for S0/S1)

### Closure Matrix completeness rule

Every issue in `06_reports/issue_log.md` must have a row. Issues without a row are treated as `STILL-OPEN` by the re-audit. If `proof-repair` chooses to ignore an issue (rare, only for S3), the row still exists with closure status `DEFERRED` and a rationale.

## Weaken-Claim Change Log Schema

**MANDATORY** when any repair is class `Weaken-Claim` (ladder L5). Lives in REPAIR_PLAN.md AND in the per-unit repair file at `audit/07_repairs/section_*/*_repair.md`. `/proofcheck --post-repair` reads this log to distinguish intentional semantic changes from defects.

```markdown
## Weaken-Claim Change Log

| Patch ID | Original claim (verbatim) | Revised claim (verbatim) | Reason for weakening | Downstream impact (units that consumed the original strength) |
|---|---|---|---|---|
| Patch 5 | "$\hat\theta_n - \theta^* = O_P(n^{-1/2})$ for all $\theta^* \in \Theta$" | "$\hat\theta_n - \theta^* = O_P(n^{-1/2} \log n)$ for all $\theta^* \in \Theta$" | Original proof used a chaining argument that did not yield the parametric rate; the $\log n$ factor is the tight rate under the stated assumptions. See `07_repairs/section_3/thm_3_1_repair.md`. | Cor 3.2 (rate restated as $O_P(n^{-1/2} \log n)$); Sec 5 abstract / introduction (rate now stated with the log factor); rate comparison table updated. |
```

The `Downstream impact` column is the propagation contract. Every listed unit must have a corresponding patch in PATCHES.md that updates the consumer. A Weaken-Claim repair without this log is treated as `NOT CURRENTLY JUSTIFIED` and demoted to a blockage report. There is no third path: either the weakening is documented + propagated, or the theorem is downgraded.

The re-audit treats an unpropagated downstream consumer as `NEW-S0` (the patched paper now has a corollary or application that silently overstates what the weakened theorem actually delivers).

## Assumption-Extension Change Log Schema

**MANDATORY** when any repair is class `Add-Assumption` (ladder L4). Analogous to the Weaken-Claim Change Log; for assumption changes rather than claim changes. Lives in the per-unit repair file at `audit/07_repairs/section_*/*_repair.md`.

```markdown
## Assumption-Extension Change Log

| Issue ID | Original assumption set | Added assumption (verbatim) | Natural weaker variant considered | Why the weaker variant fails | Scientific-scope impact | Propagation to downstream theorems/lemmas |
|---|---|---|---|---|---|---|
| I-01 | [list the original assumptions exactly as used by the repaired unit] | [state the new assumption exactly as added to the theorem / lemma / assumption block] | [state at least one natural weaker alternative that was considered] | [give the concrete blocking reason: which step still fails, which theorem remains inapplicable, or which counterexample direction survives] | [describe how the new assumption changes the paper's regime, applicability, model class, tail condition, dependence structure, or rate interpretation] | [list every downstream lemma, theorem, corollary, application, abstract sentence, or introduction claim that now depends on the added assumption; for each, name the patch ID or repair file that propagates the change] |
```

The "Natural weaker variant considered" column is the **local-minimality defense**. The author does not need to prove global minimality (usually impossible) but does need to show that one obvious weakening of the added assumption was tried and rejected with a concrete reason. Without this, the audit treats the added assumption as overstrengthening.

## Repair Ladder Defense Block

Every per-issue repair file MUST contain a `## Repair Ladder Defense` block documenting the ladder discipline decision.

```markdown
## Repair Ladder Defense

- Chosen ladder level: [L1 / L2 / L3 / L4 / L5 / L6]
- Chosen repair class: [Strengthen-Proof / Insert-Lemma / Replace-Technique / Add-Assumption / Weaken-Claim / Fill-Skipped-Steps / Citation-Fix / Fix-Constants / Fix-Quantifiers / Expand-Sketch-to-Proof / Blockage]
- Claim preserved: [yes / no]
- Assumptions preserved: [yes / no]

### Phase A Exhaustion Record
Record only the **relevant** lower-level branches. Do not fabricate attempts for irrelevant branches.

| Branch | Tried? | Concrete attempt | Specific obstacle | Why the obstacle is genuine | Verdict |
|---|---|---|---|---|---|
| L1 Internal correction | [yes / no / not relevant] | [exact local rewrite, skipped-step fill, citation correction, constant fix, etc.] | [what failed] | [counterexample, contradiction, theorem mismatch, dependency failure, or formal blocking issue] | [ruled out / succeeded / not relevant] |
| L2 Supporting lemma | [yes / no / not relevant] | [candidate helper lemma from existing assumptions] | [what failed] | [why the lemma cannot be proved from the current assumptions, or why it is insufficient] | [ruled out / succeeded / not relevant] |
| L3 Alternative technique | [yes / no / not relevant] | [named alternative proof route, theorem, or decomposition] | [what failed] | [why the alternative route still cannot prove the original claim under current assumptions] | [ruled out / succeeded / not relevant] |

### Phase B Justification
Required only for `L4` or `L5`.

- Why Phase A did not close the issue: [one concise paragraph]
- Why this semantic edit was chosen over the other Phase B option:
  - If chosen level is `L4`: explain why adding an assumption is scientifically preferable to weakening the claim here.
  - If chosen level is `L5`: explain why weakening the claim is scientifically preferable to strengthening the assumptions here.

### Semantic-Edit Log Pointer
- If chosen level is `L4`: `Assumption-Extension Change Log` row pointer: [Issue ID / row reference]
- If chosen level is `L5`: `Weaken-Claim Change Log` row pointer: [Patch ID / row reference]
- Otherwise: [NA]

### Blockage Pointer
Required only for `L6`.

- Blockage report: [path / section pointer]
```

## Repair Ladder Summary Table

Paper-level summary of how each issue satisfied the ladder discipline. Lives in REPAIR_PLAN.md. The full defense lives in the per-issue repair file's Repair Ladder Defense block.

```markdown
## Repair Ladder Summary

| Issue ID | Unit | Chosen repair class | Chosen ladder level | Claim preserved? | Assumptions preserved? | Escalation justified? | Pointer to per-issue defense |
|---|---|---|---|---|---|---|---|
| I-01 | Lemma C.3 | Insert-Lemma | L2 | yes | yes | NA | `audit/07_repairs/section_C/lemma_C_3_repair.md` |
| I-02 | Thm 3.1 | Add-Assumption | L4 | yes | no | yes | `audit/07_repairs/section_3/thm_3_1_repair.md` |
| I-03 | Cor 4.2 | Weaken-Claim | L5 | no | yes | yes | `audit/07_repairs/section_4/cor_4_2_repair.md` |
```

Use `Escalation justified? = yes` only when the required Phase A exhaustion record exists and the relevant semantic-edit log entry is present. For Phase A repairs (L1-L3), this column is `NA`.

`/proofcheck --post-repair` cross-checks this summary against the per-issue Repair Ladder Defense blocks and the Assumption-Extension Change Log / Weaken-Claim Change Log entries. Inconsistencies are flagged as audit findings.

## Hard-Gate Completion Rule for REPAIR_PLAN.md

`REPAIR_PLAN.md` is marked `complete` only when ALL of the following are true:

1. Every original issue has a row in the Repair Closure Matrix with a terminal `Closure status` (`DESIGNED`, `DEFERRED`, or `BLOCKAGE`); no row is blank or in-progress.
2. Every Weaken-Claim repair has a row in the Weaken-Claim Change Log, including the downstream impact propagation list.
3. Every Add-Assumption repair has a row in the Assumption-Extension Change Log, including the natural weaker variant considered and the propagation list.
4. Every per-issue repair file has a Repair Ladder Defense block; L4/L5 repairs include Phase A Exhaustion Record + Phase B Justification + Semantic-Edit Log Pointer.
5. Outstanding sketches = 0 in the Sketch Expansion Tracker.
6. Every P0/P1 repair has passed the per-repair Codex stress-test (status `PASS` or `Confirmed after revision`); see `CODEX_PROTOCOL.md` Per-Repair Fresh Thread protocol.
7. The Consistency Verification checklist is fully checked.
8. **If the original audit contained any S0 or S1 issue**: `/proofcheck --post-repair` has been invoked AND `audit/08_post_repair/CONVERGENCE_VERDICT.md` reports `CONVERGED`. This is a HARD GATE — the plan cannot be marked complete without it.
9. **If the original audit contained only S2 and S3 issues**: `/proofcheck --post-repair` is strongly recommended but not a hard gate. The plan can be marked complete without it, but the executive summary must explicitly state `Convergence status: NOT YET RE-AUDITED (S2/S3-only — re-audit recommended but not required)`.

If any condition fails, the plan status is `IN-PROGRESS` and the skill reports which conditions remain unmet.

## Honest Limits

- The schemas above are templates. Specific repair workflow details (Step 1 issue triage, Step 4 literature search, Step 5 candidate generation) remain in the individual `SKILL.md` files because they are skill-specific orchestration.
- The Repair Closure Matrix and Change Logs are documentation contracts, not verification proofs. They make verification possible by `/proofcheck --post-repair`; they do not replace it.
- The Hard-Gate Completion Rule is mechanically enforced by `proof-repair` checking the schema instances exist; it cannot enforce that the schemas were filled honestly. Honest filling is the author's responsibility, with `/proofcheck --post-repair` as the verifier.

## Cross-Reference

- `CODEX_PROTOCOL.md` — Per-Repair Fresh Thread protocol (consumed by Closure Matrix's "post per-repair stress-test" requirement)
- `citation-purpose-protocol.md` — cited results in repair files use the citation-purpose schema
- `literature-cache-protocol.md` — every new reference in repair_references.bib resolves to a cache entry
- `proof-strategy.md` — proof-writer's Verification Target / Bottleneck / Trap Catalogue feeds the repair candidates and the Repair Ladder Defense Phase A Exhaustion Record
