---
name: proof-repair
description: >-
  Generate self-consistent repair plans for mathematical proof issues found by /proofcheck,
  with literature-backed support. For each problematic assumption, model, proposition, or
  theorem, proposes fixes that preserve the full dependency chain and searches arXiv,
  Semantic Scholar, and Google Scholar for new references to support repairs.
  Use when user says "repair proofs", "fix proof issues", "修复证明", "proof repair",
  "修正计划", "fix theorem", "repair assumptions", or wants to go from proof audit to
  actionable repair plan with literature support.
argument-hint: [path-to-paper-dir or path-to-audit-dir]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, WebSearch, WebFetch, mcp__codex__codex, mcp__codex__codex-reply
model: opus
---

# Proof-Repair — Literature-Backed Repair Plans for Mathematical Proofs

> 🔬 **Model Recommendation**: Run this skill on **Claude Opus** for best results.
> Repair design + literature verification requires deep reasoning. If your session is
> not on Opus, run `/model opus` before invoking. Heavy reasoning (literature search,
> verification, full proof writing) will use Opus sub-agents.

Takes a `/proofcheck` audit (or a raw .tex file with known issues) and produces
self-consistent repair plans with new literature references for every fixable issue.

**Pipeline position**:
```
/proofcheck → [THIS SKILL] → /proof-writer
  Find issues    Fix + literature    Write complete proofs
```

**Upstream**: `/proofcheck` (produces audit/ with provability triage + blockage reports)
**This skill**: audit/ → REPAIR_PLAN.md + patched .bib + per-unit repair files
**Downstream**: `/proof-writer` (writes complete corrected proofs for each repair)

**Register for any proof text this skill writes.** Full-proof creation delegates to
`/proof-writer`, which carries the register. But LaTeX patches this skill writes
directly (Fill-Skipped-Steps, Insert-Lemma, inserted derivations) must follow the same
Big Four register: key steps on display lines, connectives naming the logical move
(displays carry the *what*, connectives the *why*), no walls of undisplayed algebra, no
`Step 1 / Step 2` bulletization. Single source of truth: the "Mathematical Register and
Readability (Big Four)" section of `../stat-shared-references/stat-theory-writing.md`. A
repair must not fix correctness while regressing readability.

## Context: $ARGUMENTS

---

## 0. Locate Inputs

Parse `$ARGUMENTS` to find the paper workspace.

```
Expected structure (created by /proofcheck):
papers/<paper-name>/
  paper.tex
  CHECK_PLAN.md
  EXECUTION_ORDER.md
  audit/
    01_index/theorem_inventory.md
    02_ledgers/{notation,assumption,constants}_ledger.md
    03_dependencies/dependency_graph.md
    04_local_checks/section_*/*_check.md
    05_adversarial/{hidden_assumptions,counterexamples}.md
    06_reports/{issue_log.md, FINAL_REPORT.md}
```

Read these files in order:
1. `audit/06_reports/FINAL_REPORT.md` — executive summary, all open issues
2. `audit/06_reports/issue_log.md` — detailed issue list with severity
3. `audit/03_dependencies/dependency_graph.md` — what depends on what
4. `audit/02_ledgers/assumption_ledger.md` — all assumptions and their scope
5. `CHECK_PLAN.md` — proof architecture understanding

If no audit/ exists, tell the user to run `/proofcheck` first, or offer to run a
lightweight inline check on the specific unit they point to.

**New in v2**: Also read provability triage and blockage reports from local check files:
- Units marked `PROVABLE AFTER WEAKENING` → pre-classify as Weaken-Claim repair
- Units marked `NOT CURRENTLY JUSTIFIED` → pre-classify as Replace-Technique or blockage
- `Candidate literature` hints from blockage reports → seed the literature search (Step 4)

### 0B. Detect Reference Mode (HARD GATE before any LaTeX patch)

Run `../stat-shared-references/scripts/proof_index.py` and record the reported `reference_mode` in
`REPAIR_PLAN.md`. In Mode B (two-file main + supplement, standard at JASA / AoS /
Biometrika / JRSS-B) `
ef{}` does not resolve across files, so every cross-file
citation must be a hard-coded number ("Lemma S.3", "Theorem 2.1 of the main text").

Modes, detection, the record format, and patch-renumbering discipline:
`../stat-shared-references/reference-mode-protocol.md`.

No LaTeX patch may be written before the mode is recorded. Every patch in Step 7
must respect it, and a post-patch `cross_file_ref_leak` is a patch defect.

---

## 1. Issue Triage & Repair Classification

Read ALL issues from `issue_log.md` and each `04_local_checks/` file. Build a
**Repair Triage Table**:

```markdown
| Issue ID | Severity | Unit | Issue Type | Repair Class | Downstream Impact | Priority |
|----------|----------|------|------------|-------------- |-------------------|----------|
| I-01 | S0 | Lemma C.3 | Hidden assumption | Add-Assumption | Thm 2.1, Cor 2.2 | P0 |
| I-02 | S1 | Thm 3.1 | Rate mismatch | Weaken-Claim | Final theorem | P0 |
| I-03 | S1 | Prop B.2 | Missing step | Insert-Lemma | Lemma B.4 | P1 |
| I-04 | S2 | Def 2.3 | Notation drift | Notation-Fix | 5 units | P2 |
```

### Repair Classes (choose one per issue)

| Class | When to use | Needs literature? |
|-------|-------------|-------------------|
| **Add-Assumption** | Proof uses unstated condition | Yes — find papers with similar assumption or weaker alternative |
| **Weaken-Claim** | Theorem claims more than proved | Maybe — find if stronger result exists elsewhere. **MANDATORY**: produce a Weaken-Claim Change Log entry per the schema in `../stat-shared-references/proof-closure-machinery.md` (5 columns: Patch ID, Original claim verbatim, Revised claim verbatim, Reason for weakening, Downstream impact). Without the log entry, `/proofcheck --post-repair` will flag this as `NEW-S0` (undocumented semantic change). |
| **Strengthen-Proof** | Gap in reasoning, but claim is likely true | Yes — find technique/lemma to fill the gap |
| **Insert-Lemma** | Missing intermediate step | Yes — may exist as known result in literature |
| **Fill-Skipped-Steps** | Author skipped intermediate steps; proofcheck flagged NONTRIVIAL or UNRECONSTRUCTIBLE jumps | Sometimes — TRIVIAL/VERIFIABLE need no refs, NONTRIVIAL may need a named technique, UNRECONSTRUCTIBLE may need new lemma + refs |
| **Expand-Sketch-to-Proof** | proofcheck flagged the unit as `SKETCH-ONLY` or `PARTIAL-SKETCH` (entire proof body is outline, not rigorous derivation) | Often — sketch usually relies on cited techniques that need to be properly invoked with prerequisites verified. The "expansion" is the entire proof; literature support helps confirm cited techniques apply |
| **Replace-Technique** | Current technique fundamentally flawed | Yes — find alternative proof strategy |
| **Fix-Constants** | Rates, bounds, or constants wrong | Maybe — check if correct constants known |
| **Fix-Quantifiers** | Pointwise↔uniform, ∀∃ order, etc. | Maybe — find uniform versions of cited results |
| **Notation-Fix** | Symbol drift, type mismatch | No |
| **Citation-Fix** | External theorem misapplied | Yes — find correct version or alternative theorem |

### Expand-Sketch-to-Proof (SKETCH-ONLY / PARTIAL-SKETCH units)

**Hard priority.** A unit flagged `SKETCH-ONLY` or `PARTIAL-SKETCH` by `/proofcheck` is
automatically P0, whatever its other severity. A sketch is not a low-quality proof; it is
the *absence of verification*. Other issues correct something that exists; here the proof
must be created, and until it exists the theorem is unsupported.

Extract the sketch's intended outline, then hand the claim plus that outline to
`/proof-writer` for a complete proof (its termination rule refuses to return another
sketch). Verify the result concludes the original claim exactly, uses no smuggled
assumption, and cites a canonical reference for each nontrivial technique — if the sketch
said "similar to [Z]", the adaptation is written out, not pointed at. Re-audit via
`/proofcheck`. Distinct from Fill-Skipped-Steps, which fills isolated gaps in an
otherwise rigorous proof.

**Terminal states — exactly two.** `EXPANDED` (full proof written, re-classified COMPLETE)
or `BLOCKAGE` (report explaining why it cannot be expanded; the theorem is downgraded to
`NOT CURRENTLY JUSTIFIED`). "Partially expanded" and "deferred to revision" are not
terminal states. `REPAIR_PLAN.md` cannot be marked complete while any sketch is
unexpanded; its Sketch Expansion Tracker (one row per unit: unit, sketch class, expansion
state, final status) must show `Outstanding sketches: 0`.

Common reclassifications, none of which relax the expansion requirement: the sketch was
hiding an unprovable claim (→ BLOCKAGE, valid terminal); the cited technique does not
apply (→ Replace-Technique, then expand the alternative); expansion reveals a missing
assumption (→ Add-Assumption, then expand under it).

### Fill-Skipped-Steps repair workflow (special handling)

This class handles skips identified by `/proofcheck`'s Step Completeness Audit.
Workflow varies by the skip's classification:

**VERIFIABLE skips (S3)**:
- Re-verify proofcheck's reconstruction is correct
- Write out the 2-5 intermediate steps explicitly
- LaTeX patch: insert the steps between the existing equations
- No literature needed — uses standard manipulations only

**NONTRIVIAL skips (S1)**:
- Identify the non-obvious bridging idea
- If it's a named technique (e.g., Sherman-Morrison, dominated convergence,
  Borel-Cantelli), cite the standard reference
- If it's a problem-specific lemma, write it as a new lemma (via /proof-writer)
- LaTeX patch: insert either the cited bridging step or the new lemma + its use

**UNRECONSTRUCTIBLE skips (S0)**:
- Treat as a genuine gap — do NOT manufacture a bridge
- Investigate whether:
  (a) the original proof is wrong (the jump doesn't actually hold)
  (b) the original proof uses an unstated assumption (→ Add-Assumption repair)
  (c) a different proof technique is needed entirely (→ Replace-Technique)
- If still unable to bridge after literature search, write a Blockage Report
  and recommend the author either provide the bridge or weaken the claim

### Priority Rules

- **P0**: S0 issues + any S1 issue on the critical path to main theorem
- **P1**: S1 issues not on critical path + S2 issues affecting ≥3 downstream units
- **P2**: Remaining S2 + all S3

---

## 2. Dependency Impact Analysis

For each P0 and P1 issue, trace the **full downstream impact** using the dependency graph:

```markdown
## Impact Analysis: {ID} — {unit and issue}

### Direct dependents
[units using this unit's conclusion directly]
### Transitive dependents
[units downstream of those, to the paper's applications]
### Repair constraint
[what any fix must preserve: assumption strength promised in the intro, the stated
rate, constant universality]
### Cascading repairs needed?
[which dependents must be re-verified if this changes]
```

A worked, filled analysis:
`../stat-shared-references/examples/repair-specification-example.md`.

Build a **Repair Dependency DAG**: some repairs must happen before others (e.g., fixing
a base lemma assumption before fixing the theorem that uses it).

---

## 3. Enforce the Repair Priority Ladder (HARD GATE)

Before generating candidate repairs, classify each candidate by **ladder level** and by **repair class**. The full ladder definition (Phase A / B / C, L1-L6), the mapping from levels to repair classes, the sibling-not-ordered rules for L2/L3 and L4/L5, and the hard enforcement requirements all live in `../stat-shared-references/proof-closure-machinery.md` under "Repair Priority Ladder".

Operational summary for this step:

1. For each issue from Step 1, identify the relevant Phase A branches (L1 internal correction / L2 supporting lemma / L3 alternative technique). Attempt them with concrete candidate sketches.
2. A candidate enters Phase B (L4 Add-Assumption or L5 Weaken-Claim) only after the per-issue repair file records a Phase A exhaustion entry for the relevant branches. The Phase A Exhaustion Record block schema is in `proof-closure-machinery.md`.
3. L4 requires an Assumption-Extension Change Log entry; L5 requires a Weaken-Claim Change Log entry. Both schemas are in `proof-closure-machinery.md`. A Phase B repair without the matching log is invalid and is demoted to L6 (Blockage / NOT CURRENTLY JUSTIFIED).
4. The chosen repair's `Repair Ladder Defense` block (schema in `proof-closure-machinery.md`) must be written into the per-issue repair file before the repair is admitted to Step 5 (Complete-Proof Writing).

`/proofcheck --post-repair` enforces all of the above by checking the schema instances on the patched paper.

---

## 3B. Generate Candidate Repairs (per issue)

For each issue, generate 1-3 candidate repair strategies, each typed with a **ladder level** in addition to invasiveness:

```markdown
## Repair Candidates: {ID} — {unit and issue}

### Candidate {A/B/C}: {one-line description} (Ladder level: L{n} / invasiveness: {LOW|MEDIUM|HIGH})
- Repair class: {class}
- Fix: {what changes, precisely}
- Assumptions touched: {none / which, and whether strengthened}
- Downstream impact: {units affected}
- Literature needed: {yes/no, what}
- Feasibility: {PROVABLE AS STATED / AFTER WEAKENING / NOT CURRENTLY JUSTIFIED}
```

A worked, filled set of candidates:
`../stat-shared-references/examples/repair-specification-example.md`.

Note that Candidate A above is `L4` (Phase B). If Candidate B (`L2`) or C (`L3`) reaches `PROVABLE AS STATED`, the ladder rule requires choosing B or C over A; A may be selected only with a documented Phase A exhaustion record.

### Repair Quality Criteria

Each candidate must satisfy ALL of:
1. **Mathematically correct** — the repaired proof must be valid
2. **Self-consistent** — does not contradict other assumptions or break downstream results
3. **Minimal** — prefer the least invasive fix
4. **Preserves claims** — ideally keeps the theorem statement unchanged (or weakens minimally)
5. **Literature-supportable** — can cite existing results for any new technique/lemma used

### Feasibility Triage per Candidate (from /proof-writer methodology)

Before investing in literature search, classify each candidate:

| Status | Meaning | Next action |
|--------|---------|-------------|
| PROVABLE AS STATED | The repaired claim follows from (original + new) assumptions | Proceed to literature search + full proof writing |
| PROVABLE AFTER WEAKENING | Repair works but requires weaker theorem statement | Document the weakened claim explicitly, then proceed |
| NOT CURRENTLY JUSTIFIED | Cannot see how to make this repair work | Write blockage report, try next candidate |

**Anti-fabrication rule**: If NO candidate reaches PROVABLE status, do NOT force a repair.
Instead write a **Blockage Report**:
- Exact reason no repair works
- What additional theoretical development would be needed
- Whether the main theorem survives if this unit is dropped
- Honest assessment: is the paper's claim false, or just unproven?

### Mandatory output blocks per candidate

Each candidate selected for the next step (Step 4 literature search and Step 5 complete-proof writing) requires the following mandatory blocks in its per-issue repair file at `audit/07_repairs/section_*/*_repair.md`. The schemas live in `../stat-shared-references/proof-closure-machinery.md` and are not duplicated here.

- **Always**: `## Repair Ladder Defense` block (chosen level + repair class + claim/assumption preservation + Phase A Exhaustion Record + Phase B Justification if L4/L5 + Semantic-Edit Log Pointer + Blockage Pointer if L6).
- **If chosen class is `Weaken-Claim` (ladder L5) or candidate feasibility was `PROVABLE AFTER WEAKENING`**: `## Weaken-Claim Change Log` block per the schema in `../stat-shared-references/proof-closure-machinery.md` (5 columns: Patch ID, Original claim verbatim, Revised claim verbatim, Reason for weakening, Downstream impact). Without this block, the repair is demoted to `NOT CURRENTLY JUSTIFIED`.
- **If chosen class is `Add-Assumption` (ladder L4)**: `## Assumption-Extension Change Log` block per the schema in `proof-closure-machinery.md` (7 columns: Issue ID, Original assumption set, Added assumption verbatim, Natural weaker variant considered, Why the weaker variant fails, Scientific-scope impact, Propagation to downstream theorems/lemmas). The "Natural weaker variant considered" column is the local-minimality defense. Without this block, the repair is demoted to `NOT CURRENTLY JUSTIFIED`.

The `Downstream impact` / `Propagation` columns in both Change Logs are propagation contracts: every listed unit must have a corresponding patch in PATCHES.md. The re-audit treats unpropagated downstream consumers as `NEW-S0` (silent overstatement in the patched paper).

### Proof Strategy Selection for Repairs

When a repair involves writing new proof content (Insert-Lemma, Strengthen-Proof,
Replace-Technique), choose a proof strategy explicitly:

- **Direct**: when the result follows from straightforward calculation or known facts
- **Contradiction**: when the negation leads to a clear impossibility
- **Induction**: when the result has recursive structure (iterations, sequence convergence)
- **Reduction**: when a known theorem handles the core difficulty
- **Construction**: when we need to exhibit a specific object (counterexample, witness)
- **Coupling**: for probabilistic arguments comparing two processes
- **Optimization / variational**: for existence, bounds via optimization

Record the chosen strategy in the repair specification — this guides `/proof-writer` later.

---

## 4. Literature Search for Repair Support

For each candidate repair that needs literature support, run a targeted multi-source
search. A repair is only as credible as its references.

Full procedure — cache-consult, query formulation, the three parallel venue-aware
searches, the credibility-weighted ranking table, tier-proportional verification, cache
write-back, lock-manifest append, and the no-good-reference fallback:
`../stat-shared-references/repair-literature-protocol.md`. Venue tier lists are rule data
in `../stat-shared-references/scripts/venue_tiers.py`.

Hard gates for this step:

- **Cache before web.** Consult `~/.claude/literature_cache/` before invoking any web
  tool; write every new fetch back to the inbox.
- **Tier every result** (T1 gold / T2 strong / T3 supplementary / T4 reject) before
  recommending it. Prefer the higher tier; always cite the published version over a
  preprint.
- **Verify proportional to tier.** T1: our assumptions satisfy their prerequisites and
  their conclusion is what we need. T2: plus errata check and one T1 cross-reference.
  T3: plus read the cited proof itself. An unverified citation cannot support a repair.
- **T4 is never citable.** If nothing at T1/T2 supports the repair, take the fallback
  (new lemma, authoritative textbook, or self-prove and mark "self-proved — review
  recommended") and record the reduced confidence in the repair plan.

---

## 5. Assemble Repair Plan

For each issue, select the best candidate and write a repair specification to
`audit/07_repairs/section_X/{ID}_repair.md`. Contract:

```markdown
## Repair: {ID} — {unit and issue}

### Selected Strategy: Candidate {X} ({repair class}, ladder level L{n})
### Reason for Selection
[why this candidate over the others, in ladder terms]
### Mathematical Fix
[the new lemma or corrected step, stated precisely]
### Literature Support
| # | Reference | Venue/Tier | Credibility | What it provides | BibTeX key |
### LaTeX Patch
Reference mode: [A / B]; location: [file, anchor]
[the patch, respecting the recorded reference mode]
### Repair Provability Status
[PROVABLE AS STATED / PROVABLE AFTER WEAKENING / NOT CURRENTLY JUSTIFIED]
### Proof Strategy for New Content
### Downstream Verification Checklist
- [ ] [each dependent unit: what changes, or "no change needed"]
### Residual Obligations
[Anything this repair does not close is an OPEN obligation with an owner and one of
three dispositions: a blockage, a propagation task, or a claim downgrade. This is not
a catch-all notes field — an unresolved point recorded without one of those three
dispositions is an incomplete repair.]
```

A worked, filled specimen in both reference modes:
`../stat-shared-references/examples/repair-specification-example.md`.

Patch rule of thumb: a patch referencing only its own file uses `
ef{}`; a patch
crossing main ↔ supplement uses a hard-coded number, and a new supplement lemma gets an
S-prefixed label whose assigned number is recorded for later main-text patches.

---

## 5B. Write Complete Repaired Proofs

Any repair that introduces new proof content (Insert-Lemma, Strengthen-Proof,
Replace-Technique, Expand-Sketch-to-Proof) is written by **`/proof-writer`**, not here.
Hand it the repaired claim, the assumption IDs it may use, and the literature support
selected in Step 4; it returns a proof package whose every nontrivial obligation is
closed (`CLOSED-LOCAL` / `CLOSED-CITED` / `BLOCKED`) and which passes `proof_gap_scan.py`.

Write inline only when the fix is genuinely local: a corrected constant, an inequality
direction, a quantifier, a one-line justification of an already-stated step. Anything
that needs a dependency map or a new lemma goes to `/proof-writer`.

**The quality gate.** A repair is complete when the full proof exists and its obligations
are closed — not when a strategy is sketched. If the proof cannot be written honestly,
downgrade: extra conditions needed → `PROVABLE AFTER WEAKENING`; a wall → `NOT CURRENTLY
JUSTIFIED` plus a blockage record. A `BLOCKED` obligation returned by `/proof-writer`
propagates to the repair status; it is never absorbed silently.


### 5C. Codex Adversarial Stress-Test of Repairs (if Codex MCP available)

For every P0 and P1 repair with a complete proof, run the per-repair fresh-thread stress-test defined in `../stat-shared-references/codex-protocol.md` under "Per-Repair Fresh Thread" and "Per-Repair Stress-Test Call Template".

Rules (full rationale and template in `../stat-shared-references/codex-protocol.md`):

- One fresh `mcp__codex__codex` thread per logically-independent repair; up to 2-3 repairs may share a thread only if they sit on the same dependency edge or assumption block.
- `model_reasoning_effort: xhigh` is forced (the scope hits the Reasoning Effort Ladder triggers: theorem / lemma / proof step / rate / quantifier).
- Anti-anchor opening prompt; forced falsification attempt; structured PASS / FIXABLE / FAIL verdict.
- FIXABLE / FAIL iterate via `mcp__codex__codex-reply` on the same thread (Case B continuation).
- Verdicts are recorded in `audit/07_repairs/codex_stress_test.md` per the artifact schema in `../stat-shared-references/codex-protocol.md` "Per-Repair Stress-Test Verdict Recording" (one row per repair, threadId tracked).

The full per-repair call template, the verdict recording schema, the rationale (Codex's honest anchoring self-assessment), and the iterative push-back protocol all live in `../stat-shared-references/codex-protocol.md`. This skill does not duplicate them inline.

---

## 6. Cross-Repair Consistency Check

After all individual repairs are designed, verify they work together:

### 6A: Assumption Consistency Matrix

Build a matrix: rows = all assumptions (original + newly added), columns = all proof units.
Check: no unit requires contradictory assumptions.

```markdown
| Assumption | Scope | Added by repair? | Used by | Conflicts with |
|------------|-------|-----------------|---------|----------------|
| A1: i.i.d. | Global | No (original) | B.1-B.5 | None |
| A2: strong convexity | Global | No (original) | C.3', C.3-C.5 | None |
| A_new1: bounded 4th moment | Local to D.2 | Yes (I-03 repair) | D.2, D.4 | Check: does A1 + A2 imply this? |
```

### 6B: Rate/Constant Propagation Check

If any repair changes a rate or constant:
1. Trace through the entire dependency chain to the main theorem
2. Verify the main theorem's rate is preserved (or document the change)
3. Check that no "O(·) hides forbidden dependency" is introduced

### 6C: New Reference Compatibility & Quality Gate

Check that newly cited papers are:
- Compatible with each other (don't assume contradictory conditions)
- Compatible with the paper's existing framework
- From reputable venues — apply venue tier rules:

**Quality gate**: If ANY repair relies SOLELY on T3/T4 references:
1. Flag it in REPAIR_PLAN.md with ⚠ warning
2. Provide the self-contained proof (Step 5B) as backup
3. Recommend the author search for a published reference before submission

**Cross-check**: For each new reference, verify:
- The venue is real and indexed (check DBLP, MathSciNet, or Web of Science)
- The paper is not retracted or has a published erratum affecting the cited theorem
- If citing a preprint, check if a published version now exists (common for arXiv papers)
- If the paper's own references already cite a T1 source for the same fact, prefer that one

---

## 7. Write Master Repair Plan + Bibliography

### 7A: REPAIR_PLAN.md

Write `papers/<paper-name>/REPAIR_PLAN.md`:

```markdown
# Repair Plan: [Paper Title]

Generated from /proofcheck audit on [date].

## Executive Summary
- Total issues found: N
- Repairable issues: M
- Repairs requiring new literature: K
- New references needed: R
- Main theorem status after repair: [Preserved / Weakened to ...]
- Convergence status: [NOT YET RE-AUDITED / CONVERGED / NOT CONVERGED]

## Repair Priority Order

Execute repairs in this order (respects dependency DAG):

### Phase 1: Foundation Repairs (do first)
| Issue | Unit | Repair Class | Strategy | New refs needed |
|-------|------|-------------|----------|-----------------|

### Phase 2: Critical Path Repairs
| ... |

### Phase 3: Support Repairs
| ... |

## Repair Ladder Summary

Insert the `## Repair Ladder Summary` table per the schema in `../stat-shared-references/proof-closure-machinery.md`. One row per issue with columns: Issue ID, Unit, Chosen repair class, Chosen ladder level, Claim preserved?, Assumptions preserved?, Escalation justified?, Pointer to per-issue defense.

## Per-Issue Repair Specifications

Link to each `audit/07_repairs/section_X/*_repair.md` file. Each repair file contains a `Repair Ladder Defense` block per the schema in `proof-closure-machinery.md`.

## Repair Closure Matrix

Insert the `## Repair Closure Matrix` table per the schema in `proof-closure-machinery.md`. Every issue from `06_reports/issue_log.md` must have a row (closure-matrix completeness rule).

## Weaken-Claim Change Log

Insert the `## Weaken-Claim Change Log` block per the schema in `proof-closure-machinery.md`. **MANDATORY** if any repair is class `Weaken-Claim`. A row is required even when there is exactly one Weaken-Claim repair.

## Assumption-Extension Change Log

The per-issue repair file (not the master REPAIR_PLAN.md) holds the canonical Assumption-Extension Change Log block per the schema in `proof-closure-machinery.md`. **MANDATORY** if any repair is class `Add-Assumption` (ladder L4). The master plan's Repair Ladder Summary row points to the per-issue file's Change Log entry.

## New References Summary

| # | Key | Full citation | Venue | Tier | Credibility | Supports repair of | Verified? | Cache reference |
|---|-----|--------------|-------|------|-------------|-------------------|-----------|----------------|

Each row's `Cache reference` resolves to a `paper:<bibkey>#<result_id>` entry per `literature-cache-protocol.md`. The lock manifest at `papers/<project>/cited_results.lock.md` records the citation purpose and verification level used at decision time.

## Reference Quality Summary

- T1 (Gold Standard) references: X / Y total
- T2 (Strong) references: _
- T3 (Supplementary / preprint): _ ← flag each with ⚠ if used
- Self-proved lemmas (no external ref): _

## Consistency Verification

- [ ] Assumption matrix: no contradictions
- [ ] Rate propagation: main theorem rate preserved (or, if not, documented in Weaken-Claim Change Log)
- [ ] New references: mutually compatible
- [ ] New references: all T1/T2 venue verified (no predatory journals)
- [ ] T3 preprint references: cited theorems independently verified
- [ ] Downstream units: all re-verified after repair (via post-repair audit)
- [ ] Repair Closure Matrix is complete (every original issue has a row)
- [ ] Weaken-Claim Change Log is complete (every Weaken-Claim repair has a row + propagation patches)
- [ ] Assumption-Extension Change Log is complete (every Add-Assumption repair has a row in its per-issue file)
- [ ] Every per-issue repair file has a Repair Ladder Defense block (L4/L5 include Phase A Exhaustion Record + Phase B Justification + Semantic-Edit Log Pointer)

## Residual Issues (cannot repair without major rework)

| Issue | Why unrepairable | Impact |

## Hard-Gate Completion Rule

The full Hard-Gate Completion Rule (9 conditions) lives in `../stat-shared-references/proof-closure-machinery.md`. Headline conditions:

- Every issue has a terminal closure row; every Weaken-Claim and Add-Assumption repair has its mandatory Change Log entry; outstanding sketches = 0; every P0/P1 repair passed the per-repair Codex stress-test (per `../stat-shared-references/codex-protocol.md`); the Consistency Verification checklist is fully checked.
- **If the original audit contained any S0 or S1 issue**: `/proofcheck --post-repair` has been invoked AND `audit/08_post_repair/CONVERGENCE_VERDICT.md` reports `CONVERGED`. HARD GATE.
- **If the original audit contained only S2 and S3 issues**: `--post-repair` is strongly recommended; the executive summary states `Convergence status: NOT YET RE-AUDITED (S2/S3-only)`.

### 7B: Generate BibTeX Entries

Write new references to `papers/<paper-name>/repair_references.bib`:

```bibtex
% References added to support proof repairs
% Generated by /proof-repair on [date]

@book{boyd2004convex,
  title={Convex Optimization},
  author={Boyd, Stephen and Vandenberghe, Lieven},
  year={2004},
  publisher={Cambridge University Press}
}
```

### 7C: Generate LaTeX Patch Summary

Write `papers/<paper-name>/PATCHES.md`: the recorded reference mode, then one entry per
patch in apply order. Per patch: target file, insertion anchor, any new label and its
assigned display number (record it — later patches cite that number), the cross-file
references it contains, and the LaTeX block itself.

**Pre-patch validation (all four must hold before PATCHES.md is final):**

1. Every `
ef{}` / `\eqref{}` / `\cref{}` inside a patch resolves to a `\label{}` in the
   *same* file. Otherwise convert it to a hard-coded reference.
2. Every cross-file reference is a hard-coded number, never a `
ef{}`.
3. Supplement numbering stays consistent: new supplement objects get S-prefixed display
   numbers, and assigned numbers are tracked across patches so the master plan agrees
   with itself.
4. `\cite{}` needs no special handling — the `.bib` is shared, so citations work in both
   files; only mathematical-object references are mode-sensitive.

Renumbering discipline when a patch shifts later numbers:
`../stat-shared-references/reference-mode-protocol.md`. Re-run `proof_index.py` after
patching; a new `cross_file_ref_leak` is a patch defect.

---

## Quick Mode

If user only wants to repair a SINGLE unit (not full audit):

```
/proof-repair papers/my-paper/ --unit "Lemma C.3"
```

1. Read just that unit's check file from `04_local_checks/`
2. Read dependency graph for context
3. Generate repair candidates
4. Search literature
5. Output single repair file

## From-Reaudit Mode (`--from-reaudit`)

Invoked as `/proof-repair --from-reaudit papers/<paper-name>/`. This is a focused mode that handles residual issues found by `/proofcheck --post-repair` after a previous repair cycle. It is **manually triggered only**; the pipeline does not auto-loop.

### Pre-conditions

- `audit/08_post_repair/CONVERGENCE_VERDICT.md` exists and reports `NOT CONVERGED — RE-REPAIR REQUIRED` (not `HUMAN INTERVENTION REQUIRED` — that one requires the user to first decide whether to revert, restate, or change venue before any re-repair makes sense).
- The user has read `audit/08_post_repair/RE-AUDIT_REPORT.md` and confirmed the residual issues are within scope for another mechanical repair pass.

### Inputs

1. `audit/08_post_repair/RE-AUDIT_REPORT.md` — the delta-audit report
2. `audit/08_post_repair/new_issues.md` — NEW-S0/S1 issues introduced by previous patches
3. `audit/08_post_repair/per_issue_closure.md` — STILL-OPEN issues from the original audit
4. `audit/08_post_repair/diff_ledger.md` — unjustified diff rows
5. The previous REPAIR_PLAN.md, PATCHES.md, and patched paper

### What this mode does

This mode runs a narrowed version of the main `/proof-repair` workflow on the residual issue set only.

#### F1. Collect residuals

Build a focused issue list combining:

- Every `STILL-OPEN` issue from `per_issue_closure.md` (original issues the previous patch did not close)
- Every `NEW-S0` and `NEW-S1` issue from `new_issues.md` (issues the previous patch introduced)
- Every unjustified diff row from `diff_ledger.md` (silent semantic changes not propagated)

S2 and S3 residuals are listed but do not force the cycle to continue; the user decides whether to address them now or accept the open list.

#### F2. Classify residuals by cause

Each residual is one of:

- `INCOMPLETE-FIX`: the patch attempted the right strategy but missed steps or edge cases. Re-apply the same repair class with the missed details addressed.
- `WRONG-CLASSIFICATION`: the original repair class was wrong (e.g., Strengthen-Proof was tried where Add-Assumption was needed). Reclassify and re-design.
- `UNDOCUMENTED-WEAKENING`: a Weaken-Claim repair was applied without a PATCHES.md change-log row, or without propagation to downstream units. Generate the missing change-log table and propagate.
- `PROPAGATION-GAP`: a repair was correctly designed and locally verified, but downstream units that consumed the original claim were not updated. Add downstream-propagation patches without touching the already-correct local repair.
- `NEW-DEFECT`: the previous patch introduced a fresh defect in a unit that was previously verified. Treat as a new repair from scratch.

#### F3. Repair the residuals only

For each residual, run Steps 3-5 of the main workflow (Generate Candidates, Literature Search, Write Complete Proof) on the residual itself. **Do not re-litigate already-CLOSED-VERIFIED issues.** The previous REPAIR_PLAN.md remains the canonical record for those.

If a residual repair touches a unit already repaired in the previous cycle, the new patch is layered on top — the closure matrix gains a second row for the same unit, marked as `Repair cycle 2`. The previous cycle's row is preserved with its terminal status.

#### F4. Update REPAIR_PLAN.md and PATCHES.md

The existing REPAIR_PLAN.md is **appended to**, not rewritten:

- New section: `## Repair Cycle 2 — From Re-Audit Verdict on [date]`
- New Closure Matrix rows for the residual issues
- Updated cycle-2 patches in PATCHES.md, clearly labeled `Cycle 2 — Patch N`
- Updated Codex Stress-Test results for cycle-2 repairs

The summary section is updated to reflect both cycles.

#### F5. Re-invoke `/proofcheck --post-repair`

`--from-reaudit` does not declare convergence itself. After it finishes, the user invokes `/proofcheck --post-repair` again. This is the only path to a `CONVERGED` verdict.

### Hard rule against auto-looping

The pipeline never automatically loops `proof-repair --from-reaudit → proofcheck --post-repair → proof-repair --from-reaudit → ...`. Each invocation requires the user to confirm:

- Are the residual issues mechanically fixable, or do they signal a deeper problem (wrong theorem, wrong assumption set, wrong technique entirely)?
- Has the cycle count exceeded 2? If so, the user should consider whether the paper's framework needs to be revisited via `/theory-design` or `/theory-sharpen` rather than continuing to patch.

If a residual cannot be closed after two `--from-reaudit` cycles, escalate: the affected theorem is downgraded to NOT CURRENTLY JUSTIFIED in the patched paper, the abstract and introduction are updated to remove the claim, and the user decides whether the paper still has a publishable contribution without it.

### Common failure modes

- **Cascading rate degradation**: a Weaken-Claim repair in Lemma 5 cascades to corollaries 6, 7, 8, each requiring its own propagation patch. By cycle 2, the paper's headline rate may no longer be defensible. Flag this in `RE-AUDIT_REPORT.md` and let the user decide whether to weaken the headline rate or revert to the original (stronger but unproven) statement.
- **Assumption infection**: an Add-Assumption repair adds a moment condition to Lemma 3; cycle-2 reveals this condition contradicts a sparsity assumption used in Theorem 1. The repair set is inconsistent. Escalate to human intervention rather than producing another cycle.
- **Sketch-expansion loops**: a SKETCH-ONLY unit expanded in cycle 1 reveals new sketches in its expansion (because the cited technique itself was a sketch in the cited paper). Treat as `BLOCKAGE` and stop expanding; do not chain sketch-expansion across cycles.

---

## Output Summary

When complete, report to user:

```
Repair plan generated for [Paper].

Issues addressed: X / Y total
├── P0 (critical): A repaired, B residual
├── P1 (important): C repaired
└── P2 (minor): D repaired

New literature found: N papers
├── T1 Gold (AoS/JASA/Biometrika/JRSS-B/Econometrica/NeurIPS/ICML/JMLR/textbooks): K
├── T2 Strong (EJS/Bernoulli/AAAI/KDD/IEEE-IT): M
├── T3 Supplementary (arXiv preprints): J ← ⚠ if any
└── Self-proved (no external ref): L

Files created:
├── REPAIR_PLAN.md — master repair roadmap
├── PATCHES.md — ordered LaTeX modifications
├── repair_references.bib — new BibTeX entries
└── audit/07_repairs/ — per-unit repair specifications

Next steps:
  1. Review REPAIR_PLAN.md — accept/reject each repair, verify the
     Repair Closure Matrix and Weaken-Claim Change Log are complete
  2. For complex repairs, run: /proof-writer [specific repaired claim]
     to get publication-ready proof text
  3. Apply patches: /proof-repair --apply to auto-patch paper.tex
  4. Convergence test (REQUIRED if any S0/S1 issue existed):
     /proofcheck --post-repair papers/my-paper/
     → produces audit/08_post_repair/CONVERGENCE_VERDICT.md
     → REPAIR_PLAN.md cannot be marked complete until verdict is CONVERGED
  5. If re-audit reports NOT CONVERGED — RE-REPAIR REQUIRED:
     /proof-repair --from-reaudit papers/my-paper/
     then re-run step 4. Max 2 cycles; after that, downgrade affected
     theorems to NOT CURRENTLY JUSTIFIED.
```
