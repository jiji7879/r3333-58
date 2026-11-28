# Reading of the complete scoped audit

## What the argument actually claims

The artifact defines a library of conditional clauses for the selected physical pivots in 11,549 rows and for 240 local configurations used by those rows. The claimed result is limited to exact reconstruction, local entropy/minimum arithmetic, native consequence proofs on ten reconstructed parents, and evaluation of what the supplied benchmark records do not establish. It does not claim any wall-parent refutation, new SAT model or bound change.

## Case and quantifier check

- **Row identities and geometry.** One standard-library reconstruction covers all 11,585 identities/bindings and full 240 configurations. Another reconstruction covers 1,448,380 local physical words and every one of the 720 per-pivot-color branch records. All 11,549 sender geometries and all arm-site palettes are checked. The 36 null pivots are not counted as configurations and are not claimed impossible to split by another rule.
- **Counters.** Each comparator has OR and AND outputs. Induction starting from the empty cover covers every number of inputs, not just the tested 1–12. Each new variable is a Boolean function of preceding values, so the extension is unique. Suffix sortedness identifies output $j$ with threshold $j+1$ rather than reversing it.
- **Conditional clauses.** Every nonempty branch minimum supplies its threshold clause. Every nonpivot forced site supplies a guarded clause at the branch minimum. The alternative $T_{m+1}$ preserves all above-minimum assignments. The pivot has its specified color from its guard, so omitting it from additional forced-site targets is accounted for.
- **Minimality and baseline.** All feasible local word masks are used to define minimal transversals. Each inclusion-minimal mask has an actual positive clause. Every literal of that mask has a separate weaker-mask counterexample; the baseline audit supplies 21,173 physical counterwords. This covers validity and literal minimality but says nothing about solver usefulness.
- **Model preservation.** All physical local words satisfy every color target under the correct simulated output thresholds. Combined with unique auxiliary definition and the RUP proof, the projection of exported models onto original physical variables is exactly the original model set. No assertion that an individual minimum word extends beyond the arm is needed or made.
- **Proof scope.** Miter flags cause target violation rather than target assumption. All required targets are derived in the traces. Negative and omitted-lemma controls establish the difference between a bad trace and an actual proof. For large comparison/transport queries, only the exact supplied statuses are claimed; no timed/proofless trial is upgraded.
- **Parent provenance.** Six stored parents are byte-identical to independent regeneration. Four others retain their bundled threshold suffix. Their independently generated K58 body and physical pins do not prove that suffix independently, and that is why they are not called a new provenance audit of the whole production parent.
- **Performance.** There are 24 variant formulas, two seed receipts each, 48 total. No run completes. Selected child cubes and unit-propagation status are outside the parent completion ledger. Child proof absence and timestamp boundaries are explicitly retained rather than rounded away.

## Finding

No gap found in the scoped argument. The proof and performance claims must remain separately scoped as described above. Earlier exploratory OR/AND reversals and incorrect test expectations were retracted before the final controls; the accepted control outputs, not those hypotheses, are in force.
