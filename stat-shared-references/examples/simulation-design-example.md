# Worked Example: A Filled Experiment Design Block

Extracted from `theory-simulation` Step 1A. The contract is in the skill; this is one
filled ADEMP-style design for a rate claim.

```markdown
## Experiment E1 — Verify Theorem 1 (√n-consistency)

### Theoretical prediction
Under Assumptions 1-3: ‖θ̂ − θ*‖ = O_P(n^{-1/2})

### Data Generating Process (DGP)
- X_i ~ i.i.d. P_θ* with θ* = [stated value]
- Sample sizes: n ∈ {50, 100, 200, 500, 1000, 2000, 5000}
- Dimensions: d = [fixed value or sweep]
- Reps: B = 500 per (n, d) cell

### Quantities reported per cell
- Bias: mean(θ̂) − θ*
- Variance: var(θ̂)
- MSE: E‖θ̂ − θ*‖²
- Log-log slope of MSE vs n (should be ≈ −1)

### Pass/fail criteria
- Slope within [−1.1, −0.9] (rate confirmed)
- Bias decays to 0 with n
- 95% bootstrap CI for slope contains −1

### Figure target
- Figure E1: log MSE vs log n, with theoretical slope line overlaid
- Table E1: bias, SD, MSE × n at each n (verifies it stays bounded)
```
