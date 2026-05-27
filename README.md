# stat-theory-skills

A pipeline of 4 Claude Code skills for working with mathematical proofs in
statistics, econometrics, and ML theory papers. Goes from **finding proof errors**
all the way to **theoretical sharpening with literature support**.

> References [maweiruc/proofcheck-stat-paper](https://github.com/maweiruc/proofcheck-stat-paper)
> as inspiration for the proof-checking methodology, and extends it with proof repair,
> theory sharpening, and Codex MCP cross-review.

## The Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌────────────────────┐    ┌──────────────┐
│ /proofcheck │ →  │ /proof-repair│ →  │/theory-sharpen │ →  │ /theory-simulation │ →  │ /proof-writer│
│             │    │              │    │                │    │                    │    │              │
│ Find proof  │    │ Fix issues + │    │ Strengthen the │    │ Monte Carlo verify │    │ Write the    │
│ errors      │    │ literature   │    │ theory itself  │    │ + stress-test +    │    │ corrected /  │
│             │    │ support      │    │                │    │ feed back to theory│    │ new proof    │
└─────────────┘    └──────────────┘    └────────────────┘    └────────────────────┘    └──────────────┘
```

Each skill can be used standalone, or chained together.

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

Three of the four skills can optionally invoke Codex (OpenAI GPT via MCP) as an
independent second opinion ("adversarial reviewer"). To enable:

```bash
claude mcp add codex -s user -- codex mcp-server
```

When Codex MCP is available, the skills will:
- `proofcheck`: cross-confirm S0/S1 issues + spot-check verified units
- `proof-repair`: stress-test each proposed repair
- `theory-sharpen`: independently assess assumption relaxability, rate optimality, and theory-practice gaps

The pattern is **first-independent-then-reconcile**: Codex never sees Claude's
findings until after it forms its own judgment. Disagreements are flagged for
human review.

## Pipeline example

Full workflow on a single paper:

```bash
# 1. Find all proof issues
/proofcheck papers/my-paper/paper.tex
# → produces papers/my-paper/audit/ with theorem inventory,
#   per-unit checks, issue log, final report

# 2. Design repairs with literature support
/proof-repair papers/my-paper/
# → produces REPAIR_PLAN.md, PATCHES.md, repair_references.bib

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
