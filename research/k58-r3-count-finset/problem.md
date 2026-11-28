# R3: emitted count to physical neighbours

At the retained K58 target, prove in Lean 4.33.1 from a true emitted 41-atom
`prefixCount` lower bound that there is a finite set `W` of at least 14 genuine
physical vertices adjacent to the corresponding sender in physical colour 1,
with every member distinct from the sender and with the root not in `W`.

The desired stronger conclusion is the existing emitted support-step readiness
with that `W` constructed from the count, rather than passed as a hypothesis.
Prefer a theorem for every sender `k : Fin 15`, using the retained exact atom
lists. The sender-18 case is a useful partial milestone, not completion of the
all-sender theorem.

All other currently existing geometric and classification hypotheses must remain
explicit and truthful; where possible use the actual `K58.classified_15` and
`K58.classified_16`, whose real types are to be inspected rather than imagined.
Nothing in this problem asserts `ChainReady`, a closed wall profile, or a changed
Ramsey bound. PROVED requires a kernel-compiling theorem with only
`propext`, `Classical.choice`, and `Quot.sound` in its axiom dependencies, plus
an independent statement/proof review and the root Lean build.
