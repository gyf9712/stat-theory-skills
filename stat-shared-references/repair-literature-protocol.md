---
artifact: shared_reference
scope: repair_literature_support
generator: extracted from proof-repair Step 4 per Codex threadId 019fa42e-217f-7171-b94f-99b95177aab8 (fixed libraries + prompt blocks out of the hot body)
---

# Repair Literature Support Protocol

The search, tiering, verification, and cache/lock write-back procedure for finding
literature that supports a proof repair. Consumed by `proof-repair` Step 4; the venue
tier lists themselves are rule data in `scripts/venue_tiers.py` (single source of truth,
also used by `theory-sharpen` and the writing repo).

**Guiding principle.** A repair is only as credible as its references. Prefer top-tier
venues; treat unreviewed preprints as supplementary evidence only.

## A. Cache-consult first (mandatory)

Before any web tool, consult `~/.claude/literature_cache/`. Router:
`literature-cache-protocol.md` (Minimum Load Map). Typical additional loads:
`applicability-axes.md` when the candidate is `load_bearing` / `benchmark_claim` /
`comparative`; `cache-verification-states.md` when fetching new entries or when a source
version may be stale.

1. Read `~/.claude/literature_cache/INDEX.md`; identify hits matching the repair's need
   (technique, anchor paper, schema, comparator).
2. For each hit, do a result-scoped load (`Read` with `offset`/`limit`). Do not dump full
   paper containers.
3. For each miss, run the web search below, then write the proposal back to
   `~/.claude/literature_cache/inbox/<bibkey>.draft.md`.

Tier classification applies to cache hits and fresh results alike.

## B. Venue tiers and credibility scoring

Tier lists live in `scripts/venue_tiers.py` (`TIER_1` … `TIER_4`). Summary:

- **T1 Gold standard** — stat Big Four, Annals of Probability / PTRF / SPA, top pure-math
  journals, NeurIPS / ICML / ICLR / COLT / ALT / AISTATS, JMLR, Econometrica / JOE /
  ReStud / JBES, Math Programming / SIOPT / MOR, SIAM Review / SINUM / MathComp,
  authoritative textbook series. A single T1 citation can anchor a repair.
- **T2 Strong** — EJS, Bernoulli, Statistica Sinica, Scand. J. Stat.; AAAI / IJCAI / UAI /
  KDD / JAIR; Trans. AMS, J. Funct. Anal., Adv. Math.; Econometric Theory, J. Appl.
  Econometrics, Econometric Reviews; IEEE Trans. IT / SP.
- **T3 Supplementary** — unpublished arXiv preprints, workshop papers, tech reports,
  secondary conferences. Lower confidence; flag explicitly.
- **T4 Avoid** — untraceable manuscripts, blogs / slides / StackExchange, retracted
  papers, predatory journals.

Scoring:

| Situation | Credibility | Use |
|---|---|---|
| T1 published, ≥50 citations | GOLD | primary anchor |
| T1 published, 10-49 citations | STRONG | reliable |
| T1 published, <10 citations or very recent | ACCEPTABLE | verify the theorem carefully |
| T2 published | GOOD | acceptable; prefer T1 if available |
| T3 preprint, ≥20 citations | CONDITIONAL | only if the theorem is self-contained and verifiable |
| T3 preprint, <20 citations | WEAK | only if no alternative; verify step by step |
| T4 any | REJECT | do not cite |

When two references support the same repair, prefer the higher tier. When a preprint and
its published version both exist, always cite the published version.

## C. Query formulation and multi-source search

Convert each repair need into 2-3 precise queries targeting different source types: a
classic/textbook query, a journal-result query, and a recent-technique query. Example
shape for "hidden invertibility assumption in an M-estimation Hessian": *"strong convexity
Hessian positive definite"* (textbooks), *"minimum eigenvalue Hessian strongly convex
M-estimation"* (AoS / JASA / Biometrika / JMLR), *"M-estimator regularity condition
relaxation"* (recent COLT / NeurIPS / stat.TH).

Run three parallel `Agent` searches, each venue-aware, each returning title, authors,
year, venue, tier, citation count, and the exact theorem statement:

1. **arXiv + published cross-check** — stat.TH / math.ST / stat.ML / cs.LG, last ~5 years.
   For each hit, check for a published version (DOI, "published in" in comments); if
   published, cite that version and record the venue; if preprint-only, mark T3 with its
   citation count.
2. **Semantic Scholar, venue-filtered** — `api.semanticscholar.org/graph/v1/paper/search`
   with `fields=title,authors,year,abstract,externalIds,citationCount,venue,publicationTypes`.
   Take all T1 hits; take T2 hits with >10 citations; take anything else only above 50.
3. **Targeted high-quality sources** — `projecteuclid.org` (AoS, Ann. Prob., Bernoulli,
   EJS), `jstor.org` (Econometrica, JASA, JRSS-B, Biometrika), `jmlr.org`, `springer.com`,
   plus a `"textbook" OR "monograph"` variant for the standard reference.

## D. Evaluate and rank

Build a credibility-weighted table: paper, venue, tier, citations, credibility, theorem,
matches-the-need, assumptions-OK, recommendation (PRIMARY / SECONDARY / SUPPLEMENTARY /
SKIP). Include at least one T1 reference per repair where possible. If only T3 is
available, flag the repair "lower confidence — needs independent verification."

## E. Verify, with rigor proportional to tier

- **T1**: fetch the exact statement; verify our assumptions satisfy their prerequisites;
  verify their conclusion gives exactly what we need; check notation, constants, and
  finite-sample vs asymptotic. Trust HIGH after the prerequisite check.
- **T2**: all T1 checks, plus confirm the result is not superseded by a corrigendum, and
  cross-reference one T1 source for the same or a similar result.
- **T3**: all T1 checks, plus read the *proof* (not just the statement), verify it has no
  gaps of its own, and check for independent reproduction or T1/T2 citation. Trust LOW;
  the repair plan must say "preprint, not yet peer-reviewed."

This is what prevents citation misuse — the same error class `proofcheck` audits.

## F. Cache write-back and lock manifest (mandatory for new sources)

For every reference that was a cache miss and has now been fetched and verified, write
`~/.claude/literature_cache/inbox/<bibkey>.draft.md` per `cache-verification-states.md`,
including: manifest header with `verification_status: unverified_extract`; source URL,
version, retrieval date, hash, and verbatim quote blocks with locators and text hashes;
the applicability contract on the 8 axes per `applicability-axes.md`; and the lineage
block (`primary_line`, `role_in_literature`) per `citation-purpose-protocol.md`.

The repair may proceed on its own `unverified_extract` (it just read the source).
Downstream skills require `/lit-cache verify` promotion (`lit-cache-verify-protocol.md`)
before consuming it at `source_checked` or higher; notify the user that an inbox entry
awaits verification.

**Lock manifest** (per `cited-results-lock-protocol.md`): append a row to
`papers/<project>/cited_results.lock.md` for the new citation site. Repair purposes are
typically `load_bearing` (Citation-Fix, Strengthen-Proof invoking the result as a step),
`technique_inheritance` (Replace-Technique borrowing a device), or `standard_tool` (a
named tool such as Talagrand or Bernstein). Read before write; append, do not edit.

## G. Fallback when no high-quality reference exists

1. **Provable from scratch?** Write it as a new lemma with proof; note "self-contained,
   no external reference needed."
2. **Classic textbook result?** Cite the authoritative textbook even if search missed it
   (Durrett for probability, Billingsley for convergence, Rockafellar for convex analysis,
   van der Vaart for asymptotics, Tsybakov for nonparametric estimation).
3. **Only a T3 preprint?** Cite it, and record: the reference is a non-peer-reviewed
   preprint, the cited theorem was independently verified during this repair, and it
   should be replaced with a published reference when one appears.
4. **No reference at all?** Write the complete proof and mark the repair "self-proved —
   review recommended."
