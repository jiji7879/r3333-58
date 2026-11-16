# Complete classification of the monochromatic-triangle-free 3-colourings of
# K_16 and K_15, redone from scratch (member m4)

Result (this supersedes "the colouring of K_16 is unique"):

  K_16: exactly TWO good 3-colourings up to vertex relabelling and colour
        permutation: untwisted U with |Aut(U)| = 160, twisted T with |Aut(T)| = 32.
  K_15: exactly TWO: U-minus-a-vertex (|Aut| = 10) and T-minus-a-vertex (|Aut| = 2).

Method (a complete enumeration, not a search).

1. In a good 3-colouring of K_n, every colour degree is at most 5, because the
   colour-i neighbourhood of a vertex carries a good 2-colouring and R(3,3) = 6.
   For n = 16 the three colour degrees at a vertex sum to 15, hence all equal 5:
   every colour class is a 5-regular triangle-free graph on 16 vertices.
   For n = 15 they sum to 14 with each in [0,5], hence each lies in {4,5}.
2. nauty `geng` enumerates those graphs up to isomorphism: 388 of them for n=16
   (`geng -d5 -D5 -t 16`), 1,021,416 for n=15 (`geng -d4 -D5 -t 15`).
3. For each candidate class graph G, decide whether the complement of G admits an
   edge 2-colouring with no monochromatic triangle (equivalently: is G a colour
   class of some good 3-colouring). Done exhaustively by DPLL with unit
   propagation over the 3-clauses (C program `g2c6.c`, graph6 input, ~17 s for the
   1.02e6 n=15 instances). Exactly ONE candidate survives in each case:
     n=16: OsaBA`GP@`dIHWEcas_]O   (5-regular)
     n=15: N?`@F?kQcKBwsglCN@?     (5 vertices of degree 4, 10 of degree 5)
4. Enumerate all good 2-colourings of the complement of that one graph (72 in each
   case), turn each into a 3-colouring, and group by colour-preserving
   isomorphism (exhaustive backtracking). Two classes each, with |Aut| 160/32
   (n=16) and 10/2 (n=15).

Reproduced templates: artifacts/k16_template_U_aut160_m4.col,
k16_template_T_aut32_m4.col, k15_template_Uminus_aut10_m4.col,
k15_template_Tminus_aut2_m4.col. All four verified triangle-free by my
bit-parallel checker.

Cross-check with the literature: M. Tatarevic, arXiv:2610.36648v2, Theorem 2.1
(attributed to Kalbfleisch-Stanton and Heinrich) states exactly two good
3-colourings of K_16, U and T, and Lemma 2.2(b) gives |Aut(U)| = 160,
|Aut(T)| = 32, with U- and T- keeping 10 and 2. All four numbers match.

Structural consequence worth using: in EVERY good 3-colouring of K_16 all three
colour classes are isomorphic to the single graph G16 = OsaBA`GP@`dIHWEcas_]O,
and in every good 3-colouring of K_15 all three are isomorphic to the single
graph G15 = N?`@F?kQcKBwsglCN@?. So a critical link (15 or 16 vertices) in any
hypothetical K_51 colouring is rigid up to that fixed graph, but there are two
ways to 3-colour it, not one.
