# The two good 3-colourings of K_16 (templates U and T), extracted and checked

Files: `k16_template_U_aut160_m4.col`, `k16_template_T_aut32_m4.col`
Format: first line `16 3`, then 16 rows (entry (i,j) = colour of edge {i,j}).

Both pass `tools/verify_coloring.py`-style checking (my bit-parallel `verify2`):
0 monochromatic triangles.

Provenance: they are the colour-1 link of vertex 0 and the colour-2 link of vertex 48
of the *verified* K_50 `artifacts/k50_z4z4_m6.col` (member m6's certificate, which I
re-checked). So both templates occur inside one valid (3,3,3,3;50)-colouring.

Identified against the literature by automorphism-group order:
  |Aut(k16_template_U_aut160_m4.col)| = 160   (untwisted U)
  |Aut(k16_template_T_aut32_m4.col)|  =  32   (twisted T)
computed by exhaustive backtracking over colour-preserving position permutations.
This matches M. Tatarevic, arXiv:2610.36648v2, Theorem 2.1 and Lemma 2.2(b)
(he attributes Theorem 2.1 to Kalbfleisch and Stanton, and Heinrich): up to vertex
relabelling and colour permutation there are EXACTLY TWO good 3-colourings of K_16,
U with |Aut(U)| = 160 and T with |Aut(T)| = 32; every good 3-colouring of K_15 is
obtained from one of them by deleting a vertex.

The two are NOT isomorphic as edge-coloured graphs: proven by an exhaustive
backtracking isomorphism search (`.ultramath/smwiiyj7u/m4/coliso.py`, which finds
witnesses for isomorphic pairs, e.g. two links of the same type from one K_50);
consistent with networkx VF2 and a colour-sensitive Weisfeiler-Lehman hash.
Note that their colour-0 class graphs ARE isomorphic as abstract graphs, and the
spectra of all unions of two colour classes coincide — the difference is genuinely
in how the three colours are distributed.

Consequence worth knowing: any argument of the form "the link of a degree-16 vertex
is rigid/unique" is false; there are two link types, and both can appear in the same
colouring.
