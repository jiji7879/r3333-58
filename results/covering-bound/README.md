# The covering bound cannot reach 58 — arithmetic, and a calibration

The K50 argument's shape: cover `V` by sets that each omit some colours. A set
that omits `j` colours is coloured by the remaining `4-j`, so it has size at most
`R_{4-j}(3)`: omitting one colour gives `R(3,3,3) = 17 -> <= 16`, omitting two
gives `R(3,3) = 6 -> <= 5`, omitting three gives `2`.

For the K50 that is `3*16 + 2 = 50`, sharp. For a 58-vertex branch object:

| covering shape | bound | contradicts `|V| = 58`? |
| --- | ---: | --- |
| 3 sets omitting one colour + one colour-clique | 50 | yes — but a 58-vertex object cannot have such a covering, so the hypothesis is unavailable |
| 4 sets omitting one colour each | 64 | no |
| 11 sets omitting two colours | 55 | yes — but nothing in the branch forces such a covering |

So only a <=3-set covering would contradict, and such a covering is *impossible*
for 58 vertices by the bound itself: the argument is vacuous at 58.

**And no shrinkage is available.** The per-set bound 16 cannot be improved,
because the bound is attained: computed here on every genuine colouring of order
at least 44 in `artifacts/`, the independence number in each colour is

    k49_from_n48_m5.col      n=49   alpha per colour [16,16,16,16]
    k50_blockcayley_...      n=50   [16,16,16,16]
    k50_sanity_f2.col        n=50   [16,16,16,16]
    k50_z4z4_m6.col          n=50   [16,16,16,16]
    k51_relax_... (invalid)  n=51   [16,16,16,16]
    n48_z4z4_f0.col          n=48   [15,16,16,16]

Every colour reaches 16 from order 49 on. So the arithmetic `16k` is tight and
there is nothing to shave: the covering technique gives 50 at n = 50 and 64 at
n = 58, and no branch-specific input changes that.

**Verdict.** The covering route is closed by arithmetic plus this calibration,
not by search. The only surviving shape is 11 two-colour sets (`11*5 = 55 < 58`),
and the K50 is *exactly tight* for the analogous 10-set shape (`50 = 10*5`), which
says the technique is tight rather than slack — so nothing suggests 11 sets would
suffice at 58.

