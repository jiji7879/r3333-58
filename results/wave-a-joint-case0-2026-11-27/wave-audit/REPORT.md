# Wave A six-rule audit: what is supplied, what the table implies, and what I could check

Direction d2 (m2): **rule semantics and symmetry**, not joint two-vertex
compatibility. Everything below is a statement about the six rows of
`attachments/let-s-try-and-rbdv/WAVE_A_RULES.md` (the only Wave A text in this
repository), not about any branch, parent or child of the K58 wall.

## 1. The Wave A JSON/source is not supplied (verified absence)

Searched, in the project root: all 116 `*.zip` member listings, and the whole
text tree with `rg -u --hidden` (so `attachments/`, `.scratch/`, `.ultramath/`
included) for `waveA`, `wave_a`, `wave-a`, `?0201`, `??120`, `?1?01`, `1221?`,
`553721`, `819552`, `852674`, `838094`, `donor index`, `outside mask`,
`four-outside`.  Additionally scanned every member of the eight most recent
K58 attachment zips (`K58_full_cover_local_witnesses`, `K58_case0`,
`K58_cube_conquer_verification`, `K58_adaptive_wall_solver`,
`K58_wall_sweep_evidence`, `K58_square_six_rules`, `K58_two_arm_compatibility`,
`K58_reviewer_quickstart`) for the byte strings `waveA`, `?0201`,
`four-outside`, `outside_mask`: **no hit**.

So the following are **missing**, and nothing in this report presumes them:

1. the six rule JSON files (`waveA-13-00201-…` … `waveA-14-01012-…`) with their
   source query and binary RUP digests;
2. the "source folder" with the physical vertex map, physical colour map and
   the three exact target-query digests;
3. the rule-generation code that turns a proved RUP core into a mask row and
   its 20 relabelings;
4. whatever "Donor index" indexes (values 553721, 819552, 852674×3, 838094
   exceed every case index in `release/` and every representative table I
   could find, so no local table resolves them);
5. the ledger rows behind "466,544 exclusions at one common depth of two /
   225,119 weighted representatives", and the "0 first-word exclusions".

Consequences, stated plainly:

* I cannot replay any Wave A RUP digest, and I do not claim the six rules were
  proved by whoever produced them.
* I cannot check the *physical* transfer (actual revised owner, nominated
  vertices, palette) at all.
* **Nothing in this repository currently ties the Wave A masks to any encoding.**
  No CNF, generator, ledger row or solver script in the tree mentions the masks.
  As supplied, Wave A is six rows of *rule metadata*; full-rule generation is
  not supplied.

## 2. What the table itself fixes (and what it leaves open)

Each row is four masks of five entries over `{0,1,2,?}`, one entry per pentagon
vertex, giving the colours of the four spokes from four distinct outside
vertices. Checks that pass on the table as given (`src/waveA_audit.py`):

| row | min arm | masks | donor | smaller | arm−smaller |
| ---: | ---: | --- | ---: | ---: | ---: |
| 0 | 13 | `?0201 ?1?01 10010 1??20` | 553721 | 12 | 1 |
| 1 | 14 | `??120 10010 1?1?? ??2??` | 819552 | 13 | 1 |
| 2 | 14 | `?1?01 1?1?2 1221? 21??1` | 852674 | 13 | 1 |
| 3 | 14 | `01?10 01?01 1?1?? 12?1?` | 852674 | 13 | 1 |
| 4 | 14 | `01?10 1??22 12?1? 201?0` | 852674 | 13 | 1 |
| 5 | 14 | `01?1? ?1?21 1??22 1201?` | 838094 | 13 | 1 |

* 6 rows, 4 distinct masks each, all length 5 — yes, 6/6.
* `smaller = min arm − 1` — yes, 6/6.
* The certificate names carry four 5-digit masks each (e.g.
  `waveA-14-00120-10010-10102-12210`). In every row those resolved masks refine
  the displayed mask entry by entry, i.e. the name is exactly the displayed
  pattern with every `?` filled in. 6/6 consistent.

Left open by the text, and therefore declared as my reading (R_i):

* **mask position** `i` = the spoke to pentagon vertex `i` in the cycle order.
  Any dihedral re-indexing is immaterial: it relabels pentagon vertices and the
  formulas below are isomorphic.
* **arm of size n** = the n vertices joined to a common root in one colour, so
  their internal edges use only the other three colours and carry no
  monochromatic triangle (this matches the repository's own use of "arm" as a
  colour class of a vertex's neighbourhood, e.g. `review/WALL_STRUCTURAL_NOTE.md`
  §"arm c has at least t_c", and the "nominated 14-vertex arm (91 edges)" of
  `results/local-cover-audit-2026-11-27/REPORT.md`).
* the pattern's nine vertices **are arm vertices** (the four are "outside" the
  pentagon, not outside the arm), and the remaining `n−9` arm vertices are free.

An important negative: `?` is *not* shorthand for 0. Per-mask wildcard domains
from the pentagon alone already allow two or three colours in many positions
(full table in `out/waveA_audit.json`, key `wildcard_domains`), e.g. `??2??`
allows `{0,1}` at position 0 and `{0,1,2}` at position 1. Any encoding that
silently resolves `?` to a fixed colour would be *unsound*; resolving it to 0
happens to be what the certificate names do, which is a coincidence of the
donor patterns, not a rule.

## 3. The six rows are not relabelings of one another

Patterns are compared as multisets of masks (the four outside vertices are
unlabeled). Actions: the pentagon dihedral group `D5` (order 10) on positions,
times a palette group on colours. Computed orbit sizes, all six rows:

| palette group | order | orbit size per row | pairwise orbit intersections | cross-row subsumption |
| --- | ---: | --- | --- | --- |
| `{id}` | 1 | 10 | none | none |
| `{id,(0 3)}` | 2 | **20** | none | none |
| `{id,(1 2)}` | 2 | **20** | none | none |
| `{id,(0 3),(1 2),(0 3)(1 2)}` | 4 | 40 | none | none |

So "all twenty simultaneous pentagon and palette relabelings" is arithmetically
exactly a `10 × 2` group: the pentagon has no stabilizer in any row (orbit size
equals group order), and the palette factor must have order 2. The two
order-2 candidates are swapping the two colours the pentagon does not use
(natural in a four-colour setting: the arm's third colour is 0 or 3) or
transposing the pentagon's own colours (which turns "cycle 1, diagonal 2" into
"cycle 2, diagonal 1"). The text does not say which; §4 tests both.

No pairing of rows is related by a relabeling and no row's relabeling is a
specialisation of another row (subsumption test: a pattern `P` is implied by a
more general `P'` iff every mask of `P` refines some mask of `P'`). The six rows
are therefore six independent rules: under a `Z2` palette reading they are
`6 × 20 = 120` distinct forbidden patterns.

## 4. The stated arm bounds are correct and tight for the displayed masks

Test (`src/arm_extension.py`): is there a triangle-free 3-colouring of a
complete 3-coloured `K_n` containing the pattern? Encoding: one variable per
(edge, colour); per edge at-least-one + at-most-one; unit clauses for the ten
pentagon edges and every specified mask entry; per colour and triangle one
"not all three equal" clause. Since deleting a free vertex from a realisation
at `n` realises the same pattern at `n−1`, satisfiability is monotone in `n`, so
`n = min arm` is the sharp test of "an arm of at least the stated size cannot
realize the pattern".

Result, all six rows, solver cadical 2.1.2, refutations replayed by drat-trim in
binary RUP mode:

| row | n = min arm | vars / clauses | cadical | drat-trim `cnf proof -i -U` |
| ---: | ---: | --- | --- | --- |
| 0 | 13 | 234 / 1195 | UNSAT 0.014 s | rc 0, one `s VERIFIED`, 0 warnings |
| 1 | 14 | 273 / 1477 | UNSAT 0.182 s | rc 0, one `s VERIFIED`, 0 warnings |
| 2 | 14 | 273 / 1479 | UNSAT 0.247 s | rc 0, one `s VERIFIED`, 0 warnings |
| 3 | 14 | 273 / 1479 | UNSAT 0.324 s | rc 0, one `s VERIFIED`, 0 warnings |
| 4 | 14 | 273 / 1480 | UNSAT 0.083 s | rc 0, one `s VERIFIED`, 0 warnings |
| 5 | 14 | 273 / 1479 | UNSAT 0.273 s | rc 0, one `s VERIFIED`, 0 warnings |

and at `n = min arm − 1` every row is **SAT**, with the model parsed from
cadical and re-checked by an independent routine (`check_assignment`) that
requires all `C(n,2)` edges coloured, the pentagon cycle/diagonal colours, every
specified mask entry, and no monochromatic triangle among all triples:

| row | n | model | edge count | mono triangles | sha256(model)[:16] |
| ---: | ---: | --- | --- | --- | --- |
| 0 | 12 | SAT, checked | 66/66 | 0 | `9e6a94c0d89c3479` |
| 1 | 13 | SAT, checked | 78/78 | 0 | `f104830a6663bc52` |
| 2 | 13 | SAT, checked | 78/78 | 0 | `84ddc58c2e0ed66b` |
| 3 | 13 | SAT, checked | 78/78 | 0 | `c1a0bd74f3fc0406` |
| 4 | 13 | SAT, checked | 78/78 | 0 | `4bcafa141503b252` |
| 5 | 13 | SAT, checked | 78/78 | 0 | `844bb119b88d4c8c` |

Total solver time for all twelve instances: 1.1 s cadical plus about 1 s
drat-trim. So, under reading R_i, the six stated minimum arm sizes are not
merely sufficient but exact: one vertex fewer and the displayed pattern is
realised.

Palette transposition (`?`-patterns with `1↔2` swapped, pentagon cycle colour 2
and diagonals 1 — a genuinely different pattern in a fixed palette, not a
relabeling of my CNF): all six are again UNSAT at the same `n`, each with the
same drat-trim conditions met (`out/arm_extension_swap12.json`). The `(1 2)`
half of the "palette relabelings" therefore holds at the arm level too; the
`(0 3)` half is a pure relabeling of the arm's palette and carries no content of
its own.

## 5. What this does and does not settle

Established here (independently, from the table text alone):

1. The six rows are internally consistent, mutually inequivalent, and generate
   120 distinct patterns under a `Z2` palette reading.
2. For each row, the displayed mask pattern (wildcards included) is realisable
   by a triangle-free 3-colouring of a complete 3-coloured arm of size
   `min arm − 1`, and not realisable at `min arm`. Both directions are
   machine-checked: explicit checked models, and cadical refutations replayed by
   drat-trim in binary RUP mode with `-i -U`, rc 0, exactly one `s VERIFIED`,
   zero warnings.
3. Therefore the *displayed* masks cannot be a strengthening of the underlying
   proof hypotheses in the way that would make them unsound as exclusions: as
   exclusions at arm size ≥ 13/14 they are true statements under reading R_i.

Not established, and not implied by anything above:

* No Wave A RUP digest was replayed; no physical transfer (revised owner,
  nominated vertices, palette) was checked; the missing JSON and source folder
  are what would settle both.
* A local arm exclusion is not a branch, child or parent refutation. Nothing
  here says any of the 28 pivot-colour branches is UNSAT, or that any joint
  choice at two second-arm vertices `w1, w2` is incompatible. In particular the
  individual-per-`w` models and the joint question are untouched.
* Whether Wave A participates in an encoding at all: no supplied artifact shows
  that it does (see §1). If a future encoding adds these masks as clauses, it
  must also carry the arm-size pin (13/14) and the exact mask variables; the
  masks alone, at a smaller arm, are satisfiable — §4 exhibits the models.

## 6. Reproduction

```
python3 src/waveA_audit.py            # table parse, local models, orbits   (~0.05 s)
python3 src/arm_extension.py all      # 6 rows x {n, n-1}: CNF, cadical, drat-trim
python3 src/arm_extension.py swap12   # palette-transposed test
```

`bin/drat-trim` is built from `src/drat-trim.c` (Heule/Wetzler, last edit
2024-04-21) with `gcc -O2`. Two quirks of this build, both hit during the work:

* it reads the two file arguments from `argv[1]`/`argv[2]`, so the files must
  come **before** the flags: `drat-trim CNF PROOF -i -U`, not `-i -U CNF PROOF`;
* a formula that unit-propagates to a contradiction is reported as
  `c trivial UNSAT` / `s VERIFIED` and the program returns **1**, because the
  status variable is not set on that path. None of the six instances above takes
  that path: all replay through backward checking and return 0.

Files: `src/waveA_audit.py`, `src/arm_extension.py`, `out/waveA_audit.json`,
`out/arm_extension_all.json`, `out/arm_extension_swap12.json`, per-instance
`out/row*.cnf` and `out/row*.drat`.

### Controls run on the same encoding

* Pentagons only (five cycle-1/diagonal-2 edges, no outside vertices pinned) is
  **SAT at n = 13 and n = 14**, model checked. So the six UNSAT answers above
  are caused by the masks, not by the pentagon.
* The same encoding reproduces the classical threshold in the small: a
  3-coloured complete graph with the pentagon pinned is SAT at n = 16 (model
  checked) and cadical reached no answer at n = 17 inside 25 s (UNKNOWN — no
  claim; this is only a plausibility check that the encoding is not broken in
  the obvious direction).
