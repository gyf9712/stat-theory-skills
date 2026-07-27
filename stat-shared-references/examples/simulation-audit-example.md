# Worked Example: Simulation Audit Artifacts

Filled specimens extracted from `theory-simulation` AUDIT mode. The contracts and the
typed-state vocabulary live in the skill's Claim Evidence Ledger section; these are
illustrations.

## A filled Claim Evidence Ledger (audit entry route)


```markdown
## Coverage Matrix: Claims × Existing Evidence

| Claim | Priority | Coverage axis | Evidentiary strength axis | Final tag |
|-------|----------|--------------|---------------------------|-----------|
| Thm 1 rate n^{-1/2} | PRIMARY | Exp 1 plot exists | underpowered: 3 cells, no slope CI, wrong metric | PARTIAL[grid,metric,precision] |
| Thm 2 asymptotic normality | PRIMARY | Exp 1 QQ plot | one n, one DGP, no QQ band | PARTIAL[grid,reporting] |
| Thm 2 coverage of 95% CI | PRIMARY | Exp 2 coverage table | single n, no Wilson CI on coverage | PARTIAL[grid,precision] |
| Thm 3 rate n^{-2/(2+d)} | PRIMARY | none | n/a | NO |
| Cor 1 uniformity over Θ | SECONDARY | Exp 1 (single θ) | uniformity claim NOT identified by single-θ test | PARTIAL[setup,identification-mismatch] |
| Robustness to violations | SECONDARY | Exp 3 heavy-tail | only t_3; missing dependence, misspec | PARTIAL[stress-coverage] |
| Computational claim | PRIMARY | none | n/a | NO |
```

**Axis 1: Coverage** — Is there ANY experiment aimed at this claim? (yes / no)

**Axis 2: Evidentiary strength** — Does the experiment actually identify the
claim under top-journal standards?

**Final tag = combination + structured reason code**:

| Tag | Coverage | Strength | Meaning |
|-----|----------|----------|---------|
| `YES[strong]` | ✓ | adequate on all dimensions | claim is genuinely verified |
| `YES[weak]` | ✓ | meets minimum but barely | claim is supported but easily attacked |
| `PARTIAL[X,Y,...]` | ✓ | fails on one or more dimensions | claim only partially verified; reason codes specify which |
| `NO` | ✗ | n/a | no experiment addresses this claim |
| `CONTRADICTED[X]` | ✓ | result conflicts with prediction | red flag — follow CONTRADICTED protocol (A2.5) |

**Reason codes for PARTIAL / CONTRADICTED**:
- `[path]` — asymptotic path violated (e.g., n varies but `s log d/n` not held fixed)
- `[metric]` — measured quantity does not match what the theorem bounds
- `[precision]` — too few replications; MCSE too large to identify the claim
- `[grid]` — too few cells (e.g., 3 sample sizes for rate verification)
- `[comparator]` — required baseline missing or wrong
- `[reporting]` — raw numbers / figure don't permit verification
- `[stress-coverage]` — robustness claim, but only one violation type tested
- `[identification-mismatch]` — experimental setup cannot identify the theoretical claim
  (e.g., single-θ test for a uniform-over-Θ claim)

Multiple codes allowed: `PARTIAL[grid, precision, metric]`.

Audit severity = function of (priority, tag). PRIMARY-claim + `NO` or
`CONTRADICTED[*]` = CRITICAL. SECONDARY-claim + `PARTIAL[reporting]` = MINOR.


---

## A filled per-experiment audit

```markdown
## Audit: Experiment 1 (Section 4.1, "MSE vs sample size")

### What the experiment does
- DGP: X_i ~ N(θ*, I_d), θ* = (1, 1, ..., 1)/√d, d = 5 fixed
- Sample sizes: n ∈ {100, 500, 1000}
- Methods: Proposed, MLE
- Metric: MSE = (1/B) Σ ‖θ̂ − θ*‖²
- B = 500
- Reported: Table 1 (MSE values), Figure 2 (log-log plot)

### Audit against standards

| Criterion | Status | Issue |
|-----------|--------|-------|
| Asymptotic path declared | ❌ | n varies but d fixed; theorem 1 says "fixed d", so OK |
| Loss object matches theorem | ⚠ | Theorem says ‖θ̂−θ*‖, paper measures MSE; slope target = -2a not -a |
| ≥6 cells along path | ❌ | Only 3 n values; cannot reliably fit slope |
| MCSE reported | ❌ | No standard errors on MSE estimates |
| Slope estimate with CI | ❌ | Plot shown but no slope number |
| Paired across methods | UNKNOWN | Code not provided; cannot tell if methods share seeds |
| B selected by MCSE target | ⚠ | B=500 fixed, no justification |
| Failure rate reported | ❌ | Not stated |
| Stress tests | ⚠ | Only baseline; no assumption violations |
| Anti-cherry-picking | ⚠ | Single θ value; no preregistration of headline |
| Figure shows MC uncertainty | ❌ | No error bars or bands |
| Caption is content-bearing | ⚠ | Caption says "MSE vs n" but does not state DGP, B, theoretical slope |

### Severity
- 3 ❌ critical: too few cells, no MCSE, no slope estimate
- 4 ⚠ moderate: loss object mismatch, B not justified, single θ, weak caption
- Verdict: PARTIAL verification of Theorem 1
```
