# stat-theory-skills

[![tests](https://github.com/gyf9712/stat-theory-skills/actions/workflows/tests.yml/badge.svg)](https://github.com/gyf9712/stat-theory-skills/actions/workflows/tests.yml)

A pipeline of 4 Claude Code skills for working with mathematical proofs in
statistics, econometrics, and ML theory papers. Goes from **finding proof errors**
all the way to **theoretical sharpening with literature support**.

> References [maweiruc/proofcheck-stat-paper](https://github.com/maweiruc/proofcheck-stat-paper)
> as inspiration for the proof-checking methodology, and extends it with proof repair,
> theory sharpening, and Codex MCP cross-review.

## The Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌──────────────────────────┐    ┌────────────────┐    ┌────────────────────┐    ┌──────────────┐
│ /proofcheck │ →  │ /proof-repair│ →  │ /proofcheck --post-repair │ →  │/theory-sharpen │ →  │ /theory-simulation │ →  │ /proof-writer│
│             │    │              │    │                          │    │                │    │                    │    │              │
│ Find proof  │    │ Fix issues + │    │ Convergence test:        │    │ Strengthen the │    │ Monte Carlo verify │    │ Write the    │
│ errors      │    │ literature   │    │ verify every original    │    │ theory itself  │    │ + stress-test +    │    │ corrected /  │
│ (full 6-pass│    │ support +    │    │ S0/S1 closed; no new     │    │                │    │ feed back to theory│    │ new proof    │
│ audit)      │    │ closure mtx  │    │ defect introduced        │    │                │    │                    │    │              │
└─────────────┘    └──────────────┘    └──────────────────────────┘    └────────────────┘    └────────────────────┘    └──────────────┘
                            ↑                          │
                            └──── /proof-repair ───────┘
                                   --from-reaudit
                              (only when re-audit finds residual issues;
                               manual trigger, no auto-loop)
```

Each skill can be used standalone, or chained together.

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
- 19 common failure-pattern checklist
- Provability triage: PROVABLE AS STATED / WEAKENING / NOT JUSTIFIED
- Proof-strategy classification: direct / contradiction / induction / coupling / …
- Anti-fabrication enforcement: flags "clearly / obviously / by standard arguments"
- Codex MCP cross-review (independent second opinion)

### `/proof-repair` — Literature-backed repair plans

Takes a `/proofcheck` audit and produces self-consistent repair plans with
new references from top venues:

- 9 repair classes (Add-Assumption / Weaken-Claim / Insert-Lemma / Replace-Technique / …)
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
- **22 framework-tagged relaxation pathways** across 5 categories:
  dependence, tail/moment, curvature, domain/dimension, model/specification
- **Rate sharpening directions**: chaining, localization, Bernstein, DML, fast-rate, …
- **9 reviewer-critical dimensions** (lower bounds, identification, adaptivity,
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

**AUDIT mode (when paper already has sims)**:
- Parses existing simulation section, figures, and tables
- Builds **Coverage Matrix**: theoretical claims × existing evidence (YES / PARTIAL / NO / CONTRADICTED)
- Per-experiment **adequacy audit** against top-journal standards
- **Gap analysis** in three buckets:
  - Claims with NO experimental evidence (most serious)
  - Experiments with adequacy problems (extend / fix)
  - Reporting / discipline issues (revise without re-running)
- **Targeted improvement plan**: minimal new work to close gaps, not full redesign
- Distinguishes what can be REUSED from existing runs vs what MUST be rerun
- Codex independent audit for cross-validation

### `/proof-writer` — Rigorous proof drafting

Writes the actual corrected proofs identified by the upstream skills:

- Three honest output modes:
  PROVABLE AS STATED / PROVABLE AFTER WEAKENING / NOT CURRENTLY JUSTIFIED
- Dependency map + numbered steps
- Refuses to fabricate steps; will write a blockage report instead

## Install

```bash
# Clone the repo
git clone https://github.com/gyf9712/stat-theory-skills.git
cd stat-theory-skills

# Run the install script
bash install.sh

# Or manually copy each skill to ~/.claude/skills/
cp -r skills/proofcheck       ~/.claude/skills/
cp -r skills/proof-repair     ~/.claude/skills/
cp -r skills/theory-sharpen   ~/.claude/skills/
cp -r skills/proof-writer     ~/.claude/skills/
```

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
- `proofcheck`: needs to spot subtle quantifier errors, hidden assumptions
- `proof-repair`: needs to verify cited theorems match prerequisites exactly
- `theory-sharpen`: needs to reason about minimax lower bounds and rate optimality
- `proof-writer`: needs to write rigorous proofs without fabrication

Sonnet/Haiku may produce results that *look* right but miss critical mathematical
gaps. The difference compounds across the 4-skill pipeline.

## Invocation

After install + `/model opus`:
```
/proofcheck papers/my-paper/paper.tex
/proof-repair papers/my-paper/
/theory-sharpen papers/my-paper/
/proof-writer [specific claim]
```

## Codex MCP (optional but recommended)

All five skills can optionally invoke Codex (OpenAI GPT via MCP) as an
**adversarial reviewer**. To enable:

```bash
claude mcp add codex -s user -- codex mcp-server
```

### The discussion protocol — NOT wholesale acceptance

All skills follow [`CODEX_PROTOCOL.md`](CODEX_PROTOCOL.md): Codex is an adversarial
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
