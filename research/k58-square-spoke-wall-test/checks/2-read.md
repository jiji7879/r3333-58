# Line-by-line reading of the clean scoped proof

Scope: exact supplied K15 matching CNF and exact 14 first-tier parents, plus
separate 13 full-root empirical controls. The end claim is deliberately not a
whole parent, wall row or Ramsey theorem.

1. Root-group cap: for a colour-$c$ neighbour in group $b$, every internal
   edge excludes $b$ by triangle $(0,v,w)$ and $c$ by triangle $(x,v,w)$.
   This yields a 2-colouring and cap five with no classification of arbitrary
   K15/K16 templates required.
2. Special four-set: all valid K5 two-colourings have each colour on a C5;
   deleting one leaves two P4s. A square plus matching therefore lies in a
   group with exactly four vertices. With 14 non-root colour-$c$ neighbours
   across three groups of cap five, the others together have ten and each
   must have five. More than 14 neighbours can be thinned to a 14-vertex
   selection with the same property, so the assumption is a faithful local
   relaxation rather than an assertion that total degree is exactly 15.
3. Permutation coverage: every labelled valid K5 graph and every independent
   palette-first cycle walk is normalized at the full CNF level. Palette-first
   is actual colour 0 for BOTH groups. No global colour swap is smuggled into
   these five-group maps. The six four-group square/matching cases and the
   colour/group exchange are covered independently. They operate on disjoint
   pin groups and compose; cross-group constraints remain unchanged.
4. Formula sufficiency: native proof and independent strict RUP establish the
   ENTAILED inequality on the exact 315-var/1,825-clause relaxation. A
   colouring with the guard and four matching spokes would restrict on
   $\{r,x\}\cup A$ for suitable 14 other neighbours to such a normalized
   colouring, contradiction. No need to know or reproduce the rest of the K58
   colouring inside K15.
5. Entailment signs: since guard plus four positive spokes is impossible,
   $\neg g\lor\neg E_1\lor\neg E_2\lor\neg E_3\lor\neg E_4$ follows. If an
   original positive spoke is pinned, removing that negative literal preserves
   the implication. A different-colour unit makes the target positive spoke
   false, so omitted full candidates do not evade the proof.
6. Boundary data are existential local objects, not rows: K15-path SAT and
   K14 square/matching SAT do not contradict UNSAT at the intended K15
   square/matching template and do not promote themselves to K58 geometry.
7. Ordinary set completeness: complete regenerated emitted-set comparison
   corrects the stock verifier's count-only gap. Original-parent status OPEN
   remains unknown. There is no invocation of a parent refutation unless an
   actual parent/query/proof tuple is cited.
8. Historical count corrections: 13 rows, not 14; 728 keys checked against
   guard values, not sender map keys; bounded subcube calls have no minimality
   conclusion. Extra propagation is not refutation.

Every number in the ordinary table of `audit.md` was recomputed from retained
row receipts: 7,831+1,446=9,287, 4,807 survivors, ten gain rows and four
zero-gain rows. The corrected copy of m3's small RUP diagnostic is recorded
rather than hidden. There is no unchecked remaining case in the scoped
normalization implication.
