# Hail mary 3 (their item 4): pseudo-Boolean solving — 200x slower per conflict

Their hypothesis: the ticket and interface arguments are *counting* arguments, so a
pseudo-Boolean solver with cutting planes (RoundingSat, Exact, VeriPB) should be
the natural tool on the retry tier, which carries the ticket hypothesis.

**Setup.** RoundingSat 2 (`MIAOresearch/software/roundingsat`, commit `d4edbf7`)
built here from source against boost-cpp installed with micromamba. The cover's
host CNF encodes "one of four colours per edge" as six clauses; in OPB it is a
single `= 1` equality per edge, and each triangle clause becomes one `>= 1`
constraint over negated literals — so the encoding is *better shaped* for PB, not
worse. `opb.py` emits it:

| case | tier | variables | constraints |
| --- | --- | ---: | ---: |
| `16,14,14,13` #7 | first (pin only) | 6,612 | 125,415 |
| `16,14,14,13` #7 | **retry (pin + ticket / threshold / full-root)** | 6,612 | **165,217** |

**Result: UNKNOWN, at a conflict rate two orders of magnitude below kissat's.**

| solver | case | budget | conflicts | rate |
| --- | --- | ---: | ---: | ---: |
| kissat 4.0.4 | #7 first tier | 120 s | 2,972,946 | ~24,800/s |
| RoundingSat 2 | #7 first tier | 130 s | 9,000 | ~69/s |
| RoundingSat 2 | #7 **retry tier** | 300 s | 41,000 | ~137/s |

And the cutting-planes machinery never engaged: every core-guided counter is zero
(`CG solutions found 0`, `CG cores constructed 0`, `CG core cardinality
constraints returned 0`). RoundingSat spent the whole budget in propagation and
CDCL, on a formula whose PB content is trivial: all coefficients are 1, so the
"PB advantage" reduces to at-most-one constraints that kissat handles with its own
cardinality reasoning, and the bulk of the formula is triangle clauses — pure
resolution work.

**Verdict.** The hypothesis is wrong for this instance family, and the reason is
structural rather than a matter of tuning: the ticket hypothesis is *encoded as
clauses and cardinality gadgets* in the CNF, not as PB structure that a
cutting-planes solver can exploit. A PB solver sees the same clause-level
reasoning with slower propagation. Exact might close some of the 200x gap on
coefficient-heavy instances; it will not close it here.

What would make the hypothesis right is a different encoding: keep the ticket and
interface arguments as *native PB constraints with real coefficients* (the `H >= w`
identity, the per-position coverage sums) instead of expanding them into selector
and counter CNF. Nobody has built that, and this experiment says the payoff would
have to come from the encoding, not from the solver swap.
