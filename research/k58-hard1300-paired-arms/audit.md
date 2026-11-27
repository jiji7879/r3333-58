# Paired-arm clauses: mathematical form and package audit

## Verdict

The proposed general form is correct **under the stated root-arm guard and
neighbourhood conditions**. The package instantiates it with **16,530 row-
specific ternary clauses in 1,236 of the 1,300 inputs**. All 1,300 reconstructed
full-root inputs and the full census regenerate exactly, and all 14 supplied
physical implications pass strict native proof replay.

This is not a universal arbitrary-graph degree lemma, a proof that every guard
is active, a row closure, or a Ramsey bound. It is a useful conditional
clause-generating mechanism with a real counting proof and a modest set of
actual physical certificates.

## 1. Why the other-arm neighbourhood has at most five vertices

Let \(a\) lie in the root arm of colour \(c\), and consider another root arm
\(B\), of a different root colour \(b\). The cap comes from triangle structure,
not from choosing a particular K15/K16 template.

A neighbour \(v\in B\) with \((a,v)=c\) contributes to two relevant possible
triangles with root vertex 0. Its mutual edges inside \(B\) cannot have colour
\(b\) (since \((0,v)=b\)), nor colour \(c\) (since \((0,a)=c\)). Mutual edges
within a colour-\(c\) neighbourhood therefore use only the remaining two local
colours. Six such neighbours would form a two-colour triangle-free \(K_6\),
which is impossible by \(R(3,3)=6\). Hence **no other arm can supply more than
five vertices** to the colour-\(c\) neighbourhood at \(a\).

The package independently verifies the central finite case: all **32,768**
edge-colourings of \(K_6\) have a monochromatic triangle. It also checks all
**48** `size in {15,16}`, `kind in {U,T}`, ordered `b != c` template/colour
combinations for their internal triangle-free and five-set structure.

The five-set enumerator must be fresh per row:

- `catalog(n,kind,b,c)` uses `named_template(n,kind,b)`, whose permitted
  internal colours already exclude the arm colour \(b\), and excludes any set
  with an internal \(c\)-edge. It gets the intended two-colour local structure,
  not a generic “independent set” count;
- the chosen five-sets are filtered by positive fixed spokes and all negative
  or differently-coloured fixed spoke variables on the current root/cube;
- an arm which lacks a classified template still cannot supply more than
  five vertices, for the same two-colour Ramsey argument. Classification is
  needed to enumerate its alternatives, not for the global counting bound.

## 2. The ternary and hitting-set consequences

Write \(g=g_{a,c}\) for the condition, as encoded, that at least 14 neighbours
of colour \(c\) for \(a\) lie outside its own root arm, excluding the root. In
the supplied full-root encoder this is exactly what
`marked_threshold` constructs:
`needed = 14`, coloured other-arm candidate spokes \(E_{a,y,c}\), excluding
\(y=0\), with a `CardEnc.atleast` requirement on an explicit guard literal.
Already fixed spokes reduce the needed count appropriately. The proof uses the
forward implication \(g\Rightarrow\text{at least 14}\); it does not claim that
this guard is forced true in every model or even in every owner.

Choose two arms \(B_1,B_2\), with \(B_3\) the third. If \(H_i\) hits every
feasible five-neighbourhood inside \(B_i\), then

$$
\neg g\ \lor\ \bigvee_{v\in H_1\cup H_2} E_{a,v,c}.
$$

Indeed, suppose \(g\) is true and every positive edge literal to every
\(v\in H_1\cup H_2\) is false. On each chosen arm, any feasible five-
neighbourhood must include a member of its hitting set, so it cannot occur.
The chosen arms consequently supply at most four vertices each. The third
supplies at most five; \(4+4+5=13\) contradicts \(g\). The singleton choice in
the proposed ternary formula is exactly this argument.

Useful special cases follow without changing the mechanism:

- if an arm cannot supply five, it supplies at most four, so \(g\) forces five
  from each other arm (and a common mandatory vertex there can yield a binary
  clause);
- if no singleton is common to all feasible five-sets, a nonempty hitting set
  provides a longer but equally valid disjunction;
- if already fixed spokes already realise a five-set, that arm is satisfied;
  the source treats this empty-residual case separately, not as another
  missing single vertex.

The package's `census.py` implements exactly the singleton case: compute the
intersection of compatible local five-sets after removing already-required
spokes, require it to be nonempty for both arms, and take the cross product of
those unfixed singleton literal sets. It also filters impossible count ranges
and differently coloured fixed spokes. Cross-arm pairs are distinct physical
alternatives; the count is not a number of verified rows or of global Ramsey
certificates.

## 3. Cube-and-conquer scope

A learned \(H_i\) depends on what currently remains feasible. If it is valid
only after a cube \(Q=\ell_1\land\cdots\land\ell_k\) fixes further
constraints, then \(Q\) proves the short implication. At parent level, the
valid weakened clause is

$$
\neg Q\ \lor\ \neg g\ \lor
\bigvee_{v\in H_1\cup H_2} E_{a,v,c},
$$

where \(\neg Q = \neg\ell_1\lor\cdots\lor\neg\ell_k\). It preserves the parent
statement rather than claiming the stronger clause outside \(\mathcal Q\).

Recomputing compatibility under the cube is essential; a vertex common to
fewer surviving alternatives need not have been common to all possibilities
before the cube narrowed them. Guard identifiers, physical vertex numbers,
colour names and local arm choices are likewise not free-floating reusable
constants. The catalogue is **guarded, row-specific logical content**, not a
single schema that can be copied blindly to another root. Further compatible
embeddings are not ruled out by this search, which was designed for sufficient
conditions.

## 4. What the full package recomputation establishes

The `hard1300.tsv` identifiers bind each row by family, placement and charge.
The formula fingerprint is recomputed from these three fields. The whole run
was done in a new directory so that supplied measurement files were not
overwritten. Results:

- all **1,300/1,300 full-root CNF SHA-256 values** match the supplied input
  hashes, using the pinned existing `python-sat 1.9.dev22` environment;
- all **48** template/colour combinations pass the triangle and pentagon
  consistency checks;
- all **32,768 \(K_6\)** edge colourings check as expected;
- the regenerated per-row vector is **byte-for-byte JSON identical** to the
  supplied `ternary-counts.json`, with **1,300** entries, **1,236** nonempty
  rows, range **0–33**, total **16,530** ternary clauses.

Thus the *metadata instantiation* of the counting argument is checked for the
whole stated cohort. It is not a claim of 1,300 independent SAT refutations.
The TSV's historical byte total (191,031,232,170) does **not** mean those
historical proof bytes are present or replayed in this package. This archive
contains new small proofs for its selected instances.

## 5. Actual physical proof evidence and the search limits

The 14 matched physical cases have ranks

```text
1, 8, 28, 146, 522, 636, 677, 708, 728, 747, 924, 959, 1121, 1231
```

They all use sender 48 and targets 19/35 under colour 3. Each verifier rebuilds
its particular full-root parent, retrieves the guard literal for sender 48,
and tests the intended false cube of the learnt implication. For rank 1,
clause `-25165 3764 5652` becomes units `25165, -3764, -5652`, reinforcing
that the signs in the exported implication are interpreted in the natural
(not negated) direction.

Each one of the 14 checks matches the specified query/proof SHA-256. Fresh
binary-input drat-trim with no warning suppression verifies all 14, with
return code 0 and exactly one `s VERIFIED`, no warnings/errors, full proof-file
read counts, and `0 RAT lemmas in core`. The total is **32,972 proof bytes**.
The supplied metadata records 840 discovery conflicts over all 14; that is a
recorded search statistic, not a new performance measurement by this reviewer.
The little proofs validate real physical implications. They do not by
themselves prove the other 16,516 generated clauses by explicit replay.

The broader validity claim for them rests on the **general mechanical count
and exact regenerated guard/five-set rebindings**, not on a bogus universal DRAT
trace or on an interpretation of OPEN as SAT/UNSAT.

All six advertised complete parents at 60,000 conflicts reach their limits
for stock, direct-hit-set and extended-selector encodings. The separate
ternary-only four-row panel likewise returns OPEN throughout. At **800,000**
conflicts, ranks **1200 and 1300** also remain OPEN under stock, direct and
extended encodings. Those CPU times are recorded single-seed measurements, not
non-existence or time-to-solve conclusions. Direct clauses are valid
implications; auxiliary-selector extensions preserve original models by choosing
realised supports for the new variables, but none of these observations offers
a solver speed-up guarantee.

## 6. What can reasonably be claimed now

A validated reusable theorem family exists here:

$$
\boxed{\text{If }g_{a,c}\text{ is active, at least one target spoke in every
chosen two-arm hitting set has colour }c.}
$$

Its importance is a large, systematically derivable **local preprocessing
space**. This may help root/provider branching, but does not turn clause counts
into progress on the unresolved wall. The published search data specifically
fails to show a conclusion at the tested budgets. Any next experiment needs
actual original-parent validation and matched solver outcomes, not simply more
clauses or cold single-seed timings.

Native proof replay here is not a Lean kernel proof, and this local audit was
performed without starting or resuming Ultramath, as requested.
