# Verified Cross-Repo Refactor Review (June 2026)

This review answers the question: are the skills too long, and can deterministic parts move to code so the prose body stays focused? It covers both `stat-writing-skills` and `stat-theory-skills`. The findings here are **verified by reading the files**, not taken from agent summaries; where an automated scan over-counted, the correction is noted.

## The diagnosis (confirmed)

The failure mode of a 1,000+ line `SKILL.md` is **priority distortion**, not literal forgetting. The model runs the first ~200 lines as hard rules and the rest as suggestions. Mid-file checklists get downweighted, examples compete with judgment, and the same rule restated in two skills drifts.

Current sizes:

| Repo | Lines | Largest files |
|---|---|---|
| stat-writing-skills | ~8,300 | stat-paper-write 1,211; stat-polishing 811; stat-paper-plan 843 |
| stat-theory-skills | ~10,300 | theory-simulation 1,443; proof-repair 1,149; theory-sharpen 1,146; proofcheck ~1,020; theory-design 966 |

## The principle (five buckets)

Each piece of content goes to exactly one place:

1. **scripts/** — deterministic mechanics (pattern matching, counting, cross-checks, graph algorithms, schema validation).
2. **rule data** — venue profiles, fixed thresholds, severity maps, regex catalogs. Python module for structured data; `.txt` for flat lists. Never `.md` as machine source.
3. **candidate generators** — scripts that flag likely issues plus evidence; never decide. Emit `CANDIDATE`/`REVIEW`, never affect exit code.
4. **SKILL.md** — orchestration, hard gates, escalation, interpretation. Target 250-500 single-mode, 500-800 multi-mode, 800 ceiling.
5. **references** — judgment detail, examples, edge cases, architecture.

`PASS`/`FAIL` is reserved for truly mechanical checks. This guards against **false authority**: once a script exists, a `PASS` gets trusted as correctness.

## Correction to the automated scan

A parallel agent scan over the five biggest theory files reported large "duplication" counts (one agent estimated ~450 lines of duplicated schema content in proof-repair alone). **This was an over-count.** Reading the files shows the theory repo already underwent a major shared-reference extraction in the v1.8/v1.9 commits:

- `proof-repair` already references every schema ("per the schema in `proof-closure-machinery.md`, not duplicated here") rather than inlining it.
- `proofcheck` already references the severity system, verification statuses, and provability triage ("defined in `proof-closure-machinery.md`, single source of truth") rather than restating them.
- The cache protocols, Codex protocol, and equivalence-ledger protocol are all referenced cross-file.

The agents matched on schema *names* without noticing the reference language. Lesson reinforced: agents flag, the editor verifies before deleting. Almost none of the flagged duplication was real.

## What genuinely remains (verified)

### Tier 1 — deterministic mechanics not yet in code (real, highest value)

| Item | Where | Status |
|---|---|---|
| LaTeX integrity + template conformance | writing repo | DONE — `latex_audit.py` (v1, June 2026) |
| Proof architecture indexing: theorem inventory, dependency DAG, topological order, cross-ref integrity, reference-mode | theory repo, proofcheck Step 1 + Pass 0 | DONE — `proof_index.py` (this commit) |
| Markdown ledger schema validation (Repair Closure Matrix, Weaken-Claim / Assumption-Extension Change Logs, Repair Ladder Defense) | theory repo, proof-repair writes + proofcheck --post-repair validates | DEFERRED — shared `proof_artifacts_validate.py`; born-shared, but validates LLM-produced freeform markdown so it carries higher false-authority risk; spec carefully before building |

### Tier 2 — rule data extractable to config (real, medium value)

| Item | Where | Note |
|---|---|---|
| Venue credibility tiers (T1-T4) | proof-repair, theory-sharpen, research skills | Shared `venue_tiers.py`; used by several skills |
| Relaxation pathways library (~50 lines of fixed From→To transitions) | theory-sharpen Step 1C | `relaxation_pathways.py` data module |
| Framework tags, reviewer-critical dimensions | theory-sharpen | Fixed lists → config |
| Paper-type templates, topic-signature schema, venue lists | theory-design | Fixed structures → config |
| 19 failure-pattern checklist, proof-strategy classification table | proofcheck | Fixed lists → `failure_patterns.py` (candidate-scanner input) |

### Tier 3 — mostly judgment, leave alone (verified)

`theory-sharpen` (~775 of 1,146 lines) and `theory-design` (~550 of 966 lines) are overwhelmingly judgment: assumption-relaxation reasoning, rate-optimality assessment, paper-type design pedagogy, Codex dialogue design. Extracting their rule-data tables saves 150-300 lines each but the bodies stay large because the substance is irreducible narrative. Do not force these under 800; the prose is the product.

## What landed in this commit

`proof_index.py` (theory repo), the proofcheck analog of `latex_audit.py`:

- Theorem-like-environment inventory with label, line, summary.
- Dependency graph from `\ref` inside proof blocks, attributed to the owning unit.
- Topological layers (Kahn) giving a check order, with cycle detection (`dependency_cycle` is a CRITICAL FAIL).
- Cross-reference integrity: `undefined_ref` and `cross_file_ref_leak` (the two-file submission bug).
- Reference-mode detection.
- JSON + Markdown output; provenance stamp (`script_version`, `rules_version`, `rules_digest`); exit codes 0/1/2.
- 10 stdlib unittest cases against a synthetic fixture; all pass.

`proofcheck` Step 1B/1C and Pass 0 Task 2B were slimmed: the grep/find/topological-sort bash and the cross-file-leak `comm` pipeline are replaced by a single script call. The judgment that remains (core proof strategy narrative, critical-path identification, hard-coded-number convention phrasing, supplement numbering) is kept in prose and explicitly marked as judgment.

## Maintenance discipline

- Bump `RULES_VERSION` when rule logic changes; `SCRIPT_VERSION` when behavior changes. The `rules_digest` is automatic.
- Add a fixture under `tests/fixtures/` for any new rule.
- Run `python -m unittest tests.test_proof_index` (and `tests.test_latex_audit` in the writing repo) before committing.
- Never duplicate the script's check list in prose; if a SKILL.md step restates what the script does, drift is back.

## Roll-out queue (deferred, prioritized)

1. `proof_artifacts_validate.py` — shared ledger-schema validator (Tier 1, biggest leverage, spec carefully for the freeform-markdown / false-authority risk).
2. `venue_tiers.py` — shared rule data (Tier 2, used by proof-repair + theory-sharpen + writing skills).
3. theory-sharpen rule-data extraction: relaxation pathways, framework tags, reviewer dimensions.
4. theory-design rule-data extraction: paper-type templates, venue lists, topic-signature schema.
5. proofcheck `failure_patterns.py` — the 19-pattern checklist as a candidate-scanner input.
6. AI-tell candidate scanner for the writing repo (heuristic, `CANDIDATE` only).

Each is one bounded extraction with its own fixture and test, applied and verified before the next.
