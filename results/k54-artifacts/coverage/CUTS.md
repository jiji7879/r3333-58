# What a reduced-instance refutation proves about a cut, and when it proves nothing

A cut is a clause over the outer count variables.  With the unary chains of
`pilot/cnfs/B.counts.json`, "column `k` has at least one outsider" is the literal `u_{k,1}`,
so a clause is a set `C` of columns with the reading

  **not** (every column of `C` holds at least one outsider).

## The obligation

By `COVERAGE.md`, every triangle-free colouring that realizes the pins of `B` induces a count
vector satisfying the outer CNF — *after choosing one table rectangle per outsider*.  So the
cut is implied by the graph constraints iff **no** such colouring admits **any** admissible
choice whose induced vector has `count_k >= 1` for all `k` in `C`.

## When `|C|` positive counts force `|C|` distinct outsiders

An outsider `w` is assigned exactly one table rectangle `R`, and contributes exactly one
column on each side at `R`, namely `(R, s, sigma_s(w))`.  Therefore two columns
`(R,s,sigma)` and `(R',s',sigma')` can be witnessed by the same outsider exactly when

  `R = R'` and `s != s'`,

i.e. **the same rectangle on opposite sides**.  Consequences:

* If no two columns of `C` share a rectangle with opposite sides ("`C` is side-injective"),
  every graph with `count_k >= 1` on all of `C` contains `|C|` **distinct** outsiders, one
  per column, and the reduced instance that pins `|C|` distinct outsiders - one to each
  column - covers exactly the graphs the cut forbids.  A DRAT refutation of that instance
  then certifies the cut.
* If some pair **does** share a rectangle on opposite sides, one outsider may witness both
  literals.  The instance that pins `|C|` distinct outsiders is then a *stronger* hypothesis,
  and its refutation proves nothing about the cut.  The honest certificate is a case split
  over the legal merges (at most one merge partner per column, since an outsider has one
  signature per side): refute one reduced instance per matching.  `cut_witness.py` computes
  the matchings.

Three columns never need more than `1 + 3 = 4` instances (all distinct, or one merged pair).

## Numbers for the pilot boards

`cut_witness.json`, from `python3 cut_witness.py`:

| board | columns (left/right) | rectangles with both sides | sharable pairs | fraction of all pairs | risk for a random triple (union bound) |
| --- | --- | --- | ---: | ---: | ---: |
| local-15 | 717 (257/460) | 141 | 773 | 0.30% | 0.9% |
| live-07 | 495 (127/368) | 80 | 460 | 0.38% | 1.1% |
| live-14 | 672 (427/245) | 120 | 767 | 0.34% | 1.0% |

Small, but not zero, and the soundness rules call out exactly this trap.  Any three-literal
cut handed to the swarm should be run through

```sh
python3 cut_witness.py local-15 <k1> <k2> <k3>
```

before its reduced instance is used as a certificate.  `side_injective: True` means one
refutation suffices; `False` prints the extra instances that must also be refuted.

## What this is not

It is not a check of the DRAT proof, the clause-to-unary mapping, or the killed-vector count;
those belong to the cut's own certificate.  It only settles whether the reduced instance the
certificate refutes is the one the cut needs.
