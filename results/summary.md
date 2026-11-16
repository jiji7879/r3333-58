# R(3,3,3,3): what two swarm runs established (and did not)

Two Ultramath runs, 8 members each, model deepseek-v4.1-flash at max reasoning effort
(ids smwiiyj7u, stopped by request; smwikrjou, ended with budget spent). Target: a
4-colouring of K_51 with no monochromatic triangle, i.e. R_4(3) >= 52.

## Answer to the question asked

The lower bound was **not** improved. No valid 4-colouring of K_51 was found, and no
proof that none exists. What the runs did produce is a precise map of why the obvious
routes are closed, and a certified body of negative results. Bounds stand at
51 <= R_4(3) <= 60 (the upper end is a Nov 2026 preprint, arXiv:2610.36648, not yet in
Radziszowski's survey DS1.18, which still says 62).

## Established, and checked

1. **R_4(3) >= 51 is a theorem of Lean 4** in kernel mode (no `native_decide`, axioms
   [propext, Quot.sound], 4 min). Three pairwise non-isomorphic K_50 witnesses in
   `artifacts/`, all verified by two independent checkers.
2. **Accepted theorem (m1).** Every monochromatic-triangle-free 4-colouring of K_n with
   n >= 51 is *primitive*: no nontrivial module partition, hence no substitution, blow-up
   or Abbott-type product construction. Proof: for a module part P with cut-colour count
   j, n - s <= 16j and s <= R_{4-j}(3) - 1, so n <= 32, 37, 50, 65 for j = 1..4 and
   j = 4 forces s = 1. Sharp: 50 = 3R_3(3) + R_1(3) - 4 is one below Chung's recursion,
   and a K_32 module colouring attains the j = 1 bound.
3. **Anabanti (2023)**: the bound 51 cannot be improved by group-partition/Cayley means.
   Together with (2), the two classical construction techniques that could have reached
   52 are closed.
4. **No triangle-free K_51 within Hamming distance 5** of the 1-defect record
   (873M-node exhaustive chain search, validated against brute force). The record is the
   best object known: exactly one monochromatic triangle, {48,49,50} in colour 1, and it
   sits on a defect-1 plateau (37 colourings at distance 1, 680 at distance 2).
   Note the exact sphere counts killed an earlier "isolated local minimum" claim.
5. **~14,700 DRAT-certified exclusions**, all with encoding audits: 6,050 one-/two-vertex
   extension instances (no valid K_51 restricts to these K_50/K_49 bases), 4,855
   frozen-edge repairs and 3,825 multi-vertex extensions around the record, 13 large
   star-family exclusions. Samples re-verified independently by three different members
   and by the judge with a from-scratch encoder.
6. **Lean-checked structural lemmas** used by every case split: every colour-degree lies
   in [2,16], d_a + d_b >= 18, every 6-set uses >= 3 colours, no twin pair, every 17-set
   meets all four colours.
7. **Profile counts**: exactly 47 admissible colour-degree profiles at n = 51 and 6 at
   n = 60 (the latter matching the preprint's list).

## Refuted during the runs (all caught by cross-checking)

* "A prime-order automorphism has order 2 or 5" (m8): rests on between-orbit constancy,
  false — the invariant is the cyclic difference. Counterexample at n = 10, and m3's
  Lean `orbit_pair_diff` gives the correct form. Withdrawn.
* "Exact defect landscape, isolated local minimum at the record" (m4): the chain
  reduction gives only triangle-free exclusions, not per-sphere minima. Corrected.
* "The K_16 link is unique up to isomorphism" (early m1): the literature has two,
  untwisted and twisted; m5's enumeration settled it (2 classes, |Aut| = 160 and 32).
* "Link alphabet has 12 types at m = 14": counts only restrictions of the two K_16
  templates; the true count is larger (literature: 115).

## Still open / not established

* No K_51 colouring; no proof of R_4(3) = 51. The conjecture is untouched.
* "Every valid K_51 colouring has trivial automorphism group": the prime-order sweep was
  not completed (undecided (p,f) cases; the p = 2 quotient in particular).
* Whether a *modular* K_50 exists (sharpness of theorem 2 at n = 50).
* The upper bound 60: profile skeleton verified, its 296,081 SAT refutations not
  reproduced (two solvers, no DRAT).

## Files

* `results/literature_status.md` — verified state of the art with sources.
* `artifacts/` — all colourings (three valid K_50, the 1-defect K_51 record, K_16/K_15
  templates, a K_32 module witness), each passing `tools/verify_coloring.py`.
* `.ultramath/smwiiyj7u/m2/lean/` — kernel-mode Lean development and the certificate
  pipeline (`gen_cert.py`).
* `.ultramath/smwikrjou/m4/LEDGER.md` — the audit ledger: every claim sorted into
  machine-checked / DRAT-certified / encoding-level / withdrawn.
