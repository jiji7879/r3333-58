# Reading check for ledger entry 2

This reading compares the [verbatim supplied claim](claim.md) with the clean
[scoped audit](../proof.md). I did not write the original argument, so its
stepwise reading is a model reading; the separate recomputation is recorded in
[2-compute.md](2-compute.md). I concentrated on the exact supplied formulas,
condition scopes and case partitions rather than extrapolating from the word
"verified".

No gap remains in the **scoped package claims**, after separating what the
package says from what its checker alone can establish and after rejecting two
incorrect intermediate audit checks.

## Statement and objects

The same `signed-parent.cnf.gz`, row and branch objects are used: the signed
parent SHA-256 is
`ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`,
with 19,218 variables and 178,823 clauses. A proof is against the regenerated
CNF with named units, not against an incidentally similar file. All 47 owner
formulas regenerate from the restored source route and have their distinct
owner guard cubes; this does not turn 47 guard variants into 47 independent
Ramsey products.

The trigger literals are correctly identified as 2721 and 2766; pivot literals
are 5249–5252; the four word positions and 435-character K30 witness strings
are the same as in the package. The mapping controls on a sample local witness
reject reversal, rotation, all-zero and colour swap, supporting that there is
no reading-away of the edge map.

## The four-edge table

The supplied table includes four trigger conditions, not just the final
one: the independent recomputation evaluates all 315 witness objects in its
eight word tables and replays all eight block-cover proofs. The 57/36/29
counts before both pins and the 8/28/0 counts with both pins are obtained from
actual table keys, and every local model is evaluated against its complete
retained CNF. These finite local models are never read as global models.

The 24,686-clause projection for either both-pinned signature contains 5,201
clauses involving owner auxiliaries beyond the physical-edge-only subset. A
review that evaluates fewer than those is incomplete. The exact count and aux
range are now independently asserted, so the formerly incomplete check cannot
silently be reused as evidence.

## Case coverage and forcing

There are twelve CLOSED words: 1 in local pivot colour 0 and 11 in colour 3.
There are then exactly 24 OPEN words: 7 and 17. The conditional frontier has
exactly those words, once each. The two separate branch-block proofs and the
one unsplit 24-block proof match the stated query identities. This leaves both
whole pivot branches open; it does not promote a bounded three-second OPEN
into SAT or a refutation.

The wording "Each word closure also replays on the unsplit parent" is weaker
than what is actually proved: unsplit omits the pivot unit, so every such
closed word is excluded whichever pivot colour is used. On the other hand,
`branch-{0,3}.cnf.gz` contains more than parent+pivot (31 or 34 added
clauses), so "full parent" does not mean "parent plus all extra branch units".
These two scope distinctions are now explicit and do not change the supplied
claim; they constrain how it may later be used.

For the owner/lattice argument, all eight subsets per forced index are
covered directly or by monotonicity, with local models on proper-side subsets
where asserted. Eleven have a feasible local antecedent witness, but three
have impossible antecedents. The only six genuinely live two-site minima are
3,5,7,19,23,32. There are five further live three-pin minima, not "all fourteen
are a two-site result". The 14-forced status count and the 11-live/3-dead split
must be kept distinguishable. The 33 `LOCAL_COUNTEREXAMPLE` records are not
full counterexamples to any guarded implication.

## Other clauses and checks

The copies of the supplied byte-level proof obligations have been checked
under the strict full verifier: 196 calls cover unrelated-to-12 owner, cut,
resolved-clause, ordinary-row, pair-cover and conditional-recolouring
records. The ordinary row replay count is 66 and the pair search keeps 25/30
OPEN. Nothing in those obligations changes the status of the 24 frontier
words: they stay OPEN.

The supplied verifier's `-w` and substring criterion is not the argument. It
is instrumentally unsuitable, since a reachable warning-bearing verified
output is admitted in that mode. Running all calls through the no-`-w`, exact-
status, no-warning proxy is therefore a necessary correction to the evidence
chain.

Cases' literal formula/query hashes were checked instead of treating an
archived digest or unreferenced file as proof. Unreferenced proof files and
missing historical event proof bytes are not counted. The source-deprivation
block reported by the archive direction is confined to its missing-package
route; my alternate restored `revised.py::export` regeneration is separately
documented, and source generation is not conflated with a universally checked
historical derivation.

## Negative inference check

Applying a candidate global inference immediately exposes the prohibited
scope changes: a 30-vertex model would have to assign only 435 of 1653 K58
edges, an `OPEN` record has no full model, the 47 owners cover one row rather
than the 11,585-row wall, and the twelve closures leave a 24-word conditional
frontier. None yields a global K58 model, representative/branch conclusion or
Ramsey bound.

No citation beyond the supplied finite objects is needed to make a formula-
replay conclusion. All cited numeric or finite facts are recomputed, with
positive controls and rejecting corruption controls as specified in the
compute record. No Lean statement is supplied and no kernel proof is claimed.
