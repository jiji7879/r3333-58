# Encoding adequacy: first piece landed

The one remaining Lean obligation was that a colouring realising a case's units
also satisfies that case's **extra clauses** (thresholds, `s_crit ≥ 2M − 57`,
full-root `H ≥ w`, support selectors). This records the first concrete step.

## The port is not the file the handoff suggested

`UniformK60/Core.lean` — whose `coloring_satisfies_formula` was the natural port
target — states in its own header that K60's marked cases have **no auxiliary
variables**: every clause there is a unit on a physical edge variable. So it is
the trivial case and does not transfer.

The K58 encoding is different: `dense.marked_threshold` builds cardinality
constraints through `CardEnc.atleast`, with selector and counter variables.
The matching K60 development is `UniformK60/SequentialCounter.lean` (330 lines,
constructive soundness of the staggered at-*most* counter), not `Core.lean`.

## What was verified

PySAT's `CardEnc.atleast(lits, bound)` with the default encoding emits **exactly**
`SequentialCounter.counter` applied to the negated literals, with the same
variable allocation (`index` interleaves the first two rows). Checked clause for
clause and including `nv`, for every `n` from 2 to 9 and every bound:

```
python3 tools/verify_atleast_encoding.py
checked every bound for n = 2..9; mismatches: 0
```

This is the fact the whole port rests on: the Lean counter's adequacy lemma
applies to the encoding the campaign actually used.

## What was ported and proved

Three new modules, all depending on Mathlib only, so they compile in the base
repository without the marking patch:

| file | content |
| --- | --- |
| `K58/CNF.lean` | clause/valuation semantics and agreement lemmas (from `UniformK61/CNF.lean`) |
| `K58/SequentialCounter.lean` | the counter, `regular_sat`, `satisfiable_extension`, `counter_atoms_le` |
| `K58/AtLeast.lean` | the polarity flip and **`satisfiable_atLeast`** |

The new theorem, axiom-clean:

```lean
theorem satisfiable_atLeast (v : Valuation) (x : Nat → Nat) (n bound top : Nat)
    (inputs_below : ∀ i < n, x i ≤ top)
    (hcount : bound ≤ prefixCount (fun i => v (x i)) n) :
    ∃ w : Valuation, (∀ a ≤ top, w a = v a) ∧ FormulaSat w (atLeastCNF x n bound top)
```

Spelled out: if at least `bound` of the atoms are true, the counter cells can be
filled so that every `atleast` clause holds, **leaving the atoms untouched**.
That is precisely the extension a colouring must admit.

It goes through the polarity flip rather than a duplicated proof: satisfiability
transfers across `flipCNF` (`formulaSat_flip`, axioms `[propext, Quot.sound]`),
and `prefixCount_neg` gives `#true + #false = n`.

```
'K58.SequentialCounter.satisfiable_atLeast' depends on axioms: [propext, Classical.choice, Quot.sound]
'K58.SequentialCounter.formulaSat_flip'     depends on axioms: [propext, Quot.sound]
```

## What remains of the layer

1. **Guarded constraints.** `dense.marked_threshold` emits `¬guard ∨ clause`;
   with `satisfiable_atLeast` in hand this is a two-line wrapper per family.
2. **The support-selector family.** Given a support equal to an allowed set, set
   that selector true and the rest false. Needs the clause shape from
   `support_tables.support_clauses`.
3. **The assembly.** State the whole clause set of a case (base ++ units ++
   extras) and prove `RealizesKey G k → ∃ aux, FormulaSat (G ⊕ aux) (caseCNF k)`.
4. **The binding.** PROOF_PLAN step 5: show the Lean clause families are the
   emitted DIMACS, by hash. Today only the units are bound.

Steps 1–2 are mechanical now. Step 3 is bookkeeping over the families. Step 4
needs the recipe table extracted from the certificates — which is what
`K58/hard_tail`-style extraction produces per case.
