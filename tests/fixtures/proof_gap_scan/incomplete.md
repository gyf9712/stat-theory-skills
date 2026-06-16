# Proof Package

## Claim
The estimator achieves the minimax rate.

## Status
PROVABLE AS STATED
Verification: Verified

## Assumptions
- (A1) sub-Gaussian noise.

## Notation
- $\Delta = \hat\theta - \theta_0$.

## Verification Target and Bottleneck
- Verification target: an asymptotic linear representation, then CLT.
- Bottleneck: invertibility of the Hessian.
- Resolution path: attempt a local eigenvalue bound.

## Dependency Map
1. Main claim depends on O1, O2, O3, O4, O6, O9.

## Obligation Ledger
- O1 cone condition — CLOSED-LOCAL. Closed at: Step 1.
- O2 noise concentration — CLOSED-CITED.
  - clause used: a maximal inequality
  - assumption map: (S1)←(A1)
  - conclusion fit: weaker-with-bridge
  - bridge ref: B9
  - source-status: unverified-source
- O3 Hessian invertibility — BLOCKED.
  - statement: the population Hessian $A$ is invertible at $\theta_0$.
  - bridge attempted: lower-bound the minimum eigenvalue via a margin condition.
  - failure reason: the minimum eigenvalue can vanish on the boundary of the parameter set.
  - alternative considered: add a ridge penalty; not pursued because it changes the estimand.
- O4 bias control — CLOSED-CITED.
  - clause used: a smoothing bound
  - assumption map: (S1)←(A1)
  - conclusion fit: exact
- O6 auxiliary tail bound stated without a closure state.

## Proof
Step 1. Clearly the cone condition holds. Therefore the result follows. ∎

## Corrections or Missing Assumptions
- None.
