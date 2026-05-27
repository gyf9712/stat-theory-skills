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
allowed-tools: Bash(*), Read, Write, Edit, Grep, Glob, Agent, WebSearch, WebFetch
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

## Context: $ARGUMENTS

---

## Step 0: Locate Inputs

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

---

## Step 1: Issue Triage & Repair Classification

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
| **Weaken-Claim** | Theorem claims more than proved | Maybe — find if stronger result exists elsewhere |
| **Strengthen-Proof** | Gap in reasoning, but claim is likely true | Yes — find technique/lemma to fill the gap |
| **Insert-Lemma** | Missing intermediate step | Yes — may exist as known result in literature |
| **Replace-Technique** | Current technique fundamentally flawed | Yes — find alternative proof strategy |
| **Fix-Constants** | Rates, bounds, or constants wrong | Maybe — check if correct constants known |
| **Fix-Quantifiers** | Pointwise↔uniform, ∀∃ order, etc. | Maybe — find uniform versions of cited results |
| **Notation-Fix** | Symbol drift, type mismatch | No |
| **Citation-Fix** | External theorem misapplied | Yes — find correct version or alternative theorem |

### Priority Rules

- **P0**: S0 issues + any S1 issue on the critical path to main theorem
- **P1**: S1 issues not on critical path + S2 issues affecting ≥3 downstream units
- **P2**: Remaining S2 + all S3

---

## Step 2: Dependency Impact Analysis

For each P0 and P1 issue, trace the **full downstream impact** using the dependency graph:

```markdown
## Impact Analysis: I-01 (Lemma C.3 — hidden invertibility assumption)

### Direct dependents
- Lemma C.5 (uses C.3 conclusion directly)
- Theorem 2.1 (assembles C.3 + C.5)

### Transitive dependents
- Corollary 2.2 (follows from Thm 2.1)
- Section 4 applications (all use Cor 2.2)

### Repair constraint
Any fix to C.3 must:
1. Not strengthen assumptions of Thm 2.1 beyond what the paper's intro promises
2. Preserve the rate O(n^{-1/2}) in Thm 2.1
3. Keep the constant universal (not parameter-dependent)

### Cascading repairs needed?
- If we add "H is invertible" to C.3, must verify C.5 and Thm 2.1 still hold
- Check: does the application section provide invertibility naturally?
```

Build a **Repair Dependency DAG**: some repairs must happen before others (e.g., fixing
a base lemma assumption before fixing the theorem that uses it).

---

## Step 3: Generate Candidate Repairs (per issue)

For each issue, generate 1-3 candidate repair strategies ranked by invasiveness:

```markdown
## Repair Candidates: I-01 (Lemma C.3 — hidden invertibility assumption)

### Candidate A: Minimal — Add explicit assumption (invasiveness: LOW)
- Add "Assume H(θ) is invertible for all θ ∈ Θ" to Lemma C.3 statement
- Propagate to Theorem 2.1 assumptions
- Check: is this already implied by existing Assumption 2 (strong convexity)?
- Risk: may narrow the theorem's applicability

### Candidate B: Prove invertibility — Insert supporting lemma (invasiveness: MEDIUM)
- Add Lemma C.3' proving H(θ) invertibility under existing assumptions
- Needs: strong convexity (Assumption 2) ⟹ H(θ) ≻ 0
- Advantage: no new assumptions needed in main theorem
- Literature needed: standard result connecting strong convexity to Hessian invertibility

### Candidate C: Alternative technique — Avoid inversion entirely (invasiveness: HIGH)
- Replace matrix inversion step with pseudo-inverse + regularization
- Requires reworking Eqs. (47)-(52)
- May change constants but preserves rate
- Literature needed: perturbation theory for pseudo-inverse in M-estimation
```

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

## Step 4: Literature Search for Repair Support

For EACH candidate repair that needs literature support, run a targeted multi-source search.

**Guiding principle**: A proof repair is only as credible as its references. Prioritize
results from top-tier venues; treat unreviewed preprints as supplementary evidence only.

### 4A: Venue Credibility Tiers

All search results MUST be classified by venue tier before recommendation.

**Tier 1 — Gold Standard** (prefer these; a single T1 citation can anchor a repair)

| Domain | Venues |
|--------|--------|
| Statistics "Big 4" | Annals of Statistics (AoS), Journal of the American Statistical Association (JASA), Journal of the Royal Statistical Society Series B (JRSS-B), Biometrika |
| Probability | Annals of Probability, Probability Theory and Related Fields, Stochastic Processes and their Applications |
| Mathematics | Annals of Mathematics, Inventiones Mathematicae, Acta Mathematica, CPAM |
| ML/AI Top Conferences | NeurIPS, ICML, ICLR, COLT, ALT, AISTATS |
| ML Journals | Journal of Machine Learning Research (JMLR), Machine Learning (Springer) |
| Econometrics | Econometrica, Journal of Econometrics (JOE), Review of Economic Studies, Journal of Business & Economic Statistics (JBES) |
| Optimization | Mathematical Programming, SIAM Journal on Optimization, Mathematics of Operations Research |
| Applied Math / Numerical | SIAM Review, SIAM Journal on Numerical Analysis, Mathematics of Computation |
| Authoritative Textbooks | Springer GTM/Lecture Notes, Cambridge Tracts, Princeton Series in Applied Mathematics |

**Tier 2 — Strong** (acceptable, especially alongside a T1 reference)

| Domain | Venues |
|--------|--------|
| Statistics | Electronic Journal of Statistics (EJS), Bernoulli, Statistica Sinica, Scandinavian Journal of Statistics |
| ML/AI | AAAI, IJCAI, UAI, KDD, JAIR |
| Math | Transactions AMS, Journal of Functional Analysis, Advances in Mathematics |
| Econometrics | Econometric Theory, Journal of Applied Econometrics, Econometric Reviews |
| Applied | IEEE Trans. on Information Theory, IEEE Trans. on Signal Processing |

**Tier 3 — Supplementary** (use only when T1/T2 unavailable; flag as lower confidence)

| Source | Use case |
|--------|----------|
| arXiv preprints (not yet published) | Cutting-edge technique, no peer-reviewed version yet |
| Workshop papers (NeurIPS/ICML workshops) | Preliminary results |
| Technical reports / working papers | University reports, NBER working papers |
| Conference papers outside top tier | Regional or secondary conferences |

**Tier 4 — Avoid** (do NOT cite unless absolutely no alternative exists)

| Source | Reason |
|--------|--------|
| Unpublished manuscripts with no arXiv ID | No traceability |
| Blog posts, lecture slides, StackExchange | Not citable in academic work |
| Retracted papers | Compromised |
| Predatory journals (check Beall's list heuristics) | Unreliable peer review |

### Credibility Scoring Rules

1. **T1 published + high citations (≥50)** → Credibility: GOLD — use as primary anchor
2. **T1 published + moderate citations (10-49)** → Credibility: STRONG — reliable
3. **T1 published + low citations (<10) or very recent** → Credibility: ACCEPTABLE — verify theorem carefully
4. **T2 published** → Credibility: GOOD — acceptable, prefer T1 if available
5. **T3 arXiv preprint, ≥20 citations** → Credibility: CONDITIONAL — acceptable if theorem is self-contained and verifiable
6. **T3 arXiv preprint, <20 citations** → Credibility: WEAK — use only if no alternative; must verify theorem step-by-step
7. **T4 any** → Credibility: REJECT — do not cite

**When two references support the same repair, always prefer the higher-tier one.**
**When a preprint exists alongside its published version, always cite the published version.**

### 4B: Formulate Search Queries

Convert each repair need into 2-3 precise search queries, targeting different source types:

```
Issue: Hidden invertibility assumption in M-estimation Hessian
Repair: Prove invertibility from strong convexity

Query 1 (textbook/classic): "strong convexity Hessian positive definite" 
  → target: T1 textbooks (Boyd, Nesterov, Rockafellar)
Query 2 (journal result): "minimum eigenvalue Hessian strongly convex M-estimation"
  → target: AoS, JASA, Biometrika, JMLR, Econometrica
Query 3 (recent technique): "M-estimator regularity condition relaxation"
  → target: recent NeurIPS/ICML/COLT + stat.TH arXiv
```

### 4C: Multi-Source Search (parallel)

Launch parallel searches using Agent tool, each with venue-awareness:

**Agent 1: arXiv + Published Venue Cross-Check**
```
Search arXiv for: [query]
Focus on stat.TH, math.ST, stat.ML, cs.LG categories
Prefer papers from last 5 years

For each hit:
1. Check if it has a PUBLISHED version (journal or conference)
   - Look for DOI, "published in [venue]" in abstract/comments
   - If published: record the venue and cite the published version
   - If preprint only: flag as T3, record citation count
2. Extract the specific theorem/lemma that supports our repair
3. Assign venue tier (T1/T2/T3)

Return: title, authors, year, arxiv ID, published venue (if any), tier, 
        citation count, the exact theorem statement
```

**Agent 2: Semantic Scholar (venue-filtered)**
```
Use WebFetch on Semantic Scholar API:
https://api.semanticscholar.org/graph/v1/paper/search?query=[encoded-query]&limit=20&fields=title,authors,year,abstract,externalIds,citationCount,venue,publicationTypes

Apply filters:
- First pass: venue matches T1 list → take all
- Second pass: venue matches T2 list → take if citationCount > 10
- Third pass: remaining → take only if citationCount > 50

Return: title, authors, year, venue, tier, citation count, DOI, relevant theorem
```

**Agent 3: Targeted High-Quality Source Search**
```
WebSearch for: [query] site:projecteuclid.org OR site:jstor.org OR site:springer.com OR site:jmlr.org

These sites host T1/T2 journals directly:
- projecteuclid.org → AoS, Annals of Prob, Bernoulli, EJS
- jstor.org → Econometrica, JASA, JRSS-B, Biometrika, AoS
- jmlr.org → JMLR
- springer.com → Math Programming, Prob Theory & Related Fields

Also search: [query] + "textbook" OR "monograph" for authoritative book references

Return: title, authors, year, venue/publisher, tier, the standard reference for this result
```

### 4D: Evaluate & Rank Search Results

For each paper found, build a **Credibility-Weighted Evaluation Table**:

| Paper | Venue | Tier | Citations | Credibility | Theorem | Matches need? | Assumptions OK? | Recommend? |
|-------|-------|------|-----------|-------------|---------|---------------|-----------------|------------|
| van der Vaart (1998) | Cambridge UP (textbook) | T1 | 10k+ | GOLD | Thm 5.41 | Exact | Yes | **PRIMARY** |
| Chen & Li (2022) | AoS | T1 | 35 | STRONG | Lemma 3.1 | Close variant | Check condition 2 | **SECONDARY** |
| Zhang (2024) | arXiv only | T3 | 8 | WEAK | Thm 2 | Exact but new | Unverified | SUPPLEMENTARY |
| Anonymous (2023) | ICML workshop | T3 | 2 | WEAK | Prop 1 | Partial | Unknown | SKIP |

**Selection priority**: PRIMARY > SECONDARY > SUPPLEMENTARY. Always include at least
one T1 reference per repair if possible. If only T3 available, flag explicitly in
repair plan as "lower confidence — needs independent verification."

### 4E: Verify Cited Results (with venue-appropriate rigor)

For each recommended paper, do a verification proportional to its tier:

**T1 Gold/Strong references (textbooks + top journals)**:
1. Fetch the exact theorem statement
2. Verify: do OUR assumptions satisfy THEIR prerequisites?
3. Verify: does THEIR conclusion give us exactly what we need?
4. Check: notation compatibility, constants, finite-sample vs asymptotic
5. Trust level: HIGH — can cite with confidence after prerequisite check

**T2 Good references**:
1. All T1 checks, PLUS:
2. Verify the theorem is not from a corrigendum or errata
3. Cross-reference with at least one T1 source for the same or similar result

**T3 Supplementary references (preprints, workshops)**:
1. All T1 checks, PLUS:
2. Read the proof of the cited theorem (not just the statement)
3. Verify the proof is complete and does not itself have gaps
4. Check if the result has been independently reproduced or cited by T1/T2 papers
5. Trust level: LOW — must note "preprint, not yet peer-reviewed" in repair plan

**This prevents citation misuse** — the same error class we check for in /proofcheck.

### 4F: Fallback When No High-Quality Reference Found

If no T1/T2 reference supports a repair:

1. **Can the result be proved from scratch?** → Write it as a new lemma (Step 5B)
   with proof, and note "self-contained proof, no external reference needed"
2. **Is a classic textbook result?** → Cite the most authoritative textbook even
   if not found via search (e.g., Durrett for probability, Billingsley for
   convergence, Rockafellar for convex analysis, van der Vaart for asymptotics,
   Tsybakov for nonparametric estimation)
3. **Only T3 preprint available?** → Cite it but add:
   ```
   ⚠ Reference [X] is an arXiv preprint (not peer-reviewed).
   The cited theorem was independently verified during this repair.
   Consider replacing with a published reference when available.
   ```
4. **No reference at all?** → Write the complete proof yourself (Step 5B) and mark
   the repair as "self-proved — review recommended"

---

## Step 5: Assemble Repair Plan

For each issue, select the best candidate and write a detailed repair specification.

Create per-unit repair files: `audit/07_repairs/section_X/{ID}_repair.md`

```markdown
## Repair: I-01 — Lemma C.3 invertibility assumption

### Selected Strategy: Candidate B (Insert supporting lemma)

### Reason for Selection
- Candidate A adds assumption to main theorem (undesirable)
- Candidate B proves invertibility from existing assumptions (minimal impact)
- Candidate C is too invasive (rewrites 6 equations)

### Mathematical Fix

**New Lemma C.3' (to insert before Lemma C.3)**:

Under Assumption 2 (strong convexity with parameter μ > 0),
the Hessian H(θ) satisfies λ_min(H(θ)) ≥ μ for all θ ∈ Θ.

Proof sketch:
By strong convexity, ∇²f(θ) ≽ μI for all θ.
Since H(θ) = E[∇²f(θ)], and expectation preserves PSD ordering,
H(θ) ≽ μI, so λ_min(H(θ)) ≥ μ > 0.  □

### Literature Support

| # | Reference | Venue/Tier | Credibility | What it provides | BibTeX key |
|---|-----------|-----------|-------------|------------------|------------|
| 1 | Boyd & Vandenberghe (2004), Convex Optimization, §9.1.2 | Cambridge UP (T1 textbook) | GOLD | Strong convexity ⟹ H ≻ 0 | boyd2004convex |
| 2 | Nesterov (2018), Lectures on Convex Optimization, Thm 2.1.10 | Springer (T1 textbook) | GOLD | λ_min bound from strong convexity | nesterov2018lectures |

### LaTeX Patch

Location: paper.tex, after line [XXX] (end of Lemma C.2 proof)

```latex
\begin{lemma}[Hessian invertibility]\label{lem:hessian-invert}
Under Assumption~\ref{assump:strong-convex}, for all $\theta \in \Theta$,
$\lambda_{\min}(H(\theta)) \geq \mu > 0$.
\end{lemma}
\begin{proof}
By strong convexity (Assumption~\ref{assump:strong-convex}),
$\nabla^2 f(x;\theta) \succeq \mu I$ for all $x$ and $\theta \in \Theta$.
Taking expectations preserves the Loewner order, so
$H(\theta) = \mathbb{E}[\nabla^2 f(X;\theta)] \succeq \mu I$.
\end{proof}
```

### Repair Provability Status
PROVABLE AS STATED — invertibility follows from strong convexity (Assumption 2)

### Proof Strategy for New Content
Direct (strong convexity → PSD Hessian → positive minimum eigenvalue)

### Downstream Verification Checklist
- [ ] Lemma C.3: replace "H(θ) is invertible" with "by Lemma C.3'"
- [ ] Lemma C.5: no change needed (inherits through C.3)
- [ ] Theorem 2.1: no new assumptions (invertibility now proved)
- [ ] Corollary 2.2: no change needed

### Open Risks
- [Any remaining fragile points after this repair]
```

---

## Step 5B: Write Complete Repaired Proofs (via /proof-writer methodology)

For each repair that involves new proof content (Insert-Lemma, Strengthen-Proof,
Replace-Technique), write a COMPLETE proof — not just a sketch.

Apply /proof-writer's rigor standards:

1. **Claim normalization**: Restate the repaired claim with all quantifiers, domains, types explicit
2. **Dependency map**: List every fact the new proof depends on
3. **Numbered steps**: Every step justified, no "clearly/obviously/standard arguments"
4. **Edge cases**: Handle or explicitly exclude degenerate cases
5. **Final verification**: Theorem statement matches exactly what was proved

Write each complete proof into the repair file under a new section:

```markdown
### Complete Repaired Proof

**Repaired Claim** (normalized):
[Exact statement with all quantifiers and assumptions]

**Proof Strategy**: [chosen strategy from Step 3]

**Dependency Map**:
1. This proof uses: [list]
2. Assumption A2 provides: [what]
3. New reference [Smith 2023, Thm 3.2] provides: [what]

**Proof**:
Step 1. [justified step]
Step 2. [justified step]
...
Therefore [conclusion]. ∎

**Verification Checklist**:
- [ ] Statement matches what was proved (not stronger)
- [ ] Every assumption used is listed
- [ ] Every nontrivial implication justified (no "clearly")
- [ ] Every inequality direction correct
- [ ] Every cited result applicable under stated assumptions
- [ ] Edge cases handled or excluded
- [ ] No hidden dependence on unproved lemma
```

If the complete proof cannot be written honestly, downgrade the repair status:
- If proof works but under extra conditions → status: PROVABLE AFTER WEAKENING
- If proof hits a wall → status: NOT CURRENTLY JUSTIFIED + blockage report

**This is the key quality gate**: a repair is only "complete" when the full proof is
written and verified, not when the strategy is sketched.

### Step 5C: Codex Adversarial Stress-Test of Repairs (if Codex MCP available)

After Claude writes each repair + proof, send it to Codex for adversarial stress-testing.
Codex's job: try to BREAK the proposed repair.

**For each P0/P1 repair with a complete proof**:
```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are stress-testing a proposed REPAIR to a mathematical proof in a statistics/ML
    theory paper. The original proof had an issue; a fix has been proposed.

    ORIGINAL ISSUE:
    [Paste: issue description, affected unit, severity]

    PROPOSED REPAIR:
    [Paste: repair strategy, new/modified lemma statement, complete proof]

    NEW REFERENCES CITED:
    [Paste: each cited result with venue, theorem statement, assumptions]

    Your tasks (be adversarial — try to break it):
    1. Is the repaired proof ACTUALLY correct?
       - Check every step for validity
       - Check inequality directions, quantifier order, edge cases
       - Check that cited references actually provide what is claimed
    2. Does the repair INTRODUCE new problems?
       - New hidden assumptions?
       - Changed constants or rates?
       - Broken downstream dependencies?
    3. Is the repair MINIMAL?
       - Could a simpler fix work?
       - Are the new assumptions weaker than necessary?
    4. Are the cited references APPROPRIATE?
       - Do their prerequisites match our setting?
       - Is there a stronger/more standard reference?

    Output:
    - PASS: repair is correct and minimal
    - FIXABLE: repair has issues but they're minor [list them]
    - FAIL: repair is fundamentally flawed [explain why]
```

If Codex returns FIXABLE or FAIL:
1. Address Codex's specific objections
2. Revise the repair
3. Re-submit to Codex (use `mcp__codex__codex-reply` on the same thread)
4. Iterate until PASS or document the disagreement

Write results to `audit/07_repairs/codex_stress_test.md`:
```markdown
| Repair | Codex verdict | Issues raised | Resolved? | Final status |
|--------|--------------|---------------|-----------|-------------|
| I-01 | PASS | None | — | Confirmed |
| I-03 | FIXABLE | Edge case d=1 not handled | Yes, added | Confirmed after revision |
| I-05 | FAIL → revised → PASS | Original proof had sign error | Rewritten | Confirmed after rewrite |
```

---

## Step 6: Cross-Repair Consistency Check

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

## Step 7: Write Master Repair Plan + Bibliography

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

## Repair Priority Order

Execute repairs in this order (respects dependency DAG):

### Phase 1: Foundation Repairs (do first)
| Issue | Unit | Repair Class | Strategy | New refs needed |
|-------|------|-------------|----------|-----------------|

### Phase 2: Critical Path Repairs
| ... |

### Phase 3: Support Repairs
| ... |

## Per-Issue Repair Specifications
[Link to each audit/07_repairs/section_X/*_repair.md file]

## New References Summary
| # | Key | Full citation | Venue | Tier | Credibility | Supports repair of | Verified? |
|---|-----|--------------|-------|------|-------------|-------------------|-----------|

## Reference Quality Summary
- T1 (Gold Standard) references: X / Y total
- T2 (Strong) references: _
- T3 (Supplementary / preprint): _ ← flag each with ⚠ if used
- Self-proved lemmas (no external ref): _

## Consistency Verification
- [ ] Assumption matrix: no contradictions
- [ ] Rate propagation: main theorem rate preserved
- [ ] New references: mutually compatible
- [ ] New references: all T1/T2 venue verified (no predatory journals)
- [ ] T3 preprint references: cited theorems independently verified
- [ ] Downstream units: all re-verified after repair

## Residual Issues (cannot repair without major rework)
| Issue | Why unrepairable | Impact |
```

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

Write `papers/<paper-name>/PATCHES.md` with all LaTeX modifications in order:

```markdown
# LaTeX Patches — Apply in Order

## Patch 1: Insert Lemma C.3' (Hessian invertibility)
- File: paper.tex
- After line: [XXX]
- Insert: [the latex block]

## Patch 2: Fix Theorem 3.1 rate from O(n^{-1}) to O(n^{-1} log n)
- File: paper.tex
- Line: [YYY]
- Change: `O(n^{-1})` → `O(n^{-1} \log n)`

## Patch 3: Add new bibliography entries
- File: references.bib
- Append: [entries from repair_references.bib]
```

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
  1. Review REPAIR_PLAN.md — accept/reject each repair
  2. For complex repairs, run: /proof-writer [specific repaired claim]
     to get publication-ready proof text
  3. Apply patches: /proof-repair --apply to auto-patch paper.tex
  4. Re-verify: /proofcheck papers/my-paper/ to confirm repairs hold
```
