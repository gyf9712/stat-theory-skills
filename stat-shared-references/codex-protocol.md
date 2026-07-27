# Codex Discussion Protocol — Shared across all skills

This document defines how Claude skills in `stat-theory-skills` invoke Codex
(via MCP) as an adversarial reviewer. It applies uniformly to **proofcheck**,
**proof-repair**, **theory-sharpen**, **theory-simulation**, and **theory-design**.

## Core principle

**Codex is an adversarial reviewer, NOT an oracle.**

The goal is **iterative discussion until convergence or escalation** — never
wholesale acceptance, never reflexive rejection. Each Codex finding must be
critically evaluated, and Claude must defend its position or update it
with explicit reasoning.

## Why this matters

LLM-to-LLM review has two failure modes:
- **Capitulation**: Claude accepts every Codex finding to avoid disagreement,
  producing output shaped by whichever model is louder, not whichever is right
- **Defensiveness**: Claude dismisses Codex findings to defend prior work,
  losing the value of independent review

Both produce worse outputs than a single careful Claude pass. The protocol
below forces structured deliberation that exploits both models without
inheriting either's blind spots.

## The 5-round protocol

### Round 1 — Claude produces its output
The skill completes its primary task (proof check, repair plan, framework
design, simulation plan, etc.) using its own reasoning.

### Round 2 — Send to Codex with adversarial framing
```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are an adversarial reviewer / senior referee for a top stat journal.
    Be harsh — find real weaknesses. Do not be polite. Do not "balance" praise.

    [Claude's output to review]

    Adversarial review tasks:
    1. [specific dimensions to attack]
    2. [more specific dimensions]
    ...

    Output: numbered findings with severity (CRITICAL / MAJOR / MINOR / NIT).
    For each, propose a concrete fix.
```

### Round 3 — Claude critically evaluates each finding
For each Codex finding, Claude MUST decide one of:

| Decision | When to use | What Claude does |
|----------|------------|-------------------|
| **ACCEPT** | Finding is factually correct OR exposes a real gap | Update the output; record what changed |
| **PUSH BACK** | Claude has a substantive counter-argument | Send the counter-argument to Codex |
| **REQUEST CLARIFICATION** | Finding is ambiguous or the proposed fix is unclear | Ask Codex for specifics |

**Forbidden behaviors**:
- Silently accept all findings to "avoid friction"
- Silently reject all findings to "defend the work"
- Accept findings without recording WHY they were correct
- Reject findings without recording WHY the push-back is substantive

### Round 4 — Codex responds to push-back / clarification
Send via `mcp__codex__codex-reply` on the same threadId. Codex can:
- **Concede**: agree with Claude's push-back; finding withdrawn
- **Refine**: adjust the finding based on Claude's point
- **Hold firm**: give a concrete reason a reviewer would still attack on this

### Round 5+ — Iterate until convergence
Repeat Round 3-4 until one of:

| Outcome | Action |
|---------|--------|
| **Convergence** — both agree | Apply changes; document log |
| **Persistent disagreement** on specific point | Escalate to user with both arguments |
| **>3 rounds without progress** | Stop; escalate; do not waste cycles |

### Round Final — Document the discussion log
Every skill that uses Codex MUST emit a `codex_discussion.md` file containing:

```markdown
# Codex Discussion Log — [skill name] for [topic]

## Round 1: Claude's initial output
[summary or link]

## Round 2: Codex review (N findings)
| # | Severity | Finding | Codex's proposed fix |

## Round 3: Claude's per-finding evaluation
| # | Decision | Reasoning | Action |

## Round 4: Codex response to push-back
| # | Codex response | Refined position |

## Round 5+: Iterations (if any)
[per round]

## Final state
| # | Original Codex finding | Final resolution | What changed |

## Escalations to user (if any)
| # | Disagreement | Claude's position | Codex's position |
```

This log is visible to the user — it makes the LLM-to-LLM negotiation
**transparent**, so the user can override either model's position.

## When NOT to use Codex

- Tasks too small to justify the round-trip cost (<1 minute of Claude work)
- Tasks where Codex's training cutoff might make it less informed than Claude
- Tasks where the user has already given strong direction (Codex's "what's missing"
  may contradict explicit user preferences — surface to user, don't auto-act)

## When Codex disagreement is irreducible

Some disagreements are not about facts but about taste / philosophy / venue
preferences. In these cases:
- Document both positions in the log
- Surface to the user with explicit "Claude says X because A; Codex says Y because B"
- Let the user pick — do not let either LLM unilaterally win

## Reasoning Effort Ladder

The default `model_reasoning_effort` for Codex calls is `medium`. Escalate to `xhigh` whenever **what is being audited** (not which skill is calling) falls into one of the high-risk content classes below.

### Forced `xhigh` triggers

Use `xhigh` whenever the Codex call's scope includes any of:

- A theorem, lemma, proposition, or corollary statement
- An assumption block, or any change to an assumption (addition, removal, narrowing, broadening)
- A proof step, especially one involving an inequality, exchange of limits, or a "by standard arguments" jump
- A rate, constant, or order-of-growth expression
- A quantifier choice (pointwise vs uniform, $\forall \exists$ vs $\exists \forall$, "fixed $t$" vs "uniformly over $t \in T_n$")
- A probability level (high-probability bound, sub-Gaussian / sub-exponential conditions, tail control)
- A dependency edge between proof units (Lemma A used by Theorem B)
- A Weaken-Claim change-log row (original → revised claim)
- A post-repair convergence verdict
- An assumption-ledger consistency check
- A minimax lower-bound argument or optimality claim

The trigger is content-driven, not skill-driven. If `stat-polishing` is polishing a theorem statement, the Codex call must be `xhigh` even though polishing is normally a `medium` task. Conversely, `proof-repair` cleaning up the prose of a remark can be `medium` if the remark contains no math.

### Allowed `medium` calls

`medium` is appropriate when the entire scope of the call is one of:

- Prose polish on non-mathematical sentences (introduction motivation, application discussion, abstract opening)
- Figure caption critique
- Figure-design audit (color, legend, sentence-case caption)
- Reproducibility checklist triage (data availability statement language, code availability statement language)
- LaTeX template conformance (documentclass, line spacing, bibliography style)
- Citation completeness scan (is paper X cited? is the citation key correct?)
- Style-discipline audit (em-dash count, semicolon use, watchword scan)
- Venue-checklist triage

### Honest failure cases that motivate the ladder

`medium` will mis-call `xhigh` findings in stats-theory proof verification in at least three concrete ways (verified by Codex's own self-assessment, threadId `019e6ed3-0b5d-7e72-b424-5428423a2276`):

1. **Quantifier order**: medium may accept "for each fixed $t$" as if it were "uniformly over $t \in T_n$", especially in empirical process or high-dimensional rate arguments.
2. **Rate bookkeeping**: medium may miss that $o_p(n^{-1/2})$ requires a sparsity / log-factor condition stronger than the paper states, or that constants depend on dimension after a "uniformly bounded" claim.
3. **Dependency depth**: medium may verify Lemma 3 locally but miss that it depends on Assumption B only after a repair weakened Assumption A, breaking the main theorem's dependency graph.

These are exactly the bugs the proof skills exist to catch. Using `medium` on these classes silently weakens the pipeline's correctness guarantee.

## Artifact Manifest Header

Every artifact generated by a Codex-invoking skill must begin with a six-line YAML-style manifest header. The header lets downstream skills load only the artifacts they actually need, and lets re-audit verify whether an artifact is still fresh against the current paper state.

```markdown
---
artifact: [audit | repair_plan | re_audit_report | diff_ledger | codex_discussion | proof_package | simulation_report | framework_design]
scope: [local | dependency_expanded | global]
source_files: [paper.tex, supplement.tex, ...]
theorem_ids: [Thm 2.1, Lemma C.3, Cor 2.2, ...]    # or [] if N/A
assumption_ids: [A1, A2, A_new1, ...]              # or [] if N/A
issue_ids: [I-01, I-03, I-05, ...]                 # or [] if N/A
commit: [short SHA or content hash]
generated: [YYYY-MM-DD HH:MM]
generator: [skill name + version, e.g., proof-repair v1.6.0]
---

# [Artifact body starts here]
```

### Why the manifest

- **Lazy loading**: a downstream call (e.g., `stat-mock-review` reading `REPAIR_PLAN.md`) checks the manifest first. If `scope: local` and the call needs `dependency_expanded` context, the call knows to also load the dependency graph artifact rather than assuming the repair plan covers it.
- **Staleness detection**: if the manifest's `commit` is older than the latest `git rev-parse HEAD` of the paper repo, the artifact may be stale; re-audit flags it.
- **Token economy in chained calls**: a Codex call passing `RE-AUDIT_REPORT.md` does not need to also paste `REPAIR_PLAN.md` if the manifest declares which `issue_ids` the re-audit covers — Codex can ask for specific upstream artifacts by ID instead of receiving them speculatively.

### Required fields

| Field | Meaning |
|---|---|
| `artifact` | One of the canonical artifact types in the pipeline |
| `scope` | `local` = single unit; `dependency_expanded` = unit + its dependencies; `global` = whole-paper view |
| `source_files` | All `.tex` (or other source) files this artifact derives from |
| `theorem_ids` | Every theorem / lemma / proposition / corollary whose statement is in scope |
| `assumption_ids` | Every assumption whose statement is in scope |
| `issue_ids` | Every issue from `issue_log.md` referenced in the body |
| `commit` | Git short SHA of paper repo at generation time, or content hash if not in git |
| `generated` | Timestamp |
| `generator` | Skill + version that produced the artifact |

### Where the manifest appears

Every generated `.md` file in `audit/`, `papers/<paper-name>/`, and any `*_DISCUSSION.md` / `*_REPORT.md` / `*_PLAN.md` / `*_LEDGER.md` file. Per-unit local checks in `audit/04_local_checks/` should also have a manifest with `scope: local` and a single theorem_id.

## Per-Repair Fresh Thread (the OPT7-C anti-pattern)

The naive approach to per-repair adversarial stress-testing — `proof-repair` Step 5C — is to run all P0 / P1 repairs sequentially in one Codex thread, accumulating context. This is **forbidden**. Codex anchors to its emerging narrative across the thread:

> Codex's own self-assessment (threadId `019e6ed3-0b5d-7e72-b424-5428423a2276`):
> "I do anchor somewhat. Not catastrophically, but enough that eight sequential stress-test calls in one thread will drift toward the thread's emerging narrative, especially if earlier repairs were accepted."

### The protocol

For each independent repair under stress-test:

1. **Fresh thread per logically-independent repair.** Use `mcp__codex__codex` (not `codex-reply`). Repairs that share a direct dependency edge (e.g., Patch 3 fixing Lemma B.2 and Patch 4 fixing Lemma B.4 which uses B.2) may be batched into one fresh thread as a small dependency cluster, up to 2–3 repairs.
2. **No batching of unrelated repairs.** Patch 1 fixing Lemma C.3 and Patch 5 fixing Theorem 3.1 (logically independent) must be separate threads.
3. **Manifest travels, conversation does not.** Each fresh call carries the artifact manifests for the current patch and any direct dependencies. Prior verdicts from other repairs are NOT included in the prompt.
4. **Anti-anchor prompt language.** Each fresh call opens with: "This is an independent repair review. Treat the proposed repair on its merits. Prior repair verdicts in this pipeline are not part of your context."
5. **Require falsification attempt.** Each call must explicitly attempt one of: missing assumption, dependency break, rate / quantifier mismatch, downstream theorem impact. The verdict must name which falsification was attempted and whether it succeeded.

### Two-vs-three cluster rule

Logically-related repairs can share a fresh thread (token savings) only when:

- They sit on the same dependency edge OR
- They modify the same assumption block OR
- They are part of a single Weaken-Claim propagation chain

Even within a cluster, each repair must end with its own ACCEPT / PUSH BACK / REQUEST CLARIFICATION verdict, with the anti-anchor framing repeated before each new repair in the cluster.

### What this costs

Per-repair fresh thread is **slightly more expensive in tokens** than the naive shared-thread approach because the manifest is re-sent each time. The trade is correctness: silent anchoring on a proof skill produces silent false-pass verdicts, which is the exact failure mode the skill exists to prevent.

### Per-Repair Stress-Test Call Template

The canonical template for the per-repair Codex stress-test call. Used by `proof-repair` Step 5C and by any other skill performing per-unit adversarial stress-tests.

For each P0 / P1 repair with a complete proof, in its own fresh thread:

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "xhigh"}
  prompt: |
    This is an independent repair review. Treat the proposed repair on its
    merits. Prior repair verdicts in this pipeline are not part of your
    context. You are an adversarial reviewer / senior referee for a top
    stat journal.

    Artifact manifest for this call:
    - artifact: repair_review
    - scope: dependency_expanded
    - source_files: [paper.tex, supplement.tex if Mode B]
    - theorem_ids: [the unit being repaired + direct dependents]
    - assumption_ids: [original assumptions in scope + any new ones added by this patch]
    - issue_ids: [the original issue ID this repair targets]
    - generator: proof-repair v1.x.x Step 5C

    ORIGINAL ISSUE:
    [Paste: issue description, affected unit, severity]

    PROPOSED REPAIR (this patch only):
    [Paste: repair strategy, new/modified lemma statement, complete proof]

    NEW REFERENCES CITED (this patch only):
    [Paste: each cited result with venue, theorem statement, assumptions]

    DIRECT DEPENDENCIES (manifest references only, not full content):
    - Assumption ledger: papers/<name>/audit/02_ledgers/assumption_ledger.md
    - Dependency graph: papers/<name>/audit/03_dependencies/dependency_graph.md
    Request these by ID if you need them.

    ADVERSARIAL TASKS — pick at least one falsification attempt:
    1. Missing-assumption attack: does the repaired proof rely on a condition
       not in the assumption block?
    2. Dependency-break attack: does the repair weaken a property that a
       downstream theorem needs at the original strength?
    3. Rate / quantifier mismatch attack: are quantifiers pointwise where
       the conclusion needs uniform? Does a constant secretly depend on
       dimension / sample size?
    4. Downstream theorem impact: if this repair propagates, do declared
       downstream patches in the Weaken-Claim Change Log cover every affected
       consumer?

    Output (required structure):
    - Falsification attempt: [name which attack you tried]
    - Falsification result: [succeeded — repair has a real defect / failed —
      repair survives this attack]
    - Verdict: PASS / FIXABLE / FAIL
    - If FIXABLE or FAIL: specific objection, location in proof, proposed minimal fix
    - If PASS: state the strongest specific objection you considered and
      rejected, so the discussion log shows the attack you ran
```

### Per-Repair Stress-Test Verdict Recording

Verdicts are recorded in `audit/07_repairs/codex_stress_test.md`. The file begins with the artifact manifest header and has one row per repair:

```markdown
---
artifact: codex_stress_test
scope: dependency_expanded
source_files: [paper.tex, supplement.tex]
theorem_ids: [Thm 2.1, Thm 3.1, Lemma B.2, Lemma B.4, Lemma C.3, Cor 2.2, ...]
assumption_ids: [A1, A2, A_new1, A_new2, ...]
issue_ids: [I-01, I-03, I-05, ...]
commit: [paper-repo short SHA]
generated: [YYYY-MM-DD HH:MM]
generator: proof-repair v1.x.x Step 5C
---

# Codex Stress-Test Verdicts (per-repair, fresh threads)

| Repair | Codex threadId | Falsification attempt | Verdict | Issues raised | Resolved? | Final status |
|--------|---------------|----------------------|---------|---------------|-----------|--------------|
| I-01 | 019eXXXX-... | Missing assumption | PASS | None | — | Confirmed |
| I-03 | 019eXXXX-... | Dependency break | FIXABLE | Edge case d=1 not handled | Yes, added | Confirmed after revision |
| I-05 | 019eXXXX-... | Quantifier mismatch | FAIL → revised → PASS | Original proof had sign error in step 4 | Rewritten | Confirmed after rewrite |
| I-07 + I-08 (cluster, share dependency edge) | 019eXXXX-... | Downstream impact | PASS | None | — | Confirmed |
```

The `Codex threadId` column is required so the user can resume any individual repair's dialogue. Each threadId is a fresh thread, not a continuation of an earlier repair's thread.

### Iterating on FIXABLE / FAIL verdicts

If Codex returns FIXABLE or FAIL on a given thread:

1. Address Codex's specific objections.
2. Revise the repair.
3. Re-submit to Codex via `mcp__codex__codex-reply` **on that thread** (Case B continuation: same finding under discussion, same thread).
4. Iterate until PASS or document the disagreement (see the 5-round protocol above).

The iteration uses `codex-reply` because the object under discussion is the same finding. Switching to a fresh thread here would lose the dialogue context that makes convergence possible.

### Inter-phase application

The same fresh-thread + manifest rule applies across the audit → repair → post-repair phases. Each phase opens a fresh thread; the manifest carries the cross-phase context (issue IDs, repair patches, diff ledger summary). Conversation history does not cross phases — only manifest references do.

Within the same phase, the iterative dialogue protocol (the 5-round protocol above) uses `codex-reply` on a single thread because the object under discussion is the same finding. This is correct and required; it is not the anchoring failure mode.

## Examples of the protocol in practice

The repo's CHANGELOG documents real instances:
- `theory-simulation v1.1.1`: Codex raised 20 findings; Claude accepted 13,
  pushed back on 6 (Codex agreed with 5 refinements, held firm on 1 which
  Claude then accepted)
- `theory-simulation v1.2.0`: Codex raised 4 more in second round; all accepted
- `theory-simulation v1.2.0` (AUDIT mode review): Codex raised 4 major + 2 minor;
  all accepted after discussion

The discussion is the value — not the verdict.
