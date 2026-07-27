---
artifact: shared_reference
scope: theory_literature_search
generator: extracted from theory-sharpen Step 0.5B per Codex threadId 019fa42e-217f-7171-b94f-99b95177aab8
---

# Theory Literature Search — Query Templates and Gating

Query templates by framework axis, recency and venue gating rules, and worked examples of
why pathway relevance depends on the paper's own classification. Consumed by
`theory-sharpen` Steps 0.5B and 5A.


**Template 1: T1 journal search (Semantic Scholar API)**
```
GET https://api.semanticscholar.org/graph/v1/paper/search
  ?query={topic} {technique} {framework_keyword}
  &limit=20
  &year={current_year - 5}-{current_year}
  &fields=title,authors,year,abstract,venue,citationCount,externalIds,publicationTypes
  &venue=Annals of Statistics,JASA,Biometrika,JRSS B,Econometrica,Journal of Econometrics,JMLR,Bernoulli,EJS

Filters applied client-side:
  - Sort by: publicationDate desc (recent first)
  - Drop: citationCount = 0 AND year < current_year-1 (filters dead papers)
  - Keep top 5-10 most-cited from last 3 years
```

**Template 2: T1 conference search (WebSearch)**
```
WebSearch query: "{topic} {technique}" site:proceedings.neurips.cc OR
                  site:proceedings.mlr.press OR
                  site:openreview.net (after:2022)
                  
Also try: "{topic}" "{technique}" arxiv.org/abs (cs.LG OR stat.ML OR stat.TH)
         site:arxiv.org (after:2023)
         
For each hit, check if has published venue annotation (e.g., "Accepted at NeurIPS 2024")
```

**Template 3: Highly-cited consensus search**
```
GET https://api.semanticscholar.org/graph/v1/paper/search/bulk
  ?query={topic} {framework_keyword}
  &sort=citationCount:desc
  &limit=20
  &year={current_year - 5}-{current_year}

Purpose: identify what the field considers "canonical" recent work
```

**Topic signature builder** (call before searches):
```
Given paper P, extract:
1. PRIMARY_TOPIC = main subject (1-3 word phrase from title or first paragraph of intro)
   Examples: "treatment effect", "Markov chain Monte Carlo", "high-dim regression"
   
2. MAIN_TECHNIQUE = methodology label (1-3 word phrase)
   Examples: "doubly robust", "Poisson equation", "lasso", "M-estimation",
             "semiparametric efficient score"
   
3. DATA_KEYWORD = from Axis 1 inference
   Examples: "time series", "panel data", "stationary", "Markov chain"

4. FRAMEWORK_KEYWORD = from Axis 2 inference
   Examples: "semiparametric", "nonparametric", "parametric efficient"

5. REGIME_KEYWORD = from Axis 3 inference
   Examples: "high-dimensional", "asymptotic", "non-asymptotic", "finite-sample"

Query format: {PRIMARY_TOPIC} + {MAIN_TECHNIQUE} + {FRAMEWORK_KEYWORD} + ({REGIME_KEYWORD} OR {DATA_KEYWORD})
```

### Recency & venue gating rules

Strict rules for the Literature Anchor Table:

1. **Recency**: prefer last 3 years, hard cap at last 5 years for "recent T1" set
2. **Venue gate**: T1 only — drop T2/T3 from the anchor set
3. **Citation gate**: 
   - Papers from last 2 years: any citation count OK (too new to be cited)
   - Papers 2-5 years old: require ≥10 citations OR T1 venue with high visibility
4. **De-duplication**: if same paper appears as preprint + published, use published version
5. **Diversity gate**: ensure mix of methodology variations, not 10 papers using identical technique
6. **Minimum set size**: at least 3 T1 papers; if fewer found, broaden search and flag low confidence
7. **Maximum set size**: cap at 10 most-relevant; more is noise

### Why this matters: pathway relevance examples

| Wrong filter | Right filter | Consequence of skipping |
|--------------|-------------|------------------------|
| Suggesting "i.i.d. → mixing" for cross-sectional data | Skip dependence relaxation | Wasted time, irrelevant suggestion |
| Suggesting "fixed-d → d/n→γ" for nonparametric problem | Skip — different dimension concept | Conceptual mismatch |
| Suggesting "small-ball design" for time series | Need stationary version | Wrong technique class |
| Suggesting parametric efficiency for nonparametric problem | Use minimax / contraction rate | Different optimality concept |

After user confirms classification, FILTER the pathway library (Step 1C below) using
the [Framework Tags] on each pathway. Only show pathways that match the user's
confirmed classification.

---

