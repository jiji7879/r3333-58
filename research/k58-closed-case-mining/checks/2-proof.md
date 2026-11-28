# Claim: checked closed-case refutations and reusable physical host clauses

## Exact result

The fresh native Kissat outputs for the historical K58 cases and inputs below are genuine **auxiliary-extended original-recipe parent refutations**, not merely OPEN timeouts and not new closures of an unresolved ordinary-wall row.

| label | parent SHA-256 | fresh proof: bytes / SHA-256 | native replay |
|---|---|---|---|
| `2ce34a4453` | `1bb9f188a7c11cd8335e465e9f815991015f4c4ce4c2bce3d510cc5063b5fd97` | 5,152,549 / `083d6b3381bd2459b830ab505fd5f63e39d8f172a07dbea8275a7dfedf204e50` | `s VERIFIED`; 22 core RAT lemmas |
| `944f4a5583` | `a3e46c0ba80e51fd15c49db332471449d8a371aa5976b61c7426939b24e9b302` | 6,315,937 / `383ade3a567b35da1d868ff7baa45889e9359c08b317b48f6a0e1fb4de39a86d` | `s VERIFIED`; 24 core RAT lemmas |
| `6116d9150` | `e4dfee1874f41fdf2475c08a51f6ba05bb914064c7c9530c8c5c5735c5e1bd3a` | 6,401,828 / `5defe1b9aecff6a6874f2346e2622fc1e4f35a29fbfd0f030dba4c735cc15d31` | `s VERIFIED`; 37 core RAT lemmas |

The three full parent bodies begin with the independently reconstructed 134,995 clauses for exactly one of four colours per edge and no monochromatic triangle on 58 vertices. The physical edge variables are numbered in lexicographic order, four colours per edge, through 6612. The proof checker is `drat-trim`, SHA-256 `48891f3f9dfccbbebfc6a21fa9e6daa6b674900a3f65b16a0b0f7f21d8a03bce`. The fresh case proofs are binary DRAT with RAT enabled; none is called RUP-only.

Let $E(u,v,c)$ mean physical edge $\{u,v\}$ has colour $c$. For all distinct $u,v,w\in\{0,\ldots,57\}$ and colour $c\in\{0,1,2,3\}$:

1. **Unpinned reusable schema $Q$.**
   $$Q(u,v,w;c)=\neg E(u,w,c)\lor\neg E(u,v,c)\lor\bigvee_{d\ne c}E(v,w,d).$$
   The required premises are only the host palette on $(v,w)$ and the colour-$c$ triangle on $u,v,w$. Resolving those clauses on $E(v,w,c)$ yields exactly $Q$. Thus $Q$ is a logical consequence of every case parent retaining those clauses, with no row unit, guard, counter, projection, or auxiliary variable required.
2. **Pinned reusable schema $R$.** If the explicit positive case units $E(u,w,c)$ and $E(v,w,c)$ are present, then
   $$R(u,v,w;c)=\bigvee_{d\ne c}E(u,v,d).$$
   The two pins and triangle force $\neg E(u,v,c)$, whose four-colour palette immediately gives $R$. No other premise is used.

The exact source additions occur in the fresh backward-core lemma stream:

* $Q(12,29,49;3)$: `-2620 -2540 5065 5066 5067 0`.
* $R(1,18,21;3)$ with pins `308` and `3504`: `294 293 295 0`.

These are short physical clauses, not guarded degree/counting theorems. In these cores, no marked-threshold clause is used to justify either statement. Their simple role-rebinding argument, rather than raw proof-byte or literal substitution, establishes their scope. The earlier physical variable numbers recur in the universal $K_{58}$ host encoding, but their semantic identity must be checked at each parent.

## Native transfer certificates

For each intended clause $C$, the separate query is the precise full parent plus one unit clause $\neg\ell$ for every $\ell\in C$. It does **not** assume $C$. With the two-byte ASCII RUP proof `0\n`, the checker establishes that unit propagation refutes this false-cube query. Accepted checks use `-I -p -U -W -t 60`, return exit 0 and `s VERIFIED`, and have no warning or RAT. No empty-proof classification of any parent is inferred: these are implication certificates.

Both schemas were freshly checked on the three exact dense parents. The roles and clauses are:

| parent | LaTeX-style role | unpinned $Q$ clause | pinned residual; required pins |
|---|---|---|---|
| `2ce34a4453` | $Q(12,29,49;3)$ | `-2620 -2540 5065 5066 5067` | $R(1,18,21;3)$: `293 294 295`; pins `308, 3504` |
| `944f4a5583` | $Q(2,17,34;1)$ | `-578 -510 3397 3399 3400` | $R(49,54,0;3)$: `6485 6486 6487`; pins `196, 216` |
| `6116d9150` | $Q(5,21,38;1)$ | `-1230 -1162 4013 4015 4016` | $R(49,54,0;3)$: `6485 6486 6487`; pins `196, 216` |

All twelve incident colour literals on the $Q$ destination triangles are absent from both positive and negative parent units; neither $Q$ certificate uses a fixed unit. The original-only physical parent is merely the parent prefix containing host and case units, truncated **before** auxiliary clauses. Its implication checks are independent of the additional dense constraints. The two scopes are not conflated.

The exact controls pass as rejections:

* Raw source pinned residual `293 294 295` on `6116d9150` returns `s NOT VERIFIED`: source pin `308` is absent while pin `3504` remains. The raw proof-byte transfer failure is not reused as a clause implication.
* Removing only the required triangle `-510 -578 -3398` from the `944f4a55` parent returns `s NOT VERIFIED` for its $Q$ query.
* On the original-only physical `944f4a55` parent, removing the first positive literal from $Q$ gives altered clause `-578 -510 3399 3400`, and its direct-UP proof returns `s NOT VERIFIED`.

These checks concern the stated certificate constructions, not a claim that every stronger clause is logically false in every re-encoding. Local motif words give explicit counterexamples to missing premises: the monochrome word makes an omitted triangle fail; under two positive pins, a forbidden colour on $(u,v)$ illustrates a missing pin; the surviving palette word with one omitted positive literal falsifies a strengthened $Q$.

An exhaustive local sanity check enumerates all 60 nonmonochromatic three-edge/four-colour words. It agrees with $Q$ and the pin/residual explanation. The general argument is the one-step resolution, not that finite enumeration. The termination of the six implication checks and three native proofs demonstrates their certificates. No OPEN wall row, parent SAT model, search speedup or Ramsey-bound consequence follows.

Both other accepted audited banks remain separate: this is not a rediscovery claim for the square/matching, ternary square-escape, pivot comparator/counter, local K15 or guarded threshold families. The result is deliberately elementary; no nontrivial new guard has been mined.

## Boundaries

The original four-colour palette/host model is understood literally; auxiliary dense constraints are not erased from any native case refutation. The original-only transfer proofs apply just to host plus the stated case units; dense transfer proofs apply to the listed auxiliary-extended parents. Projection and local colour-word models are not full K58 models.

No claim is made that an arbitrary row's case units contain the two needed pins for $R$. The applicability hypotheses and vertex/edge/colour witnesses must be reconstructed per destination. The universal $Q$ needs only its two named host premises. These certificates are not a solver-policy result, a wall closure, or evidence that the Ramsey bound changes.
