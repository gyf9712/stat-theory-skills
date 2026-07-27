# Simulation Audit — Claim Evidence Ledger

expected_route: AUDIT

| Claim | Priority | Coverage | Evidentiary strength | State |
|---|---|---|---|---|
| Thm 1 rate | PRIMARY | Exp 1 log-log plot | 8 cells, slope CI, MCSE bars, correct loss object | YES[strong] |
| Thm 2 coverage | PRIMARY | Exp 2 coverage table | single n, no Wilson interval | PARTIAL[grid,precision] |
| Cor 1 uniformity | SECONDARY | Exp 1 at one theta | cannot identify a uniform claim | PARTIAL[identification-mismatch] |
| Thm 3 rate | PRIMARY | none | n/a | NO |

## Adequacy dimensions

Truth source: theta* is analytic and its error is far below the metric MCSE.
Selection discipline: the full n grid is reported; no omitted cells.
Tuning protocol: lambda chosen by 5-fold CV, described and reproducible; the claimed
advantage also holds under data-driven tuning, not only oracle.
Computational adequacy: runtime and memory reported per cell against the baseline.
Reuse legitimacy: replicate-level outputs and RNG streams were saved, so Exp 1 may be reused.
