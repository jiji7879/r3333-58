# Manuscript

`main.tex` is the working paper source; `main.pdf` is the compiled draft.
`references.bib` contains the external references. The paper states the
certified common-critical theorem and its reciprocal-profile consequence without
claiming `R(3,3,3,3) <= 58`.

Build from the repository root:

```sh
bash paper/build.sh
python3 paper/check_claims.py
```

The build requires `latexmk`, pdfLaTeX and BibTeX. It writes temporary files
under `.scratch/manuscript/` and copies only the finished PDF to `paper/main.pdf`.
The numerical script uses the Python standard library. It recomputes the eleven
degree profiles and the two reciprocal candidates, and checks the arithmetic in
`status-2026-11-25.csv` and `../results/common-critical-audit-2026-11-25/full-replay.log`.
It does **not** solve cases, replay DRAT proofs or validate the owner-reported
ledger statuses.

After building the base Lean development, the supplementary conditional profile
statement can be checked from the repository root with:

```sh
LEAN_PATH="$PWD/lean:$LEAN_PATH" lean paper/lean/ReciprocityBoundary.lean
```

Its common-critical theorem is an explicit premise, not an assertion that the
496 finite refutations have been formalised. `VERIFICATION.md` records the checks
rerun while preparing this draft and their provenance limitations. `OUTLINE.md`
and `METHODOLOGY.md` are older planning records; `main.tex` is authoritative for
the current paper.

Before external submission, replace the working author line with the human
authors, affiliations and contribution statement, and review the trust boundary
in the abstract and Sections 3, 6, 7 and 8.
