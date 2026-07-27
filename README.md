# stat-theory-skills

[![tests](https://github.com/gyf9712/stat-theory-skills/actions/workflows/tests.yml/badge.svg)](https://github.com/gyf9712/stat-theory-skills/actions/workflows/tests.yml)

A pipeline of 6 Claude Code skills for working with mathematical proofs in
statistics, econometrics, and ML theory papers. Goes from **designing a theoretical
framework** through **finding proof errors** to **theoretical sharpening with
literature support**, with deterministic Python checks behind the judgment work.

> References [maweiruc/proofcheck-stat-paper](https://github.com/maweiruc/proofcheck-stat-paper)
> as inspiration for the proof-checking methodology, and extends it with proof repair,
> theory sharpening, and Codex MCP cross-review.

## The Pipeline

```
   (blank page)
  /theory-design ──┐
   framework +     │
   literature      ▼
   anchor      ┌─────────────┐   ┌──────────────┐   ┌───────────────────────────┐
               │ /proofcheck │ → │ /proof-repair│ → │ /proofcheck --post-repair │ ─┐
               │ find errors │   │ fix + cite   │   │ convergence test          │  │
               │ (6-pass)    │   │ + closure mx │   │ every S0/S1 closed?       │  │
               └─────────────┘   └──────────────┘   └───────────────────────────┘  │
                        ↑                    │                                     │
                        └─ /proof-repair ────┘                                     │
                            --from-reaudit                                         │
                       (manual, no auto-loop)                                      │
                                                                                   ▼
               ┌────────────────┐   ┌────────────────────┐   ┌──────────────┐
               │/theory-sharpen │ → │ /theory-simulation │ → │ /proof-writer│
               │ strengthen the │   │ Monte Carlo verify │   │ write the    │
               │ theory itself  │   │ + stress-test      │   │ closed proof │
               └────────────────┘   └────────────────────┘   └──────────────┘
```

Each skill can be used standalone, or chained together. `/theory-design` is the entry
point for a new topic; the rest operate on a paper that already exists.

The new `/proofcheck --post-repair` step is the **convergence test** for the repair phase. It is a focused delta audit, **not** a full re-run of the 6-pass `/proofcheck`. It reads the original audit + `REPAIR_PLAN.md` (with its Repair Closure Matrix) + `PATCHES.md` (with the Weaken-Claim Change Log) and verifies:

- Every originally flagged issue is closed (`CLOSED-VERIFIED`, `CLOSED-WEAKENED`, or `CLOSED-BLOCKAGE`)
- No new S0/S1 issue was introduced by the patches
- The assumption / rate / probability / norm / sample-size / dependency **diff ledger** has no unjustified rows

This step is a **hard gate** when the original audit found any S0 or S1 issue: `REPAIR_PLAN.md` cannot be marked complete until `CONVERGENCE_VERDICT.md` reports `CONVERGED`. For S2/S3-only repair plans it is a strong recommendation.

If the re-audit finds residual issues, the user manually invokes `/proof-repair --from-reaudit` to address only the residuals, then re-runs `--post-repair`. The cycle is human-driven; the pipeline never auto-loops, and after two `--from-reaudit` cycles without convergence the affected theorems are downgraded to NOT CURRENTLY JUSTIFIED.

## What each skill does

### `/proofcheck` — Mathematical proof verification

Systematically audits proofs in long technical appendices using 6 passes:
indexing → critical path → support lemmas → global consistency → adversarial
review → final report.

- One file per proof unit, with severity (S0–S3) and confidence ratings
- Common failure-pattern checklist (29 patterns)
- Provability triage: PROVABLE AS STATED / WEAKENING / NOT JUSTIFIED
- Proof-strategy classification: direct / contradiction / induction / coupling / …
- Anti-fabrication enforcement: flags "clearly / obviously / by standard arguments"
- Codex MCP cross-review (independent second opinion)

### `/proof-repair` — Literature-backed repair plans

Takes a `/proofcheck` audit and produces self-consistent repair plans with
new references from top venues:

- 11 repair classes (Add-Assumption / Weaken-Claim / Insert-Lemma / Replace-Technique / …)
- **Venue tier system**: T1 (AoS, JASA, JRSS-B, Biometrika, Econometrica, JOE, NeurIPS, ICML, JMLR, COLT) → T4 (avoid)
- Credibility scoring: GOLD / STRONG / ACCEPTABLE / GOOD / CONDITIONAL / WEAK / REJECT
- Multi-source parallel search: arXiv + Semantic Scholar + targeted T1 sites
- Writes complete repaired proofs (not just sketches)
- Codex MCP stress-tests each repair

### `/theory-sharpen` — Strengthen the theory itself

Goes beyond "is the proof correct" to "can the theory be stronger":

- **Framework Classification (mandatory 3-axis triage)**:
  - Data structure: IID / mixing / TS / Markov / panel / spatial / sequential / network
  - Modeling framework: parametric / semiparametric / nonparametric
  - Asymptotic regime: classical / proportional / high-d sparse / non-asymptotic / online
- **Literature-anchored validation**: searches recent T1 papers in the same topic
  to validate the classification and identify trending pathways
- **27 framework-tagged relaxation pathways** across 5 categories:
  dependence, tail/moment, curvature, domain/dimension, model/specification
- **Rate sharpening directions**: chaining, localization, Bernstein, DML, fast-rate, …
- **10 reviewer-critical dimensions** (lower bounds, identification, adaptivity,
  structural guarantees, computational attainability, …) + assumption verifiability
- Codex MCP independent assessment

### `/theory-simulation` — Bridge theory and Monte Carlo simulation

Two modes: **DESIGN** (paper has theorems, no sims) and **AUDIT** (paper has both
theorems and sims — evaluate whether sims actually verify the theorems).

Designs and runs reproducible simulations to top-stat-journal standards
(AoS / JASA / JRSS-B / Biometrika / Bernoulli):

- **Theory-to-simulation mapping**: every theorem gets a verification experiment
- **Stress tests**: violate each assumption one at a time
- **Rate verification**: log-log slope analysis with confidence bands
- **Coverage verification**: empirical coverage of CIs vs nominal level
- **Reproducibility**: deterministic seeds, parallel execution, versioned dependencies
- **Publication-grade figures** (stat-journal conventions, NOT Nature defaults):
  - **NO titles** on plots — all content goes in LaTeX `\caption{}`
  - Concise axis labels, no jargon
  - Legend placement verified for non-overlap with data
  - Color-blind safe palettes (Okabe-Ito for lines, viridis/cividis for heatmaps)
  - PDF/EPS export with embedded fonts; no raster for line plots
  - Pre-export checklist enforced
- **Theory ↔ simulation reconciliation**:
  - Confirmed predictions → tagged for paper
  - Discrepancies → feedback to `/theory-sharpen` (relax) or `/proof-writer` (strengthen)
  - Drop-in `SIMULATION_SECTION.tex` for the paper

Both modes score against the same five **adequacy dimensions** — truth source,
selection discipline, tuning protocol, computational adequacy, reuse legitimacy — so a
simulation this skill *designs* meets the bar it *audits* against. Coverage is not
credibility: a claim covered by an experiment that cannot identify it is `PARTIAL`,
never `YES`.

**AUDIT mode (when paper already has sims)**:
- Parses existing simulation section, figures, and tables
- Populates the **Claim Evidence Ledger** — the same typed object DESIGN mode uses,
  so both modes speak one vocabulary: `PLANNED`, `YES[strong]`, `YES[weak]`,
  `PARTIAL[reason-codes]`, `NO`, `CONTRADICTED[code]`, `HYPOTHESIS-ONLY`
- Per-experiment **adequacy audit** against top-journal standards
- **Gap analysis** in three buckets:
  - Claims with NO experimental evidence (most serious)
  - Experiments with adequacy problems (extend / fix)
  - Reporting / discipline issues (revise without re-running)
- **Targeted improvement plan**: minimal new work to close gaps, not full redesign
- Distinguishes what can be REUSED from existing runs vs what MUST be rerun
- Codex independent audit for cross-validation

### `/theory-design` — Design the framework from a blank page

Paper-type-aware framework design, run before any proof exists. Three modes with
genuinely different logical orders: a **theory** paper's centrepiece is the theorem, a
**methodology** paper's is the estimator, an **application** paper's is the empirical
finding.

- Mandatory **literature anchoring** first: identify the field's *theoretical inertia*
  (the defaults a referee unconsciously expects), then choose positioning
  (`INCREMENTAL` / `LATERAL` / `DISRUPTIVE`) and derive the constraints that bind every
  later phase decision
- Produces `FRAMEWORK_DESIGN.md` + `LITERATURE_ANCHOR.md` for the downstream skills
- Initializes `assumptions.lock.md`, the shared assumption registry

### `/proof-writer` — Rigorous proof drafting

Writes the actual corrected proofs identified by the upstream skills. The unit of
completion is the **closed obligation, not prose**:

- An **Obligation Ledger**: every nontrivial step terminates in exactly one typed
  state — `CLOSED-LOCAL`, `CLOSED-CITED`, or `BLOCKED`. You cannot prose your way into
  a typed closure, and `BLOCKED` costs a full attack record, so neither faking nor
  quitting is the cheap option
- `CLOSED-CITED` requires an inline applicability block (clause used, assumption map,
  conclusion fit) — a citation invoked outside its conditions makes the proof wrong
- Provability and verification are separate axes: an uninspected source caps the
  package at `Conditionally verified`, never `Verified`
- Three honest statuses: PROVABLE AS STATED / AFTER WEAKENING / NOT CURRENTLY JUSTIFIED
- Refuses to fabricate steps; writes a blockage record instead

## Deterministic tooling

Mechanical checks live in tested Python (stdlib only, no dependencies) so the skill
bodies stay focused on judgment. Every script separates **mechanical** findings, which
affect the exit code, from **heuristic/advisory** ones, which never do — a script may
not certify correctness it cannot actually check.

| Script | Checks | Exit code |
|---|---|---|
| `proof_index.py` | Theorem inventory, `\ref` dependency DAG, topological check order, cycle detection, cross-file reference leaks | 1 on structural failure |
| `proof_gap_scan.py` | Obligation Ledger closure: `BLOCKED` under a provable status, missing closure fields, undefined bridge IDs, blank verification checks | 1 on structural incompleteness |
| `simulation_ledger_check.py` | Claim Evidence Ledger: approved state vocabulary, one row per claim, DESIGN covers every adequacy dimension, no `CONTRADICTED` without triage; plus `--self-lint` for the skill file | 1 on hard assertion failure |
| `skill_lint.py` | Every file reference in a `SKILL.md` resolves in the **installed** layout; no control characters | 1 on unresolvable reference |
| `venue_tiers.py` | Rule data: venue credibility tiers T1–T4 | — |

Run the whole suite:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Maintenance

[`MAINTENANCE.md`](MAINTENANCE.md) holds the rules that keep these skills from
re-growing. The short version:

- **Two budgets.** Hot prefix ≤ 200–250 lines (routing, invariants, state machine, hard
  gates, compact contract) and total ≤ 700–800. A long file is not merely untidy: the
  model runs the first ~200 lines as hard law and treats the rest as suggestions.
- **A `SKILL.md` grows only when the core state machine changes.** Deterministic check →
  script; fixed table → rule data or reference; worked example or prompt block →
  companion reference.
- **Compact empty contract inline, filled specimen out.** The contract defines terminal
  states; the example is illustration.
- **Do not over-cut.** A skill that becomes "go read five references" has lost its
  control logic.

It also documents the **acceptance-test method** for a rewritten skill, since prose has
no unit tests: build a fixture per route, write an `EXPECT.md`, run the skill in a
**fresh context** three times, check mechanically, and pass at ≥ 2 of 3 with no
forbidden failure. Fresh context matters — it tests the file, not your memory of what
you meant.

## Install

```bash
# Clone the repo
git clone https://github.com/gyf9712/stat-theory-skills.git
cd stat-theory-skills

# Run the install script (use --force to overwrite an existing install)
bash install.sh
```

`install.sh` copies all six skills plus `stat-shared-references/` — its `*.md`
protocols, `scripts/*.py`, and `examples/*.md`. Copying skill directories by hand is
not enough: the skills reference the shared directory as `../stat-shared-references/…`,
which only resolves once everything sits together under `~/.claude/skills/`.

This repo installs alongside [`stat-writing-skills`](https://github.com/gyf9712/stat-writing-skills)
into that one shared directory, and a few references deliberately cross between them
(theory skills read `stat-theory-writing.md`, which the writing repo owns). Install both
if you use both.

## ⚠️ Important: Use Claude Opus

These skills are designed for **deep mathematical reasoning** and are optimized for
**Claude Opus**. Each skill's YAML frontmatter declares `model: opus`, and the
skill body reminds you at the top.

Before invoking any of these skills, ensure your Claude Code session is on Opus:

```
/model opus
```

You can also set Opus as your default in `~/.claude/settings.json`:

```json
{
  "model": "opus",
  "effortLevel": "high"
}
```

Why Opus matters here:
- `theory-design`: needs to read a field's theoretical inertia, not just its topics
- `proofcheck`: needs to spot subtle quantifier errors, hidden assumptions
- `proof-repair`: needs to verify cited theorems match prerequisites exactly
- `theory-sharpen`: needs to reason about minimax lower bounds and rate optimality
- `theory-simulation`: needs to tell coverage from evidentiary strength
- `proof-writer`: needs to write rigorous proofs without fabrication

Sonnet/Haiku may produce results that *look* right but miss critical mathematical
gaps. The difference compounds across the pipeline.

## Invocation

After install + `/model opus`:
```
/theory-design            # start a new topic from a blank page
/proofcheck papers/my-paper/paper.tex
/proof-repair papers/my-paper/
/theory-sharpen papers/my-paper/
/theory-simulation papers/my-paper/
/proof-writer [specific claim]
```

## Codex MCP (optional but recommended)

Five of the six skills can optionally invoke Codex (OpenAI GPT via MCP) as an
**adversarial reviewer**. To enable:

```bash
claude mcp add codex -s user -- codex mcp-server
```

### The discussion protocol — NOT wholesale acceptance

(`proof-writer` does not: it has no web tools and closes obligations locally.)

All Codex-using skills follow [`stat-shared-references/codex-protocol.md`](stat-shared-references/codex-protocol.md): Codex is an adversarial
reviewer to **discuss with iteratively until convergence**, never an oracle whose
findings are accepted wholesale.

The 5-round protocol:
1. Claude produces output
2. Codex reviews adversarially
3. Claude critically evaluates EACH finding (ACCEPT / PUSH BACK / REQUEST CLARIFICATION)
4. Codex responds to push-back / clarifications
5. Iterate until convergence or escalate persistent disagreements to user

Every Codex-using skill emits a `codex_discussion.md` documenting the full
round-by-round dialogue so the user can override either model's position.

**Forbidden behaviors** (explicitly called out in each skill):
- Silent wholesale acceptance of Codex findings
- Silent rejection of Codex findings to defend prior work
- ACCEPT without recording the reasoning
- PUSH BACK without a substantive counter-argument

### What each skill uses Codex for

| Skill | Codex's adversarial role |
|-------|-------------------------|
| `proofcheck` | Cross-confirm S0/S1 issues + spot-check verified units + find missed issues |
| `proof-repair` | Stress-test each proposed repair; try to break it |
| `theory-sharpen` | Independently assess assumption relaxability, rate optimality, theory-practice gaps |
| `theory-simulation` | Pre-run design review + post-run figure/reconciliation review |
| `theory-design` | Adversarial referee on the entire framework + literature anchor + positioning |

Real examples of the protocol in practice are documented in CHANGELOG.md
(`theory-simulation v1.1.1` had 20 Codex findings: 13 accepted, 6 push-backs
of which 5 produced refinements and 1 was conceded by Claude).

## Pipeline example

Full workflow on a single paper:

```bash
# 1. Find all proof issues
/proofcheck papers/my-paper/paper.tex
# → produces papers/my-paper/audit/ with theorem inventory,
#   per-unit checks, issue log, final report

# 2. Design repairs with literature support
/proof-repair papers/my-paper/
# → produces REPAIR_PLAN.md (with Repair Closure Matrix and
#   Weaken-Claim Change Log), PATCHES.md, repair_references.bib

# 2.5. Convergence test — verify the repairs actually closed every original issue
#      and did not introduce new defects
/proofcheck --post-repair papers/my-paper/
# → produces audit/08_post_repair/ with RE-AUDIT_REPORT.md,
#   diff_ledger.md, per_issue_closure.md, new_issues.md, and
#   CONVERGENCE_VERDICT.md (CONVERGED / NOT CONVERGED)
#
# This step is REQUIRED before REPAIR_PLAN.md can be marked complete
# if the original audit had any S0 or S1 issue. For S2/S3-only plans
# it is strongly recommended but not gated.

# 2.6 (only if needed). Address residual issues found by re-audit
/proof-repair --from-reaudit papers/my-paper/
# → appends Cycle 2 patches to REPAIR_PLAN.md and PATCHES.md
# → after this, re-invoke /proofcheck --post-repair to confirm CONVERGED
# → never auto-loop; user explicitly invokes each cycle

# 3. Strengthen the theory beyond fixing errors
/theory-sharpen papers/my-paper/
# → produces SHARPEN_REPORT.md with relaxable assumptions,
#   sharpenable rates, recent T1 literature benchmarks

# 4. Write the actual corrected proofs
/proof-writer "the lemma replacing C.3 should establish ..."
# → produces PROOF_PACKAGE.md with full rigorous proof
```

## Credits

- **Referenced work**: [maweiruc/proofcheck-stat-paper](https://github.com/maweiruc/proofcheck-stat-paper)
  served as a useful reference point for the multi-pass proof-checking methodology
- **Pipeline design + literature integration + Codex cross-review**:
  developed iteratively with Claude (Sonnet/Opus) and Codex (GPT)
- **Reference library venue audit**: Codex GPT independent review

## License

MIT — see [LICENSE](LICENSE)
