---
artifact: shared_reference
scope: cited_results_lock_protocol
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills cited_results.lock.md ownership protocol, addresses Codex round 3 V8 REQUIRES FIX (threadId 019e7112-283e-74b1-97e5-6344592cd820)
---

# `cited_results.lock.md` Ownership Protocol

Defines who creates and who updates the project-side citation pin manifest `papers/<project>/cited_results.lock.md`. The lock manifest is referenced by every literature-touching skill in `stat-theory-skills` and `stat-writing-skills`, but without a designated owner it would be inconsistently created and silently fall out of sync with the global cache.

Codex round 3 V8 flagged this as REQUIRES FIX: "best fix: a tiny `/lock-citations` skill or shared reference owns the schema and validation; first citation-producing skill creates it, then `proof-repair`, `proof-writer`, `stat-paper-plan`/`write` update it."

This protocol is the lightweight version: no new skill binary, but the responsibility is formalized in the existing skill workflows.

## When to Read

- During `stat-paper-plan` Step 5.7 (the new initialization step) when starting a new project.
- During any skill step that adds, modifies, or removes a citation from a project's artifacts.
- During `/proofcheck --post-repair` when verifying that load-bearing citations have lock-manifest entries.
- During `/stat-mock-review` when checking that fatal-or-major concerns naming a cited theorem resolve to a lock-manifest row.
- During the final author sign-off before submission.

## The Schema

Each project carries one `cited_results.lock.md` file at `papers/<project>/cited_results.lock.md`. Full schema in `citation-purpose-protocol.md`. The columns are:

```
Citation site / Reference / Citation purpose / Role in literature /
Role relative to current paper / Source version at decision /
Entry hash at decision / Verification level at decision /
Axis or lineage bridge recorded / Decision date
```

The file begins with the standard artifact manifest header per `CODEX_PROTOCOL.md`.

## Ownership Map

| Stage | Owner skill | Responsibility |
|---|---|---|
| Initialization | `stat-paper-plan` Step 5.7 (NEW) | Create the file with manifest header and an empty table. Populate first rows from `PRIOR_WORK_MATRIX.md` Step 5.5. |
| Drafting body | `stat-paper-write` Step 2.5 (after building `CLAIM_SUPPORT_MAP`) | For every claim in `CLAIM_SUPPORT_MAP` that resolves to a cited paper, add a row. |
| Polishing | `stat-polishing` Step 11 (Codex MCP dialogue) and Step 16 (citation hygiene) | When the Codex dialogue or the citation hygiene audit identifies new or changed citations, add or update rows. |
| Mock review | `stat-mock-review` Step 3 (positioning audit) | Read-only; verifies that every fatal-or-major concern's cited theorem appears in the lock manifest at `independently_checked` or higher. |
| Proof repair | `proof-repair` Step 4 (literature search) and Step 5C (per-repair Codex stress-test) | When a repair file cites a new paper or upgrades a citation's purpose, add or update the row. |
| Proof writing | `proof-writer` Cited Results Audit | For every row in `## Cited Results Audit`, ensure the corresponding lock-manifest row exists at the matching verification level. |
| Re-audit | `/proofcheck --post-repair` Step P3.7 (NEW) | Read-only; verifies the lock manifest is consistent with the cache state and the patched paper's citations. |
| Final sign-off | author (manual) | Reviews every load-bearing row; promotes to `human_signed` where required by `citation-purpose-protocol.md`'s verification gate; signs the file. |

## Initialization (stat-paper-plan Step 5.7, NEW)

After Step 5.5 (build `PRIOR_WORK_MATRIX.md`) and Step 5.6 (build `TECHNICAL_RISK_REGISTER.md`), insert a new Step 5.7:

**Step 5.7: Initialize `cited_results.lock.md`**

Create `papers/<project-name>/cited_results.lock.md` with:

```markdown
---
artifact: project_citation_lock
project: <project-name>
generated: <YYYY-MM-DD>
generator: stat-paper-plan v1.x.x Step 5.7
---

# Citation Lock Manifest

This file records the verification state and citation purpose at the moment each citation decision was made. It prevents retroactive contamination if the global literature cache is later edited.

| Citation site | Reference | Citation purpose | Role in literature | Role relative to current paper | Source version at decision | Entry hash at decision | Verification level at decision | Axis or lineage bridge recorded | Decision date |
|---|---|---|---|---|---|---|---|---|---|
```

Populate the table with one row per `PRIOR_WORK_MATRIX.md` entry whose `Read In Full` resolves to a cache entry. For each row:

1. **Citation site**: typically `PRIOR_WORK_MATRIX.md#row-<N>` for the initial population.
2. **Reference**: `paper:<bibkey>#<result_id>` per the cache schema.
3. **Citation purpose**: usually `lineage_positioning` for the initial PRIOR_WORK matrix; benchmarks and load-bearing citations come later in stat-paper-write.
4. **Role in literature** / **Role relative to current paper**: read from the cache entry's `theoretical_lineage` block (or determine from the matrix).
5. **Source version at decision** / **Entry hash at decision**: read from the cache entry.
6. **Verification level at decision**: read from the cache entry's `verification_status`.
7. **Axis or lineage bridge recorded**: for `lineage_positioning` rows, record `primary_line: <line>`; for `benchmark_claim` and `comparative`, fill later.
8. **Decision date**: today.

This file becomes the read-only canonical record. Subsequent skills append rows; they do not edit existing rows except through documented re-binding.

## Update Discipline (downstream skills)

Each owner skill that updates the lock manifest follows the same discipline:

1. **Read before write**. Read the current state of `cited_results.lock.md` to know which rows already exist.
2. **Append new rows, do not edit old rows.** Old rows are historical record. If a citation is upgraded (e.g., from `lineage_positioning` to `benchmark_claim` because the paper later moved to a comparative claim in the contribution paragraph), add a new row with the new purpose; the old row remains.
3. **Match the cache entry's verification state at write time.** If the cache entry is `source_checked` when the row is created, the row records `source_checked` even if the entry is later upgraded.
4. **Record the bridge explicitly.** For `partial`, `same_family`, `benchmark_claim` auxiliary axes, and `lineage_positioning` cross-family use, the `Axis or lineage bridge recorded` column must name the specific bridge artifact (Lemma A.4, PATCHES.md Patch-7, etc.) or describe the family relationship.
5. **One row per citation site, not per reference.** The same paper cited at two sites generates two rows with different purposes; the same paper cited at one site generates one row.

## Consistency Validation

`/proofcheck --post-repair` (new Step P3.7) and `/stat-mock-review` (Step 3 read) perform read-only validation:

- Every row's `Reference` resolves to an existing cache entry.
- Every row's `Entry hash at decision` matches the cache entry's current hash, OR the row is flagged STALE in the validation report.
- Every load-bearing row (purpose in `{load_bearing, benchmark_claim, comparative}`) is at `independently_checked` or higher; if not, the row is flagged GAP.
- Every `axis or lineage bridge recorded` column for `partial` rows points to an existing artifact.

Validation findings are written to `papers/<project>/audit/lock_manifest_validation.md`. The findings are warnings, not blockers, except for the verification floor gap on load-bearing rows: those block submission until upgraded or downgraded.

## Conflict Resolution

Multiple skills may attempt to add rows referencing the same citation site (e.g., both `stat-paper-write` Step 2.5 and `proof-repair` Step 4 want to add a row for `REPAIR_PLAN.md#I-03`). The conflict resolution is:

1. **First-writer-wins for the citation site.** Subsequent writers check whether the citation site already has a row.
2. **If the existing row is at a lower verification level**, the subsequent writer adds a new row (does not modify the old) with the upgraded level. The previous row is preserved as historical record.
3. **If the existing row is at a higher or equal level**, the subsequent writer logs a no-op note in the manifest comments and proceeds.
4. **If the citation purpose differs**, both rows coexist. This is the documented mechanism for the same paper supporting different purposes at the same site (rare but possible during a transition).

## Why No Separate `/lock-citations` Skill

Per Codex round 3 V5 ("do not bolt further cross-cutting protocols before extracting more machinery"): the lock-citations responsibility is small enough to live in the existing skill workflows. A separate skill would add invocation overhead without functional benefit. The protocol above is the minimal viable formalization.

If the responsibility grows (e.g., automated reverse-index generation across many projects, batch validation across the cache), a `/lock-citations` skill becomes worth creating. For the MVP, the in-skill update discipline is sufficient.

## Cross-Reference

- `citation-purpose-protocol.md` (the canonical `cited_results.lock.md` schema)
- `cache-verification-states.md` (the verification states the lock records)
- `literature-cache-protocol.md` (router)
- `lit-cache-verify-protocol.md` (the workflow that promotes cache entries; lock manifests record the verification level at decision time)
- `proof-closure-machinery.md` (Repair Closure Matrix and Change Logs reference lock-manifest entries for citations)

## Honest Limits

- The lock manifest is documentation, not enforcement. A skill that fails to update the lock when adding a citation introduces silent drift; the validation step in `--post-repair` and mock-review catches this only post-hoc.
- The "first-writer-wins" rule depends on skills checking the manifest before writing. Skills that batch-write without reading first will create duplicate rows; the validation step flags duplicates.
- The schema records `Verification level at decision`, which is what the project's audit history depends on. If the cache entry is later demoted (e.g., re-extraction failed source reconciliation), the lock manifest still records the old level. The downstream re-audit reports this as a contamination warning; the user decides whether to re-verify the project's decisions against the demoted cache.
