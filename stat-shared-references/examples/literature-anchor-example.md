# Worked Example: Literature Anchor Artifacts (theory-design Step 0.5C-0.5F)

Filled specimens for the per-paper extraction, the theoretical-inertia summary, the
positioning options, and the constraints derived from the anchor. The contracts are in
the skill; these are illustrations.


For each paper, extract structured information:

```markdown
## [Paper N] Author (Year, Venue, citations)

### Problem framing
- How is the problem stated?
- What gap does it address?
- One-sentence contribution

### Theoretical anchor
- Data structure used
- Modeling framework
- Asymptotic regime
- Target estimand/object

### Assumption profile
- Key assumptions (≤5)
- Anything unusual or contested

### Result type
- Rate / asymptotic distribution / coverage / lower bound / structural recovery?

### Proof technique
- Main tool used

### Position in literature
- Direct predecessor it extends
- Alternative approach it competes with
```

Compile into `papers/<paper-name>/design/LITERATURE_ANCHOR.md`.

### 0.5D: Identify the "theoretical inertia"

From the extracted papers, identify the **current consensus framework**:

```markdown
## Theoretical Inertia of the Field

### Default data structure: [most common across recent T1 papers]
Example: "Most recent CATE papers use i.i.d. observations even when
applications are clustered."

### Default modeling framework: [most common]
Example: "Semiparametric framework with infinite-dim nuisance is dominant
for treatment effect since Robins-Rotnitzky-Zhao (1994); pure parametric
is now rare."

### Default asymptotic regime: [most common]
Example: "Non-asymptotic high-d bounds with sparsity have become standard
in the last 5 years; classical asymptotic n→∞ with d fixed is now seen
as a special case to confirm."

### Default proof technique: [most common]
Example: "Cross-fitting + orthogonal scores is now the dominant proof
technique in this subfield (Chernozhukov et al. 2018)."

### Default contribution shape
Example: "Recent papers tend to: (a) propose a new method, (b) prove
n^{-1/2} rate under semiparametric assumptions, (c) demonstrate finite-sample
performance via simulation."
```

This is the **inertia** — the path of least resistance for the field. You can
either follow it (lower friction in review) or deviate from it (higher reward
but must justify the deviation).

### 0.5E: Identify positioning options

For your contribution, where does it sit relative to the inertia?

```markdown
## Positioning Options

### Option 1: INCREMENTAL — refine within the inertia
- Adopts default data structure, framework, regime
- Provides a sharper rate, weaker assumption, OR new estimator in the standard frame
- Easier to review and publish (referees see a familiar landscape)
- Lower-novelty perception unless the refinement is technically substantial

### Option 2: LATERAL — same problem, different angle
- Same problem, but pick an alternative framework or regime
- Example: most CATE papers use cross-fitting; you might use posterior contraction
- Must justify why your angle reveals something the standard angle misses
- Higher review difficulty (referee needs to be familiar with your alternative)

### Option 3: DISRUPTIVE — challenges the inertia
- Argues the standard framework is wrong / suboptimal / mis-applied here
- Requires either (a) a counterexample showing standard framework fails, or
  (b) a new framework that supersedes the standard
- Highest reward, highest risk; usually requires a paper-length argument for the
  reframing itself
```

For each option, also identify:
- Which T1 venues are most receptive
- Which 3-5 reference papers should be cited for positioning

### 0.5F: Anchor → design constraints

The literature anchor feeds into every subsequent phase as constraints:

```markdown
## Constraints derived from anchor

For Step 1 (problem framing):
- The motivation must distinguish from [list 3 most similar papers]
- The gap must be precisely articulated; vague gaps will be attacked

For Step 2-3 (model/framework choice):
- If you adopt the inertia: cite [canonical papers]
- If you deviate: justify deviation with [specific reasoning]

For Step 5-6 (target results / proof):
- Your rate must beat / match / explicitly differ from [best known: list]
- Your proof technique should either use [dominant tool] or justify why not

For Step 7 (downstream connections):
- Specify which existing papers your work supersedes or complements
```

### 0.5G: Mandatory user confirmation

Present the LITERATURE_ANCHOR.md to the user. Force confirmation:

```
"Here is the literature anchor for your topic.

  - X recent T1 papers identified
  - Theoretical inertia: [summary]
  - Recommended positioning: [option]

Do you confirm this anchor before proceeding to framework design?"
```

User can: confirm / correct misreadings / add papers / change positioning.

Without explicit confirmation, the skill REFUSES to proceed to Step T1/M1/A1.

---

