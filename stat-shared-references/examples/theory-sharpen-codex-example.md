# Worked Example: Codex Cross-Assessment (theory-sharpen Step 5B)

Dialogue discipline is in `codex-protocol.md`; this is the reconciliation shape.


**Follow `../stat-shared-references/codex-protocol.md`** — Codex is an adversarial reviewer
to **discuss with iteratively**, not an oracle to defer to. For each Codex finding
about whether an assumption can be relaxed or a rate sharpened, Claude MUST decide
explicitly: ACCEPT (with reasoning), PUSH BACK (with substantive counter-argument),
or REQUEST CLARIFICATION. Especially critical here because simulation/Codex
evidence can OVERCLAIM theory relaxation — see the asymmetry rule in Step 5A.
The skill must emit `codex_discussion.md` documenting the full round-by-round
dialogue.

After Claude completes its analysis (Steps 1-5), use Codex as an **independent second
opinion** on the most important findings. Codex sees the paper but NOT Claude's analysis,
so it can surface blind spots.

**Assessment 1: Assumption relaxation feasibility**
```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    You are an expert in mathematical statistics and ML theory.

    Here is a theorem from a paper:
    [Paste: main theorem statement + all assumptions]

    And here is its proof:
    [Paste: proof or proof sketch of the main result]

    Task: For EACH assumption, independently assess:
    1. Is this assumption essential? (Which proof step would break without it?)
    2. Can it be relaxed? If so, to what weaker condition?
    3. What proof technique would enable the relaxation?
    4. Do you know of published results (top journals: AoS, JASA, JRSS-B, Biometrika,
       Econometrica, JOE, NeurIPS, ICML, JMLR, COLT) that achieve similar results
       under weaker conditions?
    5. If relaxed, would the convergence rate change?

    Be specific: cite theorem names, author-year, and venues when possible.
    If an assumption cannot be relaxed, explain the fundamental barrier.
```

**Assessment 2: Rate optimality check**
```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    A paper proves [result] with rate [rate] under assumptions [list].

    Questions:
    1. Is this rate minimax optimal for this problem class? Cite the lower bound if known.
    2. If not optimal, what is the best known rate? Who achieved it and in which venue?
    3. Are there specific proof steps that introduce suboptimality (e.g., loose union
       bounds, crude norm inequalities, unnecessary covering numbers)?
    4. What technique would sharpen the rate?
    
    Focus on T1 venue references (AoS, Econometrica, NeurIPS/ICML/COLT, JMLR).
```

**Assessment 3: Theory-practice gap**
```
mcp__codex__codex:
  config: {"model_reasoning_effort": "high"}
  prompt: |
    A paper proposes [model description] and proves theoretical guarantees under
    assumptions [list]. The experiments test [experimental setup].

    Questions:
    1. Are the theoretical assumptions realistic for this model?
    2. Which assumptions are likely violated in the experimental setup?
    3. Are there published results that handle more realistic conditions?
    4. Does the theoretical rate match what you would expect empirically?
    5. What additional experiments would strengthen the theory-practice connection?
```

**Reconciliation with Claude's analysis**:

After Codex responds, compare with Claude's findings from Steps 1-5:

```markdown
## Codex Cross-Assessment Reconciliation

### Assumption Relaxation
| Assumption | Claude says | Codex says | Agreement? | Combined assessment |
|-----------|------------|------------|------------|-------------------|
| A1: i.i.d. | Relaxable to mixing | Relaxable to MDS | PARTIAL | Both agree relaxable; MDS may be simpler |
| A3: sub-G | Relaxable (Catoni) | Essential — proof breaks | DISAGREE | Needs manual review ⚠ |

### Rate Sharpness
| Result | Claude says | Codex says | Agreement? | Combined assessment |
|--------|------------|------------|------------|-------------------|
| Thm 3 log factor | Removable via chaining | Removable via localization | AGREE (different technique) | High confidence: removable |

### Theory-Practice Gaps
| Gap | Claude says | Codex says | Agreement? | Combined assessment |
|-----|------------|------------|------------|-------------------|
| Strong convexity in experiments | Model only locally convex | Same + suggests PL condition | AGREE + Codex adds detail | Use PL condition approach |
```

**Disagreement handling**:
- If both models agree → HIGH confidence, proceed
- If models disagree on feasibility → flag for human review, present both arguments
- If only one model found an opportunity → MEDIUM confidence, include but mark
- If Codex finds something Claude missed → add to improvement roadmap with source = "Codex"

Write to `audit/08_sharpen/codex_assessment.md`.

---

