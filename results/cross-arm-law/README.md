# The cross-arm matching law, checked here — and it is a genuine new discriminator

Two external packages arrived. Both quick verifiers pass on this machine; the
full replays are running.

* `K58_uniform_word_cover.zip` (104 KB): at most **12** of the 42 outside words
  omit an ordinary colour. `python3 verify.py --quick` passes in 3 s and prints
  the whole chain: the two witnesses' omission counts `[0,0,0]` and `[6,0,0]`,
  the best three-set union apart from `B,C,D` at 37/42 and 38/42, 77 and 54
  blocked cross-pairs, 1,024 joins in four placements on catalogue arm 271, all
  32x32 placements blocked, and the final "at most 12 omitting words, and at most
  11 if one arm has at least five".
* `K58_cross_arm_compatibility.zip` (6.6 MB): at most **three** omissions per
  14-arm, so at least **33** of the 42 use all four colours (the previous bound
  was 30). Its `--quick` passes in 57 s: "All 30 rooted template views satisfy the
  third-colour matching law", "support incidence excludes 37 of 332 arm types",
  "4,724 partial joins reconstructed", "339 DRAT refutations and explicit
  relabellings cover all 4,724 joins", "Verified. A branch object has at most
  three omissions per small arm."

## The matching law, verified independently here

For a sender template and its root, with `I`, `J` the two ordinary neighbourhoods
of the root, the counts of the three colours between `I` and `J` are

| `|I|`,`|J|` | own colours | third colour |
| --- | ---: | ---: |
| 4,5 (either order) | 8 and 8 | 4 |
| 5,5 | 10 and 10 | 5 |

I recomputed this for **both** templates, all 15 roots and all three arm pairs
(`matching_law.py`): every case matches, with the third colour taking the small
count in each. The double count then gives, between any two arms,
`sum over own-colour edges of |Z(x) ∩ Z(y)| = 130` and over third-colour edges
`= 65` — since ten senders see a 4-5 split (8+8) and five see 5-5 (10+10):
`10*8 + 5*10 = 130` and `10*4 + 5*5 = 65`. The consequence that at least nine of
the fourteen vertices attain five follows from `t*5 + (14-t)*4 >= 65`.

## It bites: the known witnesses violate it badly

Computed on the campaign's own objects, per arm pair, as `(own, own, third)`:

| object | pair (1,2), third 3 | pair (1,3), third 2 | pair (2,3), third 1 |
| --- | --- | --- | --- |
| required | 130, 130, **65** | 130, 130, **65** | 130, 130, **65** |
| `plain.solver.wit` | 72, 88, **151** | 125, 81, **111** | 76, 96, **143** |
| `rung3.wit` (one pair) | 116, 97, **112** | — | — |

Every arm pair is wrong, and the third-colour total is roughly double what the law
requires. So this is **not** implied by the pair level or by the word families the
campaign already encodes: it is a genuine cross-arm constraint that a branch object
must satisfy and every existing witness breaks. That is the first such law the
campaign has had.

## Scope

Neither package closes a row: both READMEs say so, and the seven uniform children
remain open. What they give is a sharp structural bound (16 -> 12 -> 9 omissions)
and one exact identity that couples two arms through the senders' templates. The
identity is weighted (`|Z(x) ∩ Z(y)|` depends on the words), so it is not a clause
family; as a pseudo-Boolean or cardinality constraint it is exactly the shape that
`results/hailmary-4/` showed the SAT solvers do badly on. The right use is as a
checker and as a lemma in a paper argument, not as another clause bundle.
