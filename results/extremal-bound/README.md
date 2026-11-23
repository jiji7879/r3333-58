# The 16 -> 12 extremal bound: encoded, and worth 1 %

An external report claims a strengthening of the uniform child: at most **12** of
the 42 outside vertices can omit a colour on their edges into `A` (previously 16),
so at least 30 use all four colours. The proof is said to use the 332-colouring
catalogue of a 14-arm — machinery this campaign certified in `results/arm-alphabet-14/`
— and the proof itself has not arrived, so the claim is unverified.

**What it is, restated.** An "omitting" slot is exactly an extremal slot: its word
has an empty ordinary part (profile `(5,5,0)`). So the claim is a quantitative
version of §47's certified theorem ("not all 42 words are extremal"), giving a
ceiling of 12 rather than 16.

**Measured here.** `extremal.py` encodes it on the 42-slot instance exactly —
`e_f(x) <-> M_f(x) = empty`, `ext(x) <-> some e_f(x)`, then `at_most 12 of the 42`
— 672 extra variables, 3,221 extra clauses:

| instance | variables | clauses | status @120 s | conflicts @120 s |
| --- | ---: | ---: | --- | ---: |
| 42 slots, as built | 45,381 | 179,318 | UNKNOWN | 4,743,303 |
| + at most 12 extremal | 46,053 | 182,539 | UNKNOWN | **4,696,072** |

One per cent fewer conflicts, no decision. That is the eighth clause-level
intervention measured in this campaign and the eighth without a gain; the pattern
is now strong enough to be treated as a fact about these instances rather than bad
luck.

**Why the covering still cannot close it.** The report's own test agrees with the
arithmetic in `results/covering-bound/`: with the three compatible rooted `K_30`
colourings it built, only `B, C, D` covers all 42, every other triple covers at
most 37, and the construction dies at the cross-arm edges with 77 pairs having all
four colours forbidden. A covering of the 58 vertices by colour-omitting sets
gives `16k`, which is 50 at `k = 3` (impossible for 58 vertices) and 64 at
`k = 4` (no contradiction); the calibration there shows `16` is attained in every
colour, so there is no slack to exploit.

**What would make the 12 matter.** A bound of the form "at most 12 extremal" only
closes the branch if something else forces *at least* 13. Nothing does today: the
pair-level witnesses carry 5 or 6 extremal slots, so the achievable count is low.
The live question is therefore whether the coverage and pair-rule structure forces
a *minimum* on extremal slots — and the honest answer is that two years of work on
this profile have never needed one.

## The proof arrived, and what I could and could not check

`attachments/let-s-try-and-wcbj/K58_uniform_word_cover.md` (11.3 KiB). Structure:
a location lemma (five omitting vertices in one arm carry five of the six words
`{6,8,10,12,16,17}` of the eighteen extremal words, by a finite classification
over the 332-catalogue), a per-arm cap of six, an exterior lemma (if an arm has
five or more omissions, every omitting vertex outside it omits that arm's root
colour, and at most five occur in the other two arms), and then the table

| largest omission count in one arm | bound on the total |
| ---: | ---: |
| <= 4 | 12 |
| 5 | 10 |
| 6 | 11 |

which gives **12**. The table's arithmetic is right, the case split is exhaustive,
and the shape of the argument — finite classification, then a two-star exterior
test — is the right one.

**What I could not check.** The load-bearing computation is "2,339 multisets of
five extremal words survive the hereditary necessary conditions, and exactly six
five-subsets are realisable", which their `verify.py` performs. I attempted an
independent check with this campaign's own encoder and **the attempt was invalid**:
I built the single-arm instance with `ladder.build(tpl, [14])`, and that encoder
carries the *three-arm* coverage totality (exactly two arms at four-or-five
coverage), which is unsatisfiable with one arm. Every UNSAT it returned was an
artefact of that, not a refutation of the lemma — which is why it returned UNSAT
for five of the six claimed subsets, an outcome no honest check should produce.
The correct instance is `m4/enc.py` with sizes `(14,0)`, whose families are the
one-arm ones; I did not get to it.

**What is new and useful regardless.** Their cover analysis quantifies the target
rather than gesturing at it: 63 natural neighbourhoods, 39,711 triples, only
`B, C, D` covers `X`, every other triple covers at most 37, four sets cover at
most 41 — so **an upper bound of 41 on the outside capacity would close it**
against `|X| = 42`. That is the sharpest statement of what a covering argument
would have to prove, and it is one vertex, not sixteen.
