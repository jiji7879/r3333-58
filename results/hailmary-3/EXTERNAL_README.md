# Verified: the external hail-mary package (116-cell pattern exclusion)

`attachments/let-s-try-and-wcbj/K58_hail_mary_proof.zip`, 19.6 MiB. Everything
below was re-run here; the package's own README is `README.md`, its checker
`check_witnesses.py`, its certificates in `certificates/` (the DRATs are 32 MB in
total and are regenerable, so only the CNFs are stored here).

## What it proves

**A 116-cell partial-word exclusion.** Fix all fourteen words of arm `B` and the
42-slot instance is UNSAT (that is `results/hailmary-2/`). This package shows that
**116 specified cells on ten of those words already suffice**: a table of ten
partial rows (dots for unrestricted entries), with the ten rows allowed to occupy
**any ten distinct positions of `B`**, is unrealisable in the uniform branch. The
proof splits on which of `C`, `D` supplies the forced pentagon — two CNFs of
1,261 variables and 4,641 clauses each.

**Verified here.** All three certificates replay to `s VERIFIED` with drat-trim on
this machine:

| certificate | vars | clauses | core | RAT lemmas | verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| `pattern-2` | 1,261 | 4,641 | 2,900 | 510 | `s VERIFIED` |
| `pattern-3` | 1,261 | 4,641 | 2,790 | 522 | `s VERIFIED` |
| `local6` | 1,510 | 7,166 | 5,330 | 1,465 | `s VERIFIED` |

and `check_witnesses.py` verifies both colourings (6,545 and 7,140 triangles, the
root arms, the labelled template, all zero supports) and confirms that the
original arm matches all 116 specified cells on ten distinct rows. `sha256sum -c`
on the package's `SHA256SUMS` passes for every file.

## Why this matters for the counts-versus-words question

The package also settles *why* counting fails, in a sharper form than my profile
experiment (`results/hailmary-2/`). Pinning all fourteen words of `B` and adding
`k` further colour-2 vertices:

| fixed information on `B` | extra colour-2 vertices | result |
| --- | ---: | --- |
| all fourteen words | 5 | **SAT** (`five.col`, a good `K_35`) |
| all fourteen words | 6 | **UNSAT** (`local6`, 7,166 clauses, verified) |
| only the zero positions of all fourteen words | 6 | **SAT** (`same_zeros_six.col`, a good `K_36`) |

So the maximum is five, and the `K_36` witness has the **same 70 zero cells** in
the same rows and columns as the original arm while changing 51 of the 140
ordinary letters. **The zero-incidence matrix cannot imply the six-vertex
contradiction** — the ordinary letters carry it. That is the clean explanation of
my result that pinning the coverage *profile* leaves the instance undecided: the
profile is a coarsening of the zeros.

## Its own reproduction of the 42-slot benchmark

The package rebuilt the 42-slot model in its own labelling and measured: none 90 s
UNKNOWN, matching profile 90 s UNKNOWN, profile `{0..4}` 90 s UNKNOWN, all original
zero positions 90 s UNKNOWN, all original words **UNSAT in 17.73 s** — consistent
with my 10.5 s on `results/hailmary-2/`'s encoding.

## What it does not do

No complete coverage profile, no ledger row, no change in the Ramsey bound. The
proposed solver use — reject a branch whenever a matching covers the ten pattern
rows (`matches_pattern`) — is **not measured**: it needs the template labels
translated and the cut guarded by the branch hypotheses, and the package says so.
