---
artifact: shared_reference
scope: citation_purpose_protocol
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills citation purpose protocol, Codex round 2 threadId 019e70c3-1844-7181-b6a1-0b4041c657df
---

# Citation Purpose Protocol

Companion to `literature-cache-protocol.md` (router) and `applicability-axes.md` (axis definitions). This file defines the seven citation purposes a statistics paper uses, the per-purpose axis-match requirements, and the verification gates.

## When to Read

- When citing any cached entry from a stat-theory-skills or stat-writing-skills workflow.
- During positioning audit (`stat-shared-references/stat-positioning-and-claims.md`).
- During Repair Closure Matrix / Weaken-Claim Change Log / Assumption-Extension Change Log construction.
- During Cited Results Audit in `proof-writer`.
- During mock review fatal-or-major concern attribution.

This file does NOT need to be loaded for cache miss / new entry creation (those flows live in `cache-verification-states.md`).

## The Seven Citation Purposes

The same paper can be cited at multiple sites in the same project, each with a different purpose. The citing skill declares the purpose at citation time; the cache enforces the purpose-specific gate.

| Purpose | What the citation does | Axis-match requirement | Verification floor |
|---|---|---|---|
| `load_bearing` | Cited result is used as a step in a proof; depended on for a rate; invoked to obtain a property the current proof relies on. | All axes `match` / `compatible`. `same_family` or `partial` allowed only with documented bridge in the citing artifact. Zero `mismatch`. | `independently_checked` at high-stakes sites; `human_signed` on the main dependency chain. |
| `benchmark_claim` | Cited result defines the bar being matched, exceeded, weakened, generalized, or separated from. Powers "first-to", "improves on", "matches asymptotically", "separates from" language in the contribution paragraph. | The specific axis on which the comparison is made is explicit; other axes match / compatible / same_family. | `independently_checked`. |
| `comparative` | Cited result is the contrast being claimed (e.g., "we extend X from sub-Gaussian to sub-exponential"). The axis difference IS the contribution. | Exactly one axis difference, explicitly documented as the comparison; other axes match / compatible / same_family. | `independently_checked`. |
| `technique_inheritance` | Methodological device is borrowed: leave-one-out argument, peeling, generic chaining, primal-dual witness, slicing, doubling, blocking, coupling. The cited paper's specific theorem may not be invoked; the proof device is. | Axis match NOT required (technique citations cross domains by nature). Cache must identify the inherited object explicitly. | `independently_checked` for the technique identification; `source_checked` is acceptable when the proof device is textbook. |
| `standard_tool` | Invoking a well-known tool by name: Talagrand inequality, Bernstein's inequality, Hanson-Wright, Davis-Kahan, Sudakov-Fernique, Slepian, Le Cam two-point, Fano, Assouad, Hoeffding, McDiarmid, Cauchy-Schwarz beyond schema-exempt, Doob, Burkholder-Davis-Gundy, etc. The cited paper is the canonical source of the tool, not a specific result reused. | Axis match NOT required (tools cross settings). Cache must record which form of the tool is invoked (constants, dimensions, dependence). | `source_checked`. The tool's name + canonical form must match the entry. |
| `lineage_positioning` | Cited paper anchors or names the theoretical line the current work continues, extends, refines, or departs from. The citation is the positioning claim ("we extend the line of X by ..."). | Same `theoretical_lineage.primary_line` OR cache entry's `role_in_literature` is `anchor` / `canonical_first` for the line. Axis match NOT required; lineage match is the weight. | `source_checked`. `independently_checked` when the lineage match itself is the contribution claim. |
| `background_motivation` | Cited paper motivates the problem (real data, scientific question, prior empirical finding). The citation does not bear on technical claims. | No axis check. | `source_checked`. |

## Decision Algorithm

At citation time, the citing skill executes:

```
purpose := citing_skill.declared_citation_purpose
contract_compare := per-axis verdict from applicability-axes.md
                    (match / compatible / same_family / partial / mismatch)
verification_state := cache_entry.verification_status

if purpose UNDECLARED:
    if site is high_stakes (positioning / repair / theorem step / claim audit):
        BLOCK — refuse the citation; require explicit purpose declaration
    elif site is pure prose (intro / discussion / related work prose-only):
        treat as background_motivation
        require verification_state >= source_checked

elif purpose == load_bearing:
    require zero `mismatch` on the 8 axes
    require every `same_family` or `partial` accompanied by a documented bridge in the citing artifact
    require verification_state >= independently_checked at high-stakes sites
    require verification_state >= human_signed if on main dependency chain to headline theorem

elif purpose == benchmark_claim:
    require the specific comparison axis is recorded
    require other axes match / compatible / same_family
    require verification_state >= independently_checked

elif purpose == comparative:
    require exactly one axis difference; that difference IS the comparison being claimed
    require difference is recorded in the citing artifact
    require other axes match / compatible / same_family
    require verification_state >= independently_checked

elif purpose == technique_inheritance:
    axis match NOT required
    require inherited proof-device label is recorded (one of: leave-one-out / peeling /
        generic chaining / primal-dual witness / blocking / coupling / slicing /
        doubling / smoothing / interpolation / quantile-coupling / Bernstein-block /
        chaining-induction / progressive-conditioning / ...)
    require verification_state >= source_checked
    require verification_state >= independently_checked if the technique is the contribution

elif purpose == standard_tool:
    axis match NOT required
    require the specific form of the tool is recorded (e.g., "Talagrand generic chaining
        for sub-Gaussian processes with $\gamma_2$ functional")
    require verification_state >= source_checked

elif purpose == lineage_positioning:
    require theoretical_lineage.primary_line of cache entry matches the citing work's
        declared primary_line, OR cache entry's role_in_literature is in
        {anchor, canonical_first} for that line
    axis mismatches: allowed (lineage match carries the weight)
    require verification_state >= source_checked
    require verification_state >= independently_checked if the lineage match itself
        is the contribution claim

elif purpose == background_motivation:
    no axis check
    require verification_state >= source_checked
```

The decision plus its rationale is recorded in the project's `cited_results.lock.md` under the `citation_purpose` and `axis_or_lineage_bridge` columns.

## Default Behavior on Undeclared Purpose

A citation without a declared purpose is treated as **BLOCKED for high-stakes sites** (positioning / repair / theorem invocation / claim audit / mock-review fatal-or-major). It is treated as `background_motivation` only at sites that are pure prose with no technical or comparative language attached.

This is intentional and replaces an earlier permissive default (`lineage_positioning`) which would have let undeclared comparative or load-bearing citations slip through.

The citing skill must declare the purpose. If the skill cannot infer the purpose from context, it asks the user explicitly:

```
[citation-purpose] Citation at REPAIR_PLAN.md#I-03 references
paper:bickel_levina_2008#thm_1.

Cannot infer purpose from context. Choose one:
  load_bearing         — using their Theorem 1 as a step in our proof
  benchmark_claim      — claiming our rate matches/exceeds their Theorem 1
  comparative          — extending their conditions; the axis difference is the contribution
  technique_inheritance— borrowing their chaining argument (or other named device)
  standard_tool        — invoking Bickel-Levina as a canonical tool (rare; they are typically lineage/anchor)
  lineage_positioning  — positioning our work within their methodological line
  background_motivation— motivating the problem; no technical claim

Pending declaration.
```

## Theoretical Lineage Metadata

Each cache entry carries a `theoretical_lineage` block on the per-paper container and may carry per-result overrides on individual result entries.

```yaml
theoretical_lineage:
  primary_line: high_dim_covariance_regularization     # methodological tradition identifier
  ancestors:
    - paper:johnstone_2001
    - paper:bickel_levina_2006_proceedings
  descendants:
    - paper:cai_zhang_2010
    - paper:fan_liao_2016
  role_in_literature: anchor                           # historical role; see role list below
  role_relative_to_current_paper: refinement_target    # relational; see role list below
  position_in_line: canonical_first_paper
```

The two role fields are separate dimensions:

- `role_in_literature` is **historical / static** — what the cited paper is in the field, independent of who is citing it now. Set once when the cache entry is verified.
- `role_relative_to_current_paper` is **relational / per-citation** — what the cited paper is to the citing project. Set per-citation in the project's `cited_results.lock.md`, not in the cache entry itself.

### `role_in_literature` enum (historical)

| Value | When to use |
|---|---|
| `anchor` | One of the canonical anchoring works in the line; foundational and widely-cited |
| `canonical_first` | The first (or commonly-credited first) paper to establish the line |
| `refinement` | A within-line improvement (better constants, weaker conditions, sharper rate) |
| `generalization` | Extends the line's setting (broader function class, removed structure) |
| `weakening` | Establishes a weakened-conditions variant of an existing result in the line |
| `strengthening` | Establishes a strengthened-claim variant of an existing result in the line |
| `comparative_baseline` | Paper that competing methods are commonly compared against |
| `textbook_reference` | Textbook chapter or canonical lecture-note style exposition |
| `technique_source` | Paper that introduced a proof technique used widely afterwards |
| `problem_origin` | Paper that formulated the problem the line studies |
| `negative_example` | Paper that established a counterexample, lower bound, or impossibility result that shapes the line |
| `standard_tool` | Paper that introduced a tool now used as a primitive across many lines |
| `empirical_or_model_motivation` | Paper providing the empirical / scientific / modeling motivation the line addresses |

### `role_relative_to_current_paper` enum (relational, per-citation)

| Value | When to use |
|---|---|
| `direct_anchor` | Current paper directly inherits or extends this paper's result |
| `comparative_target` | Current paper claims contrast against this paper's specific axis |
| `benchmark` | Current paper's rate or property is positioned against this paper's |
| `technique_donor` | Current paper borrows a proof device from this paper |
| `tool_source` | Current paper invokes a tool whose canonical citation is this paper |
| `lineage_predecessor` | This paper precedes the current paper in the same line; no direct technical inheritance |
| `lineage_descendant` | This paper postdates the current paper; cited for completeness; usually rare |
| `parallel_independent` | This paper is contemporary independent work on a related problem |
| `motivation_source` | This paper supplies the problem motivation; no technical claim shared |
| `not_applicable` | Citation purpose is `background_motivation` only |

These two role fields combined disambiguate citations that look the same at the abstract level but differ in technical role. The `cited_results.lock.md` records both at citation time.

## Verification Gate by Site × Purpose

The verification floor depends on both the citation site and the citation purpose. The full matrix:

| Decision site | load_bearing | benchmark_claim | comparative | technique_inheritance | standard_tool | lineage_positioning | background_motivation |
|---|---|---|---|---|---|---|---|
| Introduction or related work, prose | n/a | `independently_checked` | `independently_checked` | `source_checked` | `source_checked` | `source_checked` | `source_checked` |
| Citation in repair file (`Citation-Fix`, `Strengthen-Proof`, `Insert-Lemma`) | `independently_checked` | n/a | `independently_checked` | `source_checked`+ identified device | `source_checked`+ identified tool | n/a | n/a |
| Positioning claim against the cited paper | n/a | `independently_checked` | `independently_checked` | n/a | n/a | `independently_checked` | n/a |
| Weakened-Claim defense / Assumption-Extension defense | `independently_checked` | `independently_checked` | `independently_checked` | n/a | n/a | n/a | n/a |
| Repair priority L4 Add-Assumption (cited "natural weaker variant considered and rejected") | `independently_checked` | n/a | `independently_checked` | n/a | n/a | n/a | n/a |
| Mock-review fatal-or-major concern | `independently_checked` | `independently_checked` | `independently_checked` | n/a | n/a | n/a | n/a |
| Theorem in manuscript invoking the cited result as a step | `independently_checked` (`human_signed` on main chain) | n/a | `independently_checked` | `source_checked`+ device identified | `source_checked`+ tool identified | n/a | n/a |
| Author sign-off before submission | `human_signed` every load-bearing reference | `human_signed` every benchmark | `human_signed` every comparative | `independently_checked` every device | `independently_checked` every tool | `independently_checked` every lineage | `source_checked` every background |

If the required floor is not met, the skill emits the verification-request prompt defined in `cache-verification-states.md`. No silent upgrade.

## `cited_results.lock.md` Schema

The project-side pin manifest records, per citation site, what evidence the decision rests on. Schema:

```markdown
---
artifact: project_citation_lock
project: my-paper
generated: 2026-05-28
generator: stat-paper-write v1.x.x
---

| Citation site | Reference | Citation purpose | Role in literature | Role relative to current paper | Source version at decision | Entry hash at decision | Verification level at decision | Axis or lineage bridge recorded | Decision date |
|---|---|---|---|---|---|---|---|---|---|
| `REPAIR_PLAN.md#I-03` | `paper:bickel_levina_2008#thm_1` | `load_bearing` | `anchor` | `direct_anchor` | `arxiv:0803.4067v2` | `sha256:abc...` | `independently_checked` | `tail_condition: sub_gaussian -> sub_exponential bridge via Lemma A.4 (PATCHES.md Patch-7)` | 2026-05-15 |
| `CLAIM_SUPPORT_MAP.md#CS-04` | `paper:bickel_levina_2008#thm_1` | `lineage_positioning` | `anchor` | `lineage_predecessor` | `arxiv:0803.4067v2` | `sha256:abc...` | `source_checked` | `mismatch on sparsity_class (bandable vs Toeplitz) is intentional; primary_line: high_dim_covariance_regularization matches` | 2026-05-15 |
| `CLAIM_SUPPORT_MAP.md#CS-05` | `paper:talagrand_1996#chaining_main` | `technique_inheritance` | `technique_source` | `technique_donor` | `published:1996` | `sha256:def...` | `independently_checked` | `inherited device: generic chaining for sub-Gaussian processes; gamma_2 functional` | 2026-05-20 |
| `PRIOR_WORK_MATRIX.md#row-3` | `paper:tibshirani_1996#lasso_main` | `lineage_positioning` | `canonical_first` | `lineage_predecessor` | `published:1996` | `sha256:ghi...` | `source_checked` | `primary_line: lasso_l1_recovery; design assumptions differ` | 2026-05-21 |
| `STAT_PAPER_PLAN.md#contribution_para` | `paper:cai_zhang_2010#thm_2` | `benchmark_claim` | `refinement` | `benchmark` | `published:2010` | `sha256:jkl...` | `independently_checked` | `benchmark axis: rate constant; our rate matches their order with explicit constant` | 2026-05-21 |
| `STAT_PAPER_PLAN.md#intro_para_2` | `paper:efron_1979#bootstrap` | `background_motivation` | `problem_origin` | `motivation_source` | `published:1979` | `sha256:mno...` | `source_checked` | `n/a` | 2026-05-22 |
```

Each row is one citation site; the same `Reference` may appear in multiple rows with different `Citation purpose` and `Role relative to current paper`.

## Why the Purpose System Exists

The 8-axis applicability contract on its own would force the skill to either accept too many citations (defaulting permissively) or reject canonical-anchor citations (rejecting on axis mismatch). Neither is acceptable for Big Four statistics writing, where:

- Citing Bickel-Levina (2008) on a Toeplitz covariance project is **lineage positioning**, not load-bearing. The sparsity axis mismatch is intended.
- Citing Talagrand (1996) for the generic chaining technique in a different metric space is **technique inheritance**. The metric mismatch is irrelevant.
- Citing Tibshirani (1996) on a sparse problem with different design conditions is **lineage positioning**. The design mismatch is part of the positioning ("we extend the Lasso line to ...").
- Citing Bickel-Levina (2008) to invoke their Theorem 1 as an explicit step in obtaining a rate is **load-bearing**. Now the sparsity mismatch must be bridged or the citation refused.

The same paper supports different citation purposes at different bars. The cache enforces the gate per citation site, not per paper.

## Honest Limits of This Protocol

- **Lineage assignment is one reading.** `primary_line` reflects the verifier's classification at entry time. Lines branch, merge, and get retroactively reframed. The cache does not certify lineage; it records a working classification with the verifier's name in the `verification_log`.
- **Purpose is the author's declaration.** The cache cannot force a citation to be load-bearing or lineage on objective grounds; the author declares, and the cache enforces the gate appropriate to the declaration.
- **Edge cases exist.** A citation that mixes purposes (e.g., simultaneously a benchmark and a lineage anchor) requires duplicate rows in `cited_results.lock.md` — one per purpose. The protocol does not collapse mixed purposes into a single row.

## Cross-Reference

- `literature-cache-protocol.md` (router with Minimum Load Map)
- `applicability-axes.md` (the 8 axes, namespaced families, compatibility verdicts)
- `cache-verification-states.md` (the 4 verification states, source integrity, lock file mechanics, F1/F2/F3 workflows)
- `stat-positioning-and-claims.md` (positioning audit consumes this protocol)
- `proof-strategy.md` (Trap #6 citation identity drift, Trap #7 applicability drift — both inform the cache invariants)
- `CODEX_PROTOCOL.md` (the dialogue protocol used for `independently_checked` upgrades)
