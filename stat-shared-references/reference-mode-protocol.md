---
artifact: shared_reference
scope: reference_mode
generator: extracted from proof-repair 0B + proofcheck Pass 0 per Codex threadId 019fa42e-217f-7171-b94f-99b95177aab8 (cross-skill protocol spillover)
---

# Reference Mode Protocol

Single source of truth for one-file vs two-file submission handling. Consumed by
`proof-repair` (before writing any LaTeX patch), `proofcheck` (Pass 0 indexing), and
`theory-simulation` (when placing figures and tables).

The detection itself is mechanical and already implemented:
`scripts/proof_index.py` reports `reference_mode` and flags `cross_file_ref_leak`. Run
the script rather than re-deriving the mode by hand.

## The two modes

**Mode A: single-file** — one `.tex` compiles to one PDF (most arXiv preprints,
NeurIPS / ICML / ICLR). Use `\label`, `\ref`, `\eqref`, `\cref` freely; every new lemma
or equation gets a `\label`.

**Mode B: two-file** — `paper.tex` plus `supplement.tex` (or `appendix.tex` / `supp.tex`)
compile to two separate PDFs. Standard for JASA, AoS, Biometrika, JRSS-B, Econometrica,
JBES.

## The rule that matters

LaTeX `\ref{}` does **not** resolve across separately compiled files (absent the fragile
`xr` package). In Mode B:

- within the same file → `\ref{...}` as normal;
- across files (main ↔ supplement) → **never** `\ref{}`; it will not compile;
- cross-file citations use hard-coded numbers: "Lemma S.3", "Theorem 2.1 of the main
  text", "equation (S.7)".

Any patch that inserts a cross-file citation must know the supplement's numbering scheme
so it writes the right hard-coded number. `proof_index.py` flags a broken cross-file
`\ref`; a human confirms the replacement text reads correctly.

## Detection

```bash
python ../stat-shared-references/scripts/proof_index.py \
    --main papers/<name>/paper.tex \
    --supplement papers/<name>/supplement.tex \
    --supplement-mode separate-self-contained
```

Manual fallback signals, if the script cannot run: multiple top-level `.tex` files with
parallel content (one short "main", one long "supp"); an "Online Supplement" or
"Supplementary Material" section at the end of the paper; `S`-prefixed labels. When two
`.tex` files exist with parallel content, treat as Mode B and confirm with the user.

## Where to record it

```markdown
## Reference Mode
Mode: [A: single-file / B: two-file main+supplement]
Files:
  - paper.tex (main text)
  - supplement.tex (supplementary material)  [Mode B only]
Numbering scheme (Mode B):
  - Main text: 1, 2, 3, ...
  - Supplement: S.1, S.2, S.3, ...
Cross-file citation style: hard-coded numbers + "of the supplement" / "of the main text"
```

## Patch numbering discipline (Mode B)

A patch that adds a numbered object to the supplement shifts every later number in that
file. Before writing the patch, read the current numbering, insert at a position whose
downstream renumbering you have accounted for, and update every hard-coded cross-file
citation that points past the insertion. Re-run `proof_index.py` after patching; a new
`cross_file_ref_leak` or a stale hard-coded number is a patch defect, not a compile
warning.
