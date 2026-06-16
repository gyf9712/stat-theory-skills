# Codex Dialogue: proof-writer strategy improvements

**Date:** 2026-05-28
**threadId:** `019e6fe3-9a34-70e2-942b-ab8343e491d4`
**Model:** gpt-5.4 at `model_reasoning_effort: xhigh`
**Topic:** how proof-writer finds proof strategies

## Background

The proof-writer skill enforces honesty (no sketches, no hand-waving, no fabrication) but Step 4 says "choose a strategy" with a flat menu (direct, contradiction, induction, construction, reduction, coupling, optimization inequality chaining). The skill does not say HOW to choose. Most of the strategy-finding work was implicitly delegated to the underlying model.

The goal of this dialogue was to make the strategy-finding step explicit and statistics-specific, mirroring the senior-statistician move of "choose the battlefield before doing algebra."

## What converged

Three rounds, mostly converged after round 3. The key changes:

### 1. New step 3.5: Locate the Verification Target and Bottleneck

Inserted between Feasibility Triage (Step 3) and the Dependency Map (Step 4). The output is a three-line artifact in the proof package:

- **Verification target**: the precise intermediate statement whose verification closes the claim under the chosen reduction (theorem-specific, not a slogan)
- **Bottleneck**: the first unresolved leaf (specific inequality, localization claim, entropy bound, invertibility step, prerequisite of a cited theorem)
- **Resolution path**: how to break the bottleneck

Codex initially called this a "proof certificate" but agreed to drop the term after I pushed back: "certificate" has specific meanings in optimization (Farkas) and complexity theory (polynomial-time verifier) that do not match how senior statisticians talk. The replacement term `verification target` is plain English and matches actual usage.

### 2. Dependency Map: backward-first, forward-verified

Codex's improvement on my draft. Build the map by:
- Backward chaining from the claim until leaves are assumptions, verified prerequisites of cited theorems, or isolated new lemmas
- Forward pass from the leaves to verify they actually support what they claim to

A purely backward map can produce subgoals that look plausible but do not hold; the forward pass catches that.

### 3. Anchor disclosure with three flavors

Three relations of a proof to the literature, each with its own discipline:

- **Template adaptation**: identify 1-3 closest anchors, name their proof spine, separate borrowed from new
- **Standard-result invocation**: name the theorem, list its prerequisites, verify each
- **Self-contained**: requires explicit Implicit Machinery Disclosure (most claimed self-contained proofs are actually using mature machinery the author has internalized)

Codex agreed (after my pushback) that "self-contained" without disclosure is too lenient. The distinction *paper-self-contained* (only enumerated graduate-core facts) vs *locally self-contained* (no prior paper imported wholesale, but mature machinery used implicitly) is now in the shared reference.

### 4. Trap Catalogue with diagnostic tests

Seven named middle-regime traps, each with a one-line ctrl-F-able diagnostic:

1. Localization-before-expansion
2. Wrong norm / wrong mode
3. Good-event bookkeeping
4. Rate leakage
5. Quantifier inflation
6. Imported-theorem prerequisite drift
7. Boundary / singularity

Codex initially gave names without tests; I pushed back that naming alone is not a defense. The current version has both, with the diagnostic phrased mechanically (search for X, check Y).

### 5. Shared reference file

`stat-shared-references/proof-strategy.md` (new). Contains:

- Claim Families → Verification Targets (the canonical map)
- Anchor Selection and Comparison
- Implicit Machinery Disclosure
- Assumption Budget and Propagation
- Norm / Mode / Quantifier Checklist
- Localization and Good-Event Bookkeeping
- Imported Theorem Prerequisite Audit
- Trap Catalogue with Diagnostic Tests
- High-Dimensional Regularization Patterns
- Asymptotic Linearity / M-Estimation Patterns
- Empirical Process / Concentration / Chaining Patterns
- Lower Bounds and Bayesian Asymptotics

Shared between `proof-writer` (consults at write time) and `proof-repair` (consults at repair time). Codex agreed to share via reference rather than duplicating content in two skill bodies.

## Where I pushed back on Codex

### Push 1: "Proof certificate" terminology — Codex withdrew

Codex initially used "proof certificate" as core terminology. I noted that the term has specific meanings in optimization (Farkas certificate) and complexity theory (polynomial-time-verifiable witness) that do not match statistics usage, and asked for two worked examples to prove the term generalizes.

Codex withdrew the term: "`Proof certificate` is not standard statistics language. I would not put that term into the skill." Replaced with `verification target`. The two examples (Bickel-Ritov-Tsybakov LASSO cone + RE, M-estimator asymptotic linear representation) work cleanly with the replacement term.

### Push 2: Trap catalogue needs diagnostics, not just names

Codex's first version listed seven traps by name and description. I pushed back: "Naming alone is not a defense. Each trap needs a one-line diagnostic test, not just a description, so the polisher can mechanically check."

Codex agreed and produced ctrl-F-able diagnostics for each trap. The current version is mechanical enough for a PhD student to apply.

### Push 3: Self-contained claims need defense

Codex initially said "if no close anchor exists, say so explicitly." I said this was too lenient — most "self-contained" proofs are actually using machinery the author has internalized and stopped citing.

Codex agreed and proposed the *paper-self-contained vs locally self-contained* distinction, plus the Implicit Machinery Disclosure block requiring authors to enumerate the mature machinery, the background a strong PhD student would need, and what is re-proved here.

## Where I held the line

### Citation accountability

Codex's second reply cited three sources: Bickel-Ritov-Tsybakov (AoS 2009), Basu-Ghosh (JASA 1980), Hall et al. (arXiv 1202.5183).

Bickel-Ritov-Tsybakov AoS 2009 is the canonical LASSO + RE paper and matches what it was sourcing. The other two were unclear — I could not tell what they were sourcing, and the format looked like padding.

I called this out in round 3: "Per our dialogue discipline, when you cite a specific paper, theorem, or constant, the burden is on the citation to be checkable. Drop unclear citations rather than padding the list."

Codex agreed: "In my previous reply, only Bickel-Ritov-Tsybakov was doing real work. Ignore the other two."

This is a clean instance of the dialogue principle from `stat-codex-dialogue.md`: Codex is reliably right on patterns, less reliable on specific citations. Verify what is verifiable, drop what is not.

## Outstanding items (not resolved in this dialogue, deferred to roadmap)

- Whether the new step 3.5 should be a separate slash command (`/locate-verification-target`) that proof-writer calls, or remain inline. Codex did not have a strong view.
- Whether `proof-repair` should also gain a Verification Target section in `REPAIR_PLAN.md`, mirroring the proof-writer step. Probably yes; deferred.
- Whether the trap-catalogue diagnostics should be exposed as a standalone `/trap-audit` command for use on existing proofs. Deferred.

## Final architecture

```
proof-writer workflow (updated):
  Step 1: Gather Proof Context
  Step 2: Normalize the Claim
  Step 3: Feasibility Triage
  Step 3.5: Locate the Verification Target and Bottleneck  ← NEW
  Step 4: Build a Dependency Map (backward-first, forward-verified)
  Step 5: Write the Proof Document
  Step 6: Final Verification (now includes 7 trap diagnostics)

Proof package structure (updated):
  ## Claim
  ## Status
  ## Assumptions
  ## Notation
  ## Verification Target and Bottleneck   ← NEW
  ## Anchors and Borrowing                  ← NEW
  ## Implicit Machinery Disclosure          ← NEW (if self-contained)
  ## Proof Strategy
  ## Dependency Map
  ## Proof
  ## Corrections or Missing Assumptions
  ## Open Risks (with trap-catalogue results)

Shared with proof-repair:
  stat-shared-references/proof-strategy.md  ← NEW
```

The Codex thread remains open for resumption at `019e6fe3-9a34-70e2-942b-ab8343e491d4` if these items need to be re-engaged.

---

## Round 2 dialogue (2026-05-28): citation precision

**threadId:** `019e7024-bea4-7171-aa11-4c352baebebe` (the previous thread expired)

**Trigger:** the user flagged that the Trap Catalogue's single "Imported-theorem prerequisite drift" item conflates two failure modes. When a statistics proof cites "by Theorem 3.2 of Bickel-Ritov-Tsybakov (2009)", LLMs habitually misattribute theorems, swap theorem numbers between papers, or state "Theorem X.Y says Z" when it actually says Z' (close but different). This is the citation-precision audit problem: the proof-level twin of the positioning audit in `stat-positioning-and-claims.md`.

### What converged

**Two-layer citation discipline.** Codex's framing: citation work in theoretical statistics fails on two independent layers.

- **Layer 1 (Citation identity / version drift)**: did the proof identify the right source, version, theorem number, and exact clause?
- **Layer 2 (Imported-result applicability drift)**: given that the identity is correct, do the source assumptions actually hold here, and is the conclusion exactly what we need?

Both must pass. The previous single diagnostic confused them.

**Four-class scope for citation audit.** Not every citation needs a statement-level audit; only proof-dispositive imported results:

| Class | Audit requirement |
|---|---|
| Background / positioning | None |
| Anchor / template | None unless a specific result is imported as black box |
| Named theorem schema, uncited | Applicability audit only (theorem-schema level) |
| Specific theorem / lemma / proposition / corollary / equation citation used to discharge a step | Full two-layer audit |

Primitive inequalities (Cauchy-Schwarz, Markov, Hölder, Jensen, Fubini, Taylor, eigenvalue bounds, Woodbury) are pattern-level checks, not whitelist citations.

**Graduate-core citation-exempt schemas (closed list).**

- Borel-Cantelli I and II (II only with independence checked locally)
- WLLN and classical CLT for iid finite-dimensional observations
- Continuous mapping, Slutsky, portmanteau (basic forms), finite-dimensional delta method
- Glivenko-Cantelli for empirical CDF of iid real-valued data
- Hoeffding, Bernstein for independent scalar sums (basic forms)
- Doob's $L^p$ inequality (basic submartingale form)

Everything else needs statement-level audit: Skorohod, dependent LLN/CLT, functional delta methods, generic Glivenko-Cantelli / Donsker / VC / bracketing-entropy, Talagrand / chaining, Fano / Le Cam / Assouad with constants, argmax / Z-estimator consistency theorems beyond basic, asymptotic linearity with nuisance, BvM, or any theorem-numbered citation.

**Four direct-inspection states** with admissibility tied to proof-dispositive role:

| State | Admissibility |
|---|---|
| `checked-now-source-of-record` | Passes |
| `checked-now-alternate-source` | Passes with version / numbering crosswalk required |
| `previously-checked-no-current-access` | Open risk only; P0 use blocks `PROVABLE AS STATED` |
| `never-checked` | Inadmissible |

**Cited Results Audit section** added to `PROOF_PACKAGE.md`. Per-row schema covers role class, audit priority, full source identity, source-of-record, version crosswalk, errata, direct-inspection status, exact used clause, source assumptions, local verification map, conclusion fit, audit verdict.

**Literature-Retrieval Handoff table** at the end of the audit section. Lists rows that need retrieval, marked P0 / P1 / P2 with explicit "if retrieval fails" consequences. Since `proof-writer` has no web tools, this is the prioritized handoff to `/proof-repair`.

### Where I pushed back on Codex (Round 2)

**Pushback A: Undefined whitelist is an empty escape hatch.** Codex's round-1 reply mentioned a "graduate-core whitelist" without defining it. I drafted my own list and asked Codex to either accept, modify, or extend. Codex accepted most of my list but corrected two errors:

1. Primitive inequalities (Markov, Cauchy-Schwarz, Fubini, Taylor) should not be on the whitelist — they are local pattern checks, not "exempt schemas." The whitelist is named theorem schemas only.
2. The whitelist must be narrow: Talagrand, VC, Donsker, BvM, Le Cam with constants are NOT graduate-core even though everyone uses them.

**Pushback B: My applicability diagnostic was inverted.** I drafted that the `Conclusion fit` field flagged "stronger than needed" or "ambiguous." Codex corrected: stronger conclusions can always be used; the dangerous fits are `weaker than needed` (without an explicit bridge) and `ambiguous-mismatch`. I had the direction backward. Accepted.

**Pushback C: Three vs four access states.** I proposed three states. Codex preferred four, renamed for admissibility clarity. I accepted because the renaming makes the rule clear: only the first two pass for proof-dispositive use; the third is admissible only as an open risk for P1/P2 work; the fourth is never admissible.

**Pushback D: Pipeline handoff.** I asked whether `proof-writer` (single-shot, no web tools) should produce a handoff list to `/proof-repair` (which does have literature retrieval). Codex confirmed: yes, the audit ends with a prioritized retrieval list. The user reads it and decides which P0 rows are essential enough to invoke `/proof-repair` on.

### Where Codex held the line (and I accepted)

- **No "stronger than needed" as a flag**: stronger conclusions discharge the proof step.
- **P0 + `previously-checked-no-current-access` is a hard fail, not a soft risk**: Codex's final tightening. The PROOF_PACKAGE cannot be `PROVABLE AS STATED` if a load-bearing citation has not been directly inspected during the current proof work.
- **No `never-checked` admission**: even for the schema-level cases that look harmless.

### Files changed in this round

- `stat-shared-references/proof-strategy.md`: trap #6 split into two (#6 Citation identity / version drift, #7 Imported-result applicability drift); boundary trap renumbered to #8; new sections *Citation Identity vs Applicability*, *Scope: which citations need a statement-level audit*, *Graduate-core citation-exempt schemas*, and *Access states for cited sources*.
- `skills/proof-writer/SKILL.md`: new `## Cited Results Audit` section in the required file structure with per-row schema and Literature-Retrieval Handoff table; Step 6 Final Verification updated to apply both new diagnostics; Open Risks template renumbered to the 8-trap set.

The thread remains at `019e7024-bea4-7171-aa11-4c352baebebe`.

---

## Round 3 dialogue (2026-05-28): repair-priority ladder

**threadId (continued):** `019e7024-bea4-7171-aa11-4c352baebebe`

**Trigger:** the user asked proof-repair to enforce a strict priority principle: when fixing a proof, try first to repair WITHOUT adding or strengthening assumptions and WITHOUT weakening the claim; only if that route fails, extend (add assumptions or weaken). The existing skill had invasiveness LOW/MEDIUM/HIGH and "Repair Quality Criteria" #3 ("Minimal — prefer the least invasive fix") and #4 ("Preserves claims — ideally keeps the theorem statement unchanged or weakens minimally") — but these were advisory, not enforced. A user could pick a HIGH-invasiveness Add-Assumption candidate without first defending why LOW candidates failed.

### What converged

**Two-phase ladder, not six-level total order.** My initial draft was strict L1 < L2 < L3 < L4 < L5 < L6. Codex correctly pushed back: L2 and L3 are not linearly ordered by invasiveness (Insert-Lemma vs Replace-Technique is a sibling choice), and L4 vs L5 is not universally ordered either (a heavy-tail paper adding sub-Gaussian to preserve the original rate may be worse than a weaker rate under the original tail assumption). The right structure is:

- **Phase A (claim-preserving, assumption-preserving)**: L1 Internal correction, L2 Supporting lemma, L3 Alternative technique. No hard order between L2 and L3.
- **Phase B (semantic edits)**: L4 Add assumption, L5 Weaken claim. Allowed only after a Phase A exhaustion record. No universal preference between L4 and L5.
- **Phase C**: L6 Blockage / NOT CURRENTLY JUSTIFIED.

**No checkbox serialism.** Codex pushed back on requiring all three Phase A branches for every issue. The right rule: document the **relevant** lower-level branches. Misapplied citation: L1 and L3 relevant, L2 irrelevant. Missing bridge inequality: L1 and L2 relevant, L3 only if route collapses.

**Phase B requires escalation artifacts.** L4 needs an Assumption-Extension Change Log (analogous to Weaken-Claim Change Log). L5 needs the Weaken-Claim Change Log. Both need the Phase A Exhaustion Record. Without these, the candidate is demoted to NOT CURRENTLY JUSTIFIED.

**Repair Ladder Defense per repair file.** A new mandatory block in each per-issue repair file: chosen level, chosen repair class, claim preserved (yes/no), assumptions preserved (yes/no), Phase A exhaustion table (with concrete attempts, specific obstacles, and why the obstacles are genuine), Phase B justification (only for L4/L5), semantic-edit log pointer.

**Repair Ladder Summary at REPAIR_PLAN.md level.** Paper-level summary table showing chosen level, claim/assumption preservation, and escalation justification status per issue, with pointers to the per-issue defense.

**Mapping ladder ↔ repair class.** Codex corrected my draft:
- L2 → Insert-Lemma (primary), Strengthen-Proof (if helper stays inline)
- L3 → Replace-Technique (primary), Strengthen-Proof (if new route is closely related to the old)
- L1 → Strengthen-Proof, Fill-Skipped-Steps, Citation-Fix, Fix-Constants, Fix-Quantifiers
- L4 → Add-Assumption
- L5 → Weaken-Claim
- L6 → Blockage report
- Expand-Sketch-to-Proof is orthogonal (lands at any level)

### Where I pushed back on Codex

**Pushback A: undefined whitelist** — see round 2 above; same dialogue principle, this time on the claim that "Phase A exhaustion" without scope would generate checkbox serialism. Codex agreed and refined to "relevant branches only."

**Pushback B: my draft inverted the L4-vs-L5 preference** — I had implicitly assumed L4 (add assumption) is less invasive than L5 (weaken claim). Codex corrected: not universally true. A weaker claim under the original tail assumption is often better than the original claim under sub-Gaussian when the paper is about heavy tails. Accepted; neither L4 nor L5 is universally preferred.

**Pushback C: "smallest possible" assumption defense was too strong** — I asked Codex to require the author to prove the added assumption is minimal. Codex correctly said: that's globally unprovable. The audit rule should be "natural weaker variant considered and rejected with a concrete reason." Accepted.

### Where Codex held the line

- **No order between L2 and L3, and no order between L4 and L5.** Both are sibling choices within their phase.
- **No re-solving Phase A in /proofcheck --post-repair.** The re-audit checks discipline (presence of artifacts, propagation, consistency), not whether a cleverer Phase A repair existed. Disputing the choice of ladder level is out of scope for the convergence test.
- **L4 + missing Assumption-Extension Change Log = NOT CURRENTLY JUSTIFIED.** Same severity as L5 + missing Weaken-Claim Change Log. Both are hard gates.

### Files changed in this round

- `skills/proof-repair/SKILL.md`: new Step 3 "Enforce the Repair Priority Ladder (HARD GATE)" before candidate generation; existing candidate-generation step renamed to Step 3B; candidate template adds `Ladder level` field next to invasiveness; new mandatory blocks added — Assumption-Extension Change Log (analogous to Weaken-Claim Change Log), Repair Ladder Defense (per-issue); new Repair Ladder Summary table added to REPAIR_PLAN.md template.
- `skills/proofcheck/SKILL.md`: new Step P3.5 "Ladder-discipline check (semantic-edit audit)" between P3 and P4 in `--post-repair` mode. Audits L4 escalation (Repair Ladder Defense block, Phase A Exhaustion Record, Assumption-Extension Change Log, propagation) and L5 escalation (Repair Ladder Defense block, Phase A Exhaustion Record, Weaken-Claim Change Log, propagation). Phase A repairs require only the Repair Ladder Defense block. Scope is documentation and propagation, not re-design.

The thread remains at `019e7024-bea4-7171-aa11-4c352baebebe`.

---

## Round 4 dialogue (2026-06-09): why proof-writer still returns incomplete proofs

**threadId:** `019ed197-0450-78e0-b8e7-7d5207e8fa4f` (fresh thread)
**Model:** gpt-5.4 at `model_reasoning_effort: xhigh`
**Topic:** the skill still tends to return incomplete proofs (it gives up into a blockage report, or returns a package that looks done but has un-discharged gaps). Also: the file had grown to 447 lines, and length itself causes priority distortion.

### My opening diagnosis

The file was built almost entirely as a *prohibition system* (a long list of don'ts). Good at preventing confident fake proofs, but it manufactures the opposite failure via three mechanisms: (1) every hard exit is offered co-equal with completion ("fixed OR downgraded"; "COMPLETE PROOF OR BLOCKAGE REPORT") with no attempt budget, so quitting is the cheap compliant move; (2) the ~120-line Cited Results Audit sits BEFORE the Proof in the template, so attention is spent on citation provenance before the math; (3) no per-step completion ledger, so a gap survives because nothing enumerates it.

### Where Codex sharpened the diagnosis

- The deeper bug is **structural**: proof-writer was impersonating four skills at once — constructor, verifier, repair triager, and citation-compliance engine. The clean decomposition is `proof-writer = construct → close obligations → lint`; `proofcheck` = full audit; `proof-repair` = provenance-heavy repair + retrieval.
- **`Open Risks` is semantically poisonous** for a "complete proof" skill. The file simultaneously said fails must be fixed or downgraded AND that residual uncertainty may live in `Open Risks`. That mixed state is exactly how a proof "looks done" while still being open. Kill it.

### What converged

1. **Obligation Ledger** (the core lever, replacing my "step ledger + attempt budget"). Only the *nontrivial* obligations `O1..Ok`, each terminating in exactly one typed state: `CLOSED-LOCAL`, `CLOSED-CITED`, or `BLOCKED`. `BLOCKED` requires an attack record (exact statement, best bridge attempted, concrete failure reason, one alternative reduction considered), then isolation as a named conjectural lemma. Codex's key correction to my proposal: a "2 named techniques" attempt budget is theaterable; the right reconciliation of finish-incentive vs never-fake is **reward only typed closure objects, never prose completion**. You cannot prose your way into a typed closure, and the linter checks the typing.
2. **`Open Risks` killed.** Provable output ends with `Verification Checks`; non-provable ends with `Blockage Record`. A residual risk is a `BLOCKED` obligation, not a footnote.
3. **Two-dimensional honesty for citations.** Provability ≠ verification. A `CLOSED-CITED` obligation whose source was not inspected carries `source-status: unverified-source`, which caps the package at `Conditionally verified` (the existing status in `proof-closure-machinery.md`) — it may not be `Verified`. proof-writer closes local math + applicability; proofcheck upgrades source verification; proof-repair retrieves.
4. **`proof_gap_scan.py` two-tier linter.** Hard-FAIL (nonzero exit) only on the mechanically decidable set; advisory `CANDIDATE` for hedge phrases; a clean lint certifies closure, not correctness.
5. **Length.** Merge ANTI-SKETCH + HARD COMPLETION into one short termination rule; move Step 3.5 examples to `proof-strategy.md` (which already held richer versions in its Claim-Families table); replace the giant inline template with a short section order, Proof before any audit. Target 220-280; landed at 286 (from 447).

### Where I pushed back on Codex (Round 4)

**Pushback 1 — applicability is correctness, not bureaucracy.** Codex would have cut the Cited Results Audit to a 5-line table and pushed everything downstream. I argued trap #7 (imported-result applicability drift) makes the proof *wrong* and must live where the proof is written. **Codex accepted**: a `CLOSED-CITED` obligation is closed only by a compact inline applicability block (clause used, assumption map, conclusion fit, bridge ref when weaker-with-bridge, source-status) — only load-bearing imports get one. Pure provenance (version crosswalk, errata, lock-manifest, cache verification-states, retrieval handoff) leaves to proof-repair/proofcheck.

**Pushback 2 — the linter can hard-FAIL on structural incompleteness.** I argued *structural* incompleteness is mechanically decidable (BLOCKED under provable status, missing closure fields, undefined referenced IDs, weaker-with-bridge with no bridge, an obligation never terminated, blank verification checks) and may legitimately affect the exit code, distinct from judging whether the math is correct. **Codex agreed**, with a narrowing: keep the hard-fail set exactly that decidable list; hedge phrases stay `CANDIDATE` (too brittle to own exit status); and require canonical IDs so "referenced but never stated" is checkable.

### Where Codex held the line (and I accepted)

- Provability vs verification must stay two orthogonal dimensions. `unverified-source` cannot honestly coexist with a package labeled fully verified — it forces `Conditionally verified`. Refusing the second dimension would reintroduce the "looks done but isn't" failure for citations specifically.

### Files changed in this round

- `skills/proof-writer/SKILL.md`: rewritten 447 → 286 lines. New core mechanism `## The Obligation Ledger`; merged termination rule (replaces ANTI-SKETCH + HARD COMPLETION essays); inline applicability block as the `CLOSED-CITED` closure condition; `source-status` dimension; `Open Risks` replaced by `Verification Checks` / `Blockage Record`; section order fixed (Proof before audit); Step 3.5 examples removed in favor of the `proof-strategy.md` reference; `Bash` added to allowed-tools for the linter call; Step 7 now runs `proof_gap_scan.py`.
- `stat-shared-references/scripts/proof_gap_scan.py` + `proof_gap_scan_rules.py`: the two-tier structural linter (STRUCTURAL-INCOMPLETE affects exit, CANDIDATE advisory). Provenance stamp; exit 0/1/2.
- `tests/fixtures/proof_gap_scan/{clean_provable,incomplete}.md` + `tests/test_proof_gap_scan.py`: 14 stdlib unittests; all pass. The clean-fixture tests caught two real linter bugs during development (a `"Verified"`-is-a-substring-of-`"Conditionally verified"` ordering bug, and a `"Proof"` / `"Proof Strategy"` section prefix collision); both fixed.
- `stat-shared-references/proof-closure-machinery.md`: added the citation source-status → `Conditionally verified` mapping note under Verification Statuses.

The thread remains at `019ed197-0450-78e0-b8e7-7d5207e8fa4f`.
