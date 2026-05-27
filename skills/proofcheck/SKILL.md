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

For EACH proof unit, create one file: `audit/04_local_checks/section_X/{ID}_{name}_check.md`

Each file follows this template:

```markdown
## Proof Unit: [ID / Name]
- Location:
- Type: [definition / lemma / proposition / theorem / proof segment]
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

Write `audit/06_reports/FINAL_REPORT.md`:

```markdown
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

Also write `audit/06_reports/issue_log.md` with all issues.

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
/proofcheck → /proof-repair → /proof-writer
  Find issues    Fix + literature    Write complete proofs
```

- **Blockage reports** in local checks feed directly into `/proof-repair` Step 1 (Issue Triage)
- **Candidate literature** hints in blockage reports give `/proof-repair` a head start on search
- **Provability triage** (PROVABLE AFTER WEAKENING) tells `/proof-repair` to use Weaken-Claim class
- After `/proof-repair` designs a fix, `/proof-writer` writes the complete corrected proof

To run the full pipeline:
```
/proofcheck papers/my-paper/paper.tex    # Step 1: find all issues
/proof-repair papers/my-paper/           # Step 2: design repairs + find literature
/proof-writer [specific claim to rewrite] # Step 3: write corrected proof text
```

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
