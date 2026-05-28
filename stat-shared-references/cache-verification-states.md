---
artifact: shared_reference
scope: cache_verification_states
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills cache verification protocol, Codex round 2 threadId 019e70c3-1844-7181-b6a1-0b4041c657df
---

# Cache Verification States, Source Integrity, and Failure-Mode Workflows

Companion to `literature-cache-protocol.md` (router). This file defines the four verification states an entry can hold, the source-integrity mechanisms that make hallucination detection possible, the upgrade workflows that move entries between states, and the F1 / F2 / F3 failure-mode procedures.

## When to Read

- When creating, updating, verifying, or auditing a cache entry.
- When the staleness check fails (source version changed).
- When the verification-floor check fails (entry at a level below what the decision site requires).
- When the source reconciliation fails (hallucination suspicion).
- When constructing or updating the project-side `cited_results.lock.md` manifest.

Not needed for cache lookup or pure read of an already-verified entry — those are described in the router.

## The Four Verification States

A cache entry transitions through up to four evidence states. Names are evidence-based, not actor-based: the same actor can produce entries at different evidence states depending on what they actually did.

| State | What it means | What was checked |
|---|---|---|
| `unverified_extract` | An LLM read the source (or claimed to) and wrote an extract. No source reconciliation. | Nothing checked; extract is a working draft |
| `source_checked` | Source was fetched and the verbatim quote hashes were verified against the source bytes. The extract matches what the source says. | Quote hashes match source; locators resolve; result statement matches verbatim |
| `independently_checked` | A second model or process (typically Codex MCP at xhigh) verified the extract against the source. | All `source_checked` requirements plus independent reading agreeing on result statement, assumption set, and applicability contract |
| `human_signed` | A human (the project author or a designated reviewer) signed off. Inscribed in the verification log. | All `independently_checked` requirements plus a recorded human attestation |

### Transition rules

- `unverified_extract → source_checked`: requires fetching the source (or the same locally-stored source if hashes match), locating each quote block, recomputing each quote's hash, and comparing. Only `/lit-cache verify` performs this transition.
- `source_checked → independently_checked`: requires an independent reader (typically a Codex MCP call at `model_reasoning_effort: xhigh`) that produces its own extract and applicability contract, then a reconciliation step against the cache entry. Disagreements demote back to `source_checked` until resolved.
- `independently_checked → human_signed`: requires a human attestation logged in the entry's `verification_log` with date, actor name, and a one-sentence rationale.
- Any state → `unverified_extract`: triggered automatically if the source version changes (staleness) or any quote hash mismatches on re-verification.

State demotion is recorded in the entry's `verification_log` with the date, actor, action, and evidence. Demotion never silently overwrites the prior state's verification log entries.

## Per-Result Entry Schema (with verification fields)

The full cache entry schema appears in the router. The verification-relevant fields:

```yaml
verification_status: source_checked                # one of the four states above
verification_log:
  - date: 2026-01-15
    actor: proof-repair v1.7.0
    action: created
    evidence: extract written by Claude on first fetch
  - date: 2026-01-20
    actor: /lit-cache verify
    action: source_check
    evidence: fetched source, located quotes, hashes matched
source_url: https://arxiv.org/abs/0803.4067v2
source_version: arxiv:0803.4067v2
retrieval_date: 2026-01-15
source_hash: sha256:abc123...                      # SHA-256 of fetched source bytes
quote_blocks:
  - id: q1
    locator: page 5, lines 12-16, theorem environment
    text_hash: sha256:def456...                    # SHA-256 of verbatim text
  - id: q2
    locator: page 7, equation (3.4)
    text_hash: sha256:ghi789...
```

## Verification Gate at Decision Time

The minimum verification level required to use an entry depends on the citation site and the citation purpose. The full matrix lives in `citation-purpose-protocol.md` under "Verification Gate by Site × Purpose". The single-state gate summary:

| Site type | Minimum state required |
|---|---|
| Background prose mention | `source_checked` |
| Tool invocation in a proof (technique inheritance / standard tool) | `source_checked` + identified device/tool |
| Repair citation (Citation-Fix / Strengthen-Proof) | `independently_checked` |
| Positioning claim against the cited paper | `independently_checked` |
| Weakened-Claim defense / Assumption-Extension defense | `independently_checked` |
| Repair priority L4 (Add-Assumption justified by cited prior work) | `independently_checked` |
| Mock-review fatal-or-major concern | `independently_checked` |
| Theorem invoking the cited result as a step | `independently_checked` (`human_signed` on main chain) |
| Author sign-off before submission | `human_signed` for every load-bearing reference; `independently_checked` for lineage / comparative / technique / tool; `source_checked` for background |

## Verification Request: No Silent Upgrade

If a decision site requires a state higher than the entry currently holds, the citing skill emits a structured verification request to the user. **No silent upgrade.**

```markdown
[lit-cache] Entry `paper:bickel_levina_2008#thm_1` is at `source_checked`.
This citation site (`REPAIR_PLAN.md#I-03`, repair priority L4) requires `independently_checked`.

Estimated upgrade cost: 1 Codex MCP call at xhigh (~3-5K input + 2K output tokens),
plus possible source re-fetch (~10-15K tokens) if source hash is stale.

Awaiting user decision: upgrade now / defer / cite at informational level only.
```

This anti-silent-cost principle matches the per-repair fresh thread protocol in `CODEX_PROTOCOL.md`: a skill that needs a Codex MCP call surfaces the cost; the user decides.

## Source Integrity

Every entry records the following so source reconciliation is mechanically verifiable:

| Field | Meaning |
|---|---|
| `source_url` | The exact URL (or DOI resolution target) that was fetched |
| `source_version` | The version snapshot. For arXiv: `arxiv:<id>v<n>`. For published: DOI + published date. For Semantic Scholar / Google Scholar: include the API call's identifier. |
| `retrieval_date` | When the source bytes were actually fetched |
| `source_hash` | SHA-256 of the fetched PDF / HTML / source document bytes |
| `quote_blocks[*].locator` | Page + line (or section + paragraph) of the quote within the source |
| `quote_blocks[*].text_hash` | SHA-256 of the verbatim quote text |

### Why DOI / published is not immutable

DOI and published versions are not fully immutable: errata, retractions, online-first replacements, supplementary-material updates, and silent corrections happen. The `source_hash` records what was actually read; if a future check finds the source has changed, the entry is demoted to `unverified_extract` regardless of `verification_status`.

### Hash algorithms

- `source_hash`: SHA-256 of the fetched bytes. For PDFs, the raw PDF; for HTML, the rendered text after stripping ads and navigation; for arXiv source tarballs, the tarball's SHA-256.
- `text_hash`: SHA-256 of the UTF-8 bytes of the verbatim quote text, after Unicode-normalizing to NFC and stripping leading/trailing whitespace.

The choice of SHA-256 is standard cryptographic practice and is required for collision resistance over the cache's lifetime.

## Staleness Detection (F1)

The skill loading a cache entry runs the staleness check:

1. Compare `source_version` field with the current canonical version (arXiv API for arXiv IDs, DOI resolution metadata for DOIs).
2. If the version has changed, mark the entry STALE.
3. STALE entries cannot be used at decision sites requiring `source_checked` or higher until re-verification.

### F1 workflow: source version changed at decision time

The citing skill is about to use `paper:<bibkey>#<result_id>` for a high-stakes decision. Cache says `source_version: arxiv:...v2`, current arXiv lookup says v3.

1. The skill aborts the use.
2. The skill triggers a re-fetch of v3 and writes an `inbox/<bibkey>.update.md` proposal.
3. The user invokes `/lit-cache verify`, which promotes the update only if the hashes and applicability contract are consistent (or records the deltas if they are not).
4. If the user wants to keep using v2 explicitly, they pin the old version in the project: `cited_results.lock.md` gets a row with `source_version: arxiv:...v2 (pinned old)` and the citing decision is marked `based on obsolete version`. The mock-review and the AE-style risk assessment will flag this.

There is no silent fall-through; either the new version is verified or the old version is explicitly pinned with documented rationale.

## Verification Gap (F2)

### F2 workflow: verification gap at decision time

The citing skill needs `independently_checked` but the entry is `source_checked`.

1. The skill emits the structured verification request (template above).
2. No automatic upgrade. The user decides one of:
   - Upgrade now (skill runs Codex MCP at xhigh and writes the upgrade proposal to the inbox).
   - Defer (citation site is left as `pending verification`; the artifact's `convergence` field cannot be marked complete until resolved).
   - Use at informational level only (citing artifact records the entry as `informational, not load-bearing`).

The decision is recorded in the project's `cited_results.lock.md` under the row's `Verification level at decision` column.

## Hallucination Defense (F3)

The only reliable defense against a fabricated cache entry is source reconciliation. Metadata alone cannot detect hallucinated entries.

### Source reconciliation procedure

`/lit-cache verify` and `/lit-cache audit` run source reconciliation:

1. Fetch the source URL.
2. Compute the source hash and compare to the stored `source_hash`. If they differ (and the difference is not a known minor edit), the entry is demoted.
3. For each quote block, locate the quoted text in the fetched source using the recorded `locator` and recompute the `text_hash`. If a hash does not match, the entry is demoted.
4. If the source cannot be fetched (paywall, dead URL, no available copy), the entry stays at its current verification state but is flagged `source_inaccessible: true` and downstream high-stakes use is blocked.

### F3 workflow: detected hallucinated entry

`/lit-cache verify` finds that a quote block's text cannot be located in the fetched source, or that the result statement does not appear at the claimed location.

1. The entry's `verification_status` is demoted to `unverified_extract`.
2. A `verification_log` entry records the detection: `date / actor: /lit-cache verify / action: detect_hallucination / evidence: quote q1 not found at locator (page 5 lines 12-16)`.
3. The cache entry is moved from `papers/<bibkey>.md` back to `inbox/<bibkey>.draft.md` for re-extraction.
4. Every project that pinned the affected `result_id` in its `cited_results.lock.md` receives an audit-time warning at the next `/proofcheck --post-repair` or `/stat-mock-review` invocation.

The warning is not auto-actionable; the user decides whether the affected citations survive once the cache entry is correctly re-extracted.

## Write Protocol: Inbox/Queue, Then Promote

Arbitrary skills do not write canonical cache entries directly. The protocol:

1. **Skill writes a proposal** to `~/.claude/literature_cache/inbox/<bibkey>.draft.md` (or `inbox/<bibkey>.update.md` if proposing a change to an existing canonical entry).
2. Proposal MUST include manifest header, `verification_status: unverified_extract`, source URL and source hash from the actual fetch, applicability contract draft, and a single `verification_log` entry naming the writing skill.
3. **`/lit-cache verify` promotes**. A separate verification step reads the inbox, fetches the source, locates each quote block, recomputes hashes, and either promotes to `papers/<bibkey>.md` at `source_checked` or rejects with reasons.
4. **`/lit-cache audit` runs `independently_checked` upgrades** on demand. A Codex MCP call at xhigh independently extracts; reconciliation against the canonical entry produces either `independently_checked` promotion or a documented disagreement (which the user resolves).
5. **Human sign-off** is recorded by the user editing the `verification_log` and changing the `verification_status` to `human_signed`. No skill does this automatically.

This separates two failure surfaces: writing skills are allowed to be wrong (they propose drafts), but the canonical cache is integrity-preserved.

### Update vs new entry

- Proposing a brand-new paper: file is `inbox/<bibkey>.draft.md`. Promotion creates `papers/<bibkey>.md`.
- Proposing an update to an existing entry (new quote block, refined applicability contract, new result section): file is `inbox/<bibkey>.update.md` referencing the existing entry by `result_id`. Promotion edits the canonical file and appends a `verification_log` entry recording the change.

Concurrent proposals on the same paper are serialized by `/lit-cache verify`: the second proposal sees the first's promotion and either supersedes or extends.

## Project-Side Pin Manifest

Each project that cites cached results records its dependence in `papers/<project-name>/cited_results.lock.md`. The schema is defined in `citation-purpose-protocol.md` (the columns include `citation_purpose`, `role_in_literature`, `role_relative_to_current_paper`, `source_version_at_decision`, `entry_hash_at_decision`, `verification_level_at_decision`, `axis_or_lineage_bridge`).

This file is the project's snapshot of what evidence its decisions rest on. If the global cache is later edited (entry deleted, demoted, or replaced), the project's audit history is not retroactively altered. At `/proofcheck --post-repair` time, the lock manifest is compared to the current cache state; discrepancies are reported as audit findings.

## Reverse Index Generation

The cache does not maintain `referenced_by` fields inside entries (these would rot under parallel writers). Instead, at audit time, a reverse index is generated by scanning all known projects' `cited_results.lock.md` files:

```bash
# Pseudo-procedure
for project_lock in $(find ~/projects -name 'cited_results.lock.md'); do
  # extract referenced result_ids
done | sort | uniq -c
```

This sidesteps the rot problem. The reverse index is computed when needed (e.g., before promoting a cache update, the verifier checks which projects might be affected), not stored.

## Sharding Policy

A single `INDEX.md` is the default. Sharding by domain kicks in when the single index exceeds the context budget a skill can scan cheaply (rule of thumb: above the cache having ~150 papers). The trigger is context-load, not file count.

When sharding:

- Top-level `INDEX.md` contains paper IDs, bibkeys, primary domain tags, and verification statuses. One row per paper. Stays tiny — under 10 KB even at 500 papers.
- Each `domains/INDEX_<domain>.md` carries fuller summaries (one-line description, primary results, applicability contract highlights) for papers in that domain.
- A paper can appear in multiple domain indexes if it has cross-domain results.

Domain examples align with the family-registry domains in `applicability-axes.md`.

When to shard is judged at `/lit-cache audit` time; the verifier can recommend sharding when scan cost becomes prohibitive.

## Versioning of the Protocol Itself

The protocol can change. Cache entries record `generator` (the skill + version that produced them). If the schema changes:

- New optional fields default to "not specified" and are filled at next `/lit-cache verify`.
- New required fields block the entry's use at high-stakes levels until filled.
- Existing entries' verification status is preserved through schema migrations unless the migration explicitly demotes.

The protocol version is recorded in the top-level `INDEX.md` manifest. Entries' `generator` field documents the protocol version under which they were created.

## Honest Limits

- **Hash collisions are vanishingly unlikely but possible.** SHA-256 is collision-resistant under cryptographic assumptions; the protocol relies on those.
- **Source reconciliation requires source access.** Paywalled or rate-limited sources, dead URLs, or institution-only access points break the reconciliation procedure; entries from those sources can be flagged `source_inaccessible` but not freshly verified.
- **`/lit-cache verify` and `/lit-cache audit` are skill-driven, not binaries.** They are workflows the user invokes through the assistant, requiring Codex MCP for `independently_checked` upgrades. They are not auto-running daemons.

## Cross-Reference

- `literature-cache-protocol.md` (router with Minimum Load Map)
- `citation-purpose-protocol.md` (purposes, gate matrix, lock-file schema)
- `applicability-axes.md` (the 8 axes and family registry)
- `CODEX_PROTOCOL.md` (`independently_checked` upgrades use Codex MCP per the reasoning effort ladder and per-repair fresh thread protocol)
