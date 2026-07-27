---
artifact: shared_reference
scope: relaxation_pathways
generator: extracted from theory-sharpen Step 1C per Codex threadId 019fa42e-217f-7171-b94f-99b95177aab8 (fixed library out of the hot body)
---

# Standard Relaxation Pathways (framework-tagged)

The catalogue of known assumption-relaxation routes, tagged by framework axis, with the
selection logic that filters them against a paper's Step 0.5 classification. Consumed by
`theory-sharpen` Step 1C. The skill keeps the selection RULE; this file holds the table.


*Venue-verified with Codex cross-check. All references T1 unless noted.*

### Framework Tag Legend

Each pathway is tagged with [Data | Framework | Regime] for filtering:

**Data**: `IID` `MIX` (mixing) `TS` (time series) `MARKOV` `PANEL` `SPATIAL`
         `SEQ` (sequential/adaptive) `NETWORK` `MDS` (martingale-difference) `ANY`

**Framework**: `PAR` (parametric) `SEMI` (semiparametric) `NONPAR` (nonparametric) `ANY`

**Regime**: `CLA` (classical asymptotic, n→∞, d fixed) `PROP` (proportional, d/n→γ)
            `HD` (high-dim sparse, d≫n) `FS` (finite-sample/non-asymptotic)
            `ONLINE` (sequential/online) `ANY`

Use the user-confirmed classification from Step 0.5 to FILTER which pathways apply.

---

**Dependence relaxation**

| From → To | Tags | Technique | Key references |
|-----------|------|-----------|----------------|
| i.i.d. → Stationary β-mixing | `MIX/TS` `ANY` `ANY` | Blocking + coupling (Berbee-type) | Doukhan (1994, Springer); Yu (1994, *AoP*); Rio (2017, Springer) |
| i.i.d. → Stationary α-mixing | `MIX/TS` `ANY` `ANY` | Covariance inequalities + blocking | Bradley (2005, *Prob Surveys*); Dedecker et al. (2007, Springer) |
| i.i.d. → Martingale difference | `MDS/SEQ` `ANY` `ANY` | MDS CLT + martingale concentration | Hall & Heyde (1980); Brown (1971, *AoMS*); McLeish (1974, *AoP*) |
| i.i.d. → Markov / geom. ergodic | `MARKOV` `ANY` `ANY` | Drift-minorization + regeneration / Poisson eq | Meyn & Tweedie (2009, Cambridge); Jones (2004, *Prob Surveys*) |
| Independent → Clustered/Panel | `PANEL` `ANY` `ANY` | Cluster CLT + within-group dependence | Liang & Zeger (1986, *Biometrika*); Hansen (2007, *Ectrica*); Cameron et al. (2011, *JBES*) |

**Tail / moment relaxation**

| From → To | Tags | Technique | Key references |
|-----------|------|-----------|----------------|
| Sub-Gaussian → Sub-exponential | `ANY` `ANY` `FS/HD` | ψ₁ control + Bernstein concentration | Boucheron et al. (2013, Oxford); Vershynin (2018, Cambridge) |
| Sub-Gaussian → Finite-variance heavy-tailed | `ANY` `PAR/SEMI` `FS/HD` | Truncation / Catoni / MOM | Catoni (2012, *AIHP*); Devroye et al. (2016, *AoS*); Lugosi & Mendelson (2019, *AoS*) |
| Clean → Huber contamination | `ANY` `PAR/SEMI` `FS` | Robust M-est / filtering / MOM | Huber (1964, *AoMS*); Lugosi & Mendelson (2021, *AoS*); Diakonikolas et al. (2019, *SIAM J. Comp*) |
| Bounded envelope → Unbounded + tail | `ANY` `NONPAR` `FS` | Truncation + empirical-process bounds | Adamczak (2008, *EJP*); Gine & Nickl (2016, Cambridge) |
| Sub-Gaussian design → Small-ball | `IID` `PAR/SEMI` `HD` | Small-ball + self-normalized control | Mendelson (2015, *JACM*); Belloni, Chernozhukov & Wang (2011, *Biometrika*) |

**Curvature / geometry relaxation**

| From → To | Tags | Technique | Key references |
|-----------|------|-----------|----------------|
| Strong convexity → Restricted SC / RE | `ANY` `PAR/SEMI` `HD` | Decomposability + localized curvature | Negahban et al. (2012, *Stat Sci*); Bickel, Ritov & Tsybakov (2009, *AoS*) |
| Global → Local curvature | `ANY` `PAR/SEMI` `CLA/FS` | Local expansion + basin-of-attraction | Balakrishnan et al. (2017, *AoS*); Mei, Bai & Montanari (2018, *AoS*) |
| Exact sparsity → Approx. ℓ_q sparsity | `ANY` `PAR/SEMI` `HD` | Oracle ineq + thresholding + bias control | Bickel, Ritov & Tsybakov (2009, *AoS*); Belloni, Chernozhukov & Hansen (2014, *RES*) |

**Domain / dimension relaxation**

| From → To | Tags | Technique | Key references |
|-----------|------|-----------|----------------|
| Compact Θ → Growing compact (r_n→∞) | `ANY` `PAR/SEMI` `CLA` | Compactness preserved at each n + sup control | Andrews (1994, *Handbook of Ectrx*); Newey & McFadden (1994, *Handbook*) |
| Compact Θ → Noncompact / sieve | `ANY` `NONPAR` `CLA/FS` | Coercivity + sieve / localization / peeling | Shen & Wong (1994, *AoS*); van de Geer (2000, Cambridge) |
| Fixed design → Random design | `IID` `PAR/SEMI` `HD/FS` | Design concentration + RIP / RE | Hsu, Kakade & Zhang (2012, *FoCM*); Oliveira (2016, *PTRF*) |
| Lipschitz → Holder / Sobolev | `ANY` `NONPAR` `ANY` | Modulus-of-continuity + entropy | van der Vaart & Wellner (1996); Gine & Nickl (2016, Cambridge) |
| Fixed d → d/n → γ | `IID` `PAR` `PROP` | Random matrix asymptotics / deterministic equivalents | Bai & Silverstein (2010); Johnstone (2001, *AoS*) |
| n≫d → d≫n high-dim | `IID` `PAR/SEMI` `HD` | Sparsity + regularization + restricted geometry | Buhlmann & van de Geer (2011); Wainwright (2019) |

**Model / specification relaxation**

| From → To | Tags | Technique | Key references |
|-----------|------|-----------|----------------|
| Parametric linear → Partially linear / semiparametric | `ANY` `PAR→SEMI` `CLA/FS` | Orthogonal scores + influence functions | Robinson (1988, *Ectrica*); Bickel et al. (1993, JHU); Chernozhukov et al. (2018, *Ectrx J*) |
| Correct spec → Misspecification | `ANY` `PAR/SEMI` `CLA` | Pseudo-true parameter + sandwich / quasi-MLE | White (1982, *Ectrica*); Kleijn & van der Vaart (2012, *EJS*) |
| Homoskedastic → Heteroskedastic / HAC | `IID/TS/PANEL` `PAR/SEMI` `CLA` | Sandwich + HAC / cluster-robust | White (1980, *Ectrica*); Newey & West (1987, *Ectrica*); Liang & Zeger (1986, *Biometrika*) |

---

### Pathway Selection Logic (based on Step 0.5 classification)

After user confirms framework on three axes, FILTER pathways:

1. **Drop irrelevant pathways**: If user said `IID`, drop pathways tagged `MIX`, `MARKOV`, `PANEL` etc.
2. **Keep `ANY`-tagged pathways**: They apply to all data/framework/regime combinations
3. **Highlight ESSENTIAL pathways**: Those tagged matching all 3 user axes are likely the most relevant
4. **Flag CONDITIONAL pathways**: Some pathways apply across multiple regimes — note which version of the technique applies in the user's regime

### Worked example: classification → pathway filter

```
User confirmed:
  Axis 1 (Data):       MIX (stationary mixing time series)
  Axis 2 (Framework):  SEMI (semiparametric)
  Axis 3 (Regime):     CLA (classical n→∞, d fixed)

Filtered pathways (only show these):

[ESSENTIAL — directly relevant]
- i.i.d. → α-mixing: this is the data axis, may already be in paper or could be tightened
- i.i.d. → β-mixing: alternative mixing condition
- Correct spec → Misspecification: standard in semiparam asymptotic theory
- Homoskedastic → HAC: classical TS reviewer-must-have
- Strong convexity → Local curvature: for the parametric-of-interest part of SEMI

[CONDITIONAL — relevant but technique-version matters]
- Sub-Gaussian → Sub-exponential: TS version requires stationary tail
- Parametric → Partially linear: only if paper is moving from PAR to SEMI

[IRRELEVANT — DROP]
- Markov pathways (data is mixing, not Markov)
- High-dim sparsity (regime is fixed-d)
- Small-ball design (i.i.d. only)
- Random matrix asymptotics (d fixed)
- Cluster errors (no panel structure)
```

---

