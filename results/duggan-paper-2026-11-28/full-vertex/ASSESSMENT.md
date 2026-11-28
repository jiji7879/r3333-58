# Duggan §7 full-vertex method: applicability to K58/K51

## Outcome

**The preferred-full-vertex/counting-and-gluing route does not transfer to
K58.  This is a proof, not a timeout or a paper-summary conclusion.**  For
every colour of a hypothetical good four-colouring of K58, the exact Duggan
full-vertex deficit is at least **3,480**.  His conclusion "at least `n-phi`
full vertices" therefore guarantees no full vertex at all.  This rules out the
existence step needed by the Grinstead--Roberts minimum-edge catalogue lemmas
and their gluing implementation; it does not rule out every use of an
anti-neighbourhood edge bound.

I also found and checked a literal defect in the generic `(p,q)` statement of
Duggan's Lemma 2 (equation (7.1), p.20): it omits the edges inside `H1`.  The
paper's actual `p=3`, triangle-free applications are unaffected.  This matters
here because a graph formed by merging two colours need not be triangle-free,
so the uncorrected identity cannot be applied to two-colour arms.

No wall row or profile is closed, no K51 colouring was found, no DRAT was
produced, and the accepted bound remains `51 <= R_4(3) <= 62`.

## 1. Exact source statement and the necessary correction

Duggan, Chapter 7, defines, for a preferred vertex `v`,

* `H1(v) = N(v)` and `H2(v) = V \ ({v} union N(v))`;
* a **full** vertex by `e(H2(v)) = e(p,q-1;n-deg(v)-1)`;
* `phi = n e - sum_v (e(p,q-1;n-deg(v)-1) + deg(v)^2)`.

For a **general simple graph**, write `Z(v) = sum_{u in N(v)} deg(u)`.
Partitioning edges into `H2`, `H1`, the root star, and the `H1--H2`
interface gives the corrected local identity

```
E = e(H2(v)) + Z(v) - e(H1(v))
  = e(H2(v)) + deg(v)^2
      + sum_{u in N(v)} (deg(u)-deg(v)) - e(H1(v)).       (C)
```

The degree corrections cancel around every undirected edge when summed over
`v`, so

```
n E = sum_v [e(H2(v)) + deg(v)^2 - e(H1(v))].              (S)
```

Duggan's displayed local and summed formulas are these with `-e(H1)` omitted.
They are correct when `G` is triangle-free, since then every `H1(v)` is
independent.  All of his `R(3,8)/R(3,9)` uses have `p=3`, so this correction
does not challenge those results.

**Literal counterexample to the general `(p,q)` statement.**  `K3` is a
`(4,3;3;3)` graph.  At every vertex `H2` is empty, so the catalogue value is
`e(4,2;0)=0`; all three degrees are two.  Equation (7.1) as printed gives

```
phi = 3*3 - 3*(0+2^2) = -3,
```

contradicting `phi >= 0`, and the claimed full-vertex count would be at least
six among three vertices.  The correction subtracts `e(H1)=1` at each root and
repairs both calculations.  This is not merely an abstract possibility for a
merged-colour transfer: in the five tested repository colourings, **all 1,482
root/two-colour-pair positions had `e(H1)>0`**.

## 2. The valid one-colour K58 transfer

Fix a colour `c` in a good four-colouring of `K_n`, and let `G_c` be its graph.
A `c`-independent 17-set carries a good three-colouring by the other colours,
contradicting `R(3,3,3)=17`.  Thus `G_c` is a `(3,17;n)` graph.  Moreover,

```
H2_c(v) = V minus ({v} union N_c(v))
```

is a `(3,16;n-1-d_c(v))` graph: an independent 16-set there, together with
`v`, would be a `c`-independent 17-set.  This gives a genuine specialization of
Duggan's `p=3` method, with `q=17`, not an invalid merged-colour version.

Put

```
h_c(v) = e(G_c[H2_c(v)]),
L_c(v) = e(3,16;57-d_c(v))                      at n=58.
```

By (S), with `e1=0`,

```
58 |E_c| = sum_v h_c(v) + sum_v d_c(v)^2.
```

Hence Duggan's exact deficit is

```
phi_c = sum_v [h_c(v)-L_c(v)]
      = sum_v [29 d_c(v) - d_c(v)^2 - L_c(v)],             (D)
```

using `sum_v d_c(v) = 2|E_c|`.  A non-full root contributes at least one to
`phi_c`, so his method guarantees at least `58-phi_c` full roots in colour
`c`.  At K58 these catalogue inputs have orders `41..48`: all colour degrees
are at most 16 and sum to 57, hence each lies in `[9,16]`.

## 3. Constructive bound that closes the transfer negatively

Each colour class of either repository K16 three-colour link was checked to be
5-regular, triangle-free, with 40 edges and no independent 6-set (and with an
independent 5-set).  Therefore each is a `(3,6;16)` graph.  Take three disjoint
copies of colour zero of the U link.  The result is:

* 48 vertices and 120 edges;
* triangle-free;
* independence number at most `5+5+5=15` (in fact equality).

It is consequently a `(3,16;48)` graph.  Taking induced subgraphs proves

```
e(3,16;m) <= 120       for every 41 <= m <= 48.             (U)
```

This is an **upper** bound on the catalogue value, exactly the direction
needed to give a rigorous lower bound on `phi_c`; no unknown exact minimum-edge
table is being assumed.

For `9<=d<=16`, the concave expression `29d-d^2` has minimum
`min(29*9-9^2,29*16-16^2)=180`.  Substitution into (D) and (U) gives

```
phi_c >= 58*(180-120) = 3,480.
```

Thus `58-phi_c <= -3,422`.  The full-vertex count supplies no preferred root
for any colour.  Computing exact values of `e(3,16;m)` cannot repair this
existence failure: the bound above holds for the exact deficit itself.

The contrast with Duggan is quantitative and structural.  In his
`(3,8;27;80)` application, Lemma 8 has `phi = 8-2s0 <= 8`, so at least 19 of
27 vertices are full (and in one case `phi=0` makes every vertex full).  That
small budget is what drives the subsequent catalogue/gluing lemmas.  At K58
the corresponding budget is not merely larger than eight; it is provably at
least 60 times the number of vertices.

Lean file `FullVertexBudget.lean` kernel-checks the interval inequality and
its 58-term sum.  Its axiom report contains only
`[propext, Classical.choice, Quot.sound]` (and `propext` for the K3 arithmetic
example).

## 4. What survives: a local anti-neighbourhood floor

The local decomposition still yields a valid counting lemma, independent of
full vertices.  Since `alpha(H2_c(v)) <= 15`, Caro--Wei/Cauchy gives, for a
graph on `m` vertices,

```
15 >= alpha >= m^2/(2E+m)  =>  E >= ceil(m(m-15)/30).
```

At K58, with `m=57-d_c(v)`,

```
h_c(v) >= ceil((57-d_c(v))(42-d_c(v))/30).                  (F)
```

The values for `d=9,...,16` are respectively

```
53, 51, 48, 45, 43, 41, 38, 36.
```

Also `|E_c| = h_c(v) + Z_c(v)`.  This is an incidence-level necessary
condition, not a degree-sequence ILP.  The repository already has the related
arm/interface double count in `lean/K58/Arm.lean::interface_count`; the new
part here is the `H2` minimum-edge/floor interpretation, not that interface
identity.

I checked (F) and the local identity at all **988 root/colour positions** in
three K50, one K49, and one K48 valid colouring.  The minimum slack
`h_c(v)-ceil(m(m-15)/30)` over each artefact was 76, 94, 94, 110, and 114.
So the bound is valid but loose on every known model.  I did not add it to a
wall CNF and make no propagation, speed, or UNSAT claim.

If this residual lemma is tested, the only justified first control is one
exact frozen parent whose root degree and physical arms determine `H2`: add
(F) as a pseudo-Boolean constraint to an explicitly theorem-augmented parent,
first measure existing-unit propagation, and only then run one matched
small-budget A/B.  It must not be represented as an original-parent DRAT
consequence unless that derivation is independently produced.  The large
model slack makes this low priority, not a recommended sweep.

## 5. Scope by repository target

| target | assessment |
| --- | --- |
| small-wall row UNSAT | **No preferred-full-vertex/gluing transfer.**  There is no guaranteed full root to glue.  Pair-union arms additionally need the `e(H1)` correction.  No row solver run was done. |
| Lemma L / profile reduction | **No consequence.**  The deficit bound is per colour and does not force three critical degrees or exclude any of the 11 root profiles. |
| finding K51 | **Not established.**  The identity is valid with anti-neighbourhood orders `34..48`, but the K58 degree range `[9,16]` and the 3,480 bound do not carry over (`d` can be as low as 2 at K51).  No model search was run. |
| proof/certificate tooling | No SAT/CAS certificate is claimed.  The evidence is a self-contained proof, exhaustive finite checks, two independently rechecked K16 objects, and a kernel-checked arithmetic lemma. |

## 6. Reproduction and exact checks

Run from `.ultramath/smwzxq4fl/m5`:

```bash
# Paper used: ../../../.scratch/paper-review/conor_duggan.pdf
pdftotext -layout ../../../.scratch/paper-review/conor_duggan.pdf duggan.txt

python3 full_vertex_audit.py > audit-results.json
lean FullVertexBudget.lean
sha256sum -c SHA256SUMS
```

`full_vertex_audit.py` reads but never modifies repository artefacts.  It:

1. exhausts all **1,098 labelled graphs on 2..5 vertices**, checking 5,404
   rooted identities and exhibiting 2,474 failures of the uncorrected local
   form; 438 triangle-free controls pass the paper's specialization;
2. checks all six K16 link colour classes, including every 6-subset for
   independence, and constructs the 48-vertex/120-edge catalogue bound;
3. checks the K58 arithmetic table;
4. checks 988 single-colour identities and 1,482 corrected pair-union
   identities on current repository K48--K50 artefacts.

The separate repository verifier accepted all seven input colourings; output
is in `artifact-verification.log`.  A second complete run of
`full_vertex_audit.py` was byte-identical to `audit-results.json`.
`audit-results.json`, `lean-check.log`, `artifact-verification.log`,
`hash-check.log`, and `SHA256SUMS` retain receipts.  No production queue,
ledger, CNF, proof store, or file outside this member directory was changed.
