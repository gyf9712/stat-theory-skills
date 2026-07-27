# Worked Example: Codex Framework-Review Dialogue (theory-design X4)

The dialogue discipline is in `codex-protocol.md`. This is the per-finding evaluation
shape and a worked round-by-round record.


Follow the repo's `../stat-shared-references/codex-protocol.md` (Codex Discussion Protocol) — Codex is an
**adversarial reviewer to discuss with, not an oracle to defer to.** Every
Codex finding requires explicit ACCEPT / PUSH BACK / REQUEST CLARIFICATION.

#### Round 2 — Send framework to Codex for adversarial review

```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are an adversarial senior referee for a top stat journal
    (AoS / JASA / JRSS-B / Biometrika / Econometrica).
    Be harsh — find real weaknesses. Do not be polite.

    A statistics researcher has drafted a framework for a new [paper_type] paper.
    The framework includes a mandatory literature anchor (Step 0.5).

    LITERATURE_ANCHOR.md:
    [paste]

    FRAMEWORK_DESIGN.md:
    [paste]

    Adversarial review tasks:
    1. Is the paper-type declaration coherent with the framework's actual focus?
       (e.g., user said THEORY but the centerpiece is an estimator → METHODOLOGY)
    2. Is the literature anchor adequate? Did the search miss obvious recent T1 work?
    3. Is the positioning (INCREMENTAL/LATERAL/DISRUPTIVE) realistic given the
       anchor? Is the contribution magnitude believable for the chosen positioning?
    4. Are there logical jumps between phases? (e.g., model setup that doesn't
       support the target results)
    5. Is the asymptotic regime / model choice sensible for the contribution?
    6. What's the most likely reviewer attack on this design?
    7. What's missing? Be specific: name the missing piece + cite an example
       of how recent T1 papers handle it.

    Output: numbered findings with severity (CRITICAL / MAJOR / MINOR / NIT).
    For each, propose a concrete fix.
```

#### Round 3 — Claude evaluates each finding (mandatory)

For EACH Codex finding, decide explicitly:

```markdown
## Per-finding evaluation

| # | Codex finding | Decision | Reasoning |
|---|--------------|----------|-----------|
| 1 | [...] | ACCEPT | [why correct, what to change] |
| 2 | [...] | PUSH BACK | [substantive counter-argument] |
| 3 | [...] | REQUEST CLARIFICATION | [what is ambiguous] |
```

**Forbidden behaviors** (from ../stat-shared-references/codex-protocol.md):
- Silent wholesale acceptance to avoid friction
- Silent rejection to defend prior work
- ACCEPT without recording why the finding was correct
- PUSH BACK without a substantive argument

#### Round 4 — Send push-back / clarifications back to Codex

Use `mcp__codex__codex-reply` on the same threadId. Codex can concede, refine,
or hold firm. Capture each.

#### Round 5+ — Iterate until convergence OR escalation

Continue until one of:
- Convergence: both agree on final findings — apply changes
- Persistent disagreement on specific points — escalate to user with both arguments
- >3 rounds without progress — stop and escalate

#### Final: Write `papers/<paper-name>/design/codex_discussion.md`

Required structure (from ../stat-shared-references/codex-protocol.md):
```markdown
# Codex Discussion Log — theory-design for [topic]

## Round 1: Claude's initial framework
[link to FRAMEWORK_DESIGN.md]

## Round 2: Codex review (N findings)
[table]

## Round 3: Per-finding evaluation
[table]

## Round 4+: Iterations
[per round]

## Final state
[what changed; what disagreements remain]

## Escalations to user (if any)
[both positions stated]
```

This log goes alongside FRAMEWORK_DESIGN.md and LITERATURE_ANCHOR.md.

**Why the protocol matters here**: framework design is precisely where reflexive
acceptance of Codex would be most harmful — the framework determines the entire
downstream paper. A framework shaped by whichever LLM is louder, rather than by
substantive deliberation, will fail review for reasons neither LLM anticipated.

---

