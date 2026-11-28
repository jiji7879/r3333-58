# Exact scope and soundness of the arm-3 configurable-MCF reduction

## Retained object

The only input row is
`06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06`,
profile `(16,16,14,11)`, charge 7. The ordinary parent is the first-tier
`tables=True,total_critical=True,full_root=False` CNF with SHA-256
`90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`.
Call its formula $P$. It has 19,533 variables and 184,335 clauses.

The first 134,995 clauses are the four-colour host encoding:

$$1653(1+6)+30856\cdot4=134995.$$

Call the remaining clauses $N$ (frozen units and threshold/support encoding).
The selected arm is arm 3, vertices $47,\ldots,57$ in the source's zero-based
numbering, and the target colour is $c=0$. Let $F$ be its unfixed internal
edges. There are 45 such edges. For every $e\in F$, all four physical edge
variables are absent from $N$. The generator-free audit recomputes exactly this
set; this is stronger than merely trusting a list of edge names.

For $e=(u,v)$, the configurable maximal-normal-form condition is

$$x_{uv,0}\ \lor\ \bigvee_{w\notin\{u,v\}}(x_{uw,0}\land x_{vw,0}).$$

For each edge and third vertex, use a fresh $y_{e,w}$ and the clauses

$$y\leftrightarrow(x_{uw,0}\land x_{vw,0}),$$

encoded as $(\neg y\lor x_{uw,0})$, $(\neg y\lor x_{vw,0})$, and
$(y\lor\neg x_{uw,0}\lor\neg x_{vw,0})$. Add the 57-literal clause containing
$x_{uv,0}$ and all 56 witnesses. This gives 2,520 fresh variables and
$45(3\cdot56+1)=7,605$ added clauses. The resulting CNF is $A_3$.

## Existential reduction (not a DRAT implication)

**Claim.** $P$ and $A_3$ are equisatisfiable, under the explicitly checked
host/non-host separation above.

*Reverse direction.* $A_3$ contains every clause of $P$, so projection of an
$A_3$ model to the old variables satisfies $P$.

*Forward direction.* Start with a satisfying host/non-host assignment of $P$.
Process the edges of $F$ sequentially. If the current edge already has colour 0
or its endpoints have a common 0-coloured two-edge path, leave it unchanged.
Otherwise recolour just that edge to colour 0.

Such a step preserves the host exactly-one semantics. It cannot create a
monochromatic triangle in colour 0, because the absence of the common path is
precisely the absence of a triangle that the new edge could close. Every other
colour class only loses an edge, so it also remains triangle-free. No variable
of $N$ changes, by the checked absence condition. A later step only adds
colour-0 edges, hence cannot remove a path already witnessing an earlier edge.
At the end, every condition on $F$ holds. Assign each fresh $y$ to the truth
value of its defining conjunction; all Tseitin and long clauses then hold.

This proves only an **existence-preserving CNF augmentation**. The MCF clauses
are not asserted to be logical consequences of $P$, and no DRAT derivation of
them exists merely from the reduction above. In particular, a future refutation
of $A_3$ would have to be read together with this reduction, not mislabeled as
an ordinary DRAT derivation of the MCF suffix from $P$ alone.

## Parent-BCP residual form

An independent implementation computes all 1,813 literals in the unit-
propagation closure of $P$. Their canonical list has SHA-256
`9d773ef00ac64b36bb7d764f323208534c635ea7a29ee7bb959e48f81e6edabd`.
Only these parent-derived assignments are used to simplify the suffix.

If a suffix clause is satisfied by such an assignment, $P$ entails it and it can
be omitted. Otherwise, deleting its false literals gives an equivalent residual
clause modulo $P$. Fresh variables are then renamed injectively above the old
maximum. The original parent body remains byte-for-byte intact. For arm 3 this
removes 465 satisfied definitional clauses and retains 7,140 residual clauses;
no long MCF clause disappears and all 2,520 witnesses remain. The resulting
CNF is `results/mcf-arm3-bcp.cnf`, SHA-256
`31108fb9204b9e615a6396bb6239019f04307e083786db3d2b8e181f82e38daa`.

A second, deliberately different full-scan BCP implementation independently
recomputed the same closure in three passes and checked every residual and every
renaming. Sign-mutation and clause-deletion controls were rejected. The same
procedure on the old 126-edge union removes 1,176 clauses, but none of its 126
long clauses and none of its 7,056 witnesses.

## Boundary of the result

This is not the full-parent Lean/DIMACS semantic assembly. It does not prove the
meaning of the frozen units, guard premises, all-profile P4/C5 support
catalogues, total allocation, or the physical-row bridge. $P$ remains the
ordinary parent relaxation identified above. A future $A_3$ UNSAT certificate
would first be a result about these exact CNF objects. No present or future SAT
model is promoted here to a semantic-row model, and an OPEN result never
implies SAT or UNSAT.
