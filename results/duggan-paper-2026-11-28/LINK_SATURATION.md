# Exact-cover partial graphs do not compress the critical links

**Swarm:** `smwzxq4fl`, member `m1`, direction `d5`
**Result:** a new saturated-link lemma, an exhaustive certificate, and a precise negative transfer result. No Ramsey bound changes; published bounds remain $51\le R_4(3)\le 62$.

## 1. What in the paper is actually being assessed

Duggan's Section 7 defines ordinary graph gluing as putting two immutable adjacency matrices on the diagonal of a larger matrix and solving for the off-diagonal entries. He explicitly says that he **did not implement graph gluing in SAT+CAS** and did not directly replicate that part of Grinstead--Roberts. The stabilizer restriction is presented as a possible resolution, not as an implemented experiment.

Section 10 describes a different ingredient from Gauthier--Brown's *A Formal Proof of $R(4,5)=25$* (arXiv:2404.01761): generalised graphs with gray edges and exact covers. In the original Definition 8 and Section 4.1, a generalisation denotes **all** colourings of its gray edges. An exact cover must cover every good graph and contain no additional graph. Exactness is what permits their gluing proof to omit the local clique obligations at the splitting vertex.

Ordinary gluing itself is not new to this repository. In particular, `tools/color-resolved-wallcc/frozen/gluing.py` already has fixed U/T templates, colour-named physical pivots, automorphisms, `support_embeddings`, and exact orbit representatives. The current handoff still has all 11,585 small-profile rows open. At K51, the recorded exhaustive K16 link split leaves 1,139 free edge variables; fixing more data without an exhaustive quotient is not a solution.

The only new compression candidate assessed here is therefore **Gauthier--Brown-style exact gray-edge generalisation of the internal K15/K16 link catalogue**.

## 2. The exact obstruction

Fix a vertex label set of size $n\in\{15,16\}$ and three colours. Let $\mathcal G_n$ be all labelled 3-colourings of $K_n$ with no monochromatic triangle.

A partial graph $P$ has fixed coloured edges and a set $Q$ of gray edges. In the direct three-colour analogue of Gauthier--Brown,

$$[P]=\{C: C\text{ agrees with }P\text{ on its fixed edges}\},\qquad |[P]|=3^{|Q|}.$$

This definition matters: graying one edge admits all three colours, not merely one selected alternative.

Call a good colouring $C$ **alternative-closed** if for every edge $uv$ and every colour $d\ne C(uv)$ there is a vertex $w$ such that

$$C(uw)=C(vw)=d.$$

Thus changing only $uv$ to $d$ creates the monochromatic triangle $uvw$.

### Lemma (critical-link saturation)

Every colouring in $\mathcal G_{15}\cup\mathcal G_{16}$ is alternative-closed.

**Proof.** The repository's reproduced exhaustive classification has two vertex/colour-relabelling classes at each order. Alternative-closure is invariant under both relabelling operations, so it suffices to check the representatives.

* At order 16, every colour class is the Clebsch graph, an $\operatorname{SRG}(16,5,0,2)$. If $C(uv)\ne d$, then $u,v$ are nonadjacent in the colour-$d$ class and hence have exactly two common colour-$d$ neighbours.
* At order 15, every colour class is the common classified graph $G_{15}$. The finite check below shows that each of its colour-class copies has diameter two. A nonedge therefore has a common neighbour; the exact counts are one or two throughout the two representatives.

The eight stored template/link copies were also checked directly, without using the SRG shortcut. $\square$

**Classification dependency.** The representative statements are independently certified below. Extending them to *every* good colouring uses the existing computational/literature two-class classification. This work does not prove `K58.Classified`; `lean/K58/Templates.lean` still only states that interface.

### Corollary (no exact gray-edge compression)

If $P$ is nonempty and $[P]\subseteq\mathcal G_n$ for $n\in\{15,16\}$, then $Q=\varnothing$ and $[P]$ is one fully specified good colouring.

Indeed, choose $C\in[P]$ and suppose some $uv$ is gray. Choose $d\ne C(uv)$. Keep every other gray edge at its colour in $C$, but assign $uv$ colour $d$. This completion belongs to $[P]$, yet alternative-closure supplies a monochromatic triangle, so it is not in $\mathcal G_n$.

Consequently, on a fixed labelled vertex set, every member of an exact cover by such generalisations is a singleton. The same argument applies to a set of unlabelled isomorphism classes: every labelled completion must still be good. Gray-edge generalisation can do **nothing beyond the existing isomorphism quotient** for critical links. It cannot merge labelled embeddings, reduce their gluing obligations, or reduce the 1,139 residual K51 variables.

This is not merely the statement that one algorithm stopped early. Any multi-gray generalisation also contains the bad one-edge-changed completion used in the proof.

## 3. Exhaustive certificate and independent checks

The generator examines both name/template copies of U/T at both orders. For every edge and every alternative colour it emits one explicit common-neighbour witness. The independent checker:

1. hashes each source against `saturation/manifest.json`;
2. parses and checks symmetry and the absence of monochromatic triangles in every input;
3. requires exactly one witness for each of the 1,800 edge/alternative obligations, with no omissions, duplicates, or extras;
4. checks the two witness edges and recomputes the number of common neighbours;
5. independently checks diameter at most two for every colour class, and $\mu=2$ for every nonedge of every K16 colour class.

Run from `.ultramath/smwzxq4fl/m1/`:

```sh
ROOT=$(git rev-parse --show-toplevel)
python3 saturation_certify.py --repo "$ROOT" --out saturation
python3 saturation_verify.py --repo "$ROOT" --out saturation \
  --report saturation/verification.json
python3 saturation_test.py --repo "$ROOT" --out saturation
```

Results:

| each stored representative | alternatives checked | common-neighbour histogram |
|---|---:|---|
| K16 U, T (and each link copy) | 240 | exactly 2: 240 |
| K15 U-minus, T-minus (and each link copy) | 210 | exactly 1: 30; exactly 2: 180 |
| **total over eight files** | **1,800 / 1,800 PASS** | |

The strict test suite also passes a positive control and rejects an omitted obligation, an invalid triangle witness, and a duplicate obligation. There is no warning suppression. Important files are:

* `saturation/witnesses.tsv` (SHA-256 `7710d630d8db548b260c9d61428d5f0ab97cd191f573ceda024575d8297feed9`);
* `saturation/manifest.json`, `saturation/verification.json`;
* `saturation_certify.py`, `saturation_verify.py`, `saturation_test.py`.

The representative statement is also kernel-checked in `work/LinkSaturation.lean`:

```sh
ROOT=$(git rev-parse --show-toplevel)
export LEAN_PATH="$ROOT/lean:$LEAN_PATH"
lean -j1 -o work/LinkSaturation.olean work/LinkSaturation.lean
```

The clean log `work/LinkSaturation.log` reports both theorems with only `[propext, Classical.choice, Quot.sound]`; there is no `sorryAx` and no `native_decide`.

## 4. Boundary controls: smaller links need a different test

Full saturation is not universal at lower degrees, but nonsaturation alone still does **not** permit an exact three-colour gray edge: both alternative colours must give good completions.

`boundary_control.py` checks real links extracted from verified K50 colourings, including a complete check of the source colourings. Run:

```sh
python3 boundary_control.py --repo "$ROOT" \
  --report saturation/boundary-controls.json
```

* The selected real K14 link has two safe single-edge alternatives among its 182 checks.
* The selected real K13 link has five safe alternatives among its 156 checks.
* Neither has an edge for which **both** alternatives are safe, so neither supplies even a one-gray-edge exact generalisation.

These are examples, not a classification of K13/K14 links. They prevent both overgeneralising the saturation lemma and claiming a positive K14 transfer without further enumeration.

## 5. Consequences by target

**(i) Small-wall rows.** Exact generalisation of the internal 15/16-arm templates is ruled out as a compression mechanism. It cannot merge any of the 11,585 rows or their labelled arm placements. Ordinary fixed-template gluing and exact support/stabilizer quotients already exist and are untouched. Off-diagonal/cross-arm generalisations are a separate object and are not ruled out.

**(ii) Lemma L / profile reduction.** No consequence is claimed. Saturation is a property of every critical three-coloured link, including links in valid K50 colourings; it supplies none of the global incidence information needed for Lemma L.

**(iii) K51 model finding.** This particular exact-cover device cannot reduce the critical-link split. It neither finds a K51 colouring nor proves that none exists. The result also does not prohibit fixing representatives under an independently justified global quotient.

**(iv) Certificates.** The 1,800 explicit triangles form a small test oracle for any future generalisation generator: a proposed exact gray-edge generalisation of these critical-link sets must be rejected. This is a direct finite mathematical certificate, not a DRAT proof of a wall row. Existing template-classification completeness remains a separate proof obligation.

## 6. What a useful next experiment would have to do

Do not spend a production sweep on graying critical internal edges. A positive continuation must target a different catalogue, most plausibly transverse interfaces or smaller links. A sound small pilot should:

1. define whether gray edges use all three colours or a more expressive restricted-domain CSP (the latter is not the Gauthier--Brown generalisation assessed here);
2. for $q\le2$ gray edges, enumerate all $3^q$ completions and independently reject any bad completion for an exact cover;
3. prove coverage of the whole labelled target set, not just one representative per isomorphism class;
4. include transverse triangles in the gluing formula and measure total generalisation-plus-proof cost, rather than counting internal block types alone.

The two smaller-link controls already show why checking merely one safe recolouring would be an invalid positive result. Non-exact overcovers with all local clauses retained, vertex-deletion generalisations, and ordinary graph gluing remain possible research directions, but no speedup or wall closure is claimed for them here.
