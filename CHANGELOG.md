# Changelog

## v1.9.0 — Equivalence ledger for the formal-statement-pass (cross-repo with stat-writing-skills)

The user proposed a dedicated capability to rewrite the mathematical FORM of body statements (assumptions, definitions, theorem/lemma statements, displayed conditions) into more formal, more conventional, equivalence-preserving forms aligned with the target venue's published register. They named the central tension themselves: more formal notation raises the reading barrier but also makes a paper *appear* deeper, and apparent depth is appearance, not substance.

Codex MCP review (threadId `019e7bc0-56ef-7710-8424-e61b6d58399b`, two rounds at xhigh) settled the design.

Round 1 gate verdict (Q1): **do not build a standalone skill.** A standalone skill creates a second owner for theorem/assumption prose, exactly where ownership must be tight (the same lesson as the `cited_results.lock.md` ownership work in v1.8.0). Build it as a `--formal-statement-pass` MODE inside `stat-polishing` (which already owns theorem statements).

Round 1 critical verdict (Q2): **equivalence preservation is a correctness-critical operation.** "Rewrite into an equivalent more formal form" is exactly the operation that silently changes meaning ("well-conditioned design" → uniform eigenvalue lower bound; "sub-Gaussian errors" → a pinned constant). It is the same failure class as proof-repair's semantic edits and gets the same grade of guardrail.

This repo hosts the protocol because it owns the silent-semantic-change ontology (axis vocabulary, change logs, diff ledger). `stat-writing-skills` references it cross-repo.

### NEW: stat-shared-references/equivalence-ledger-protocol.md

Governs the `--formal-statement-pass` mode. Contents:

- **Standing refusal condition**: never formalize to increase apparent depth; apparent depth is only ever a side effect of a genuine precision-or-register gain. Math-form analog of "mathematical precision over adjectival praise" → "precision over notational sophistication."
- **Two kinds of formalism**: precision-increasing (apply) vs decoration / theoretical theater (refuse or flag).
- **Discriminator** (Codex Q3, sharpened because the loose version is LLM-gameable): the formalized version must answer at least one referee-checkable question the original could not — with respect to what limit? uniform over which class? in which norm? what probability mode? what conditioning? If no new ambiguity is resolved and no clutter is removed, it is decoration. These ambiguity axes are the same load-bearing dimensions as `applicability-axes.md` and the `--post-repair` diff ledger.
- **Statement-formalism vs notation-formalism** (Codex Q4): both layers have legitimate and dangerous modes; notation formalism is legitimate only when the object already lives in that structure and is used downstream (use-test); statement formalism overclaims when it adds a quantifier / regime / bound not in the original (equivalence ledger).
- **Anti-theater checks** (Codex Q6, operational not slogan): the **use-test** (every introduced symbol/space/operator/topology/process must be used downstream; grep-able) and the **simpler-equivalent challenge** (if a simpler conventional statement is equally falsifiable, choose it).
- **Two-tier gate** (Codex L1): cosmetic / packaging rewrites go through stat-polishing's existing `REVISION_PLAN.md` cluster gate; semantic rewrites (touching quantifier / probability mode / uniformity / constants / regime / conditioning / norm-topology / dependence / parameter space) get a **per-atomic-claim gate** — one atomic claim, one approval, never clustered (a six-part assumption produces up to six approval items, because a single silently-strengthened assumption can sink the paper).
- **Equivalence ledger** (`papers/<project>/EQUIVALENCE_LEDGER.md`): 8 columns reusing the system's axis vocabulary — original text, proposed text, touched axis, equivalence justification, possible silent strengthening/weakening, downstream consumers, approval status, proofcheck status.
- **Proofcheck depth split** (Codex L2): semantic rewrite off the main chain → targeted dependency check; semantic rewrite on the path to a headline theorem / rate theorem / main-chain lemma → full `/proofcheck --post-repair` on the affected sub-DAG; unclear dependency → treat as load-bearing. Full proofcheck for ALL semantic rewrites was rejected as overkill that would incentivize under-reporting.
- **Venue-calibrated formalism level** (Codex Q5, no thresholds): two exemplar questions ("would this object look normal in two recent venue papers?", "does the formalism reduce or increase the modal reader's burden?") plus a per-venue register table (AoS/Bernoulli/EJS high; Biometrika/JASA compact; application venues readable).
- **Cross-reference drift audit** (Codex Q7, the first-30-day bite): rewriting a labeled object silently breaks later references ("the boundedness condition", "Assumption 3(ii)"); audit and update via `stat-notation-audit.md`.
- **Economy self-check**: the mode runs stat-polishing's Step 6 Math Expression Economy flags on its own output; formalizations that trip a flag without a precision gain are withdrawn.

### proofcheck wiring

- `--post-repair` "When to invoke" gains the formal-statement-pass entry: an `EQUIVALENCE_LEDGER.md` row with proofcheck status "required (on main chain)" triggers the re-audit, scoped by the row's touched-axis and downstream-consumers columns.
- `--post-repair` inputs list gains item 7: `EQUIVALENCE_LEDGER.md`. Rows with a non-empty touched axis are treated as semantic edits; a formalization that silently strengthened an assumption is a `NEW-S0`, exactly as an undocumented Weaken-Claim or Add-Assumption edit is.
- `proof-closure-machinery.md` cross-references the equivalence ledger as the sibling change log for formalization.

### Codex dialogue (round 2 lock)

- **L1** confirmed with a sharpening: use a per-**atomic-claim** gate, not merely per-statement; a six-part assumption has up to six independent semantic risks.
- **L2** confirmed: targeted dependency check default, full `/proofcheck --post-repair` only for main-chain rewrites; unclear status treated as load-bearing.
- **L3** confirmed: reuse the system's axis vocabulary for the equivalence-ledger columns, distinct artifact instance — one ontology of silent semantic change across cache, proof-repair, and formal-pass.
- Final: safe to build as a narrow `stat-polishing` mode; the remaining structural risk is scope creep into "make it look theoretical", which is the explicit standing refusal condition.

Companion: `gyf9712/stat-writing-skills` adds the `--formal-statement-pass` mode section to `stat-polishing/SKILL.md`, the formalization patterns + venue register + cross-ref drift to `stat-theory-writing.md`, and a roadmap entry.

## v1.8.0 — Literature cache protocol + SKILL.md compactification + schema drift cleanup

Four-commit iteration produced the durable literature cache, compactified the proof skills, and cleaned schema drift introduced by the extraction. Codex MCP review at xhigh across three rounds (round 1 threadId expired; rounds 2-3 captured in the rounds below).

### Round 2 deliverables (commits 612f170 + 668cc64 + 3bd1e65)

**Protocol split + lineage refinements (commit 612f170)**

The previously-monolithic `literature-cache-protocol.md` (623 lines) was split into a 206-line router plus three companions, each loaded only by use cases that need it (see Minimum Load Map in the router). Total content increased from 623 to 1025 lines; per-invocation context load decreased because skills now load 500-800 lines (router + 1-2 companions) rather than the full body.

- `literature-cache-protocol.md` (206 lines, router): Minimum Load Map, locations, reference syntax, per-result entry header, high-level read/write summaries, skill integration points.
- `citation-purpose-protocol.md` (253 lines): 7 citation purposes (load_bearing / benchmark_claim / comparative / technique_inheritance / standard_tool / lineage_positioning / background_motivation); methodological role split into `role_in_literature` (13 historical values: anchor / canonical_first / refinement / generalization / weakening / strengthening / comparative_baseline / textbook_reference / technique_source / problem_origin / negative_example / standard_tool / empirical_or_model_motivation) and `role_relative_to_current_paper` (10 relational values); verification gate matrix is now 2D (decision site × citation purpose); default purpose changed from `lineage_positioning` to BLOCKED at high-stakes sites or `background_motivation` only at pure-prose sites; `cited_results.lock.md` schema gains 7 new columns.
- `applicability-axes.md` (305 lines): 8 axes with value vocabularies; namespaced assumption families per domain (15 domains: highdim, empirical_process, concentration, random_matrix, m_estimation, semiparametric, bayesian_asymptotics, nonparametric, causal_inference, survival, time_series, multiple_testing, online_learning, robust_statistics, minimax_lower_bounds); 5 compatibility verdicts (match / compatible / same_family / partial / mismatch); per-axis compatibility check algorithm.
- `cache-verification-states.md` (261 lines): 4 verification states (unverified_extract / source_checked / independently_checked / human_signed); transition rules; verification floor table per decision site; verification request template (no silent upgrade); source integrity (URL + version + retrieval date + SHA-256 source_hash + per-quote text_hash + locator); F1 (staleness) / F2 (verification gap) / F3 (hallucination detection) workflows; inbox/queue write protocol; project-side pin manifest; reverse index generation; sharding policy; protocol versioning.

**SKILL.md compactification (commit 668cc64 stat-theory + 28a3004 stat-writing)**

Per Codex's Q3 verdicts on prompt length (sweet zone 500-700 lines; attention tax at 900-1200; long prompts cause priority distortion, not forgetting): extract repeated orchestration and schemas to shared refs; SKILL.md = WHAT/WHEN/orchestration; shared refs = HOW/detail.

- `skills/proof-repair/SKILL.md`: 1374 → 1121 (-253, -18%). Repair Priority Ladder, mandatory output blocks (Weaken-Claim Change Log, Assumption-Extension Change Log, Repair Ladder Defense), Step 5C per-repair Codex stress-test full template, Step 7A REPAIR_PLAN.md schemas all extracted.
- `skills/proofcheck/SKILL.md`: 1049 → 1030 (-19, -2%). Severity system, verification statuses, provability triage extracted. Most of the rest is genuinely skill-specific 6-pass workflow.
- `stat-writing-skills/stat-polishing/SKILL.md`: 855 → 783 (-72, -8%). Duplicated style-discipline content collapsed to pointers.
- **NEW** `stat-shared-references/proof-closure-machinery.md` (279 lines): canonical schemas for severity S0-S3, verification statuses, provability triage, 11 repair classes, Repair Priority Ladder (Phase A/B/C, L1-L6), Repair Closure Matrix schema, Weaken-Claim Change Log schema (5 columns including Patch ID), Assumption-Extension Change Log schema (7 columns including Natural weaker variant), Repair Ladder Defense block, Repair Ladder Summary table, Hard-Gate Completion Rule (9 conditions including HARD GATE post-repair re-audit for S0/S1).
- `CODEX_PROTOCOL.md` extended (+100 lines): Per-Repair Stress-Test Call Template + `codex_stress_test.md` artifact schema with threadId column + iterative FIXABLE/FAIL push-back protocol.

**Cache integration (commit 3bd1e65 stat-theory + ea3594d stat-writing)**

Each literature-touching skill gained minimal cache-consult orchestration (10-25 lines per skill).

- `proof-repair` Step 4: new 4A cache-consult, 4F.cache write-back. Subsections renumbered 4A→4B → 4G.
- `theory-design` Step 0.5: new 0.5.cache before parallel-agent literature search.
- `theory-sharpen` Step 5: new 5.cache before benchmark agents.
- `proof-writer` Cited Results Audit: `paper:<bibkey>#<result_id>` references; verification floor integration.
- `stat-positioning-and-claims` Step 3: cache-consult before 5-source search; write-back; lock manifest update.
- `stat-paper-plan` PRIOR_WORK_MATRIX Step 5.5: `Read In Full` and `Citation Verified` bind to cache references.
- `stat-mock-review` Step 3: fatal/major concerns map to project lock + cache; floor `independently_checked`.

### Round 3 cleanup (this commit)

Codex round 3 (threadId `019e7112-283e-74b1-97e5-6344592cd820`) audited the three landed commits and flagged 4 REQUIRES FIX + 3 SUGGEST IMPROVEMENT + 2 CORRECTLY IMPLEMENTED. The hard pushback:

> "The current system now depends on two missing enforcement points: `/lit-cache verify` and a formal citation-lock owner. Without those, the protocol can look stricter while operationally producing pending artifacts that no skill can promote or consistently audit."

> "The main correctness risk is not token economy anymore. It is 'schema drift after extraction': small inline summaries in old skills are now contradicting the shared sources."

This commit (Commit 4) addresses the schema drift and the SUGGEST IMPROVEMENT items. Codex's two enforcement gaps (`/lit-cache verify` MVP + `cited_results.lock.md` ownership) land in a follow-up (Commit 5).

- **V4 schema drift**: `proof-repair` Step 1 line 156 + Step 3 mandatory output: changed "4 columns" → "5 columns (Patch ID + 4 originals)" with explicit reference to the schema in `proof-closure-machinery.md`. `proofcheck` `--post-repair` Step P5 routing fixed: L4 (Add-Assumption) without an `Assumption-Extension Change Log` row was previously routed to "Weaken-Claim change-log row missing"; now correctly routes to its own change log. `proofcheck --post-repair` input list now references both Change Logs separately.
- **V2 trigger keywords**: `citation-purpose-protocol.md` gained a trigger-keyword table. Presence of any keyword family (extension / improvement / priority / weakening / lineage / technique-borrow / standard-tool / contrast / match) in a sentence forces explicit purpose declaration; the site cannot default to `background_motivation`. Two coexisting keyword families generate separate citation sites with separate purposes.
- **V3 benchmark axes**: `benchmark_claim` purpose split into `primary_comparison_axis` + `auxiliary_comparison_axes`. All auxiliaries are explicitly checked; any mismatch downgrades the benchmark to a partial comparative claim with corresponding prose adjustment.
- **V9 family tightening**: `applicability-axes.md` `highdim.tail_condition:moment_based` split into `exponential_concentration` (sub_gaussian + sub_exponential) and `moment_bounded` (polynomial_p_moment + bounded_variance). Cross-family substitution is `partial` with documented bridge, not `same_family`. Empirical-process and random-matrix tail families similarly split into low / high moment variants.

Codex round 3 verdicts CORRECTLY IMPLEMENTED carried forward unchanged: V1 (per-repair fresh thread inline summary sufficient), V5 (cache additions within tolerance).

Codex round 3 SUGGEST IMPROVEMENT V5 carried forward as deferred guidance: do not add further cross-cutting protocols before extracting more Step 1 / Step 4 / post-repair machinery.

### v1.8.0 continuation: enforcement infrastructure (Codex round 3 V7 + V8)

This commit (Commit 5) adds the two missing enforcement points Codex round 3 hard-pushed: `/lit-cache verify` workflow and `cited_results.lock.md` ownership.

**V7 `/lit-cache verify` MVP** (`stat-shared-references/lit-cache-verify-protocol.md`, NEW 156 lines)

The protocol previously referenced `/lit-cache verify` and `/lit-cache audit` without an implementation, so entries stayed at `unverified_extract` and the strict verification gates blocked all downstream use. The MVP is a workflow specification (not a separate skill binary) that the user runs through the assistant.

Scope of the MVP: only the `unverified_extract → source_checked` transition. The `source_checked → independently_checked` upgrade (which requires a Codex MCP call) and the human-signed transition are deferred to follow-up.

Workflow (7 steps):

1. List inbox entries at `~/.claude/literature_cache/inbox/`.
2. For each, fetch the source URL via WebFetch.
3. Compute the fetched source's SHA-256 and compare to `source_hash`.
4. For each quote block, locate the text at the recorded locator, normalize Unicode NFC + strip whitespace, compute SHA-256, compare to `text_hash`.
5. Verify the applicability contract (axis presence + family registry membership + lineage primary_line existence or rationale).
6. Promote (move to `papers/<bibkey>.md`, set state to `source_checked`, append verification_log entry, update INDEX.md) OR hold (leave in inbox with documented failure reason).
7. Print summary listing promoted / held entries.

The MVP catches the most common hallucination class (the writing skill claimed verbatim it did not actually read); deeper independent-reading checks are deferred to `/lit-cache audit`. Honest limits are documented: cannot detect self-consistent hallucinations where the writing skill invented a paper, invented quotes, and invented hashes of its invention; PDF quote-locator extraction is fragile for non-standard layouts.

Invocation forms: `/lit-cache verify` (all entries), `/lit-cache verify <bibkey>` (single), `--dry-run`, `--since <date>`.

**V8 `cited_results.lock.md` ownership** (`stat-shared-references/cited-results-lock-protocol.md`, NEW 132 lines)

Formalizes who creates and who updates the project-side citation pin manifest. The lock manifest was referenced by every literature-touching skill but had no designated owner; this protocol fixes that without adding a new skill binary.

Ownership map:

| Stage | Owner | Responsibility |
|---|---|---|
| Initialization | `stat-paper-plan` Step 5.7 (NEW) | Create file with manifest header + initial rows from `PRIOR_WORK_MATRIX.md` |
| Drafting | `stat-paper-write` Step 2.5 | For each `CLAIM_SUPPORT_MAP` claim resolving to a cited paper, add a row |
| Polishing | `stat-polishing` Steps 11 + 16 | Codex dialogue and citation hygiene additions update rows |
| Mock review | `stat-mock-review` Step 3 | Read-only verification |
| Proof repair | `proof-repair` Steps 4 + 5C | New repair citations update rows |
| Proof writing | `proof-writer` Cited Results Audit | Match audit rows to lock-manifest rows |
| Re-audit | `/proofcheck --post-repair` Step P3.7 (NEW) | Read-only consistency validation |
| Final | author (manual) | Promote load-bearing rows to `human_signed`, sign the file |

Update discipline: read-before-write, append-only (no editing of historical rows), match cache state at write time, record bridge explicitly, one row per citation site.

Conflict resolution: first-writer-wins for citation sites; subsequent writers add new rows for upgrades; same paper at different purposes coexists as multiple rows.

**stat-paper-plan Step 5.7 (NEW)** initializes the lock manifest after Steps 5.5 + 5.6 (`PRIOR_WORK_MATRIX` + `TECHNICAL_RISK_REGISTER`). Initial rows are populated from `PRIOR_WORK_MATRIX.md` `Read In Full` entries that resolve to cache hits; rows without cache entries are deferred to the downstream skill that first triggers the literature search.

**proofcheck `--post-repair` Step P3.7 (NEW)** performs read-only consistency validation:

- Every row's Reference resolves to an existing cache entry.
- Every Entry hash at decision matches current cache hash (or row flagged STALE).
- Every load-bearing row at `independently_checked` or higher (or flagged GAP).
- Every `partial` / `same_family` row's bridge artifact exists.
- Every `\cite{<bibkey>}` in the patched paper has at least one lock-manifest row.

Findings to `audit/08_post_repair/lock_manifest_validation.md`. STALE and GAP are warnings; verification floor gap on load-bearing rows blocks `CONVERGED`.

**Router Minimum Load Map updated** to include the two new protocols. New use cases:

- Cache verify → loads `lit-cache-verify-protocol.md`
- Lock manifest initialization → loads `cited-results-lock-protocol.md`
- Lock manifest consistency check (Step P3.7) → loads `cited-results-lock-protocol.md`

**Skill-level updates** for the lock manifest discipline:

- `proof-repair` Step 4F.cache: explicit "read before write + append, do not edit" rule for lock manifest updates.
- `proof-writer` Cited Results Audit: every audit row matches a lock-manifest row at the matching verification level.
- `stat-positioning-and-claims` Step 3: positioning audit citations follow append-only discipline.
- `stat-mock-review` Step 3: read-only; missing lock entries flagged as Rescue Plan items.

Convergence criterion in `proofcheck --post-repair` updated to require lock manifest validation pass (no STALE or GAP on load-bearing rows).

Why no separate `/lock-citations` skill: per Codex round 3 V5, do not add further cross-cutting protocols before extracting more machinery from proof-repair. The in-skill update discipline is sufficient. If responsibility grows (automated reverse indexes, batch validation), a separate skill becomes worth creating.

This commit completes the v1.8.0 release. The four-commit sequence (612f170 protocol split + 668cc64 compactification + 3bd1e65 cache integration + f0e2fbd cleanup + this commit) implements Codex rounds 2 and 3 in full, with the round 3 hard pushback on enforcement now addressed.

## v1.7.0 — Token economy and anti-anchoring (reasoning ladder + artifact manifest + per-repair fresh thread)

User surveyed [rtk-ai/rtk](https://github.com/rtk-ai/rtk) (a Rust CLI proxy that compresses Bash output by 60-90% with deterministic rules) and asked which strategies could save tokens in this pipeline without harming the math. A second Codex MCP review (threadId `019e6ed3-0b5d-7e72-b424-5428423a2276`, `model_reasoning_effort: xhigh`) evaluated seven candidate optimizations, of which three were ADOPTED outright, three ADOPTED with scope refinements, and one (OPT7 "shared thread for 8 sequential stress-tests") was MODIFIED into a fresh-thread-per-repair anti-anchoring protocol after Codex honestly self-assessed:

> "I do anchor somewhat. Not catastrophically, but enough that eight sequential stress-test calls in one thread will drift toward the thread's emerging narrative, especially if earlier repairs were accepted."

This release codifies the three highest-ROI changes. The remaining four (per-venue file split, paths+read-receipt in `cwd` mode, anchor-then-window Read pattern, canonical-store + ID references) are tracked as deferred items.

### New: Reasoning Effort Ladder in `CODEX_PROTOCOL.md`

Every Codex call now defaults to `model_reasoning_effort: medium`. The ladder forces `xhigh` whenever **what is being audited** (not which skill is calling) falls into a high-risk content class: theorem / lemma / proposition / corollary statement, assumption block change, proof step, rate / constant, quantifier, probability level, dependency edge, Weaken-Claim change-log row, post-repair convergence verdict, assumption-ledger consistency check, minimax lower bound.

Allowed `medium` calls are spelled out explicitly: prose polish on non-math sentences, figure caption critique, figure-design audit, reproducibility checklist triage, LaTeX template conformance, citation completeness, style-discipline / em-dash / watchword scans, venue-checklist triage.

The honest failure cases motivating the ladder (Codex's own self-reported `medium` blind spots): quantifier-order errors in empirical-process arguments, rate bookkeeping requiring sparsity / log conditions, dependency-depth misses after weakened assumptions.

### New: Artifact Manifest Header (six-line YAML at the top of every generated artifact)

Every generated `.md` artifact begins with `artifact: <type> / scope: <local|dependency_expanded|global> / source_files / theorem_ids / assumption_ids / issue_ids / commit / generated / generator`.

This enables three downstream behaviors:

- **Lazy loading**: a downstream call checks the manifest first and only expands when the scope tag says the artifact is insufficient
- **Staleness detection**: re-audit compares the manifest's `commit` against the paper repo's current SHA
- **Token economy in chained calls**: a Codex call can refer to upstream artifacts by ID and only request them on demand

The manifest is mandatory for FINAL_REPORT, issue_log, per-unit checks, REPAIR_PLAN, PATCHES, codex_stress_test, codex_discussion, RE-AUDIT_REPORT, diff_ledger, CONVERGENCE_VERDICT, and PROOF_PACKAGE files.

### New: Per-Repair Fresh Thread (OPT7-C anti-anchoring fix) in `CODEX_PROTOCOL.md` and `proof-repair` Step 5C

The previous `proof-repair` Step 5C suggested running all P0/P1 repairs through Codex sequentially. Under the OPT7 review, Codex self-assessed that this anchors verdicts to the thread's emerging narrative. The protocol now requires:

- **One fresh `mcp__codex__codex` thread per logically-independent repair.** No `codex-reply` continuation.
- **Small dependency clusters** (2-3 repairs sharing a dependency edge, the same assumption block, or one Weaken-Claim propagation chain) may share a fresh thread.
- **No batching of unrelated repairs.** Patches on different dependency branches are separate threads.
- **Manifest travels; conversation does not.** Each fresh call carries the artifact manifests for the current patch and direct dependencies.
- **Anti-anchor prompt language** opens every call: "This is an independent repair review. Treat the proposed repair on its merits. Prior repair verdicts in this pipeline are not part of your context."
- **Forced falsification attempt.** The verdict must name which attack was tried (missing assumption / dependency break / rate-or-quantifier mismatch / downstream impact) and whether it succeeded.

The within-phase iterative push-back protocol (the existing 5-round dialogue) still uses `codex-reply` on the same thread, because the object under discussion is the same finding. This is Case B and is correctly served by thread reuse; it is not the anchoring failure mode.

Across phases (audit → repair → post-repair), each phase opens a fresh thread; only the manifest travels.

### `proof-repair` Step 5C concrete updates

- `model_reasoning_effort: xhigh` forced (the scope hits the ladder's trigger list).
- Manifest header included in each call's prompt; full source files referenced by path + section anchors rather than pasted.
- Per-repair stress-test table in `codex_stress_test.md` now records the `Codex threadId` column so the user can resume any individual repair's dialogue.
- Falsification attempt column added to the table.

### `proofcheck` artifacts now carry manifests

- `audit/06_reports/FINAL_REPORT.md`: `scope: global`, every theorem/lemma in inventory, every issue.
- `audit/06_reports/issue_log.md`: `scope: global`.
- `audit/04_local_checks/section_*/*.md`: `scope: local`, single `theorem_id`.
- `audit/08_post_repair/RE-AUDIT_REPORT.md`, `diff_ledger.md`, `CONVERGENCE_VERDICT.md`: `scope: dependency_expanded`, paper-repo SHA at re-audit time recorded as `commit`.

### What this does NOT change

- The within-phase iterative dialogue protocol (5-round push-back via `codex-reply`) is unchanged.
- The cross-review independence requirement (different phases use different threads) is unchanged.
- The hard-gate convergence rule from v1.6.0 is unchanged: `/proofcheck --post-repair` is required for any S0/S1 issue.
- The Repair Closure Matrix and Weaken-Claim Change Log from v1.6.0 are unchanged.

### Token-savings estimate

Compound effect across a typical proof-cycle session:

- Manifest-enabled lazy loading and ID references: ~10-15% on artifact reloads
- Reasoning effort ladder (most polish-level Codex calls drop to `medium`): ~15% on Codex output tokens
- Per-repair fresh thread + manifest: roughly neutral on tokens (manifest re-sent), but fixes the silent-anchoring quality bug
- rtk Bash wrapping (recommended at `brew install rtk` / `rtk init`): ~60-90% on `git`/`wc`/`find`/`ls` calls inside skill workflows, ~10% session-level

The aggregate target is ~25-30% session-level token reduction with strict zero compromise on proof verification quality.

### Codex dialogue log

- threadId: `019e6ed3-0b5d-7e72-b424-5428423a2276`
- Configuration: `mcp__codex__codex`, `model_reasoning_effort: xhigh`, sandbox `read-only`
- Round 1 outcome (7 candidate optimizations): 3 ADOPT, 3 MODIFY-with-scope, 1 SKIP-with-modification-to-fresh-thread-protocol; one missed-optimization suggested (artifact manifest header).
- Round 2 outcome (push-back on OPT7's blanket "skip all shared threads"): Codex honestly self-assessed anchoring effect, distinguished Case A (cross-phase, fresh thread), Case B (within-phase iterative pushback, same thread per the existing protocol), Case C (within-phase independent units, fresh thread per repair or 2-3 cluster). All four refinements I proposed (OPT1 via rtk's own exclude_commands; OPT3 scoped to long stat-theory papers; OPT4 ladder by content not by skill; OPT5 anchor-then-window only when ledger + DAG pre-loaded) confirmed.

### Deferred items (token economy roadmap)

- **OPT2** Per-venue file split + venue-index file. ~5% session savings. Half-day effort. Targeted at `stat-venue-checklists.md`-equivalent content. Sibling repo `stat-writing-skills` has the analogous opportunity and tracks it in its roadmap.
- **OPT3** Paths + read-receipt protocol for Codex calls on long appendix proofs. ~15% on long-paper Codex calls. 1-2 days effort. Requires read-receipt protocol enforcement (Codex must list files opened, anchors inspected, line ranges read, and explicitly say `INSUFFICIENT CONTEXT` rather than infer).
- **OPT5** Anchor-then-window Read pattern (grep for anchor → Read with offset/limit), conditional on assumption ledger and dependency graph being pre-loaded into the call. ~10% session savings. Half-day effort.
- **OPT6** Canonical store + ID references in audit artifacts (issue_log.md as the only source of truth; other artifacts reference by ID with a compact auto-generated legend per call). ~5% token savings + significant consistency benefit. 1-2 days effort.

## v1.6.0 — Post-repair re-audit closure (convergence test for the repair phase)

User observation: the pipeline went `/proofcheck → /proof-repair → /theory-sharpen → ...` linearly, but had no formal mechanism to verify the repairs actually closed the original issues without introducing new ones. The per-repair Codex adversarial stress-test (Step 5C) catches local errors but cannot see downstream / global breakage. The output text suggested users "Re-verify: /proofcheck papers/my-paper/" but this was a soft hint, not a built-in convergence test.

A second Codex MCP review (threadId `019e6c52-59ca-7642-9797-a9fb686ea127`, `model_reasoning_effort: xhigh`) confirmed the gap and gave architectural guidance. Codex's verdict on the four candidate designs: **B (focused `--post-repair` mode)** was correct; full `/proofcheck` re-run is overkill for a solo workflow; stricter Step 5C alone is insufficient because it is local-only; the README pipeline diagram should show the loop explicitly. All 9 of Codex's points were accepted with no push-back; the dialogue converged in round 1.

### New: `/proofcheck --post-repair` mode

Focused delta audit, **not** a full 6-pass re-run. Reads the original audit + `REPAIR_PLAN.md` + `PATCHES.md` + the patched paper, and produces a convergence verdict.

Six steps:

- **P1**: Treat `PATCHES.md` as the semantic change log. Reads the Weaken-Claim Change Log so an intentionally weakened claim is judged against the REVISED statement, not the original. An undocumented or unpropagated semantic change is itself a `NEW-S0` defect.
- **P2**: Per-issue closure verification. Every row of the Repair Closure Matrix must reach a terminal status (`CLOSED-VERIFIED`, `CLOSED-WEAKENED`, `CLOSED-BLOCKAGE`, `STILL-OPEN`, or `WAIVED`). Targeted re-verification of `CLOSED-VERIFIED` units; propagation check for `CLOSED-WEAKENED`.
- **P3**: New-issue scan on touched units only (not on the whole paper). Detects new hidden assumptions, new quantifier mismatches, new rate dependence, new circular dependencies, new notation drift, new cross-file references broken by Mode B numbering. Labeled `NEW-S0` / `NEW-S1` / `NEW-S2` / `NEW-S3`, distinct from `STILL-OPEN` (which means the patch failed to close an original issue).
- **P4**: Global consistency re-run (assumption ledger + dependency graph only). Catches the integration-level failure modes that per-repair Step 5C cannot see by design.
- **P5**: **Assumption / Rate Diff Ledger** generated at `audit/08_post_repair/diff_ledger.md`. Compact diff across changed assumptions, constants, rates, probability levels, norms, sample-size regimes, and dependency requirements. Codex explicitly flagged this as high-ROI because in statistics-theory, most bad repairs are not algebraic errors but silent strengthening, silent rate degradation, or silent incompatibility across lemmas.
- **P6**: Convergence verdict written to `audit/08_post_repair/CONVERGENCE_VERDICT.md`. Three terminal states: `CONVERGED`, `NOT CONVERGED — RE-REPAIR REQUIRED` (cycleable via `/proof-repair --from-reaudit`), or `NOT CONVERGED — HUMAN INTERVENTION REQUIRED` (paper-level intent or assumption set must be revisited).

### New: `/proof-repair --from-reaudit` mode

Manual-only sub-mode. Triggered when `/proofcheck --post-repair` reports `NOT CONVERGED — RE-REPAIR REQUIRED`. Reads the residual issues from the post-repair audit, classifies them by cause (`INCOMPLETE-FIX`, `WRONG-CLASSIFICATION`, `UNDOCUMENTED-WEAKENING`, `PROPAGATION-GAP`, `NEW-DEFECT`), and runs Steps 3-5 of the main workflow on residuals only. Appends a new section to `REPAIR_PLAN.md` labeled `Repair Cycle 2`. Re-invokes `/proofcheck --post-repair` is required afterward; convergence cannot be declared by `--from-reaudit` itself.

**Hard rule against auto-looping**: the pipeline never automatically chains `--from-reaudit` and `--post-repair`. After two cycles without convergence, the affected theorem is downgraded to NOT CURRENTLY JUSTIFIED and the abstract / introduction are updated to remove the claim.

### `proof-repair` hard-gate completion rule

REPAIR_PLAN.md is `complete` only when ALL of the following are true:

1. Every original issue has a row in the Repair Closure Matrix with a terminal closure status.
2. Every Weaken-Claim repair has a row in the Weaken-Claim Change Log with the downstream impact propagation list.
3. Outstanding sketches = 0.
4. Every P0/P1 repair has passed Codex Step 5C.
5. The Consistency Verification checklist is fully checked.
6. **If the original audit contained any S0 or S1 issue**: `/proofcheck --post-repair` has run AND `CONVERGENCE_VERDICT.md` reports `CONVERGED`. HARD GATE.
7. **If the original audit contained only S2 and S3 issues**: `--post-repair` is strongly recommended but not gated.

### New: Repair Closure Matrix in REPAIR_PLAN.md

Canonical record of issue closure. Columns: `Issue ID | Original severity | Unit | Repair class | Patch ID | Touched units | Closure status | Post-repair status | Downstream affected units`. `/proof-repair` fills in the design-time columns; `/proofcheck --post-repair` fills in `Post-repair status`. Every issue in `issue_log.md` must have a row, even deferred or blocked ones.

### New: Weaken-Claim Change Log in REPAIR_PLAN.md and per-unit repair files

Mandatory four-column table for every Weaken-Claim repair: `Original claim (verbatim) | Revised claim (verbatim) | Reason for weakening | Downstream impact`. The downstream impact column is the propagation contract — every listed unit must have a corresponding patch. A Weaken-Claim repair without this table is treated as `NOT CURRENTLY JUSTIFIED` and demoted to a blockage report.

### README updates

The pipeline diagram now shows `/proofcheck --post-repair` as the explicit convergence test between `/proof-repair` and `/theory-sharpen`. The label uses `--post-repair` (not generic `/proofcheck`) so users understand this is a focused delta audit, not a full re-audit. The pipeline example block adds the `Step 2.5` re-audit call and the optional `Step 2.6` `--from-reaudit` cycle.

### What this catches that v1.5.1 missed

- A repair that locally proves a correct lemma but no longer correctly feeds the downstream theorem
- A weakened rate in a lemma that breaks a corollary's rate without any patch updating the corollary
- A new assumption in Lemma 5 that contradicts an existing assumption in Lemma 8
- A silent change in the paper's headline claim that downstream sections (abstract, introduction, application) do not reflect
- A patched proof that introduces a hidden assumption not present in the original assumption block

Codex Step 5C alone could not catch any of these because it reviews each repair in isolation, without a global view of the patched paper.

### Codex dialogue log

- threadId: `019e6c52-59ca-7642-9797-a9fb686ea127`
- Configuration: `mcp__codex__codex`, `model_reasoning_effort: xhigh`, sandbox `read-only`
- Outcome: 9 verdicts (Design A MODIFY, Design B ADOPT, Design C SKIP, Design D ADOPT; Step 5C vs re-audit complementary; Weaken-Claim handling via PATCHES.md; new S0/S1 = NOT CONVERGED with manual `--from-reaudit`; Repair Closure Matrix; Diff Ledger). All accepted, no push-back, dialogue converged in round 1.

## v1.5.1 — Detection-MUST-trigger-completion (sketch handling hardened)

User observation: v1.5.0 added sketch detection and an Expand-Sketch-to-Proof
repair class, but it was still possible for the system to flag a sketch and
move on without expanding it. v1.5.1 closes that loophole.

### Hard rules added (across 3 skills)

**proofcheck**: A detected sketch MUST be expanded before the audit can be
marked complete.
- New mandatory field `Expansion status: REQUIRED / IN-PROGRESS / COMPLETED`
  on every flagged unit
- Audit refuses to advance to Pass 5 (Final Report) while any sketch remains
  in REQUIRED or IN-PROGRESS state
- Final Report's executive summary REQUIRES a line accounting for every
  detected sketch (must end as EXPANDED or BLOCKAGE — no partial states)

**proof-repair**: Expand-Sketch-to-Proof becomes **P0 priority unconditionally**
- Cannot be deferred to "future revision"
- REPAIR_PLAN.md now has a mandatory Sketch Expansion Tracker section
  showing every flagged sketch and its terminal state
- Plan refuses to mark complete with "Outstanding sketches > 0"
- Reclassified failure modes still must expand: Replace-Technique → expand the
  alternative proof; Add-Assumption → expand under new assumption

**proof-writer**: New HARD COMPLETION RULE when invoked to expand sketches
- Output MUST be exactly one of two terminal states:
  - COMPLETE PROOF (every step rigorously derived)
  - BLOCKAGE REPORT (explicit NOT-CURRENTLY-JUSTIFIED with what's missing)
- Explicitly FORBIDDEN: second sketch, partial expansion, weaker claim
  without relabeling, silent assumption injection
- Refuses requests to "just expand this a bit" — forces full expansion
  or blockage report

### Why this matters

The most common failure mode when LLMs are asked to "expand a proof sketch" is
producing another sketch with slightly more words. v1.5.0 detected sketches
but did not enforce that detection lead to terminal expansion. v1.5.1 makes
"sketch detected and not expanded" an impossible terminal state of the pipeline.

## v1.5.0 — Sketch vs Complete Proof discipline (3 skills)

User observation: many papers present "proof sketches" that are actually research
outlines, not verifications. The skills must distinguish, classify, and act
on this — proof-writer must refuse to produce one, proofcheck must classify
existing proofs, proof-repair must expand sketches into full proofs.

### proofcheck — New Sketch-vs-Complete Classification

New mandatory sub-step in Pass 1 (Step 3), runs before step-by-step verification.

Three-class classification per unit:
- **COMPLETE**: rigorous step-by-step derivation; all transitions justified
- **PARTIAL-SKETCH**: rigorous in parts but with substantial gaps ("rest follows
  by similar arguments"; entire technical lemma deferred; main step is one
  paragraph for a 1-page claim) — each gap recorded as S1 issue
- **SKETCH-ONLY**: high-level outline without rigorous derivation. Title labeled
  "Proof Sketch", or purely verbal narrative, or single-paragraph "proof" for a
  substantive theorem — STATUS forced to "SKETCH-ONLY — NO PROOF PROVIDED"

8 sketch indicators listed (explicit labels, verbal-only body, "we omit details",
disproportionate length, etc.). Supplement proofs that are also sketches inherit
the same classification.

Reviewer-facing rule: a sketch in main text is NOT verification; if paper relies
on it, theorem is at best CONDITIONALLY VERIFIED pending full proof.

### proof-repair — New repair class: Expand-Sketch-to-Proof

When proofcheck flags SKETCH-ONLY / PARTIAL-SKETCH, the repair is to write
the ENTIRE proof, not just fix steps. Distinct from Fill-Skipped-Steps (which
fills isolated gaps inside an otherwise rigorous proof).

Workflow:
1. Extract intended outline from the sketch
2. For each intended step: verify cited technique applies + write actual derivation
3. Trigger /proof-writer (which refuses to produce another sketch)
4. Verify expanded proof concludes the original claim exactly
5. Cite canonical references for invoked techniques

Common failure modes documented:
- Sketch hides genuine unprovability → downgrade to NOT CURRENTLY JUSTIFIED
- Cited technique doesn't apply → reclassify as Replace-Technique
- Expansion reveals missing assumption → reclassify as Add-Assumption

### proof-writer — New ANTI-SKETCH DISCIPLINE

The skill now explicitly REFUSES to produce a sketch in place of a proof.

Distinguishes:
- Proof outline / research plan: fine (delegate to /theory-design)
- Proof sketch placed as "proof": REFUSED
- Complete proof: what this skill always produces

When user asks for a sketch:
- Refuse the disguised-as-proof version
- Offer: complete proof / explicit research outline (labeled, not proof) /
  proof of weaker verifiable claim + research outline for stronger

When the only completable thing is a sketch:
- Downgrade to NOT CURRENTLY JUSTIFIED + blockage report
- Do NOT silently substitute a sketch for a proof

New length heuristic: a substantive theorem (rate, distribution, coverage)
typically needs ≥ 1 page of dense derivation. ≤ 10 lines for a paragraph-long
theorem triggers a sketch-suspicion check.

Strengthened forbidden phrases now include: "the rest is similar", "we omit
the details", "details are routine", and pointing-at-paper-without-adaptation.

## v1.4.0 — Shared Codex Discussion Protocol (NOT wholesale acceptance)

User observation: across all skills using Codex, the implicit risk was that Claude
would "全盘接受" Codex findings rather than discussing them. This release codifies
the discipline.

### New file: `CODEX_PROTOCOL.md` (repo root)

A shared, explicit protocol for how Claude skills invoke Codex:

- **Core principle**: Codex is an adversarial reviewer to discuss with, NOT an
  oracle to defer to
- **5-round protocol**: Claude output → Codex review → Claude per-finding
  evaluation (ACCEPT / PUSH BACK / REQUEST CLARIFICATION) → Codex response →
  iterate until convergence or escalate
- **Forbidden behaviors**: silent wholesale acceptance, silent rejection,
  acceptance without recorded reasoning, push-back without substantive argument
- **Documentation requirement**: every Codex-using skill emits `codex_discussion.md`
  showing the full round-by-round dialogue
- **When to escalate**: persistent disagreement, >3 rounds without progress,
  or taste/philosophy/venue-preference disagreements (let user pick)

### Updated skills (all 5 now reference CODEX_PROTOCOL.md)

- `proofcheck` (Pass 4): adversarial cross-review uses discussion protocol
- `proof-repair` (Step 5C): stress-test repairs via discussion
- `theory-sharpen` (Step 5B): independent assessment via discussion;
  especially critical to prevent OVERCLAIM of theory relaxation
- `theory-simulation` (Step 4F): pre-run + post-run review via discussion;
  critical because reruns are expensive
- `theory-design` (Step X4): NEW — adversarial framework review via discussion;
  critical because framework shapes the whole paper

Each skill explicitly calls out the forbidden behaviors and the requirement to
emit a `codex_discussion.md` documenting the dialogue.

### Why this matters

LLM-to-LLM review has two failure modes:
- **Capitulation**: Claude accepts every Codex finding to avoid disagreement
  → output shaped by whichever model is louder
- **Defensiveness**: Claude dismisses Codex findings to defend prior work
  → loses the value of independent review

Both produce worse outputs than a single careful Claude pass. The protocol
forces structured deliberation that exploits both models without inheriting
either's blind spots.

### Documented examples

CHANGELOG entries v1.1.1, v1.2.0 already documented real instances of the
protocol working (Codex raised 20 findings; 13 accepted, 6 push-backs of which
5 produced refinements and 1 was conceded by Claude). v1.4.0 makes this pattern
explicit and uniform across all skills.

## v1.3.1 — theory-design: Mandatory literature anchoring

Designing a theoretical framework without first reading recent top-venue
literature is unsafe — you risk reinventing existing work, deviating from
field conventions for no reason, or being unable to position the contribution.
The skill now enforces literature anchoring BEFORE any phase decision.

### New Step 0.5: Mandatory Literature Anchoring

**0.5A Topic signature**: structured search keywords (subject + technique + data
structure + framework + regime + application area).

**0.5B Multi-source T1 search** (4 parallel agents):
- T1 statistics journals (AoS, JASA T&M/ACS, AOAS, JRSS-B, Biometrika,
  Bernoulli, EJS, Statistica Sinica, Biostatistics, JCGS)
- T1 ML/AI conferences (NeurIPS, ICML, ICLR, COLT, AISTATS, JMLR, UAI)
- T1 econometrics journals (Econometrica, JOE, REStud, QE, JBES, ET)
- Highly-cited consensus papers (last 10 years, citation-sorted)

Prefers last 3 years, hard cap at last 5 years. Citation gates calibrated by recency.

**0.5C Per-paper structured extraction**:
problem framing, theoretical anchor, assumption profile, result type, proof
technique, position in literature.

**0.5D Theoretical inertia identification**:
What is the current consensus on data structure, modeling framework, asymptotic
regime, proof technique, contribution shape? This is the "default path" the
field expects.

**0.5E Positioning options** (3 choices, each with trade-offs):
- INCREMENTAL: refine within the inertia (lower friction, lower novelty)
- LATERAL: same problem, different angle (justifies the angle change)
- DISRUPTIVE: challenges the inertia (highest reward, must build the case)

**0.5F Anchor → design constraints**:
Every subsequent phase must reference the anchor when making decisions:
"You're adopting the inertia here — cite [canonical papers]"
"You're deviating here — justify with [specific reasoning]"

**0.5G Mandatory user confirmation**:
Skill REFUSES to proceed to Step T1/M1/A1 until user confirms the anchor.

### New Step X2.5: Positioning audit

After framework design, verify:
- Did each phase decision match the chosen positioning?
- Did the framework drift from positioning during T1-T7 / M1-M7 / A1-A7?
- Citation strategy alignment: which 5-10 papers cited prominently, in what role?

If positioning drifted, decide: revert framework to match original positioning,
OR update positioning to match what framework evolved into. Either is fine;
the mismatch is the problem.

### Output addition
- New artifact: `papers/<paper-name>/design/LITERATURE_ANCHOR.md`
- Consumed by all downstream skills (proof-writer, theory-simulation, proofcheck)
  for context

## v1.3.0 — New skill: theory-design (paper-type-aware framework planning)

Adds a 6th skill that handles the **planning phase** — from "I have a new
research topic" to a structured FRAMEWORK_DESIGN.md.

### Key insight
Statistics papers come in three types with FUNDAMENTALLY different logical
orders for theoretical-framework design:

| Type | Centerpiece | Theory's role |
|------|-------------|---------------|
| THEORY paper | The theorem itself | The contribution |
| METHODOLOGY paper | The estimator/method | Guarantees method correctness |
| APPLICATION paper | Empirical findings | Justifies method choice + verifies assumptions |

Previous version of this skill family conflated these three. The new skill
forces a paper-type declaration first, then walks a type-specific 7-phase
logical order:

**THEORY mode (T1-T7)**:
T1: Phenomenon / mathematical-object identification
T2: Mathematical landscape mapping (existing toolkit gap)
T3: Conceptual framework & notation
T4: Formal problem setup (spaces, parameter classes, regimes)
T5: Target theorems — upper AND lower bounds equally first-class
T6: Proof strategy & lemma scaffold
T7: Connections to downstream (what methods this enables)

**METHODOLOGY mode (M1-M7)**:
M1: Practical problem & method gap
M2: Method design (CENTERPIECE)
M3: Model setup for analysis
M4: Identification
M5: Theoretical guarantees needed (consistency / rate / inference / etc.)
M6: Simulation + real-data validation plan
M7: Proof strategy (technical labor supporting the method)

**APPLICATION mode (A1-A7)**:
A1: Scientific question & data
A2: Existing-method selection
A3: Assumption verification on THIS dataset (distinguishes APP from METHO)
A4: Empirical findings
A5: Inference & uncertainty quantification
A6: Sensitivity analyses
A7: Connection to literature & implications

**Cross-type checks (X1-X4)** run for all modes:
- Internal consistency
- Novelty / contribution audit
- Reviewer hot-button preemption
- Codex independent framework review

### Pipeline placement
```
research-refine → /theory-design → /proof-writer → /theory-simulation → /proofcheck → /theory-sharpen → /proof-repair
(rough idea)      (framework)      (theorems)      (verify)              (audit)         (improve)         (fix)
```

theory-design is the planning layer BEFORE any theorem is written or experiment
run. It hands off:
- Theorem statements (T5/M5) → /proof-writer
- Validation plan (M6/A4-A5) → /theory-simulation
- Pre-paper checks → /proofcheck (after proofs drafted)

## v1.2.0 — theory-simulation: AUDIT MODE for existing simulations

Adds a second operating mode to theory-simulation, after a third round of Codex
adversarial review focused on the new audit functionality.

### New AUDIT MODE
When a paper already has a simulation section, the skill now evaluates whether
those existing simulations actually verify the theorems, identifies gaps,
and proposes targeted improvements (rather than full redesign).

**A0 — Parse existing sims**: extract experiments, DGPs, n grids, methods, metrics,
B values, figures, tables, stated conclusions.

**A1 — Two-axis Coverage Matrix** (per Codex's split):
- Axis 1: **Coverage** — does any experiment aim at this claim?
- Axis 2: **Evidentiary strength** — does the experiment actually identify the claim?
- Claim priority ranking: PRIMARY / SECONDARY / PERIPHERAL
- Final tags with structured reason codes:
  - `YES[strong]` / `YES[weak]`
  - `PARTIAL[path | metric | precision | grid | comparator | reporting | stress-coverage | identification-mismatch]`
  - `NO`
  - `CONTRADICTED[*]`

**A2 — Per-experiment adequacy audit** scoring on 12 criteria.

**A2.5 — CONTRADICTED 7-step protocol** (Codex insisted on this):
1. Replication check (rerun with saved seed)
2. Metric check (does paper measure what theorem bounds?)
3. DGP check (do assumptions actually hold in sim?)
4. Computation check (failures, tuning, numerics)
5. MC precision check (is contradiction > 2 × MCSE?)
6. Localization (all cells / pre-asymptotic / off-assumption?)
7. Escalation routing (implementation fix / not real / reframe / genuine — invoke /proofcheck)

**A2.6 — Reuse legitimacy audit**: verifies existing runs can be statistically
reused (replicate-level data saved, RNG streams recorded, no silent failures,
correct truth, etc.) before blessing reuse.

**A2.7 — Truth-source audit**: how was ground truth defined?
Analytic / oracle / numerical / high-B estimate / asymptotic limit — each needs verification.

**A2.8 — Selection-bias audit**: omitted cells, methods, regimes, DGPs, failures,
cherry-picked seeds.

**A2.9 — Tuning / procedure audit**: oracle vs data-driven; CV variability; sensitivity.

**A2.10 — Computational adequacy audit**: mandatory when paper claims "fast",
"scalable", "practical".

**A3 — Gap analysis** in 6 buckets now (was 3):
1. Claims with NO experimental evidence
2. Experiments with adequacy problems
3. Reporting / discipline issues
4. Selection-bias risks (`SELECTION_RISK`)
5. Tuning / procedure gaps (`TUNING_GAP`)
6. Computational adequacy gaps (`COMP_GAP`)

**A4 — Targeted improvement plan**: priorities ordered, distinguishing what can
be reused from existing runs vs what must be rerun.

**A5 — Codex cross-audit** (optional): independent second opinion on the audit itself.

### Result
Skill went 1001 → 1435 lines. Three Codex review rounds, all 23 + 4 + 4 findings
addressed. Skill now handles both new-from-scratch design AND audit of existing
simulations.

## v1.1.1 — theory-simulation: Codex-reviewed rigor pass

Codex GPT acted as an adversarial AoS/JASA/JRSS-B referee on the theory-simulation
skill and identified 20 issues. After discussion, 13 were accepted outright, 6 were
refined via pushback (Codex agreed), and 1 was pushed back (Codex held firm — accepted).
A second round caught 4 remaining MAJOR gaps. All 23 final findings now addressed.

### Major upgrades in theory-simulation (687 → 1001 lines)

**Statistical correctness**
- Rate protocol now declares loss object (norm vs MSE → slope `-a` vs `-2a`)
- Asymptotic path must be declared and held fixed (`s log d / n` etc.)
- Slope verified via weighted regression + local slopes + normalized-loss leveling
- B selected by MCSE target per metric (no fixed thresholds)
- Per-metric MCSE formulas (binomial / delta / bootstrap / paired)

**Inference diagnostics (was missing — biggest hole)**
- Now required: coverage + size + local power + interval length + EmpSE vs ModSE +
  bias-eliminated coverage
- Wilson/Jeffreys intervals for coverage, not arbitrary ±0.02 bands

**Design discipline (ADEMP + claim-based)**
- "One experiment per theorem" replaced with ADEMP block per empirical claim
- Stress tests in two layers: one-at-a-time (diagnostic) + factorial (robustness claim)
- DGP candidates carry mismatch warnings (t_3 finite variance, AR(1) short memory etc.)
- Theorem-matched least-favorable DGPs required
- Paired-replicate method comparison is NOW DEFAULT (was misclassified as STRICT-tier)

**Conditional diagnostics (mandatory if claim exists)**
- Oracle vs data-driven tuning gap
- Variability over tuning randomness (CV folds, random init)
- Runtime/memory scaling along asymptotic path (if scalability claimed)

**Anti-cherry-picking discipline**
- Preregister primary cells + primary summaries before running
- MCSE-relative deviation thresholds
- Anti-narration rule: no general conclusions from one-off cells

**Reproducibility (tiered, target-aware)**
- BASIC / STRICT (default) / PUBLICATION
- Declare reproducibility target: bitwise identical vs statistically equivalent
- Hierarchical RNG (SeedSequence / L'Ecuyer-CMRG), per-rep state stored
- Thread env vars + BLAS lib version recorded
- Code architecture: manifest-driven, immutable cell_id, replicate-level Parquet/JSON,
  reproduce script, regression tests on toy DGPs

**Failure handling (was missing)**
- Per-rep status field (success/nonconvergence/singular/empty/negative_var/timeout)
- Per-cell failure rate reported
- Default alerts >5% / >20% reframed as context-dependent (regime severity)

**Figure rules split**
- Actual journal requirements (alt text, color-redundant encoding, final-size legibility)
- vs stat-paper house style (no title, Okabe-Ito, in-panel labels)
- "NO title" softened to "usually omitted in stat journals" (convention, not rule)
- Figure types CONDITIONAL on claim (rate → log-log, CI → coverage, test → size/power)
- MC uncertainty required on every figure (error bars or bands)

**Reconciliation discipline (no overclaiming)**
- Findings split: EVIDENCE (can update paper) vs HYPOTHESIS (needs analytic follow-up)
- Asymmetry rule: sim can support keeping assumptions (via failure) but cannot prove dropping
- "Worked at t_5" → hypothesis only; needs adversarial expansion + proof before paper claim

**Edge cases**
- Rare events: importance sampling or scale B to ≥10/p_target
- Randomized algorithms: nested RNG layer
- No closed-form truth: HIGH-B benchmark for ground-truth estimate
- Long-running estimators: time budgets, checkpointing
- Adaptive/sequential procedures: data + algorithm randomness both seeded

**Codex cross-review (still optional but improved)**
- Pre-run plan review + post-run figure/reconciliation review
- Catches overclaim, suspicious results, missing context

References cited: Morris, White & Crowther (2019, Stat Med); Koehler, Brown &
Haneuse (2009, Am Stat); Brown, Cai & DasGupta (2001, Stat Sci); JASA
Reproducibility Editorial (2024); Andrews & Cheng (2012, Econometrica).

## v1.1.0 — New skill: theory-simulation

Adds a fifth skill, `theory-simulation`, that bridges theoretical results and
Monte Carlo simulation to top-statistics-journal standards.

### Pipeline now (5 skills)
```
/proofcheck → /proof-repair → /theory-sharpen → /theory-simulation → /proof-writer
```

### theory-simulation skill (583 lines)
- **Theory-to-simulation mapping**: each theorem gets a verification experiment
  with explicit DGP, sample-size grid, reps, metrics, pass/fail criteria
- **Stress-test design**: violate each critical assumption one at a time
  (heavy tails, dependence, misspecification, boundary, identifiability,
  growing dim, outliers, small sample)
- **Rate verification protocol**: ≥6 sample sizes, log-log slope regression
  with 95% CI on the slope
- **Coverage verification**: empirical coverage at multiple n with Wilson CI
- **Method comparison**: required ≥1 baseline (oracle/competitor/naive)
- **Implementation conventions**: seed determinism, parallel runner, atomic
  CSV writes, reproducibility check
- **Stat-journal figure conventions** (different from Nature defaults):
  - **NO titles** on plots — all content in LaTeX `\caption{}`
  - Okabe-Ito palette (color-blind safe) for lines
  - Viridis/cividis for heatmaps; never jet/rainbow
  - Embedded fonts (`pdf.fonttype = 42`) for editable text
  - Reference dashed lines for theoretical rates / nominal coverage
  - Multi-panel with (a),(b),(c) labels in-panel, no panel titles
  - Pre-export checklist (no titles, legend doesn't cover data, etc.)
- **Theory ↔ simulation reconciliation**: feedback loop to upstream skills
  - Confirmed predictions → ready for paper
  - Theory under-claims → forward to `/theory-sharpen`
  - Theory over-claims → forward to `/proofcheck` for re-audit
  - Assumption unnecessary → relaxation candidate
  - Assumption genuinely needed → strengthen statement
- **Drop-in SIMULATION_SECTION.tex** for the paper

## v1.0.3 — Reference Mode Awareness (single-file vs two-file submissions)

Handles the practical reality that JASA / AoS / JRSS-B / Biometrika / Econometrica
submissions split main text and supplement into TWO separately-compiled PDF files,
where LaTeX `\ref{}` does NOT work across files.

### proofcheck additions
- **Reference Mode detection** at Step 0: distinguish Mode A (single-file) from
  Mode B (two-file main+supplement)
- **Mode-aware cross-reference audit** (Pass 0 Task 2B):
  - Mode A: standard `\ref{}` ↔ `\label{}` audit
  - Mode B: per-file audit + flags cross-file `\ref{}` as broken (S1 issue)
  - Mode B: validates "of the supplement" / "of the main text" wording is paired
    with hard-coded numbers
  - Mode B: checks S-prefix numbering consistency in supplement

### proof-repair additions
- **Step 0B: Detect Reference Mode** before any LaTeX patch is written
- LaTeX patches now declare their reference mode and conformance rules:
  - Within-file references → `\ref{}` / `\eqref{}` / `\cref{}` as normal
  - Cross-file references → hard-coded numbers ("Lemma S.3 of the supplement",
    "Assumption 2 of the main text"), NEVER `\ref{}`
- New lemmas inserted in supplement get S-prefixed display numbers, recorded
  for downstream main-text patches to hard-code
- **Pre-patch validation rules** scan each patch to catch leaked cross-file `\ref{}`
- BibTeX `\cite{}` is shared (works in both files) — only mathematical-object
  `\ref{}` is mode-sensitive

## v1.0.2 — Step Completeness Audit

Goes beyond passive anti-fabrication word-flagging to actively detect, reconstruct,
and classify skipped proof steps.

### proofcheck additions
- New mandatory sub-step **Step Completeness Audit** within each unit's check:
  - **Skip-point detection** in 3 categories: verbal phrases ("clearly", "by
    symmetry", "after some algebra"), equation-number jumps, implicit logical jumps
  - **Reconstruction attempt** for each detected skip using only paper's
    assumptions + cited results + named standard facts (anti-fabrication on the
    checker side)
  - **Skip classification**: TRIVIAL / VERIFIABLE / NONTRIVIAL / UNRECONSTRUCTIBLE
  - **Step Completeness Table** per unit recording every skip and verdict
  - **Reconstruction discipline rules** preventing the checker from inventing
    intermediate inequalities or unstated lemmas

### proof-repair additions
- New repair class **Fill-Skipped-Steps** with class-specific workflow:
  - VERIFIABLE (S3): write 2-5 intermediate steps inline, no refs needed
  - NONTRIVIAL (S1): identify the bridging idea, cite or create lemma
  - UNRECONSTRUCTIBLE (S0): no bridge manufacturing — investigate root cause
    (wrong proof, hidden assumption, or wrong technique)

## v1.0.1 — Model recommendation: Opus

- Added `model: opus` to YAML frontmatter of all 4 skills (forward-compatible
  with future Claude Code versions; harmless if not yet honored)
- Added prominent "Model Recommendation" callout at the top of each SKILL.md
- Updated README with required Opus setup section and rationale per skill
- Updated install.sh to print the model reminder after installation

## v1.0.0 — Initial release

### Skills included
- `proofcheck` (528 lines) — multi-pass proof verification methodology (references
  maweiruc/proofcheck-stat-paper for the 6-pass structure), reorganized into a single
  SKILL.md with provability triage and proof-strategy classification
- `proof-repair` (768 lines) — new skill: triage → impact analysis → candidate
  repairs → multi-source T1 literature search → complete proof writing → Codex
  stress-test → master REPAIR_PLAN
- `theory-sharpen` (1120 lines) — new skill: mandatory 3-axis framework
  classification with literature-anchored validation → 22 framework-tagged
  relaxation pathways → rate sharpening → reviewer-critical dimensions audit →
  Codex independent assessment
- `proof-writer` — rigorous proof drafting skill, included for pipeline completeness

### Key design decisions
- **Venue tier system** (T1 Gold → T4 Avoid) applied consistently across
  proof-repair and theory-sharpen
- **Codex MCP cross-review** integrated into three skills using a
  first-independent-then-reconcile pattern
- **Framework Classification** before any relaxation analysis to prevent
  irrelevant pathway suggestions
- **Literature recency + venue gating**: prefer last 3 years, T1 only,
  with citation gates calibrated by recency
- Reference library audited by Codex: 6 venue errors corrected, 7 missing
  pathways added, 9 reviewer-critical dimensions surfaced

### Reference library size
- 22 relaxation pathways across 5 categories with framework tags
- 11 rate-sharpening directions
- 10 reviewer-critical dimensions
- All references venue-verified
