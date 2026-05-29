---
artifact: shared_reference
scope: lit_cache_verify_protocol
source_files: []
theorem_ids: []
assumption_ids: []
issue_ids: []
commit: pending
generated: 2026-05-28
generator: stat-theory-skills /lit-cache verify MVP protocol, addresses Codex round 3 V7 REQUIRES FIX (threadId 019e7112-283e-74b1-97e5-6344592cd820)
---

# `/lit-cache verify` MVP Protocol

Workflow specification for promoting inbox proposals to canonical `source_checked` cache entries. This is the MVP version: it handles only the `unverified_extract → source_checked` transition. The `source_checked → independently_checked` upgrade (which requires a Codex MCP call) and the `independently_checked → human_signed` transition (which requires explicit human attestation) are deferred to follow-up.

This file is the missing enforcement point Codex round 3 V7 flagged: without `/lit-cache verify`, entries stay at `unverified_extract` and the strict verification gates in `cache-verification-states.md` block all downstream use.

## When to Read

- Whenever inbox entries have accumulated and downstream skills need `source_checked` or higher to proceed.
- Before any high-stakes citation (positioning claim / repair file / theorem invocation) if the cache entry is at `unverified_extract`.
- At the end of each working session as a maintenance step (recommended).
- When `/proofcheck --post-repair` reports a `source_inaccessible` or `STALE` entry that blocks convergence.

## Invocation

The MVP is **not a separate skill binary**. It is a workflow the user runs through the assistant, leveraging existing tools (`Read`, `WebFetch`, `Bash`) plus this protocol.

User invocation forms:

```
/lit-cache verify                          # process all entries in inbox/
/lit-cache verify <bibkey>                 # process a single inbox entry
/lit-cache verify --dry-run                # report what would happen; make no writes
/lit-cache verify --since <date>           # only entries added after <date>
```

The assistant follows the workflow in the next section.

## Workflow

### Step 1: List inbox entries

```bash
ls ~/.claude/literature_cache/inbox/*.draft.md  ~/.claude/literature_cache/inbox/*.update.md 2>/dev/null
```

For each entry, read the manifest header to identify `paper_id`, `source_url`, `source_version`, `source_hash`, `quote_blocks`, and `applicability_contract`.

### Step 2: For each inbox entry, fetch the source

Use `WebFetch` against the recorded `source_url`. If the URL is a DOI, resolve it to the publisher's canonical PDF or HTML. If the URL is an arXiv ID, prefer the v-tagged version that matches `source_version`.

If the fetch fails (paywall, dead URL, network error), record the failure and skip to Step 6 for this entry. The entry stays in inbox flagged `source_inaccessible: true`.

### Step 3: Compute the fetched source's hash and compare

Compute the SHA-256 of the fetched source bytes:

```bash
sha256sum <fetched_file>
```

Compare to the inbox entry's `source_hash` field.

- If the hashes match: the source matches what the writing skill claimed to read. Proceed to Step 4.
- If the hashes differ but `source_version` in the inbox already records the new version: the inbox entry has a stale `source_hash` field. Update it; proceed to Step 4.
- If the hashes differ AND the `source_version` field has not been updated: the writing skill recorded a stale hash. Update both `source_hash` and `source_version`; note the discrepancy in the `verification_log`. Proceed to Step 4.

### Step 4: For each quote block, locate and hash

For each entry in `quote_blocks`:

1. Read the fetched source at the recorded `locator` (page + lines for PDF, section + anchor for HTML).
2. Extract the verbatim text at that locator.
3. Normalize the text (Unicode NFC; strip leading/trailing whitespace).
4. Compute SHA-256 of the normalized text.
5. Compare to the recorded `text_hash`.

- If all quote hashes match: the inbox entry is consistent with the source. Proceed to Step 5.
- If any quote hash mismatches: the writing skill misextracted or hallucinated this quote. Demote the entry: keep it in inbox at `unverified_extract`, add a `verification_log` entry documenting the specific mismatch (`quote q1 expected sha256:abc... but source at locator yields sha256:def...`), and proceed to Step 6 for this entry. The user must re-fetch and re-extract; the entry cannot be promoted.

### Step 5: Verify the applicability contract

The applicability contract is a working classification by the writing skill; `/lit-cache verify` MVP does not re-classify it. The MVP checks only:

1. The 8 axes are all present (or marked `not_specified` with a documented reason).
2. Any namespaced families referenced exist in `applicability-axes.md`'s family registry.
3. The `theoretical_lineage.primary_line`, if present, matches an existing line OR has a documented rationale for being new.

Discrepancies are recorded in the `verification_log` but do not block promotion at the `source_checked` level. They block promotion to `independently_checked` (deferred).

### Step 6: Promote or hold

For each entry that passed Steps 3-5:

1. Move the file from `inbox/<bibkey>.draft.md` to `papers/<bibkey>.md` (or merge into the existing container file for an update entry).
2. Update `verification_status` from `unverified_extract` to `source_checked`.
3. Append to `verification_log`:
   ```yaml
   - date: <today>
     actor: /lit-cache verify v1.0 MVP
     action: source_check
     evidence: fetched source from <source_url>; source_hash match; all N quote text_hashes match; applicability contract validated for axis presence and family registry membership
   ```
4. Update the top-level `~/.claude/literature_cache/INDEX.md` to reflect the new canonical entry.

For each entry that failed Steps 3-5:

1. Leave the file in inbox with the original `verification_status: unverified_extract`.
2. Append a `verification_log` entry documenting the failure reason.
3. Print a summary line listing the failure (so the user sees the queue at end of run).

For each entry that was `source_inaccessible`:

1. Leave in inbox.
2. Mark `source_inaccessible: true` in the manifest.
3. Report at end of run.

### Step 7: Print summary

At the end of the verify pass, print:

```
[lit-cache verify] Summary
  Processed: N entries
  Promoted (source_checked): M
  Held (hash mismatch / hallucination flag): K
  Held (source inaccessible): J
  Held (other reason): L

  Promoted entries available for downstream skills:
    paper:bickel_levina_2008#thm_1 → source_checked
    paper:talagrand_1996#chaining_main → source_checked
    ...

  Held entries requiring re-extraction:
    paper:foo_2024#thm_3 → quote q2 text_hash mismatch at locator (page 7 eq 3.4)
    ...

  Held entries requiring source access:
    paper:bar_2023#main → source_inaccessible (paywall)
    ...
```

## What This MVP Does NOT Do

The deferred items (Codex round 3 noted these are acceptable as follow-up):

- **`/lit-cache audit`** — promotion from `source_checked` to `independently_checked` via a Codex MCP call at `xhigh`. This requires fresh-thread invocation per `CODEX_PROTOCOL.md` "Per-Repair Fresh Thread" pattern adapted to cache audit. Workflow: spin up a fresh Codex thread per entry, pass the entry's verbatim quotes + the source URL + the applicability contract, ask Codex to independently extract and compare, record discrepancies, promote on agreement. Deferred because the MVP source-hash check covers the most common hallucination class (the writing skill claimed verbatim it did not actually read); the deeper independent-reading check is valuable but adds Codex token cost that the user pays per upgrade.
- **`human_signed` workflow** — explicit human attestation. The user can manually edit the `verification_log` and `verification_status` field at any time; no skill automation is needed. Document in the entry itself who signed off and when.
- **Automatic staleness re-check** — when a cached `source_version` (e.g., `arxiv:0803.4067v2`) is superseded by `v3` upstream. The MVP does not poll for new versions; it only verifies the version already recorded. A staleness check could be added as `/lit-cache verify --check-versions`.
- **Bulk re-extraction** — when many entries fail at Step 4, the MVP does not automatically re-fetch and re-attempt. The user must address each `held` entry individually (typically by re-running the originating skill's literature step against the held bibkey).
- **Cross-project reverse index updates** — when an entry is promoted or held, the MVP does not scan known projects' `cited_results.lock.md` files for affected citations. The reverse index is computed on demand (see `cache-verification-states.md` "Reverse Index Generation").

## Failure Modes

| Failure | What it means | Recovery |
|---|---|---|
| `source_hash` mismatch with no `source_version` update | Writing skill recorded a stale or wrong hash | Update `source_hash` to the fetched value; proceed |
| Quote `text_hash` mismatch | Writing skill misextracted or hallucinated the quote | Hold entry; user re-fetches and re-extracts |
| Source URL dead | Original source no longer accessible | Hold entry as `source_inaccessible`; user finds alternate source or downgrades all citation sites that depend on this entry |
| Source paywalled | User needs institution access | Same as dead; user provides locally-stored copy if available |
| Applicability axis values reference unregistered family | The writing skill drafted a new family without precedent | Hold entry; user proposes the new family to `applicability-axes.md` first |
| `theoretical_lineage.primary_line` is new and undocumented | The writing skill drafted a new line | Hold entry; user provides rationale; promote on next verify run after rationale is added |

## Integration with Other Protocols

- `cache-verification-states.md` defines the 4 states and the gate table; this file is the workflow that transitions from `unverified_extract` to `source_checked`.
- `citation-purpose-protocol.md` is consulted by downstream skills using the promoted entries; this protocol is upstream of that.
- `applicability-axes.md` is the family registry; this MVP validates membership at Step 5.
- `literature-cache-protocol.md` is the router; this MVP is one of its Minimum Load Map use cases (`cache verify`).
- `CODEX_PROTOCOL.md` Per-Repair Fresh Thread pattern is the basis for the deferred `/lit-cache audit` workflow.

## Honest Limits

- The MVP cannot detect hallucinated cache entries that happen to be self-consistent (the writing skill invented a paper, invented quotes, computed hashes of its own invention, and never fetched). Source reconciliation requires the source URL to resolve to a real document; if the writing skill invented a URL that returns 404, the MVP flags `source_inaccessible` but the deeper detection requires human or `/lit-cache audit` review.
- Quote extraction at a `locator` is fragile for PDFs with non-standard page layouts, multi-column text, or embedded equations. Mismatches may be cosmetic (whitespace, hyphenation) rather than substantive. The MVP normalizes to Unicode NFC and strips whitespace; deeper normalization (e.g., reflowing hyphenated line breaks) is not in scope.
- The MVP processes inbox entries sequentially. For large inbox queues (>50 entries), batch processing might be faster, but parallel `WebFetch` calls can hit rate limits.

## Versioning

This protocol is version `1.0 MVP`. Versioning follows the protocol versioning scheme in `cache-verification-states.md`. Future versions may add the `/lit-cache audit` workflow or staleness re-check.

## Cross-Reference

- `literature-cache-protocol.md` (router)
- `cache-verification-states.md` (4 verification states, gate table, F1/F2/F3 workflows)
- `applicability-axes.md` (family registry)
- `citation-purpose-protocol.md` (citation purposes consuming promoted entries)
- `CODEX_PROTOCOL.md` (the dialogue pattern for the deferred `/lit-cache audit`)
