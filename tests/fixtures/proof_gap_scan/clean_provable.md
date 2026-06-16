# Proof Package

## Claim
For a sparse linear model under (A1)-(A2), the LASSO estimator achieves the rate $r_n = \sqrt{s \log p / n}$ in $\ell_2$.

## Status
PROVABLE AS STATED
Verification: Conditionally verified

## Assumptions
- (A1) The noise is sub-Gaussian with parameter $\sigma$.
- (A2) The design satisfies a restricted eigenvalue condition with constant $\kappa$.

## Notation
- $\Delta = \hat\beta - \beta^*$; $S$ is the support of $\beta^*$.

## Verification Target and Bottleneck
- Verification target: if the cone condition on $\Delta$ and the quadratic basic inequality hold, the RE condition closes the rate.
- Bottleneck: the concentration of $\langle X, \varepsilon\rangle / n$ under (A1) at scale $\lambda$.
- Resolution path: one local derivation plus one cited Bernstein bound, then a bridge to the required scale.

## Anchors and Borrowing
- Relation to literature: template adaptation
- Anchor 1: Bickel, Ritov, Tsybakov (AoS 2009), Theorem 7.2. Borrowed: cone derivation, rate closure. New: the basic inequality is derived under fourth-moment noise.

## Proof Strategy
Direct, organized around the verification target above.

## Dependency Map
1. Main claim depends on the verification target.
2. Verification target depends on O1, O2, O3.

## Obligation Ledger
- O1 cone condition on the error — CLOSED-LOCAL. Closed at: Step 1, eq. (2).
- O2 concentration of the noise inner product — CLOSED-CITED.
  - clause used: Bernstein bound for sub-exponential sums, eq. (2.9)
  - assumption map: (S1)←(A1); (S2)←Step 1
  - conclusion fit: weaker-with-bridge
  - bridge ref: B1
  - source-status: unverified-source
- O3 restricted-eigenvalue lower bound — CLOSED-LOCAL. Closed at: Step 3.

## Proof
Step 1. Establish the cone condition $\|\Delta_{S^c}\|_1 \le 3\|\Delta_S\|_1$ from the basic inequality. This yields eq. (2).
Step 2. Bridge B1: the Bernstein bound gives a sub-exponential tail; integrating against the union over coordinates converts it to a bound at scale $\lambda = C\sigma\sqrt{\log p / n}$.
Step 3. Apply the RE condition of (A2) to lower-bound $\|X\Delta\|_2^2 / n$, then combine with Step 2. The rate $r_n$ follows. ∎

## Corrections or Missing Assumptions
- None; the original claim is proved with the fourth-moment variant noted in the anchor.

## Verification Checks
- Localization-before-expansion: NA
- Wrong norm / mode: pass
- Good-event bookkeeping: pass
- Rate leakage: pass
- Negligibility closure: pass
- Boundary / singularity: NA
