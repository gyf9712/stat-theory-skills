# stat-theory-skills

A pipeline of 4 Claude Code skills for working with mathematical proofs in
statistics, econometrics, and ML theory papers. Goes from **finding proof errors**
all the way to **theoretical sharpening with literature support**.

> Built on top of [maweiruc/proofcheck-stat-paper](https://github.com/maweiruc/proofcheck-stat-paper),
> then extended with proof repair, theory sharpening, and Codex MCP cross-review.

## The Pipeline

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│ /proofcheck │ →  │ /proof-repair│ →  │/theory-sharpen │ →  │ /proof-writer│
│             │    │              │    │                │    │              │
│ Find proof  │    │ Fix issues + │    │ Strengthen the │    │ Write the    │
│ errors      │    │ literature   │    │ theory itself  │    │ corrected /  │
│             │    │ support      │    │                │    │ new proof    │
└─────────────┘    └──────────────┘    └────────────────┘    └──────────────┘
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

After install, in Claude Code use:
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

- **Original methodology**: [maweiruc/proofcheck-stat-paper](https://github.com/maweiruc/proofcheck-stat-paper) by Wei Ma
- **`proof-writer`**: pre-existing skill, not authored here
- **Pipeline design + literature integration + Codex cross-review**:
  developed iteratively with Claude (Sonnet) and Codex (GPT)
- **Reference library venue audit**: Codex GPT independent review

## License

MIT — see [LICENSE](LICENSE)
