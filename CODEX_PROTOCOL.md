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

## Examples of the protocol in practice

The repo's CHANGELOG documents real instances:
- `theory-simulation v1.1.1`: Codex raised 20 findings; Claude accepted 13,
  pushed back on 6 (Codex agreed with 5 refinements, held firm on 1 which
  Claude then accepted)
- `theory-simulation v1.2.0`: Codex raised 4 more in second round; all accepted
- `theory-simulation v1.2.0` (AUDIT mode review): Codex raised 4 major + 2 minor;
  all accepted after discussion

The discussion is the value — not the verdict.
