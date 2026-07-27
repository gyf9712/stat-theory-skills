# Worked Example: A Filled Repair Specification

The compact contract lives in `proof-repair` Step 5. This is one filled specimen showing
an Insert-Lemma repair (hidden Hessian-invertibility assumption) written in both
reference modes. It is an illustration, not a schema: where the two disagree, the
contract in the skill wins.

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

# Worked Example: Impact Analysis (same I-01 issue)

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

---

# Worked Example: Candidate Repairs (same I-01 issue)

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
