# Literature-inspired experiments — coordinator status

**Scope: bounded mathematical/certificate experiments. No new Ramsey bound.**
The established interval is still $51\le R_4(3)\le62$; no result here proves
$R_4(3)\le58$, closes a wall profile, constructs a $K_{51}$ colouring, or
settles `ChainReady`. Tatarevic's claimed 60 bound is not validated by this
work.

Swarm `smx06hpp8` ended with **five accepted directions**: CAT58/attachment
bounds, finite support transport, exact emitted readiness, native-LRAT replay,
and the sender-only KMT encoding. Two further directions ended without formal
submissions (FKR and SMS); the coordinator independently replayed their final
artifacts and preserves them as bounded results, not as accepted solutions.

| experiment | established result | caveat |
|---|---|---|
| [Support catalogue and readiness](support/readiness.md) | Exact 112-entry finite semantics; production-ready equivalence for all 15 sender steps; physical-to-coded transport from real neighbour sets. Full Lean build and standard axiom checks pass. | Physical `PinnedArm`, exact emitted-order identification, physical criticality and guard=`Sends` remain open. Not `ChainReady`. |
| [CAT58 and attachment bounds](CAT58.md) | `K58.cat58`, the packing lemma and exact natural-subtraction attachment bound are proved. | A structural existence theorem, not an attachment cover or wall exclusion. Generic $k\le14$ is false/unavailable here. |
| [Native LRAT](lrat/README.md) | Four already closed CNFs regenerate and replay through ordinary DRAT and native LRAT. Two independent LRAT implementations accept, with corruption controls. | Neither checker is formally verified. CakeML/Boost/Isabelle prerequisites are not supplied. Timings are limited to those CNFs; some LRAT files are larger. |
| [Sender-only KMT](kmt/README.md) | Exact 13,364-variable / 176,660-clause parent and allocation map; 39,744 semantic-control calls pass. | CPU regresses (1.2576 at 100k; 1.2344 at 1M), despite lower RSS. All runs OPEN. Do not deploy as a speedup. |
| [One-colour lex/SMS experiment](sms/README.md) | 765 independently checked lex-indicator clauses and a matched 200k-conflict experiment were replayed. | Native SMS prerequisites are absent, physical model-set invariance is unproved, and corrupted clauses have a similar trajectory effect. No speedup is claimed. |
| [Early FKR attachment feasibility](attachment/README.md) | Exact 533/724 reference counts, full 15/15 census, independent orbit checks and full replay. The early $k\ge3$ census is **31,712**. | The declared 10,000 continuation gate fails. No cover occurs; order-15 completeness rests on the stated external classification. |

`lean/K58/SupportCatalogue.lean`, `SupportTransport.lean`, and
`SenderReady.lean` are integrated into the root Lean build and `K58.Check`.
The complete build after their integration passed in 129.33 s; its log is
`support/build.txt`. Registered results use only the permitted standard axioms
(`propext`, `Classical.choice`, `Quot.sound`), with no `sorry`, `admit`, or
`native_decide`.

All supplementary experiments are opt-in and bounded. Production `run` and
`finalise`, the frozen coverage, ledger states and default encodings were not
changed. No proof binaries, large formulas, archives, compiled Lean outputs,
or measured solver-proof artifacts are committed. The scratch member
rehearsals are separated from the member's original reports and timings.

The precise remaining structural step for support is to identify the emitted
atoms with actual T16-pinned coordinates and to derive physical guards and
criticality, then propagate through the sequential chain. The other completed
experiments do not supply that missing step.
