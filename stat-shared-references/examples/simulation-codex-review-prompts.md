# Worked Example: Codex Simulation-Design Review Prompts

Extracted from `theory-simulation` Step 4F. The dialogue discipline itself is in
`codex-protocol.md`; these are the simulation-specific prompt and the
reconciliation-table shape.


**Follow `../stat-shared-references/codex-protocol.md`** — Codex is an adversarial reviewer
to **discuss with iteratively**, not an oracle to defer to. Every Codex finding
about the simulation plan or figures requires explicit ACCEPT / PUSH BACK /
REQUEST CLARIFICATION with reasoning. Especially critical here because expensive
sim reruns triggered by reflexive Codex acceptance waste CPU days. The skill
must emit `simulation/codex_discussion.md` documenting the full round-by-round
dialogue.

Before running expensive simulations, send the SIMULATION_PLAN.md to Codex for an
independent design review. Catching design flaws BEFORE running saves CPU hours.
After running, do a second Codex pass on the figures + reconciliation.

### Pass 1: Plan review (before running)

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are a senior referee for a top statistics journal (AoS / JASA / Biometrika / JRSS-B).
    A paper provides the following theoretical claims and proposed Monte Carlo simulation plan.

    THEORETICAL CLAIMS:
    [paste main theorems with assumptions + rates]

    SIMULATION PLAN:
    [paste SIMULATION_PLAN.md]

    Adversarial review tasks (be harsh — assume the simulation IS the test of the theory):
    1. Coverage: does EVERY theoretical claim have a verification experiment?
       Which assumptions are NOT stress-tested? Name them specifically.
    2. DGP quality: are the chosen DGPs the WORST CASES the theory should handle, or
       are they easy cases that any method would pass?
    3. Sample-size grid: is the range wide enough to identify the rate? Is it deep
       enough to see finite-sample breakdown? Suggest specific n values to add.
    4. Replication count: is B large enough for the metrics? (Coverage needs B ≥ 1000
       for ±0.014 SE at nominal 0.95; tail metrics need more.)
    5. Baselines: is the comparator the right one? Is there an obvious competitor missing?
    6. Rate verification: is the slope-regression protocol valid? Is there a known
       bias-variance issue (e.g., bias term dominating at small n)?
    7. Missing stress tests: list any standard violation that should be tested but isn't.

    Output a numbered list of design issues with severity (CRITICAL / MAJOR / MINOR).
    For each, propose a specific fix.
```

### Pass 2: Figure + reconciliation review (after running)

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are reviewing simulation results from a paper aimed at a top stat journal.

    THEORY:
    [paste theorems]

    SIMULATION RESULTS:
    [paste aggregated metrics tables — e.g., bias/SD/MSE × n for each method × DGP]

    RECONCILIATION CLAIM:
    [paste RECONCILIATION.md draft]

    FIGURE CAPTIONS:
    [paste each \caption text]

    Adversarial review tasks:
    1. Do the empirical numbers ACTUALLY support the claimed reconciliation, or is
       the author overclaiming "✅ confirmed" when slope is borderline?
    2. Are any results SUSPICIOUS — e.g., coverage above 0.99 (overcoverage), or
       MSE non-monotone in n? Could these signal a coding bug?
    3. For each "discrepancy" the author flags as theory-relaxation opportunity:
       is the relaxation actually supported, or could the simulation be too easy?
    4. Caption sanity: do captions state the DGP, B, n range, baselines, and the
       theoretical prediction explicitly? Flag any captions missing context.
    5. Figure-level issues: based on the captions alone, is the figure asking the
       right question? Is the dashed reference line the right slope?

    Output: per-finding verdict (CONFIRMED / OVERCLAIMED / UNDERCLAIMED / SUSPICIOUS)
    with specific evidence.
```

### Reconciliation with Claude's findings

Same pattern as the other skills: first-independent-then-reconcile.

```markdown
## Codex Simulation Design Review

### Pass 1 (Pre-run) findings
| Issue | Severity | Codex says | Claude action |
|-------|---------|------------|---------------|
| Stress test for dependence missing | MAJOR | Add AR(1) DGP | Adding to plan |
| B=500 too small for coverage | CRITICAL | Use B=2000 for coverage cells | Adjusting plan |
| No competitor for Thm 3 | MINOR | Add MLE | Noted; addressed |

### Pass 2 (Post-run) findings
| Finding | Codex verdict | Claude original | Final |
|---------|--------------|-----------------|-------|
| Thm 1 rate slope = -0.51 | CONFIRMED | ✅ Confirmed | Agree |
| "Sub-G can be relaxed" | OVERCLAIMED — only tested t_5, didn't test t_3 | Relaxation candidate | Downgrade to "needs more tests" |
| Coverage at n=2000 is 0.991 | SUSPICIOUS — overcoverage suggests CI too wide | ✅ Confirmed | Investigate; may be variance plug-in conservative |
```

Write to `simulation/codex_design_review.md`.

**Critical**: when Codex flags OVERCLAIMED or SUSPICIOUS, DO NOT auto-update
RECONCILIATION.md to silently match. Surface the disagreement to the user.

---


---

# Codex Cross-Audit Prompt (AUDIT mode, Step A5)


After Claude completes the audit, send to Codex for independent verification:

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are a senior referee for a top stat journal reviewing a paper's existing
    simulation section.

    THEOREMS:
    [paste]

    EXISTING SIMULATION SECTION:
    [paste]

    Tasks (be harsh):
    1. For each theorem, identify whether the existing experiments actually verify
       what the theorem CLAIMS, or only something weaker / different.
    2. List every assumption the theorem makes that is NOT stress-tested.
    3. List every metric the paper REPORTS that does NOT match what the theorem
       BOUNDS. (E.g., theorem on ‖·‖, paper reports MSE.)
    4. Find any cherry-picking signals (single θ, single DGP variant, suspicious
       choice of n grid).
    5. Find any results that look TOO clean (suspiciously low variance, MSE exactly
       matching theoretical curve, etc.) — possible coding errors or selection.
    6. List the top-3 most important missing experiments.

    Output: ordered list of issues with severity (CRITICAL / MAJOR / MINOR).
```

Reconcile Codex's findings with Claude's audit. Disagreements get flagged for user.

### Output for AUDIT mode

```
papers/<paper-name>/simulation_audit/
  EXISTING_SIMS.md          # parsed inventory
  COVERAGE_MATRIX.md        # claims × evidence
  ADEQUACY_AUDIT.md         # per-experiment scoring
  GAP_ANALYSIS.md           # what's missing
  IMPROVEMENT_PLAN.md       # targeted, minimal new work
  codex_audit.md            # independent second opinion (if Codex available)
```

After AUDIT, if user wants to implement the improvement plan, the skill switches
to HYBRID mode: re-uses Steps 1-7 below for ONLY the new experiments identified
in `IMPROVEMENT_PLAN.md`.

---

