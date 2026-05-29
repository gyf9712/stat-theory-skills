---
artifact: shared_reference
scope: literature_cache_router
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills literature-cache router, Codex round 2 threadId 019e70c3-1844-7181-b6a1-0b4041c657df
---

# Literature Cache Protocol (Router)

Durable, reusable cache of read-in-full literature evidence shared across `stat-theory-skills` (proofcheck, proof-repair, theory-sharpen, theory-simulation, theory-design, proof-writer) and `stat-writing-skills` (stat-paper-plan, stat-paper-write, stat-polishing, stat-mock-review). The cache turns the dominant recurring token cost in the pipeline — reading published statistics papers — into a verifiable, reusable artifact, while preserving the correctness guarantees the skills exist to enforce.

This file is a router. The full protocol lives in three companion files; load only what your use case needs (see Minimum Load Map below).

## Minimum Load Map

Each skill / use case loads only the companion files it actually needs. The router (this file) is always loaded as a small entry point.

| Use case | Load this router | + `citation-purpose-protocol.md` | + `applicability-axes.md` | + `cache-verification-states.md` | + `lit-cache-verify-protocol.md` | + `cited-results-lock-protocol.md` |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Cache lookup (hit / miss check; read INDEX) | ✔ | | | | | |
| New entry creation (skill writes proposal to inbox) | ✔ | | ✔ (declare applicability) | ✔ (write integrity fields) | | ✔ (lock manifest update) |
| High-stakes citation (positioning / repair / theorem step / claim audit) | ✔ | ✔ | ✔ (run axis check) | ✔ (check verification floor) | | ✔ (lock manifest update) |
| Lineage / positioning prose-only citation | ✔ | ✔ (purposes + roles) | | ✔ (state floor only) | | ✔ |
| Comparative / benchmark claim | ✔ | ✔ | ✔ | ✔ | | ✔ |
| Technique inheritance / standard tool citation | ✔ | ✔ (purposes + identification) | | ✔ (state floor) | | ✔ |
| Background motivation citation | ✔ | ✔ (default purpose handling) | | ✔ (state floor) | | ✔ |
| Cache verify (promote inbox entry to `source_checked`) | ✔ | | ✔ (verify applicability contract) | ✔ (full verification workflow) | ✔ (the MVP workflow) | |
| Cache audit (`independently_checked` upgrade via Codex MCP) | ✔ | ✔ (consistency check) | ✔ (consistency check) | ✔ (full upgrade workflow) | (deferred follow-up) | |
| Lock manifest initialization (project start) | ✔ | ✔ (schema) | | ✔ (state floor) | | ✔ (ownership protocol) |
| Lock manifest consistency check (e.g. `--post-repair` Step P3.7) | ✔ | | | ✔ | | ✔ |
| Staleness / version conflict handling (F1) | ✔ | | | ✔ | | |
| Hallucination detection (F3) | ✔ | | | ✔ | | |

The router carries the small amount of cross-cutting structure (locations, syntax, schema header). The companion files carry the per-use case detail.

## Core Principle

**The cache is a fallible evidence index, not a source of truth.**

A cache entry says what one prior reading found in the source on one date. It does not relieve the citing skill of the obligation to check that the cited result actually applies to the current problem.

Three honest limits of any LLM-built cache:

1. The first writer may have misread or hallucinated. Source reconciliation (fetch + locate + hash compare) is the only reliable detection.
2. The cache cannot certify the source itself is correct; it can only certify the cache faithfully records what the source said.
3. Applicability of a cached result to a current problem is not automatic. The cache stores the applicability contract; the citing skill checks compatibility.

## Architecture

### Locations

- **Global cache root**: `~/.claude/literature_cache/` — shared across all projects and both skill families.
- **Inbox**: `~/.claude/literature_cache/inbox/` — skill-written proposals; not yet canonical.
- **Per-paper containers**: `~/.claude/literature_cache/papers/<bibkey>.md` — one container per paper; per-result entries live inside as sections.
- **Domain shards** (optional, enabled above threshold): `~/.claude/literature_cache/domains/INDEX_<domain>.md`.
- **Project-side pin**: `papers/<project-name>/cited_results.lock.md` — project's snapshot of what evidence its decisions rest on.

### Directory layout

```
~/.claude/literature_cache/
├── INDEX.md                                    # top-level scannable index
├── inbox/
│   ├── arxiv_2401.12345.draft.md               # skill-written proposals
│   └── ...
├── domains/                                    # enabled when single INDEX exceeds scan budget
│   ├── INDEX_highdim.md
│   ├── INDEX_empirical_process.md
│   └── ...
└── papers/
    ├── bickel_levina_2008__regularized_covariance.md
    └── ...
```

### Reference syntax

Unified syntax with type-specific validation rules:

```
paper:<bibkey>#<result_id>             external literature; requires source/version/hash metadata
audit:<issue_id>                       internal audit issue; requires project commit hash
repair:<patch_id>                      internal repair patch; requires REPAIR_PLAN row
claim:<cs_id>                          internal claim from CLAIM_SUPPORT_MAP; requires CLAIM_SUPPORT_MAP row
```

The syntax is uniform; the metadata each form carries is type-specific. A `paper:` reference is invalid without `source_url`, `source_version`, and at least `source_checked` verification status. An `audit:` reference is invalid without a project commit hash.

## Per-Result Entry Header (the unit of caching)

The unit of caching is the **result**, not the paper. One paper container holds multiple result entries; each entry has independent verification status, source integrity fields, and applicability contract. The same paper may prove Theorem 1 under one set of conditions and Theorem 2 under another; these are independent entries.

Each per-result entry begins with:

```yaml
---
artifact: literature_cache_entry
result_id: bickel_levina_2008/thm_1              # canonical: <bibkey>/<stable_label>
paper_container: papers/bickel_levina_2008.md
source_url: ...
source_version: ...
doi: ...
publication: ...
retrieval_date: ...
source_hash: sha256:...
quote_blocks: [...]                              # see cache-verification-states.md
verification_status: source_checked              # see cache-verification-states.md (4 states)
verification_log: [...]
applicability_contract: {...}                    # see applicability-axes.md (8 axes)
theoretical_lineage: {...}                       # see citation-purpose-protocol.md
---
```

The body sections (verbatim quote, result statement, assumption set, proof technique, anti-miscitation note, caveats, suitability) are defined in `cache-verification-states.md` for the integrity fields and `citation-purpose-protocol.md` for the lineage and purpose fields.

## Read Protocol (high level)

The cache only pays off when reads are result-scoped. Loading a 30 KB paper container file because a skill wants Theorem 1 of that paper is waste.

Three-step read:

1. **INDEX scan**. Skill reads `INDEX.md` (or relevant domain shard) — a few KB total. Determines which papers have cache entries that might match the current query.
2. **Container header scan**. For each candidate paper, the skill reads only the YAML manifest of `papers/<bibkey>.md`. Determines which result entries the container has and which axes look promising.
3. **Targeted result load**. The skill loads only the relevant per-result entry (one section of the container). Uses `Read` with `offset` and `limit` to grab the result entry's lines.

If the INDEX scan finds no candidates, the skill proceeds to WebFetch / arXiv / Semantic Scholar as usual.

## Write Protocol (high level)

Arbitrary skills do NOT write canonical cache entries. Skills write **proposals** to the inbox; only `/lit-cache verify` promotes proposals to canonical.

- New paper: `inbox/<bibkey>.draft.md`. Promotion creates `papers/<bibkey>.md`.
- Update to existing entry: `inbox/<bibkey>.update.md`. Promotion edits the canonical file and logs the change.

The skill can use its own just-extracted content for the current call (the writing skill is allowed to use its own `unverified_extract` because it just read it). Downstream skills require at least `source_checked`.

Full workflow lives in `cache-verification-states.md`.

## Failure Mode Workflows (summary)

| ID | Trigger | Where the full workflow lives |
|---|---|---|
| F1 | Source version changed at decision time | `cache-verification-states.md` |
| F2 | Verification gap at decision time (entry below required floor) | `cache-verification-states.md` |
| F3 | Detected hallucinated entry (source reconciliation fails) | `cache-verification-states.md` |

Default behavior on all three: abort the use; emit a structured request to the user; record the resolution in the project's `cited_results.lock.md`. No silent fall-through.

## Skill Integration Points

Each skill that touches literature gains a "consult cache first" step at its literature step. The artifact templates gain a "cache reference" column for citations. The router + Minimum Load Map determines which companion files each skill loads.

| Skill | Step | Loads | Notes |
|---|---|---|---|
| `proof-repair` Step 4 (Literature Search) | cache-consult before WebFetch | router + applicability-axes + cache-verification-states (lookup + applicability check) | High-stakes; L4 Add-Assumption requires `independently_checked` |
| `proof-repair` Step 5C (per-repair fresh thread) | cite cache references in Codex prompt | router + citation-purpose-protocol | Manifest carries cache refs by ID |
| `proofcheck` Pass 4 (Codex cross-review) | cache-consult for prior literature | router + cache-verification-states | xhigh reasoning per CODEX_PROTOCOL |
| `proofcheck` `--post-repair` | verify cited results in patched proof | router + cache-verification-states | Staleness check against lock manifest |
| `proof-writer` Cited Results Audit | every cited result resolves to cache entry | router + citation-purpose-protocol + applicability-axes + cache-verification-states | Full protocol; this is the heaviest user |
| `theory-sharpen` Step 4 (Literature anchoring) | cache-consult; 22 pathways become cache-aware | router + applicability-axes | Lineage citations dominate here |
| `theory-design` Step 0.5 (Mandatory Literature Anchoring) | cache-consult before search | router + citation-purpose-protocol + applicability-axes | 4 parallel agents check cache |
| `stat-positioning-and-claims.md` | positioning audit consumes cache | router + citation-purpose-protocol | `independently_checked` for positioning claims |
| `stat-paper-plan` PRIOR_WORK_MATRIX `Read In Full` column | cache reference at `source_checked` or higher | router + cache-verification-states | Lock manifest tracks this |
| `stat-mock-review` fatal-or-major citation | cache reference required | router + citation-purpose-protocol + applicability-axes + cache-verification-states | Gates at `independently_checked` |

## Project-Side Pin Manifest

Each project records its dependence on cached results in `papers/<project-name>/cited_results.lock.md`. The full schema (with `citation_purpose`, `role_in_literature`, `role_relative_to_current_paper`, `verification_level_at_decision`, `axis_or_lineage_bridge` columns) is in `citation-purpose-protocol.md`.

The lock manifest prevents retroactive contamination: if the global cache is edited after the project's decisions were made, the project's audit history is preserved. At `/proofcheck --post-repair` time, discrepancies between the lock manifest and the current cache are reported as audit findings.

## Versioning

Cache entries record `generator` (skill + version). Schema migrations are handled in `cache-verification-states.md`. The protocol version is recorded in the top-level `INDEX.md` manifest.

## Honest Limits

The protocol does NOT promise:

- **Correctness of cached results**. The cache faithfully records what the source said; it does not certify the source itself is correct.
- **Automatic applicability**. The 8-axis contract is the structural check; final applicability remains a human judgment for non-trivial cases.
- **Lineage certainty**. `theoretical_lineage.primary_line` is a working classification, not a canonical taxonomy. Disagreements are documented in `verification_log`, not silently overwritten.
- **Hallucination detection without source access**. If the source URL is dead and no local copy exists, the entry cannot be verified beyond metadata consistency.
- **Convergence in disputes**. When `source_checked` and `independently_checked` reviewers disagree on the result statement, applicability, or lineage, the human resolves; the cache records both positions until resolution.

## Cross-Reference

- `citation-purpose-protocol.md` — 7 citation purposes, 13 methodological roles, gate matrix, `cited_results.lock.md` schema
- `applicability-axes.md` — 8 axes, namespaced family registry, 5 compatibility verdicts
- `cache-verification-states.md` — 4 verification states, source integrity, F1/F2/F3 workflows, inbox/queue, lock manifest mechanics
- `CODEX_PROTOCOL.md` (repo root) — dialogue protocol, reasoning ladder, per-repair fresh thread, artifact manifest convention
- `stat-shared-references/stat-positioning-and-claims.md` — positioning audit consumes cache entries
- `stat-shared-references/stat-codex-dialogue.md` — mirrors the dialogue discipline for stat-writing-skills
- `proof-strategy.md` — Trap #6 citation identity drift, Trap #7 applicability drift

## Codex Dialogue Log

This protocol was designed and refined via Codex MCP review.

- threadId: `019e70c3-1844-7181-b6a1-0b4041c657df`
- Round 1 (10 design decisions + 3 failure modes + 2 honest questions): 9 MODIFY + 1 SKIP; Q2 surfaced assumption drift as the dominant failure mode, motivating the 8-axis applicability contract.
- Round 2 (lineage refinements + protocol length + meta architecture): 6 additional MODIFY (default purpose change, 3 new citation purposes, role-field split, namespaced families, protocol split, SKILL.md compactification). All accepted. Codex confirmed first-person attention dilution at >50K-token instruction loads; threshold for SKILL.md is 500-700 sweet, 900-1200 paying attention tax.
- Cumulative outcome: this router plus three companions (citation-purpose-protocol.md, applicability-axes.md, cache-verification-states.md) replace the prior monolithic protocol. Skills load only the companions their use case needs (see Minimum Load Map).
