# The partition-cover branch is empty — verified here in 31 seconds

Bundle: `K58_partition_branch_exclusion.zip` (22.7 MiB), unpacked at `.scratch/pbe/`. Every checksum
in `SHA256SUMS` verifies.

## What it establishes

In the **uniform fully-sending** branch of the `(15,14,14,14)` profile, an ordinary arm cannot carry a
**partition cover** — disjoint blocks of sizes 5, 5, 4 with each block used by exactly five senders.
The route in is a clean lemma:

> In each ordinary arm, **at least two of the five four-vertex supports are different.**

So the branch where one ordinary arm's five light supports are all equal — the only shape in which a
partition cover can arise — is excluded, for both classified colourings of `A`.

## Verified

```
python verify.py --workers 4
  All 3093 fivefold four-set covers on the 332 roles have partition form.
  T: verified 138 partitions, 856 joins and DRAT proofs.
  U: verified 136 partitions, 676 joins and DRAT proofs.
```

31 seconds, exit 0. The verifier compiles `enumerate.cpp` and `drat-trim.c` from source, rebuilds the
joins, regenerates every CNF with a SHA-256 check, and **asserts `s VERIFIED` on each of the 1,532
DRAT proofs** — 856 in `evidence/T/drat` and 676 in `evidence/U/drat`, matching the reported totals.
A silent skip is ruled out in the code: the subprocess uses `check=True` and the assertion would abort.

| template | partitions with a join to A | campaign roles | joins after symmetry | allow single C/D extensions | after the sender test |
| --- | ---: | ---: | ---: | ---: | ---: |
| T twisted | 138 | 65 | 856 | 116 | **0** |
| U | 136 | 63 | 676 | 114 | **0** |

An optional independent census of single new vertices exists (`--single-vertices`): it enumerates all
254,628 five-zero words on `T` (254,088 on `U`) and checks the recorded missing columns without using
the DRAT checker. Not run here.

## Relation to the earlier campaign result

The campaign's own "partition design family is empty" — 138 designs, 276 oriented DRAT instances — is
the **inherited** result, reproduced here (the bundle says so). What is new is the **sender-level**
argument, which closes the whole cover branch rather than individual designs, and does it by
exhibiting two arm-specific columns such that every completion requires at least one, then refuting
any single new vertex that could realise either.

## What it does not do

The bundle is explicit: it **"makes no assertion that K58 has been excluded"**. The complement — the
branch where no ordinary arm has a partition cover, so at least two four-supports differ — remains
open, and that is the larger part of the uniform child. `R_4(3)` is unmoved.
