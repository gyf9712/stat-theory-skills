# Worked Example: Simulation Figure Conventions and matplotlib Template

Extracted from `theory-simulation` Step 4. General figure conventions (captions,
legends, panels, colour-blind palettes, venue rules) are owned by
`stat-figure-design.md` in the writing repo; this file keeps the simulation-specific
detail and the runnable template.


### 4A: Figure conventions (split: actual journal rules vs stat house style)

#### Actual journal requirements (CHECK each venue's current guidelines)

| Requirement | Source | Applies to |
|------------|--------|------------|
| Alt text for figures (accessibility) | JRSS-B, Biometrika guidelines | JRSS-B, Biometrika submissions |
| Final-size legibility (camera-ready dimensions) | All top stat journals | All — verify at intended print size |
| Color must encode redundantly (also via line style / marker) for grayscale printing | JRSS-B, Biometrika | All |
| Vector format for line plots | Most | All |

**Always check the venue's current guidelines** before submission. The skill cannot
keep these up to date.

#### Stat-paper house style (strong convention, not always required)

These reflect AoS / JASA / Biometrika / JRSS-B house conventions:

1. **Plot titles are usually OMITTED** — content moves to LaTeX `\caption{}`
   - This is convention, not a hard rule. Compare Nature, where titles are common.
2. **Content-bearing captions**: DGP, n range, B, metric, theoretical prediction
3. **Axis labels**: short but precise ("Sample size n", "Empirical MSE")
4. **Legend placement** does not cover data — verify visually; use `bbox_to_anchor`
   when needed; ≥5 entries → 2-column legend
5. **Color-blind-safe palettes** (emerging expectation): Okabe-Ito for lines,
   viridis/cividis for heatmaps. Avoid jet/rainbow.
6. **Redundant encoding**: each method gets (color, marker, linestyle) — supports
   grayscale + color-blind readers
7. **Reference lines for theoretical predictions** (dashed black for rate, dashed
   grey for nominal coverage)
8. **MC uncertainty shown**: every data point should have an MCSE error bar or
   shaded band — referees expect to see uncertainty
9. **Multi-panel**: in-panel labels (a) (b) (c) (lowercase is common but check
   venue); no panel titles; share axes when comparing
10. **Embedded fonts** (`pdf.fonttype = 42`): best practice for editable PDF,
    not a journal requirement

The previous version of this skill called some of the above "rules" — they are
conventions and best practices, not legal requirements. Verify against each
venue's current guidelines.

### 4B: Figure menu — CONDITIONAL on the empirical claim

Pick figures matched to the claim being supported. Not every paper needs every
figure; some need figures not on this list.

| Claim being supported | Figure type | Notes |
|---------------------|-------------|-------|
| Rate of convergence | Log-log loss vs n, with theory reference slope and MC bands | Add normalized-loss leveling-off plot as a sanity check |
| Limiting distribution | QQ plot of studentized pivot vs N(0,1) | Plus density / ECDF comparison |
| Coverage of CIs | Empirical coverage vs n with Wilson CIs and nominal dashed line | Add interval-length plot |
| Test size and power | Size vs n; power curve vs local alternative | Reference at nominal α |
| Estimator distribution | Boxplots / violins of `θ̂ − θ*` vs n | Reference line at 0 |
| EmpSE vs ModSE calibration | Scatter or ratio plot, target ratio = 1 | One point per cell |
| Method comparison (paired) | Paired-difference plot with MC CIs, or lollipop with bars | More informative than overlaid lines for >3 methods |
| Two-parameter sweeps | Heatmap on viridis/cividis (NEVER jet/rainbow) | Colorbar with units |
| Failure rates per cell | Bar/heatmap of nonconvergence rates | Required if any cell has >5% failures |

Figures must show MC uncertainty (error bars, shaded bands, or visible MCSE).
A point estimate plot without uncertainty is not publishable.

### 4C: Concrete matplotlib template (Python)

```python
import matplotlib.pyplot as plt
import matplotlib as mpl

# Stat-journal style setup
mpl.rcParams.update({
    'pdf.fonttype': 42,            # editable text in PDF
    'ps.fonttype': 42,
    'font.family': 'serif',        # matches LaTeX document
    'font.size': 10,
    'axes.labelsize': 11,
    'axes.titlesize': 0,           # we don't use titles — force 0
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'lines.linewidth': 1.5,
    'lines.markersize': 5,
    'axes.spines.top': False,      # remove top/right spines (Tufte-ish)
    'axes.spines.right': False,
})

# Okabe-Ito palette (color-blind safe)
OKABE_ITO = ['#E69F00','#56B4E9','#009E73','#F0E442',
             '#0072B2','#D55E00','#CC79A7','#000000']

fig, ax = plt.subplots(figsize=(3.5, 2.8))  # single-column-friendly

# Plot data
for i, method in enumerate(methods):
    ax.plot(log_n, log_mse[method],
            color=OKABE_ITO[i], marker='os^DvX'[i], linestyle='-',
            label=method)

# Theoretical slope reference
ax.plot(log_n, theoretical_intercept - 1.0*log_n,
        color='black', linestyle='--', linewidth=1, label='theory: slope $-1$')

# Axis labels — short + precise, NO title
ax.set_xlabel(r'$\log n$')
ax.set_ylabel(r'$\log$ empirical MSE')

# Legend placement
leg = ax.legend(loc='best', frameon=False)
# Verify no overlap; if needed: ax.legend(bbox_to_anchor=(1.02, 1), loc='upper left')

fig.tight_layout()
fig.savefig('figures/E1_rate.pdf')
plt.close(fig)
```

### 4D: Caption template (for the LaTeX paper)

```latex
\begin{figure}[t]
  \centering
  \includegraphics{figures/E1_rate.pdf}
  \caption{Empirical MSE versus sample size for the proposed estimator and two
  baselines (oracle and MLE). DGP: $X_i \stackrel{iid}{\sim} N(\theta^*, 1)$ with
  $\theta^* = 0.5$; $d=5$ fixed; $B=500$ Monte Carlo replications per cell.
  The dashed line shows the theoretical rate $n^{-1}$ (slope $-1$) predicted by
  Theorem~1. The fitted slope for the proposed estimator is $-1.02$
  (95\% CI: $[-1.08, -0.97]$), confirming the theoretical rate.}
  \label{fig:E1-rate}
\end{figure}
```

### 4E: Pre-export checklist (run before saving every figure)

- [ ] No `title()` call anywhere
- [ ] Legend does not cover data points (visual check)
- [ ] All axis labels are present and readable
- [ ] Color scheme is color-blind safe (Okabe-Ito or viridis)
- [ ] At least one reference line (theoretical prediction) when applicable
- [ ] Font sizes consistent across all figures in the paper
- [ ] Saved as PDF/EPS with embedded fonts
- [ ] `tight_layout()` applied — no clipping at edges
- [ ] Caption written and stored alongside the figure file
- [ ] Figure has a unique label for cross-referencing

---
