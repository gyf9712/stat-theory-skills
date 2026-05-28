---
name: proofcheck
description: Systematically verify mathematical proofs in statistics/ML theory paper appendices. Use when user says "proof check", "check proofs", "verify proofs", "audit paper", "检查证明", "证明验证", or wants to verify correctness of a paper's mathematical proofs.
argument-hint: [path-to-paper.tex or paper-name]
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent
model: opus
---

# ProofCheck — Mathematical Proof Verification for Statistics/ML Theory Papers

> 🔬 **Model Recommendation**: Run this skill on **Claude Opus** for best results.
> Mathematical proof verification requires deep reasoning. If your session is not on
> Opus, run `/model opus` before invoking. The skill will also delegate heavy
> reasoning to Opus sub-agents internally when the Agent tool is used.

Systematically check proofs in long technical appendices using a structured, evidence-based methodology with multi-pass verification.

Based on: https://github.com/maweiruc/proofcheck-stat-paper

## Context: $ARGUMENTS

## Core Objective

> Given the paper's stated assumptions, definitions, and cited results, does each claimed theorem follow with the stated constants, rates, quantifiers, probability levels, domains, and edge cases?

**Goal**: Find correctness issues — NOT summarize the proof. Never silently repair proofs.

---

## Operating Principles

1. **Evidence First**: Every conclusion cites exact page/section/equation/line numbers. No vague references.
2. **Small Proof Units**: One definition, one lemma, one proof at a time. Never verify 20+ pages at once.
3. **Separate Facts/Inferences/Suspicions**: Verified (checked + referenced), Inferred (likely but unchecked), Suspect (possible gap).
4. **No Silent Repairs**: If proof proves B but claims A, record the mismatch explicitly.
5. **Human Owns Final Judgment**: Agent indexes, cross-checks, and reconstructs. Human reviews all S0/S1 issues.

## Severity System

| Level | Meaning | Examples |
|-------|---------|---------|
| S0 | Fatal — main theorem does not follow | Circular dependency, wrong inequality direction in critical chain |
| S1 | Major — missing assumption or step, likely repairable | Hidden invertibility assumption, missing log factor |
| S2 | Moderate — local ambiguity, may not affect final result | Unclear quantifier scope, uncited intermediate step |
| S3 | Minor — typo, notation, reference | Missing label, inconsistent symbol |

## Verification Statuses

- **Verified** — all dependencies checked, logic sound
- **Conditionally verified** — correct IF listed dependencies hold
- **Gap found** — specific missing step identified
- **Incorrect** — error found
- **Not checked** — not yet examined

## Provability Assessment (per unit, from /proof-writer methodology)

Before deep-checking any unit, first triage its provability:

| Status | Meaning | Action |
|--------|---------|--------|
| PROVABLE AS STATED | Claim follows from listed assumptions | Proceed with full verification |
| PROVABLE AFTER WEAKENING | Needs extra assumption or narrower claim | Record gap, verify the weakened version |
| NOT CURRENTLY JUSTIFIED | No clear path to a valid proof | Write blockage report, skip deep-check |

This triage prevents wasting effort on units where the claim is fundamentally flawed.

## Proof Strategy Classification (per unit)

Identify the proof technique BEFORE step-by-step checking — different strategies have
different failure modes:

| Strategy | Common failure modes to watch |
|----------|-------------------------------|
| Direct | Missing case, unjustified step, wrong inequality direction |
| Contradiction | Negation error, unconsidered third case, vacuous hypothesis |
| Induction | Missing base case, hypothesis used outside valid range, wrong induction variable |
| Construction | Object may not satisfy all requirements, uniqueness not checked |
| Reduction to known result | Cited result used outside its conditions, notation mismatch |
| Coupling / probabilistic | Independence assumed, coupling fails at boundary, measurability |
| Optimization / variational | Existence of minimizer, local vs global, compactness missing |
| Epsilon-delta / approximation | Quantifier order, uniformity, limit exchange |

---

## Workflow

### Step 0: Setup Workspace

Parse `$ARGUMENTS` to locate the paper's LaTeX source file.

```bash
# Create workspace structure
PAPER_DIR="papers/$(basename "$PAPER_PATH" .tex)"
mkdir -p "$PAPER_DIR/audit"/{01_index,02_ledgers,03_dependencies,04_local_checks,05_adversarial,06_reports}
```

If `$ARGUMENTS` is a directory, look for `paper.tex` inside it. If it's a `.tex` file path, use it directly.

#### Detect Reference Mode (one-file vs two-file submission)

Before any cross-reference audit, detect whether the paper is:

- **Mode A: single-file** — one .tex compiles to one PDF (arXiv, NeurIPS/ICML)
- **Mode B: two-file** — `paper.tex` + `supplement.tex` (or similar) compile separately
  (typical for JASA, AoS, JRSS-B, Biometrika, Econometrica, JBES, JOE)

```bash
# Count top-level .tex files (excluding files that are \input by others)
find "$(dirname "$PAPER_PATH")" -maxdepth 1 -name "*.tex" -type f
# Look for explicit supplement files
ls "$(dirname "$PAPER_PATH")"/{supp*,supplement*,appendix*,SI*}.tex 2>/dev/null
# Look for S-prefix labels — strong signal of Mode B
grep -l 'label{[^}]*:S[._]\|label{S' "$(dirname "$PAPER_PATH")"/*.tex 2>/dev/null
```

Record in `CHECK_PLAN.md`:
```markdown
## Reference Mode
Mode: [A: single-file / B: two-file]
Files: [list]
Cross-file convention (if Mode B): hard-coded numbers (e.g., "Lemma S.3", 
       "Theorem 2.1 of the main text") — NOT \ref{} across files
```

This mode affects Pass 0's cross-reference audit (Step 2B) — see below.

### Step 1: Bootstrap — Generate CHECK_PLAN.md + EXECUTION_ORDER.md

Read the paper and extract the proof architecture. Do NOT check any proofs yet — only map the terrain.

#### 1A. Extract Proof Architecture (→ CHECK_PLAN.md Part A)

Read these sections of the LaTeX source:
1. **Introduction** — contributions subsection, look for TikZ dependency diagrams
2. **Proof strategy section** — "Proof Strategy", "Proof Outline", "Overview of Proofs"
3. **Appendix structure section** — the appendix's own roadmap
4. **Main theorem statements**

Produce:
- **Core Proof Strategy** (≤5 sentences): the fundamental challenge, the solution, the key innovation
- **Dependency Diagram** (ASCII art): reconstruct from paper's figures or theorem statements
- **Critical Proof Chains** (3-5 chains): base lemmas → main theorems
- **Key Definitions Table**: notation appearing across multiple sections

#### 1B. Index the Appendix (→ CHECK_PLAN.md Part B)

Run grep on LaTeX source:
```bash
grep -n '\\begin{theorem}\|\\begin{lemma}\|\\begin{proposition}\|\\begin{corollary}\|\\begin{definition}\|\\begin{assumption}' "$PAPER_PATH"
```

Build:
- Appendix structure table: Section | Lines | Content
- Proof unit inventory: ID | Type | Label | Line | Statement summary | Status (all "Unchecked")

#### 1C. Build Dependency Graph (→ EXECUTION_ORDER.md)

For each proof unit, extract all `\ref{}` in its proof block. Each target is a dependency.

**Topological Sort**: Layer 0 = no internal deps. Layer k = all deps in layers < k.
**Parallelism**: Units in same layer can run in parallel (‖).
**Critical Path**: Units cited by ≥3 later units, or on transitive chain to main theorem.

Write `EXECUTION_ORDER.md` with:
- Dependency Map (ASCII DAG)
- Phase Plan table: ID | Unit | Section | Lines | Depends On
- Parallelism Summary: Phase | Parallel units | Gate conditions

### Step 2: Pass 0 — Indexing (Map the Terrain)

Three parallel tasks:

**Task 2A: Theorem Inventory** → `audit/01_index/theorem_inventory.md`

| ID | Type | Location | Short name | Statement summary | Depends on | Used by | Status |
|----|------|----------|------------|-------------------|------------|---------|--------|

For each: label, exact location, mathematical objects, assumptions (explicit + inherited), claimed conclusion, probability/asymptotic regime, constants (universal vs problem-dependent), where used.

**Task 2B: Cross-Reference Audit** → `audit/01_index/cross_reference_audit.md`

Audit logic depends on Reference Mode (detected in Step 0):

**Mode A (single-file)**: standard audit
- Match all `\ref{}` / `\eqref{}` against `\label{}` within the same file
- Report: broken refs, orphan labels, duplicate labels

```bash
grep -no '\\label{[^}]*}' "$PAPER_PATH" | sort > /tmp/labels.txt
grep -no '\\ref{[^}]*}\|\\eqref{[^}]*}' "$PAPER_PATH" | sort > /tmp/refs.txt
```

**Mode B (two-file main+supplement)**: per-file audit + cross-file convention check
1. **Within-file audit** (run for each file separately):
   - `\ref{}` in main.tex must resolve to `\label{}` in main.tex only
   - `\ref{}` in supplement.tex must resolve to `\label{}` in supplement.tex only
2. **Cross-file `\ref{}` is a bug**:
   - If main.tex has `\ref{LABEL}` whose `\label{LABEL}` lives in supplement.tex → REPORT as broken ref (S1)
   - The author should have used a hard-coded number ("Lemma S.3 of the supplement")
3. **Hard-coded number convention check**:
   - Scan main.tex for "of the supplement", "of the supplementary material", "in the supplement"
   - Each should be paired with a hard-coded number (e.g., "Lemma S.3 of the supplement")
   - Scan supplement.tex for "of the main text", "in the main text"
   - Each should be paired with a hard-coded number (e.g., "Assumption 2 of the main text")
4. **Supplement numbering consistency**:
   - Supplement lemmas/equations should use S-prefix display numbers
   - Verify the supplement's `\begin{theorem}` / equation counters are properly redefined
     (e.g., `\renewcommand{\thelemma}{S.\arabic{lemma}}` or use of `\appendix` reset)

```bash
# Per-file labels and refs
for f in main.tex supplement.tex; do
  grep -no '\\label{[^}]*}' "$f" > /tmp/labels_$f.txt
  grep -no '\\ref{[^}]*}\|\\eqref{[^}]*}\|\\cref{[^}]*}' "$f" > /tmp/refs_$f.txt
done

# Detect cross-file leaks
comm -12 <(sed 's/.*\\ref{\([^}]*\)}.*/\1/' /tmp/refs_main.tex.txt | sort -u) \
         <(sed 's/.*\\label{\([^}]*\)}.*/\1/' /tmp/labels_supplement.tex.txt | sort -u)
# Any output here means main.tex \ref{}'s a label that lives in supplement.tex → BUG
```

Record findings (Mode B):
```markdown
## Cross-File Reference Issues (Mode B)
| Issue | File | Line | Problem | Severity |
| Bad cross-file \ref | main.tex | 142 | \ref{lem:S3} but label is in supplement.tex; should be "Lemma S.3 of the supplement" | S1 |
| Missing "of the supplement" | main.tex | 89 | "by Lemma S.7" but doesn't say which file | S2 |
```

**Task 2C: Notation Ledger** → `audit/02_ledgers/notation_ledger.md`

| Symbol | Meaning | First defined | Domain/type | Parameters | Later uses | Drift risk |
|--------|---------|--------------|-------------|------------|------------|------------|

Check for: symbols used before definition, same symbol for different objects, scalar/vector mismatch, random/deterministic mismatch, norm changes, constants with changed dependencies.

Also build:
- `audit/02_ledgers/assumption_ledger.md` — ID | Assumption | Location | Scope | Used by | Strength needed | Status
- `audit/03_dependencies/dependency_graph.md` — dependency table + circularity analysis

### Step 3: Pass 1 — Check Critical Path

Check the chain leading to the main theorem FIRST. Prioritize lemmas used by many later results.

#### MANDATORY first sub-step: Sketch-vs-Complete Classification

Before checking proof correctness, classify whether what the paper provides is
ACTUALLY a proof, or only a sketch / outline. This is distinct from step-skipping
(which is about individual missing steps within a proof) — this is about whether
the entire proof body is rigorous derivation or just high-level summary.

**Three-class classification**:

| Class | Definition | Action |
|-------|-----------|--------|
| **COMPLETE** | Rigorous step-by-step derivation; all transitions justified; cited results have prerequisites verified; edge cases handled | Proceed with normal step-by-step verification |
| **PARTIAL-SKETCH** | Some rigorous derivation but with substantial gaps (e.g., "the rest follows by similar arguments"; entire technical lemma deferred to supplement; proof of main step is one paragraph for a 1-page-claim theorem) | Treat each gap as an S1 issue; demand expansion before any "verified" verdict |
| **SKETCH-ONLY** | High-level outline without rigorous derivation. Title says "Proof Sketch" / "Sketch of Proof", or proof body is purely verbal narrative with no equation derivations, or proof says "we (1) bound X, (2) apply Y, (3) conclude" without actual algebra | The unit cannot be marked Verified — it's not a proof, it's a plan. Report as `STATUS: SKETCH-ONLY — NO PROOF PROVIDED` |

**Sketch indicators** (any combination triggers PARTIAL-SKETCH or SKETCH-ONLY):

- Title or section explicitly says "Proof Sketch" / "Sketch of Proof" / "Outline of Proof"
- Body contains: "We sketch the proof", "Full details in the supplement", "Detailed proof is omitted"
- Proof length disproportionate to claim complexity (e.g., 5 lines for a 2-page theorem)
- Body is purely verbal narrative ("we first bound X using Y, then apply Z") with no derived equations
- "Similar to / follows from [Paper Z]" without showing the adaptation
- Heavy use of "it can be shown that" / "by standard arguments" / "after some algebra"
- "We omit the details for space"
- Technical core deferred entirely: "Lemma N is proved in Appendix X" but Appendix X is also sketch-only
- A theorem whose proof is a single paragraph + a citation to another paper

**Crucially**: a proof labeled "Proof Sketch" is NOT a sufficient verification of
the claim. If the paper relies on this sketch as evidence for the theorem, the
theorem's actual status is at best `CONDITIONALLY VERIFIED` pending the full
proof. Reviewers at AoS / JASA / JRSS-B / Biometrika do not accept main-text
sketches without full proofs in supplement.

**Record in the unit check file**:
```markdown
### Sketch-vs-Complete Audit
- Class: [COMPLETE / PARTIAL-SKETCH / SKETCH-ONLY]
- Sketch indicators found: [list specific evidence]
- For PARTIAL-SKETCH: each gap recorded as an S1 issue requiring expansion
- For SKETCH-ONLY: STATUS is forced to "SKETCH-ONLY — NO PROOF PROVIDED"
- Supplement location (if proof is supposed to be elsewhere): [pointer + verify it IS complete there]
- **Expansion status**: [REQUIRED / IN-PROGRESS / COMPLETED] ← MANDATORY field
- **Expanded proof file**: [path, set once expansion is complete]
```

If the "real" proof is supposed to be in supplementary material, follow the link
and audit the supplement proof; if the supplement proof is also a sketch, both
get tagged SKETCH-ONLY.

#### HARD RULE: detection requires immediate expansion

A sketch detected during /proofcheck **cannot remain unexpanded** in the final
audit output. The audit is NOT complete while sketches remain.

When SKETCH-ONLY or PARTIAL-SKETCH is found:
1. Mark the unit with `Expansion status: REQUIRED`
2. **Immediately hand off** to /proof-repair (Expand-Sketch-to-Proof repair class)
   which then invokes /proof-writer for the actual writing
3. /proof-writer must produce either:
   - A COMPLETE proof (Expansion status → COMPLETED)
   - An explicit NOT-CURRENTLY-JUSTIFIED blockage report (then the theorem
     itself is downgraded; the sketch is still removed)
4. After expansion, re-run the Sketch-vs-Complete classification on the new
   proof body — verify it now classifies as COMPLETE
5. The audit is blocked from "Pass 5: Final Report" until every detected
   sketch has Expansion status of either COMPLETED or BLOCKAGE-REPORT-WRITTEN

The Final Report's executive summary MUST contain a row:
```
Sketches detected: N
├── Expanded to complete proof: M
├── Determined to be unprovable as stated (blockage report): K
└── Outstanding (NOT ALLOWED in final state): 0
```

If any sketch remains in "REQUIRED" or "IN-PROGRESS" state when the audit
attempts to finalize, the skill REFUSES to mark the audit complete and
returns to expansion.

For EACH proof unit, create one file: `audit/04_local_checks/section_X/{ID}_{name}_check.md`

Each file follows this template:

```markdown
## Proof Unit: [ID / Name]
- Location:
- Type: [definition / lemma / proposition / theorem / proof segment]
- **Sketch class**: [COMPLETE / PARTIAL-SKETCH / SKETCH-ONLY]   ← from Sketch-vs-Complete audit
- Proof Strategy: [direct / contradiction / induction / construction / reduction / coupling / optimization / epsilon-delta]
- Provability: [PROVABLE AS STATED / PROVABLE AFTER WEAKENING / NOT CURRENTLY JUSTIFIED]
- Status:
- Confidence:

### Claim Normalization
**Original statement**: [exact copy from paper]
**Normalized form**: [rewritten with all quantifiers, domains, types explicit]
**Interpretation notes**: [any ambiguity resolved, notation clarified]

If the normalized form is stronger/different from the original, flag this explicitly.

### Explicit Assumptions
- [Assumption 1]

### Inherited / Implicit Assumptions
- [Standing assumption]
- [Hidden assumption detected: ...]

### Dependencies
| Dependency | Location | Required form | Available? | Verified? | Notes |
|------------|----------|---------------|------------|-----------|-------|

### Step-by-Step Verification
| Step | Location | Claim | Justification | Verdict | Notes |
|------|----------|-------|---------------|---------|-------|
| 1 | Eq.(42)→(43) | Triangle ineq | Same norm | Valid | None |
| 2 | Eq.(43)→(44) | Lemma A.2 | Needs boundedness | Gap | Missing assumption |

**Anti-fabrication checklist** — flag ANY instance of:
- "clearly" / "obviously" / "it is easy to see" hiding a nontrivial step
- "by standard arguments" without specifying WHICH standard argument
- "similarly" referring to a non-analogous situation
- A step justified only by "by the above" without exact reference
- Unmarked use of a stronger assumption than what is stated

### Edge Cases & Boundary Analysis
- [Boundary case checked: what happens when parameter = 0/1/∞?]
- [Degenerate case: what if matrix is singular / set is empty / dimension = 1?]
- [Domain boundary: does the result hold at the boundary of Θ?]

### Issues
| Severity | Confidence | Description | Evidence | Proposed repair |

### Final Verdict
[Verified / Conditionally verified / Gap found / Incorrect / Unclear]

### If Gap Found: Blockage Report
- **Exact blocker**: [which step fails and why]
- **What would fix it**: [minimal extra assumption / lemma / technique needed]
- **Weaker claim that IS provable**: [if applicable]
- **Candidate literature**: [known results that might bridge the gap — to be expanded by /proof-repair]
```

**Key checks for each step**:
- Every equation transition and inequality direction
- Every quantifier and probability statement
- Every constant, rate, domain, dimension
- Every boundary case
- Conclusion vs. statement match
- **Conclusion matches EXACTLY what was proved** (not a stronger restatement)
- **Every nontrivial implication is justified** — no "clearly" or "obviously" allowed

#### Step Completeness Audit (sub-step within each unit check)

This audit is mandatory for every proof unit. Going beyond passive anti-fabrication
word-flagging, it ACTIVELY identifies step jumps and reconstructs them.

##### A. Skip-point detection

For each proof unit, scan for skip indicators in three categories:

**Category 1: Verbal skip phrases**
- "clearly" / "obviously" / "it is easy to see" / "trivially"
- "by standard arguments" / "as is well-known" / "it is well-known"
- "after some algebra" / "after simplification" / "by direct calculation"
- "by symmetry" / "similarly" / "the same argument applies"
- "the rest follows" / "the conclusion is now immediate" / "we omit the details"
- "as before" / "by the above" / "in an analogous manner"

**Category 2: Equation-number jumps**
- Eq.(k) appears, then Eq.(k+m) for m ≥ 2 without intermediate equations
- A displayed equation followed by ≥2 lines of unjustified manipulation
- Use of an unstated identity to transform one expression to another

**Category 3: Implicit logical jumps**
- A conclusion drawn from a previous claim without stating the inference rule
- A bound used as both upper and lower without separate justification
- An optimization step where existence of optimizer is assumed but not shown
- A limit/sum/integral exchanged without naming the convergence theorem

##### B. Reconstruction attempt

For EACH detected skip, attempt to fill in the missing steps:

1. **List what is being claimed before the skip** (the input state)
2. **List what is being claimed after the skip** (the output state)
3. **Reconstruct the bridging steps explicitly** (using paper assumptions + cited
   results + standard mathematical facts only — no fabrication)
4. **Count the reconstructed steps** and assess the techniques used

##### C. Skip classification (for each detected skip)

Based on the reconstruction:

| Class | Reconstruction needed | Verdict | Action |
|-------|----------------------|---------|--------|
| **TRIVIAL** | ≤1 line of standard manipulation (e.g., expand brackets, apply definition) | Legitimate skip | Note as TRIVIAL, no action |
| **VERIFIABLE** | 2-5 lines of standard manipulation (e.g., chain of substitutions, named inequality applications) | Legitimate but author should write it | Suggest filling in (severity: S3) |
| **NONTRIVIAL** | Requires a non-obvious idea, a hidden lemma, or a specific technique | **MUST be filled in** by the author | Record as S1 issue; downstream `/proof-repair` will need to insert |
| **UNRECONSTRUCTIBLE** | Cannot bridge from input to output state using available assumptions + cited results | **Possible error** | Record as S0/S1 issue; demand author justification or counterexample |

##### D. Step Completeness Table (per unit)

Add to each unit's check file:

```markdown
### Step Completeness Audit

| Skip # | Location | Skip indicator | Input state | Output state | Reconstruction | Class | Severity |
|--------|----------|---------------|-------------|--------------|----------------|-------|----------|
| 1 | Line 152, "obviously" | verbal | f(x) ≥ 0 ∀x | ∫f dμ ≥ 0 | Apply monotonicity of integral (1 line) | TRIVIAL | — |
| 2 | Eq.(47)→(50) | equation jump | LHS of (47) | RHS of (50) | Algebraic expansion + Cauchy-Schwarz + bound on ‖∇f‖ (4 lines) | VERIFIABLE | S3 |
| 3 | "by symmetry" line 198 | verbal | Bound on E[XY] | Bound on E[X²]+E[Y²] | Symmetry NOT applicable here — X,Y not exchangeable | NONTRIVIAL | S1 |
| 4 | "after some algebra" line 220 | verbal | Eq.(60) | Eq.(61) | Cannot reconstruct — requires unstated identity for matrix inverse | UNRECONSTRUCTIBLE | S0 |

**Summary**: 4 skips found. 1 trivial, 1 verifiable, 1 nontrivial (S1), 1 unreconstructible (S0).
```

##### E. Reconstruction discipline (anti-fabrication for the checker)

When reconstructing steps, the checker itself must follow rigor rules:

- Use ONLY: paper's stated assumptions + cited results + named standard facts
  (e.g., Cauchy-Schwarz, Jensen, triangle inequality, Holder's)
- For named standard facts, cite the name explicitly ("by Cauchy-Schwarz")
- Do NOT invent intermediate inequalities or unstated lemmas
- If a reconstruction requires invoking a non-obvious lemma, classify as NONTRIVIAL
  and record what lemma is needed
- If reconstruction succeeds but uses techniques not in the paper's framework
  (e.g., heavy machinery from a different subfield), flag as suspect — the
  author probably intended a simpler bridge that we're missing

### Step 4: Pass 2 — Check Support Lemmas

After critical path confirmed, check remaining lemmas in parallel within each phase. Same per-unit template as Pass 1.

Also maintain:
- `audit/02_ledgers/constants_ledger.md` — track which constants are universal vs problem-dependent
- Event ledger — track probability events, their definitions, and how they compose

### Step 5: Pass 3 — Global Consistency

Cross-cutting checks after all local checks:

1. **No circular dependencies** — trace every chain to base assumptions
2. **Notation consistent** — no symbol drift between sections
3. **Assumptions propagate** — every cited assumption is in scope where used
4. **Theorems assemble** — each main theorem's transitive dependencies all proved
5. **Quantifier consistency** — check "for all ∃" vs "∃ for all", uniform vs pointwise, parameter-dependent vs universal constants
6. **Probability/event consistency** — events defined? Intersections handled? Failure probability accumulated correctly?
7. **Constants/rates consistency** — are O(·) terms hiding forbidden dependencies? Rates preserve all n, d, δ, ε?

### Step 6: Pass 4 — Adversarial Review

Deliberately try to break the proof:

**Counterexample search**: What happens with d=1, n=1, zero variance, singular matrix, boundary of parameter space, heavy tails, equal parameters, probability-zero events, flat/non-smooth functions?

**Hidden assumption search**: For each proof unit check:
- Division by zero? Matrix invertibility without proof?
- Limit/expectation/derivative/integral exchange without justification?
- Concentration without independence/tail checks?
- Compactness without compact domain?
- Minimizer existence assumed? Uniqueness used but not proved?
- High-probability statements used simultaneously without union bound?
- Uniform result claimed from pointwise proof?

**External theorem misuse**: Check exact prerequisites, finite-sample vs asymptotic, pointwise vs uniform, matching notation.

**Stress assumptions**: Remove each assumption → which step fails? Does proof use stronger version than stated? Are there unused assumptions?

Write findings to `audit/05_adversarial/hidden_assumptions.md` and `audit/05_adversarial/counterexamples.md`.

#### Codex Adversarial Cross-Review (if Codex MCP available)

**Follow `CODEX_PROTOCOL.md` (in repo root)** — Codex is an adversarial reviewer
to **discuss with iteratively**, not an oracle to defer to. Every Codex finding
requires explicit ACCEPT / PUSH BACK / REQUEST CLARIFICATION with reasoning.
Forbidden behaviors: silent wholesale acceptance, silent rejection, agreement
without recording why. The skill must emit `codex_discussion.md` documenting
the full round-by-round dialogue.

Use `mcp__codex__codex` to get an **independent second opinion** from a different model.
The key design: Codex does NOT see Claude's findings — it forms its own judgment first.

**For each S0/S1 issue found by Claude**, send to Codex:
```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are an adversarial reviewer of mathematical proofs in statistics/ML theory.

    Here is a proof unit from a paper:
    [Paste: lemma statement + proof text + assumptions + dependencies]

    Claude (another AI) claims this proof has a SPECIFIC issue:
    [Paste: issue description, severity, evidence]

    Your tasks:
    1. INDEPENDENTLY verify: do you agree this is a genuine issue?
       - If YES: confirm and rate severity (S0 fatal / S1 major / S2 moderate / S3 minor)
       - If NO: explain why Claude's concern is invalid or overstated
    2. Find issues Claude MISSED: are there other problems in this proof unit?
    3. For each genuine issue: is there an obvious fix?

    Rules:
    - Cite exact equations, line references, or proof steps
    - Do not fabricate issues — "no additional issues found" is a valid answer
    - Be precise about severity: S0 means the main theorem breaks, not just a local gap
```

**For each unit Claude marked "Verified"**, spot-check 20-30% via Codex:
```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are checking a mathematical proof for correctness.

    Here is a proof unit:
    [Paste: lemma statement + proof text + assumptions]

    Another reviewer marked this as "Verified — no issues."
    Your job: try to BREAK this verdict. Look for:
    - Hidden assumptions not listed
    - Inequality direction errors
    - Quantifier mistakes (pointwise vs uniform)
    - Missing edge cases
    - External theorems used outside their conditions

    If you find a genuine issue, describe it with severity and evidence.
    If the proof is indeed correct, say "Confirmed: no issues found" and briefly explain
    why the key steps are valid.
```

**Reconciliation**: After Codex responds, classify each finding:

| Reconciliation | Meaning | Action |
|----------------|---------|--------|
| **Both agree: issue** | High confidence it's real | Keep, upgrade confidence to HIGH |
| **Claude found, Codex disagrees** | Possible false positive | Re-examine manually, add note |
| **Codex found, Claude missed** | Possible blind spot | Add to issue log, mark source = "Codex cross-review" |
| **Both agree: verified** | High confidence correct | Upgrade to "Verified (cross-confirmed)" |

Write reconciliation to `audit/05_adversarial/codex_cross_review.md`.

### Step 7: Pass 5 — Final Report

Every generated artifact begins with the **Artifact Manifest Header** described in `CODEX_PROTOCOL.md`. The manifest lets downstream skills (`proof-repair`, `--post-repair`, `theory-sharpen`) load only what they need and detect staleness against the paper's current state.

Write `audit/06_reports/FINAL_REPORT.md`:

```markdown
---
artifact: audit_final_report
scope: global
source_files: [paper.tex, supplement.tex if Mode B]
theorem_ids: [every theorem / lemma / proposition / corollary in the inventory]
assumption_ids: [every assumption in the assumption ledger]
issue_ids: [every issue in issue_log.md]
commit: [paper-repo short SHA at audit time, or content hash if not in git]
generated: [YYYY-MM-DD HH:MM]
generator: proofcheck v1.7.0 Pass 5
---

# Final Proof-Check Report: [Paper]

## Executive Summary
- Overall verdict:
- Main theorem support:
- Highest severity issue:
- Checked units: X / Y total
- Open issues: N (S0: _, S1: _, S2: _, S3: _)

## Checked Scope
- Sections checked:
- Results checked:
- Results NOT checked:

## Main Dependency Chain
[How main theorem depends on intermediate results]

## Verified Results
| Result | Status | Confidence | Notes |

## Open Issues (ranked by severity)
| ID | Severity | Confidence | Affected result | Summary |

## Conditional Results
| Result | Condition needed | Evidence |

## Recommended Repairs
1. [Repair]

## Final Judgment
[Correct / Correct modulo repairs / Incomplete / Incorrect]
```

Also write `audit/06_reports/issue_log.md` with all issues. Same manifest header (`artifact: issue_log`, `scope: global`).

Per-unit local check files in `audit/04_local_checks/section_*/` carry their own manifest with `scope: local`, `theorem_ids: [single unit being checked]`, and `assumption_ids: [assumptions used in that unit's proof]`. This lets downstream calls (and re-audit) skip loading the full FINAL_REPORT.md when they only need one unit's verdict.

`audit/08_post_repair/RE-AUDIT_REPORT.md` and `audit/08_post_repair/diff_ledger.md` likewise begin with manifest headers; their `scope` is usually `dependency_expanded` (the touched units plus their dependencies) and their `commit` field records the paper-repo SHA at re-audit time, allowing downstream consumers to detect whether the re-audit is fresh.

---

## 19 Common Failure Patterns (Diagnostic Checklist)

### Logical
- Proving weaker statement than claimed
- Assuming the conclusion / circular dependency
- Missing induction base case
- Existence without compactness/coercivity
- Uniqueness used but not proved

### Quantifier
- Pointwise result used as uniform
- Parameter-dependent constant claimed universal
- "∀ε ∃N" confused with "∃N ∀ε"
- High-prob for fixed object used over class without covering

### Probability
- Missing independence
- Conditional probability mishandled
- Event intersection not adjusted
- Expectation bound used as high-prob bound
- Random index in fixed-index concentration

### Analysis
- Limit/expectation exchanged without DCT/MCT/UI
- Derivative/integral exchanged without regularity
- Compactness assumed but not stated

### Algebra & Inequality
- Wrong inequality direction
- Dropping absolute value
- E[XY] = E[X]E[Y] without independence
- Jensen in wrong direction
- Operator/Frobenius/vector norm confused

### Asymptotic & Rate
- O_P used as deterministic O
- Constants in O(·) depend on n
- Dimension/log factors dropped
- Finite-sample theorem proved only asymptotically

### Citation
- External theorem requires stronger assumptions
- External theorem conclusion weaker than needed
- Asymptotic theorem used for finite sample

---

## Paper-Type Adaptations

### Asymptotic Theory
- Check o_P, O_P, o, O usage correctness
- Verify CLT/Lindeberg conditions
- Watch uniform vs pointwise convergence

### Concentration Inequalities
- Check tail conditions (sub-Gaussian, sub-exponential, bounded moment)
- Verify union bounds over infinite classes
- Check δ (failure probability) propagation

### Optimization Theory
- Check convexity/smoothness assumptions
- Verify minima exist (compactness + continuity)
- Watch local vs global optimum confusion

### Markov Chain Theory
- Check drift conditions uniform over parameter space
- Verify small set conditions simultaneous (not pointwise)
- Watch geometric vs plain ergodicity

### M-Estimation
- Check identifiability (unique maximizer)
- Verify score function mean zero
- Check Hessian invertibility

---

## Quick-Start Mode

If time is limited, do the minimal version:

1. Build theorem/lemma inventory
2. Identify main theorem's dependency chain
3. Check final theorem proof
4. Check each direct dependency
5. Track assumptions + notation while checking
6. Run hidden-assumption search on main chain
7. Run constants/rates check on main chain
8. Produce issue log with severity
9. State final confidence + unchecked scope

---

## Session Management

After each checking session, update `PROGRESS.md`:

```markdown
## Session Summary: [Date]
- Proof units checked:
- New verified results:
- New issues:
- Updated dependencies:
- Open blockers:
- Next targets:
```

## Pipeline Integration

This skill is part of a 3-skill pipeline:

```
/proofcheck → /proof-repair → /proofcheck --post-repair → /proof-writer
  Find issues    Fix + literature    Convergence test         Write complete proofs
```

- **Blockage reports** in local checks feed directly into `/proof-repair` Step 1 (Issue Triage)
- **Candidate literature** hints in blockage reports give `/proof-repair` a head start on search
- **Provability triage** (PROVABLE AFTER WEAKENING) tells `/proof-repair` to use Weaken-Claim class
- After `/proof-repair` designs a fix, `/proof-writer` writes the complete corrected proof
- After patches are applied, `/proofcheck --post-repair` performs the convergence test (see Post-Repair Re-Audit Mode below)

To run the full pipeline:
```
/proofcheck papers/my-paper/paper.tex          # Step 1: find all issues (full 6-pass audit)
/proof-repair papers/my-paper/                 # Step 2: design repairs + find literature
/proofcheck --post-repair papers/my-paper/     # Step 2.5: convergence test (delta audit)
/proof-writer [specific claim to rewrite]      # Step 3: write corrected proof text
```

## Post-Repair Re-Audit Mode (`--post-repair`)

Invoked as `/proofcheck --post-repair papers/<paper-name>/`. This is a **focused delta audit**, not a full 6-pass re-run. The goal is to verify that `/proof-repair`'s output actually converged: every originally flagged issue is closed, no new fatal/major issue was introduced by the patches, and the global consistency of assumptions and dependencies still holds.

### When to invoke

- Always after `/proof-repair` finishes a plan that touches any S0 or S1 issue. This is a **HARD GATE**: `/proof-repair` cannot mark `REPAIR_PLAN.md` complete until this mode has run and reports `CONVERGED`.
- Strongly recommended (not gated) after `/proof-repair` on S2/S3-only plans, because patches can still introduce silent regressions even when they target minor issues.
- After applying any human-authored patch to a paper that already has an `audit/` directory, to verify the manual edit did not break a downstream proof.

### Inputs

The mode reads, in order:

1. The original audit at `papers/<paper-name>/audit/` — especially `06_reports/FINAL_REPORT.md`, `06_reports/issue_log.md`, `02_ledgers/{notation,assumption,constants}_ledger.md`, and `03_dependencies/dependency_graph.md`.
2. `papers/<paper-name>/REPAIR_PLAN.md` — the master repair roadmap, including the **Repair Closure Matrix** (see `proof-repair` Step 7A).
3. `papers/<paper-name>/PATCHES.md` — the ordered list of LaTeX modifications, including any **Weaken-Claim change-log table** for repairs that intentionally narrow a claim.
4. The patched paper itself (`papers/<paper-name>/paper.tex`, plus `supplement.tex` if Mode B).
5. `audit/07_repairs/codex_stress_test.md` (if it exists from `/proof-repair` Step 5C) — the per-repair adversarial verdicts, to avoid re-litigating the same questions.

### What it does NOT do

This mode is a delta audit. It explicitly skips:

- The Pass 0 indexing of theorems and lemmas (already done; just reload).
- Step-by-step verification of proofs in units that the repair did not touch.
- Re-running the full hidden-assumption sweep across the whole paper.
- Re-running the proof-strategy classification across all units.
- Sketch detection on untouched units (already classified in the original audit).

If the user wants any of these, they should run full `/proofcheck` instead — but that should be rare for a normal repair cycle.

### What it DOES

#### Step P1: Treat PATCHES.md as the semantic change log

For each entry in PATCHES.md, record what intentionally changed:

- Which unit was edited (lemma, theorem, assumption, definition)
- Whether the change is a **STRUCTURAL EDIT** (proof rewritten, new lemma inserted, missing step filled) or a **SEMANTIC EDIT** (claim weakened, assumption added, rate revised, quantifier tightened)
- For any SEMANTIC EDIT, read the **Weaken-Claim change-log table** (`ORIGINAL CLAIM → REVISED CLAIM → REASON FOR WEAKENING → DOWNSTREAM IMPACT`) in PATCHES.md. If the table is missing for a SEMANTIC EDIT, that itself is a fatal re-audit issue (`RE-AUDIT-NEW-S0`: an undocumented or unpropagated semantic change is a defect even if the algebra is correct).

The audit is performed **against the REVISED claim**, not the ORIGINAL claim. A claim weakening is not a defect when documented; an undocumented or unpropagated weakening is.

#### Step P2: Per-issue closure verification

For every issue in the original `06_reports/issue_log.md`, look up the matching row in the Repair Closure Matrix in REPAIR_PLAN.md. Each row must have one of these terminal statuses:

- `CLOSED-VERIFIED`: the patch addresses the issue; re-audit confirms the unit now passes verification under the revised claim. The original S-level is gone.
- `CLOSED-WEAKENED`: the original claim was found unprovable; the patch weakened it; the weakening is documented in PATCHES.md and propagated to downstream units that consumed the original claim.
- `CLOSED-BLOCKAGE`: the unit could not be repaired; a blockage report exists; the unit is downgraded to NOT CURRENTLY JUSTIFIED in the patched paper, with all downstream consequences propagated (corollaries downgraded, the abstract and introduction no longer cite the unprovable claim).
- `STILL-OPEN`: the patch did not actually close the issue. This is a re-audit failure. The issue carries its original S-level into the re-audit report.
- `WAIVED`: the user explicitly waived the issue with documented rationale (rare, allowed for S2/S3, almost never for S0/S1).

For each `CLOSED-VERIFIED` row, perform a **targeted re-verification** of the touched unit:

- Re-read the unit's local check file from `04_local_checks/section_*/`
- Apply the verification methodology (Pass 1 + Pass 2 + Step Completeness Audit) only to this unit and its direct dependencies that were also touched
- Compare the verification verdict before and after the patch
- Record the result in the re-audit report

For each `CLOSED-WEAKENED` row, verify the **propagation**:

- Identify all downstream units that consumed the original claim (use the dependency graph)
- Check that each downstream unit was either (a) also patched to use the revised claim, (b) downgraded if it required the stronger original claim, or (c) verified to still work under the weaker claim
- Any downstream unit silently using the original strength is a `NEW-S0` propagation defect.

#### Step P3: New-issue scan on touched units

For every unit edited by a patch (per PATCHES.md), run a **focused new-issue scan**. This is narrower than the full Pass 5 adversarial pass; it asks only: did the patch introduce a new issue that did not exist in the original audit?

Checks performed:

- New hidden assumption in the patched proof (proof now relies on a condition not in the assumption block)
- New quantifier mismatch (pointwise vs uniform, ∀∃ order, etc.) introduced by the patch
- New constant or rate dependence in the patched proof (e.g., the patched bound has a worse rate than the unit's role in the dependency chain requires)
- New circular dependency created by inserting a new lemma
- New notation drift between body and supplement caused by the patch
- New cross-file reference broken by Mode B numbering changes

Issues found in this step are labeled `NEW-S0`, `NEW-S1`, `NEW-S2`, `NEW-S3`. They are distinct from `STILL-OPEN` issues, which are original-audit issues the patch failed to close.

#### Step P3.5: Ladder-discipline check (semantic-edit audit)

This step audits the repair ladder discipline introduced in `/proof-repair` Step 3. It is a documentation-and-propagation check only. The re-audit does **not** try to re-solve whether a cleverer Phase A repair existed; that is not the job of the convergence test.

**For any repair with chosen ladder level `L4` (Add-Assumption):**

Verify all of the following:

1. The per-issue repair file contains a `## Repair Ladder Defense` block.
2. The `Phase A Exhaustion Record` is present and non-empty for the relevant lower-level branches.
3. The chosen repair is marked `Claim preserved: yes` and `Assumptions preserved: no`.
4. An `## Assumption-Extension Change Log` row exists for the issue.
5. The added assumption in the log matches the assumption actually inserted into the patched theorem / lemma / assumption block.
6. The `Scientific-scope impact` field is filled.
7. Every downstream unit listed in `Propagation to downstream theorems/lemmas` has a corresponding patch in PATCHES.md or a documented re-verification.
8. The patched paper's assumption ledger reflects the new assumption consistently and without contradiction.

If any item fails, record a new re-audit issue:
- `NEW-S0` for missing log row, missing propagation, or silent assumption injection
- `NEW-S1` for incomplete scope-impact documentation or inconsistent assumption bookkeeping

**For any repair with chosen ladder level `L5` (Weaken-Claim):**

Verify all of the following:

1. The per-issue repair file contains a `## Repair Ladder Defense` block.
2. The `Phase A Exhaustion Record` is present and non-empty for the relevant lower-level branches.
3. The chosen repair is marked `Claim preserved: no`.
4. A `## Weaken-Claim Change Log` row exists for the issue / patch.
5. The revised claim in the log matches the claim actually inserted into the patched paper.
6. Every downstream consumer listed in the change log has a corresponding propagation patch or documented downgrade.
7. The abstract, introduction, corollaries, and applications no longer silently use the original stronger claim.

If any item fails, record a new re-audit issue:
- `NEW-S0` for missing change-log row, silent weakening, or missing downstream propagation
- `NEW-S1` for incomplete documentation of the weakening rationale

**For repairs at L1, L2, L3 (Phase A) or L6 (blockage):**

Verify only that the Repair Ladder Defense block is present with the correct level recorded. No semantic-edit log is required for Phase A repairs.

**Scope limit of this check:**

This ladder-discipline check verifies:
- presence of the required escalation artifacts,
- propagation of semantic edits,
- consistency of the patched paper with those edits.

It does **not** require the re-audit to prove that no better Phase A repair existed. Disputing the choice of ladder level itself is out of scope; the re-audit's job is to verify the discipline, not to second-guess the design.

#### Step P4: Global consistency re-run (assumption ledger + dependency graph only)

Re-build the assumption ledger and the dependency graph from the patched paper. Compare against the originals:

- New assumptions introduced anywhere → must be consistent with the existing assumption set (no contradictions) and must be acknowledged in the relevant statement (no silent injection)
- Removed assumptions → must be justified (e.g., the patch tightened a lemma so the assumption is no longer used)
- New dependency edges → must not create circularity
- Notation ledger drift → must be reconciled across body and supplement

This step is the integration test. It catches the silent breakage that `Step 5C` adversarial per-repair tests cannot see, because per-repair tests do not have a global view of the post-patched paper.

#### Step P5: Assumption / Rate Diff Ledger

Generate `audit/08_post_repair/diff_ledger.md`. This is a compact, machine-readable diff across the entire dimensional structure of the paper:

```markdown
# Assumption / Rate Diff Ledger

Generated by /proofcheck --post-repair on [date]. Compares the patched paper
against the pre-patch audit baseline.

## Assumption diff
| Assumption | Pre-patch scope | Post-patch scope | Change | Justified? |
|---|---|---|---|---|
| A1 (i.i.d.) | Global | Global | unchanged | n/a |
| A2 (strong convexity) | Global | Sec 3 only | NARROWED | yes (Patch 4 splits cases) |
| A_new1 (4th moment) | — | D.2 local | ADDED | yes (Patch 7, required by Lemma B.5 fix) |
| A_old3 (Hessian invertibility) | Global | — | DROPPED | yes (Patch 2 supplies it from C.3) |

## Rate / constant diff
| Object | Pre-patch | Post-patch | Change | Downstream impact |
|---|---|---|---|---|
| Thm 2.1 rate | $O(n^{-1/2})$ | $O(n^{-1/2})$ | unchanged | n/a |
| Cor 2.2 rate | $O(n^{-1/2})$ | $O(n^{-1/2} \log n)$ | DEGRADED by log | Sec 5 application paragraph now overstates; PATCH NEEDED |
| Lemma C.3 constant | universal | $\propto p^{1/2}$ | DIMENSION-DEPENDENT | review whether Thm 2.1 still holds uniformly in $p$ |

## Probability level diff
| Statement | Pre-patch | Post-patch | Change |
|---|---|---|---|
| Thm 3.1 high-prob | $1 - 2e^{-c n}$ | $1 - 2 e^{-c \log n}$ | WEAKER probability level |

## Norm / metric diff
| Object | Pre-patch norm | Post-patch norm | Change |
|---|---|---|---|

## Sample-size regime diff
| Statement | Pre-patch regime | Post-patch regime | Change |
|---|---|---|---|

## Dependency requirement diff
| Edge | Pre-patch direction | Post-patch direction | Change |
|---|---|---|---|

## Summary
Total diffs: N
Justified: M
Unjustified or unpropagated: K  ← K > 0 means re-audit is NOT CONVERGED
```

The diff ledger is the single most useful artifact for catching the failure mode Codex flagged: **most bad repairs are not algebraic errors; they are silent strengthening, silent rate degradation, or silent incompatibility across lemmas.** The ledger forces these into the open.

A row is `Unjustified or unpropagated` when:

- An assumption was added without a Weaken-Claim change-log row in PATCHES.md
- A rate degraded without the downstream consumers being updated
- A probability level weakened without the corollaries being adjusted
- A norm changed without the related statements being reconciled

Any unjustified row triggers `NEW-S0` or `NEW-S1` in the convergence decision.

#### Step P6: Convergence decision

The re-audit produces one of three terminal states.

- `CONVERGED`: every original S0/S1 issue is `CLOSED-VERIFIED`, `CLOSED-WEAKENED`, or `CLOSED-BLOCKAGE`; no `STILL-OPEN` S0/S1; no `NEW-S0` or `NEW-S1`; the diff ledger has zero unjustified rows. The repair phase is complete; the user may advance to `/theory-sharpen` or submission.
- `NOT CONVERGED — RE-REPAIR REQUIRED`: at least one of `STILL-OPEN-S0`, `STILL-OPEN-S1`, `NEW-S0`, `NEW-S1`, or an unjustified diff row remains. The user invokes `/proof-repair --from-reaudit` to address only the residual issues. Auto-triggering is forbidden; the user must explicitly confirm.
- `NOT CONVERGED — HUMAN INTERVENTION REQUIRED`: the re-audit detected a change in theorem intent, paper-level claim, or dependency structure that exceeds what a re-repair cycle can handle. Examples: the patched paper's contribution is now meaningfully different from the abstract; a Weaken-Claim repair was not propagated to the introduction's stated rate; the new assumption changes the paper's empirical scope. The user must review and decide whether to revert, restate the paper's contribution, or change venue.

The convergence decision is written to `audit/08_post_repair/CONVERGENCE_VERDICT.md`.

### Outputs

```
papers/<paper-name>/audit/08_post_repair/
  RE-AUDIT_REPORT.md           # Main delta-audit report
  diff_ledger.md               # Assumption / rate / constant / probability / norm / regime diff
  CONVERGENCE_VERDICT.md       # CONVERGED / NOT CONVERGED + reason
  per_issue_closure.md         # Per-original-issue closure verification
  new_issues.md                # NEW-S0/S1/S2/S3 detected by patches
```

Every file in `08_post_repair/` begins with the Artifact Manifest Header (see `CODEX_PROTOCOL.md`). For these post-repair artifacts:
- `scope: dependency_expanded` (the touched units plus their direct dependencies)
- `theorem_ids` lists every unit whose patch is verified by this artifact
- `assumption_ids` lists every assumption referenced (original + new from patches)
- `issue_ids` lists every original issue verified for closure plus every NEW-S* issue created
- `commit` is the paper-repo short SHA at re-audit time (so downstream can detect staleness if a later patch lands)

### Interaction with Codex Step 5C

The per-repair Codex adversarial stress-test in `/proof-repair` Step 5C and this post-repair re-audit are **complementary, not redundant**:

- Step 5C asks: *"Can this individual repair be broken in isolation?"* — local adversarial test.
- `--post-repair` asks: *"Did the patched paper as a whole converge?"* — integration test.

Step 5C cannot detect:

- A repair to Lemma 3 that no longer correctly feeds Theorem 1
- A weakened rate in a lemma that breaks a corollary's rate
- A new assumption in Lemma 5 that contradicts an existing assumption in Lemma 8
- A silent change in the paper's headline claim that downstream sections do not reflect

`--post-repair` is the only mechanism that catches these. Both must exist; neither subsumes the other.

### When NOT to run

- The user has only changed comments, typos, or notation cosmetics that the diff ledger would record as zero-impact. A full re-audit is overkill.
- The original audit found zero S0/S1/S2 issues (paper was already verified) and no patches were applied. There is nothing to re-audit.
- The user is actively rewriting the paper's framework and the original audit no longer reflects the current paper structure. Re-run full `/proofcheck` instead.

## Final Acceptance Criteria

A proof check is complete only when:
- Every main theorem dependency identified
- Every critical dependency locally checked or marked conditional
- No unresolved S0 issues
- All S1 issues repaired, downgraded, or explicitly reported
- Assumption propagation checked
- Notation drift checked
- Constants/rates/probability/quantifiers checked for main chain
- Circular dependencies ruled out or reported
- Final report states checked AND unchecked scope honestly

A repair cycle is complete only when, after `/proof-repair`:
- `/proofcheck --post-repair` has been invoked (HARD GATE if any S0 or S1 issue existed in the original audit)
- `CONVERGENCE_VERDICT.md` reports `CONVERGED`
- Every original S0/S1 issue has a terminal closure status (`CLOSED-VERIFIED`, `CLOSED-WEAKENED`, or `CLOSED-BLOCKAGE`)
- The diff ledger has no unjustified rows
- No `NEW-S0` or `NEW-S1` issues introduced by patches remain open
