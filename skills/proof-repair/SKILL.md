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

### Step 0B: Detect Reference Mode (MANDATORY before any LaTeX patch)

JASA / AoS / Biometrika / JRSS-B / Econometrica submissions typically separate
**Main Text** and **Supplementary Material** into TWO compiled PDF files. LaTeX
`\ref{}` does NOT work across files (without the fragile `xr` package), so every
cross-file citation must use **hard-coded numbers**, not `\ref{}`.

Detect the paper's reference mode BEFORE writing any LaTeX patches:

**Mode A: Single-file paper** (one .tex compiles to one PDF)
- Most arXiv preprints, NeurIPS/ICML/ICLR (one combined PDF)
- Use `\label{...}` and `\ref{...}` / `\eqref{...}` / `\cref{...}` freely
- Any new lemma/equation gets a `\label{}`

**Mode B: Two-file submission** (separate main.tex + supplement.tex → two PDFs)
- Common for JASA, AoS, Biometrika, JRSS-B, Econometrica, JBES
- Identify by:
  - Multiple top-level .tex files (e.g., `paper.tex` + `supplement.tex` /
    `appendix.tex` / `supp.tex`)
  - Author's `cover_letter.txt` or submission notes mentioning "supplement"
  - Section labeled "Online Supplement" / "Supplementary Material" at end of paper
- **Reference rules**:
  - Within the same file → use `\ref{...}` as normal
  - Across files (main↔supplement) → **NEVER use `\ref{}`** (it won't compile)
  - Cross-file references must use hard-coded numbers:
    - "Lemma S.3" (S prefix for supplement items)
    - "Theorem 2.1 of the main text" (when supplement refers to main)
    - "equation (S.7)" (equations in supplement use S.N numbering)
  - When patching, you must KNOW the supplement's lemma numbering scheme to insert
    the right hard-coded number

**Detection procedure**:
```bash
# Count top-level .tex files (excluding those \input'd by others)
find papers/<paper-name> -maxdepth 2 -name "*.tex" -type f

# Check for explicit supplement files
ls papers/<paper-name>/{supp*,supplement*,appendix*}.tex 2>/dev/null

# Check for S-prefix labels (signal of two-file mode)
grep -l "\\label{.*:S\\.\|\\label{S" papers/<paper-name>/*.tex
```

If two .tex files exist with parallel content (one shorter "main", one longer
"supp"), this is Mode B. Confirm with the user before proceeding.

**Where in REPAIR_PLAN.md to record**:
```markdown
## Reference Mode
Mode: [A: single-file / B: two-file main+supplement]
Files:
  - paper.tex (main text)
  - supplement.tex (supplementary material)  [if Mode B]
Numbering scheme (Mode B):
  - Main text: 1, 2, 3, ...
  - Supplement: S.1, S.2, S.3, ... (or "S1, S2, S3")
Cross-file citation style: hard-coded numbers + "of the supplement" / "of the main text"
```

All LaTeX patches in Step 7 (PATCHES.md) MUST respect this mode.

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
| **Weaken-Claim** | Theorem claims more than proved | Maybe — find if stronger result exists elsewhere. **MANDATORY**: produce a 4-column change-log table for the Weaken-Claim Change Log in REPAIR_PLAN.md Step 7A. Without the table, `/proofcheck --post-repair` will flag this as `NEW-S0` (undocumented semantic change). |
| **Strengthen-Proof** | Gap in reasoning, but claim is likely true | Yes — find technique/lemma to fill the gap |
| **Insert-Lemma** | Missing intermediate step | Yes — may exist as known result in literature |
| **Fill-Skipped-Steps** | Author skipped intermediate steps; proofcheck flagged NONTRIVIAL or UNRECONSTRUCTIBLE jumps | Sometimes — TRIVIAL/VERIFIABLE need no refs, NONTRIVIAL may need a named technique, UNRECONSTRUCTIBLE may need new lemma + refs |
| **Expand-Sketch-to-Proof** | proofcheck flagged the unit as `SKETCH-ONLY` or `PARTIAL-SKETCH` (entire proof body is outline, not rigorous derivation) | Often — sketch usually relies on cited techniques that need to be properly invoked with prerequisites verified. The "expansion" is the entire proof; literature support helps confirm cited techniques apply |
| **Replace-Technique** | Current technique fundamentally flawed | Yes — find alternative proof strategy |
| **Fix-Constants** | Rates, bounds, or constants wrong | Maybe — check if correct constants known |
| **Fix-Quantifiers** | Pointwise↔uniform, ∀∃ order, etc. | Maybe — find uniform versions of cited results |
| **Notation-Fix** | Symbol drift, type mismatch | No |
| **Citation-Fix** | External theorem misapplied | Yes — find correct version or alternative theorem |

### Expand-Sketch-to-Proof repair workflow (when unit was SKETCH-ONLY / PARTIAL-SKETCH)

**HARD PRIORITY RULE**: Any unit flagged SKETCH-ONLY or PARTIAL-SKETCH by
/proofcheck is **automatically P0 priority** for this repair class, regardless
of severity ranking on other dimensions. Sketches MUST be expanded — they
cannot be deferred to "later revision" or "future work".

The reason: a sketch is not just a low-quality proof; it is the **absence of
verification**. Other issues (constants, quantifiers, etc.) are corrections of
something that exists. A sketch needs the proof to be CREATED. Until it exists,
the theorem's status is unsupported.

When proofcheck flags a unit as `SKETCH-ONLY` or `PARTIAL-SKETCH`, the repair is
to **write the entire proof** — not just fix a step. This is distinct from
Fill-Skipped-Steps (which fills isolated gaps inside an otherwise rigorous proof).

**Approach**:

1. **Read the sketch carefully** — what high-level strategy does it claim?
   Extract the proof outline as a numbered list of intended steps.

2. **For each intended step**:
   - Is the cited technique actually applicable here? (verify prerequisites)
   - Is there a standard reference for the technique? Cite it explicitly
   - Write out the actual derivation, not just the verbal claim

3. **Trigger `/proof-writer`** with the original claim + extracted outline,
   asking for a COMPLETE proof (not a sketch — see proof-writer's anti-sketch
   rules). The skill should refuse to produce another sketch.

4. **Verify the expanded proof**:
   - Does it conclude the original claim exactly?
   - Are all assumptions used? Are any extra assumptions snuck in?
   - Send to `/proofcheck` for re-audit after expansion

5. **Literature support**:
   - For each non-trivial technique invoked, cite the canonical reference
   - If the sketch said "similar to [Paper Z]", verify Paper Z actually has the
     full proof and adapt it explicitly (not just point at it)

**Output**: a complete proof replacing the sketch, with explicit derivations and
proper citations. Marked in PATCHES.md as `Patch: replace sketch with full proof`.

**Hard completion rule**: REPAIR_PLAN.md cannot be marked complete while ANY
sketch unit remains unexpanded. Each detected sketch must end in one of two
terminal states:
- **EXPANDED**: full proof written by /proof-writer, re-classified as COMPLETE
  by /proofcheck
- **BLOCKAGE**: blockage report written explaining why the sketch cannot be
  expanded (theorem itself is downgraded to NOT CURRENTLY JUSTIFIED)

There is no third option. "Partially expanded" or "expansion deferred to
revision" are NOT terminal states.

The REPAIR_PLAN.md must contain a sketch-tracking section:

```markdown
## Sketch Expansion Tracker (auto-generated)

| Unit | Sketch class (from proofcheck) | Expansion state | Final status |
|------|------------------------------|----------------|-------------|
| Thm 3.1 | SKETCH-ONLY | EXPANDED | COMPLETE proof written; verified by re-check |
| Lemma B.2 | PARTIAL-SKETCH | EXPANDED | 4 gaps filled with full derivations |
| Cor 5.3 | SKETCH-ONLY | BLOCKAGE | Cited technique inapplicable; theorem downgraded |

Outstanding sketches: 0  ← MUST be 0 for plan to be marked complete
```

If any row has Expansion state ≠ EXPANDED / BLOCKAGE, the skill returns to
expansion before producing the final plan.

**Common failure modes for this repair class**:
- The sketch was actually NOT provable as stated (was hiding the real issue)
  → downgrade to NOT CURRENTLY JUSTIFIED + blockage report (this is BLOCKAGE state, valid terminal)
- The cited technique doesn't actually apply
  → reclassify as Replace-Technique → still must expand the resulting alternative proof
- Expansion reveals a missing assumption
  → reclassify as Add-Assumption → still must expand the resulting proof under the new assumption

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

## Step 3: Enforce the Repair Priority Ladder (HARD GATE)

Before generating candidate repairs, classify each candidate by **ladder level** and by **repair class**. The full ladder definition (Phase A / B / C, L1-L6), the mapping from levels to repair classes, the sibling-not-ordered rules for L2/L3 and L4/L5, and the hard enforcement requirements all live in `stat-shared-references/proof-closure-machinery.md` under "Repair Priority Ladder".

Operational summary for this step:

1. For each issue from Step 1, identify the relevant Phase A branches (L1 internal correction / L2 supporting lemma / L3 alternative technique). Attempt them with concrete candidate sketches.
2. A candidate enters Phase B (L4 Add-Assumption or L5 Weaken-Claim) only after the per-issue repair file records a Phase A exhaustion entry for the relevant branches. The Phase A Exhaustion Record block schema is in `proof-closure-machinery.md`.
3. L4 requires an Assumption-Extension Change Log entry; L5 requires a Weaken-Claim Change Log entry. Both schemas are in `proof-closure-machinery.md`. A Phase B repair without the matching log is invalid and is demoted to L6 (Blockage / NOT CURRENTLY JUSTIFIED).
4. The chosen repair's `Repair Ladder Defense` block (schema in `proof-closure-machinery.md`) must be written into the per-issue repair file before the repair is admitted to Step 5 (Complete-Proof Writing).

`/proofcheck --post-repair` enforces all of the above by checking the schema instances on the patched paper.

---

## Step 3B: Generate Candidate Repairs (per issue)

For each issue, generate 1-3 candidate repair strategies, each typed with a **ladder level** in addition to invasiveness:

```markdown
## Repair Candidates: I-01 (Lemma C.3 — hidden invertibility assumption)

### Candidate A: Add explicit assumption (Ladder level: L4 / invasiveness: LOW within Phase B)
- Repair class: Add-Assumption
- Claim preserved: yes; Assumptions preserved: no
- Add "Assume H(θ) is invertible for all θ ∈ Θ" to Lemma C.3 statement
- Propagate to Theorem 2.1 assumptions
- Check: is this already implied by existing Assumption 2 (strong convexity)? If yes, this is actually an L2 candidate, not L4.
- Risk: may narrow the theorem's applicability

### Candidate B: Insert supporting lemma (Ladder level: L2 / invasiveness: MEDIUM)
- Repair class: Insert-Lemma
- Claim preserved: yes; Assumptions preserved: yes
- Add Lemma C.3' proving H(θ) invertibility under existing assumptions
- Needs: strong convexity (Assumption 2) ⟹ H(θ) ≻ 0
- Advantage: Phase A repair; no main-theorem assumption change
- Literature needed: standard result connecting strong convexity to Hessian invertibility

### Candidate C: Alternative technique — Avoid inversion entirely (Ladder level: L3 / invasiveness: HIGH)
- Repair class: Replace-Technique
- Claim preserved: yes; Assumptions preserved: yes
- Replace matrix inversion step with pseudo-inverse + regularization
- Requires reworking Eqs. (47)-(52)
- May change constants but preserves rate
- Literature needed: perturbation theory for pseudo-inverse in M-estimation
```

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

Each candidate selected for the next step (Step 4 literature search and Step 5 complete-proof writing) requires the following mandatory blocks in its per-issue repair file at `audit/07_repairs/section_*/*_repair.md`. The schemas live in `stat-shared-references/proof-closure-machinery.md` and are not duplicated here.

- **Always**: `## Repair Ladder Defense` block (chosen level + repair class + claim/assumption preservation + Phase A Exhaustion Record + Phase B Justification if L4/L5 + Semantic-Edit Log Pointer + Blockage Pointer if L6).
- **If chosen class is `Weaken-Claim` (ladder L5) or candidate feasibility was `PROVABLE AFTER WEAKENING`**: `## Weaken-Claim Change Log` block (four columns: original claim verbatim, revised claim verbatim, reason for weakening, downstream impact). Without this block, the repair is demoted to `NOT CURRENTLY JUSTIFIED`.
- **If chosen class is `Add-Assumption` (ladder L4)**: `## Assumption-Extension Change Log` block (seven columns including original assumption set, added assumption verbatim, natural weaker variant considered, why the weaker variant fails, scientific-scope impact, downstream propagation). The "Natural weaker variant considered" column is the local-minimality defense. Without this block, the repair is demoted to `NOT CURRENTLY JUSTIFIED`.

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

## Step 4: Literature Search for Repair Support

For EACH candidate repair that needs literature support, run a targeted multi-source search.

**Guiding principle**: A proof repair is only as credible as its references. Prioritize results from top-tier venues; treat unreviewed preprints as supplementary evidence only.

### 4A: Cache-consult first (mandatory)

Before invoking any web tool, consult the durable literature cache at `~/.claude/literature_cache/`. The protocol lives in `stat-shared-references/literature-cache-protocol.md` (router with Minimum Load Map). For this step, the typical loads are:

- `literature-cache-protocol.md` (router) — always.
- `applicability-axes.md` — if the candidate is `load_bearing` / `benchmark_claim` / `comparative` and an axis check is needed.
- `cache-verification-states.md` — when fetching new entries; when the entry is below `source_checked`; when source version may be stale.

Procedure:

1. Read the cache INDEX (`~/.claude/literature_cache/INDEX.md`) to identify cache hits matching the repair's literature need (technique, anchor paper, schema, comparator).
2. For each cache hit, do a result-scoped load (Read with `offset`/`limit`) of the matching per-result entry. Do not dump full paper containers.
3. For each cache miss, proceed to the web search workflow below, then write the proposal back to `~/.claude/literature_cache/inbox/<bibkey>.draft.md` per the inbox protocol in `cache-verification-states.md`.

Credibility tier classification (next subsection) applies to BOTH cache hits and fresh web results.

### 4B: Venue Credibility Tiers

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

### 4C: Formulate Search Queries

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

### 4D: Multi-Source Search (parallel)

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

### 4E: Evaluate & Rank Search Results

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

### 4F: Verify Cited Results (with venue-appropriate rigor)

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

### 4F.cache: Write back to cache (mandatory for new sources)

For every reference that was a cache miss in Step 4A and has now been fetched and verified, write a proposal to the cache inbox at `~/.claude/literature_cache/inbox/<bibkey>.draft.md` per `cache-verification-states.md`. The proposal must include:

- Manifest header with `verification_status: unverified_extract`
- Source URL, source version, retrieval date, source hash, verbatim quote blocks with locators and text hashes
- Applicability contract on the 8 axes per `applicability-axes.md`
- Theoretical lineage block (`primary_line`, `role_in_literature`) per `citation-purpose-protocol.md`
- The citation purpose at this repair's site (typically `load_bearing`, `technique_inheritance`, or `standard_tool`)

The repair itself can proceed using the just-fetched content (the writing skill is allowed to use its own `unverified_extract` immediately because it just read the source). Downstream skills consuming this evidence will require `/lit-cache verify` promotion before using it at `source_checked` or higher. The user is notified that an inbox entry awaits verification.

Update the project's `papers/<project-name>/cited_results.lock.md` with the citation site, reference (`paper:<bibkey>#<result_id>`), citation purpose, role in literature, role relative to current paper, source version at decision, entry hash at decision, verification level at decision, axis or lineage bridge recorded, and decision date. The schema is in `citation-purpose-protocol.md`.

### 4G: Fallback When No High-Quality Reference Found

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

**Reference mode**: A (single-file) — using `\ref{}` cross-references
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

**If reference mode were B (two-file)** the same patch would instead use hard-coded
numbers for any cross-file reference:

```latex
% In supplement.tex — inserting Lemma S.3 (next supplement number)
\begin{lemma}[Hessian invertibility]\label{lem:hessian-invert}
% Cross-file: Assumption 2 of the main text — DO NOT use \ref{}
Under Assumption~2 of the main text, for all $\theta \in \Theta$,
$\lambda_{\min}(H(\theta)) \geq \mu > 0$.
\end{lemma}
% Within supplement, normal \ref{} is fine:
% ... use Lemma~\ref{lem:hessian-invert} later in the supplement
```

When the main text needs to cite this new supplement lemma, it must write
"Lemma S.3 of the supplement" with a hard-coded `S.3`, NOT `\ref{lem:hessian-invert}`.

**Rule of thumb** (apply automatically when writing patches):
- Patch lives in the SAME file as everything it references → use `\ref{}` / `\eqref{}`
- Patch references something in the OTHER file (main↔supplement) → hard-coded number
- When inserting new lemmas in supplement (Mode B), assign them S-prefixed labels
  AND record the assigned number, so subsequent main-text patches can hard-code it

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

For every P0 and P1 repair with a complete proof, run the per-repair fresh-thread stress-test defined in `CODEX_PROTOCOL.md` under "Per-Repair Fresh Thread" and "Per-Repair Stress-Test Call Template".

Rules (full rationale and template in `CODEX_PROTOCOL.md`):

- One fresh `mcp__codex__codex` thread per logically-independent repair; up to 2-3 repairs may share a thread only if they sit on the same dependency edge or assumption block.
- `model_reasoning_effort: xhigh` is forced (the scope hits the Reasoning Effort Ladder triggers: theorem / lemma / proof step / rate / quantifier).
- Anti-anchor opening prompt; forced falsification attempt; structured PASS / FIXABLE / FAIL verdict.
- FIXABLE / FAIL iterate via `mcp__codex__codex-reply` on the same thread (Case B continuation).
- Verdicts are recorded in `audit/07_repairs/codex_stress_test.md` per the artifact schema in `CODEX_PROTOCOL.md` "Per-Repair Stress-Test Verdict Recording" (one row per repair, threadId tracked).

The full per-repair call template, the verdict recording schema, the rationale (Codex's honest anchoring self-assessment), and the iterative push-back protocol all live in `CODEX_PROTOCOL.md`. This skill does not duplicate them inline.

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

Insert the `## Repair Ladder Summary` table per the schema in `stat-shared-references/proof-closure-machinery.md`. One row per issue with columns: Issue ID, Unit, Chosen repair class, Chosen ladder level, Claim preserved?, Assumptions preserved?, Escalation justified?, Pointer to per-issue defense.

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

The full Hard-Gate Completion Rule (9 conditions) lives in `stat-shared-references/proof-closure-machinery.md`. Headline conditions:

- Every issue has a terminal closure row; every Weaken-Claim and Add-Assumption repair has its mandatory Change Log entry; outstanding sketches = 0; every P0/P1 repair passed the per-repair Codex stress-test (per `CODEX_PROTOCOL.md`); the Consistency Verification checklist is fully checked.
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

Write `papers/<paper-name>/PATCHES.md` with all LaTeX modifications in order.
**Each patch declares its reference mode and conformance**:

```markdown
# LaTeX Patches — Apply in Order

## Reference Mode
- Mode: [A: single-file / B: two-file main+supplement]
- Files involved:
  - paper.tex (main text)
  - supplement.tex (if Mode B)
- Supplement numbering scheme (if Mode B): S.1, S.2, S.3, ... or S1, S2, S3, ...

## Patch 1: Insert Lemma S.3 (Hessian invertibility)
- File: supplement.tex   ← which file
- After line: [XXX]
- New label assigned: `\label{lem:hessian-invert}` (only valid within supplement.tex)
- New display number: **S.3** (record this for any future main-text patch citing it)
- Cross-file references inside this patch:
  - "Assumption 2 of the main text" — hard-coded (cross-file)
- Within-file references inside this patch:
  - `\ref{assump:strong-convex-supp}` — OK if assumption is also in supplement
- Insert:
  ```latex
  [the latex block, mode-correct]
  ```

## Patch 2: Update Theorem 2.1 in main text to invoke new Lemma S.3
- File: paper.tex   ← main text
- Line: [YYY]
- Change: "since H(θ) is invertible (Lemma~\ref{...})"
       → "since H(θ) is invertible (Lemma~S.3 of the supplement)"
- NOTE: hard-coded "S.3" because this is a cross-file reference

## Patch 3: Fix Theorem 3.1 rate
- File: paper.tex
- Line: [ZZZ]
- Change: `O(n^{-1})` → `O(n^{-1} \log n)`

## Patch 4: Add new bibliography entries
- File: references.bib (shared between main.tex and supplement.tex)
- Append: [entries from repair_references.bib]
- Note: .bib is shared, so BibTeX `\cite{key}` works in BOTH files normally
```

### Pre-patch validation rules

Before finalizing PATCHES.md, the agent must verify:

1. **Every `\ref{}` in a patch resolves within the SAME file**
   - Scan each patch's LaTeX block for `\ref{LABEL}` / `\eqref{LABEL}` / `\cref{LABEL}`
   - For each, check whether the `\label{LABEL}` exists in the patch's target file
   - If not → ERROR: convert to hard-coded reference

2. **Every cross-file reference uses hard-coded numbers**
   - Scan for phrases like "Lemma X.Y", "Theorem N", "equation (M)" in cross-file contexts
   - Verify the number is hard-coded, not a `\ref{}`

3. **Supplement-file lemma numbering is consistent**
   - If Mode B: new lemmas in supplement get S-prefixed display numbers
   - Track assigned numbers across patches so the master plan is internally consistent

4. **Citation `\cite{}` works in both files**
   - BibTeX `\cite{}` is fine cross-file because .bib is shared
   - Only mathematical-object `\ref{}` is mode-sensitive

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

#### Step F1: Collect residuals

Build a focused issue list combining:

- Every `STILL-OPEN` issue from `per_issue_closure.md` (original issues the previous patch did not close)
- Every `NEW-S0` and `NEW-S1` issue from `new_issues.md` (issues the previous patch introduced)
- Every unjustified diff row from `diff_ledger.md` (silent semantic changes not propagated)

S2 and S3 residuals are listed but do not force the cycle to continue; the user decides whether to address them now or accept the open list.

#### Step F2: Classify residuals by cause

Each residual is one of:

- `INCOMPLETE-FIX`: the patch attempted the right strategy but missed steps or edge cases. Re-apply the same repair class with the missed details addressed.
- `WRONG-CLASSIFICATION`: the original repair class was wrong (e.g., Strengthen-Proof was tried where Add-Assumption was needed). Reclassify and re-design.
- `UNDOCUMENTED-WEAKENING`: a Weaken-Claim repair was applied without a PATCHES.md change-log row, or without propagation to downstream units. Generate the missing change-log table and propagate.
- `PROPAGATION-GAP`: a repair was correctly designed and locally verified, but downstream units that consumed the original claim were not updated. Add downstream-propagation patches without touching the already-correct local repair.
- `NEW-DEFECT`: the previous patch introduced a fresh defect in a unit that was previously verified. Treat as a new repair from scratch.

#### Step F3: Repair the residuals only

For each residual, run Steps 3-5 of the main workflow (Generate Candidates, Literature Search, Write Complete Proof) on the residual itself. **Do not re-litigate already-CLOSED-VERIFIED issues.** The previous REPAIR_PLAN.md remains the canonical record for those.

If a residual repair touches a unit already repaired in the previous cycle, the new patch is layered on top — the closure matrix gains a second row for the same unit, marked as `Repair cycle 2`. The previous cycle's row is preserved with its terminal status.

#### Step F4: Update REPAIR_PLAN.md and PATCHES.md

The existing REPAIR_PLAN.md is **appended to**, not rewritten:

- New section: `## Repair Cycle 2 — From Re-Audit Verdict on [date]`
- New Closure Matrix rows for the residual issues
- Updated cycle-2 patches in PATCHES.md, clearly labeled `Cycle 2 — Patch N`
- Updated Codex Stress-Test results for cycle-2 repairs

The summary section is updated to reflect both cycles.

#### Step F5: Re-invoke `/proofcheck --post-repair`

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
