# Duggan certificate separation applied to K58 encoding adequacy

## Outcome

There is a concrete, limited transfer for **proof-certificate tooling**, not for
closing a K58 row or finding a K51 colouring. Duggan's modified DRAT-trim checks
ordinary solver inferences and checks each trusted CAS symmetry clause using a
permutation witness (Chapters 4, 8 and 11). Chapter 5 separately warns that
additional constraints can be encoded incorrectly. The corresponding repository
requirement is therefore not merely “retain a DRAT”: every non-basic encoding
family needs a checkable justification that a physical colouring extends to its
auxiliary variables.

This direction produced:

1. a kernel-checked **native PySAT at-least extension theorem**, its guarded
   wrapper, and a guarded support-selector extension theorem;
2. an exact, small **binding defect** in the previous counter-to-PySAT argument;
3. artifact-matched positive and negative controls, including one nontrivial
   real frozen-family sample.

There is no new UNSAT, row/profile closure, Ramsey bound, or solver speedup.
The published bounds remain $51\le R_4(3)\le62$.

## 1. Precise defect in the old counter binding

`tools/color-resolved-wallcc/frozen/dense.py:123-125` emits PySAT
`CardEnc.atleast` and prefixes every clause with the negative guard. The old
`lean/K58/AtLeast.lean:53-55` instead defines

```lean
atLeastCNF x n bound top := flipCNF (counter x n (n-bound) top)
```

This flips **both physical-input and counter-cell literals**. Native PySAT uses
the at-most counter on negated **inputs only**, leaving counter-cell literals
unchanged. `tools/verify_atleast_encoding.py:54-58` checks the latter native
shape, not the former flip-all shape, so its successful output does not close
the gap between that script and `AtLeast.lean`.

The new theorem `legacy_atLeastCNF_not_native` proves this syntactic distinction
in Lean, with no axioms. At $n=3$, bound $2$, top $4$:

```text
native:        1  5    -5  6     2 -5    2  6     3 -6
flip-all old:  1 -5     5 -6     2  5    2 -6     3  6
```

The full controls found 28 differing regular-counter formulas among 52 cases
(including trivial bounds). This is a **certificate-binding defect**, not a
Ramsey counterexample or evidence that an existing emitted CNF is wrong.
Complementing auxiliary cells gives an auxiliary-sign renaming between the two
formulas, so satisfiability can be repaired by explicitly transporting that
renaming. Existing DRATs against emitted CNFs are unaffected. What is missing
in the old documentation is precisely that renaming; the new native theorem
avoids it altogether.

## 2. New extension lemmas

All definitions and proofs are in `EncoderExtensions.lean`.

### Native and guarded at-least

`nativeAtLeastCNF x n bound top` applies `flipWhereCNF` only to variables in
`inputMask x n`, leaving counter cells fixed. The theorem
`satisfiable_nativeAtLeast` states, in mathematical notation, that if

$$b\le \#\{i<n: v(x_i)=\mathrm{true}\},$$

then there is a valuation $w$ satisfying the native PySAT counter and agreeing
with $v$ on every old variable $a\le top$. The proof reuses the repository's
axiom-clean sequential-counter construction instead of assuming the cardinality
solver's correctness.

`satisfiable_guardedAtLeast` extends exactly the clause family emitted at
`dense.py:123-125`. Its essential hypothesis is

$$v(g)=\mathrm{true}\ \Longrightarrow\ b\le \#\{i<n:v(x_i)=\mathrm{true}\}.$$

If the guard is false, the guarded clauses are vacuous. If it is true, the
native counter extension applies. Old inputs and (because $g\le top$) the guard
are unchanged.

### Guarded $P_4/C_5$ support selectors

For fresh, pairwise-distinct selectors $s_i$, allowed supports $P_i$, and signed
literals $\ell_{ij}=x_j$ when $j\in P_i$ and $\ell_{ij}=\neg x_j$ otherwise,
`supportFamilyCNF` represents

$$(\neg g\lor \bigvee_i s_i)\ \land\ \bigwedge_{i,j}(\neg s_i\lor\ell_{ij}).$$

The theorem `satisfiable_supportFamily` assumes that a true guard makes the
physical support equal one listed $P_i$. It then fills only fresh selectors:
choose exactly the matching $P_i$ if $g$ is true and choose none if $g$ is false.
Every old variable is preserved. The proof covers implications at all
positions, hence also the generator's omissions at already-pinned positions.

This conditionality matters: the support clause does **not** assert that an
arbitrary non-sender has an allowed support. The graph input needed from
`K58.pinned_support_shape` remains an explicit premise, not something smuggled
into the Boolean proof.

The three main extension theorems print only
`[propext, Classical.choice, Quot.sound]`; the small legacy/native inequality
prints no axioms. `lean-build.log` has no warnings, errors or `sorryAx`.

## 3. Validated pilot and negative controls

`validate_encoder_extensions.py` reimplements the Lean clause shapes, invokes no
SAT solver, and checks the real generators. `validation.json` is its receipt.

### Generic native counters

Using `python-sat 1.9.dev25`:

- exact ordered clause identity for **52 formulas / 668 guarded clauses**, over
  $n=2,\ldots,9$ and every bound $0,\ldots,n$;
- **1,208** constructive positive extensions for $n\le6$, covering valid true
  guards and arbitrary false guards, with all old values preserved;
- **128** false-semantic-guard physical hypotheses for $n\le5$, with **every**
  auxiliary assignment exhaustively rejected;
- 28 explicit legacy flip-all/native syntactic mismatches.

Bound zero exposes only a PySAT bookkeeping convention (`nv=0` on the empty
formula); the native and Lean clause sets are both empty. All positive bounds,
including those used by the wall generator, also match allocation tops.

Running the repository's original check still prints
`checked every bound for n = 2..9; mismatches: 0` (`legacy-check.log`). That
pass and the new mismatch result are consistent: they compare different CNFs.

### One actual frozen-family sample

The control uses the current `color-resolved-wallcc/frozen` generator, profile
$(16,16,13,12)$, kinds `UT--`, root arm 0, marked template 15/U, all orbit
indices zero, and 438 fixed units (SHA-256
`b59d15b076d894d0230a4d8e43e52593e3bea04d6f33dfd19a5675f66b0da470`).

- Candidate vertex 2 has threshold 14 over 41 candidates. Guard 6614 yields
  **743 emitted guarded clauses**, exact native/Lean clause-order identity and
  allocation top 6992.
- The support construction immediately follows that counter, exactly as in
  `dense.py`: guard 6614, counter top 6992, and selectors **6993–7104**.
  Independent $P_4/C_5$ enumeration (direct permutation tests, not the
  generator's degree shortcut) gives **112 selectors**. The actual
  `support_clauses` output regenerates exactly: **1,793 clauses**, SHA-256
  `1dbd5c07225860d950d5f50874891873d00fbdd0d94e2480e40508409d3b7637`.
  Here no pinned implications were omitted, so the emitted set equals the
  proved full set.
- One joint valuation satisfies the contiguous **2,536-clause**
  counter+support suffix (SHA-256
  `112685ff3df8cbc08d8bea31d5988774b61c19a854ea1b5ecfaead9eecb73e29`)
  and changes no old/counter value. A wrong selector is rejected by an actually
  emitted implication while the valid counter extension is unchanged. A false
  guard admits an invalid support with all selectors false. With a true guard
  and invalid support, each of the 112 individual selectors is rejected, and
  the all-false disjunction also fails.

These controls are deliberately small and are encoding checks only.

## 4. Reproduction

From `.ultramath/smwzxq4fl/m6/` at repository commit `203233c3cab65772e47fd1ea90751402d6ac43c1`:

```sh
ROOT=$(cd ../../.. && pwd)
export LEAN_PATH="$ROOT/lean:$LEAN_PATH"
lean EncoderExtensions.lean

# Only needed if the local vendored dependency is absent:
python3 -m pip install --target vendor python-sat==1.9.dev25
PYTHONPATH=vendor python3 validate_encoder_extensions.py
PYTHONPATH=vendor python3 ../../../tools/verify_atleast_encoding.py
```

The resulting logs are `lean-build.log`, `validation.log`, `validation.json`,
and `legacy-check.log`; `SHA256SUMS` pins the main files. No production sweep or
large compute was run.

## 5. Applicability and next experiments

| Target | Assessment from this direction |
|---|---|
| (i) Small-wall row UNSAT | No row refutation or acceleration. The results reduce the semantic assumptions needed *after* a strict DRAT refutation; they do not replace it. |
| (ii) Lemma L / profile reduction | No contribution. These are local encoding lemmas, not incidence counting. |
| (iii) K51 model finding | No contribution. Existential auxiliary extension does not guide the physical-colouring search. |
| (iv) Proof-certificate tooling | Direct, checked transfer: separate emitted-CNF refutation from independently verified encoding semantics, and test each trusted encoding family with negative controls. |

The next bounded experiment should be a **single exact UT-- parent semantic
assembly**, with no solver call:

1. Prove that physical criticality supplies every guard premise and that
   `K58.pinned_support_shape` implies membership in the generator's complete
   15/16 `allowed_supports` lists.
2. Assemble the guarded candidate counters, support families, and the three
   selector-level at-least goals, recording disjoint fresh-variable intervals.
3. Hash-bind that Lean formula to the actual parent DIMACS. Then any retained
   UNSAT proof for that parent must be replayed strictly (whole proof, no `-w`,
   zero warnings, no trusted additions).

That full assembly, all-profile support-list binding, and DIMACS hash binding
were **not** completed here. Also unaddressed are Duggan's permutation-checked
CAS symmetry clauses and any runtime benefit from alternative guarded counters;
those belong to separate directions.
