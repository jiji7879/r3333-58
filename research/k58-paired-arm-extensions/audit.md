# Paired-arm extensions: useful new positive clauses, warning-clean repair,
# and separate signed results

## 1. Result and scope

The package extends the previously checked two-colour sender-counting rule in a
genuine way. The main new family is **176,136 four-literal clauses**, with at
least one on every one of the 1,300 inputs. A 13-row propagation screen leaves
**1,747** falsifying cubes after the old positive ternaries and **939** after
the previous direct encoding plus ternaries.

These are **additional** conditional implications, not merely a claim that
four literals are stronger than three. Each must be justified by its current
root-arm guard and local five-set intersection conditions. Clause counts are
not solved rows, global transfer permissions, solver speed-ups or a Ramsey
theorem.

The two main positive examples now pass a stronger RUP replay with no warning
suppression. So do fourteen representative signed examples. The **other eleven
wide falsifying cubes remain OPEN**, with 40,000 conflicts each and no supplied
native refutation. No full K58 model or positive solver completion was found.
These examples are distinct from the fourteen ternary proofs in the preceding
archive.

The full-root CNF identities, generated clause data, screen and independent
13-example support checks all reproduce. A defect also surfaced in a
warning-free face of the original replay: the raw positive traces issue warnings
that `-w` conceals. It is repaired without changing the original artifacts,
and every proved example then passes strict full-byte RUP checking.

## 2. Common mathematical basis

As before, \(a\) lies in the root arm of colour \(c\), and \(g_{a,c}\) denotes
the encoded condition that \(a\) send colour \(c\) to at least 14 vertices in
the other three root arms, excluding the root. For another root arm \(B\) of
colour \(b\), its colour-\(c\) neighbours of \(a\) cannot have internal edges of
colour \(b\) or \(c\): otherwise a triangle with the root or with \(a\) is
monochromatic. Their mutual edges have only the remaining two colours. Six such
neighbours would create a two-colour triangle-free \(K_6\), impossible by
\(R(3,3)=6\). Each arm consequently supplies at most five vertices.

This is why, when \(g\) is true, the three supply counts have one of the forms
5,5,4 or 5,5,5. Choose any two classified arms. If no hitting-set literal is
chosen in either, those two arms each supply at most four, contradicting
\(14\) by \(4+4+5=13\). The third arm's counting bound needs no classified
template; only enumeration of its alternatives uses one.

Regeneration checks all **48 template/colour alternatives** and all **32,768
\(K_6\)** colourings. All **1,300 full-root input hashes** match. This makes
the claim more than a broadly similar argument—there is a discrete root model,
literal colour and hitting-family audit for the supplied rows.

For signed variants, let a literal be either \(E_v\) or its negation. If every
compatible five-set makes that literal true, a false literal means that the
arm cannot supply five. Literal substitution does not change the counting
step. The verifier negates every clause literal when constructing its false
cube, so the guard is true while chosen signed edge/literal evidence is false.
This direction is crucial and is checked for the replayed examples.

## 3. Four literal positive clauses

One arm can provide a singleton in every feasible five-set, while the other
has no singleton but has a **two-vertex hitting set**. If those two arms are
\(B_1,B_2\), the clause is

$$
\neg g_{a,c}\;\lor\;E(u)\lor E(v)\lor E(w).
$$

Here a compatible five-set in the first arm contains \(u\), while each in the
second contains \(v\) or \(w\). A previous example in the pair can require a
singleton from one side and a **different** two-vertex-hit from the other.
Removing otherwise-common literals avoids a disguised copy of the old ternaries.

At rank 8 the recorded clause is `-24663 1056 2428 6024`. Its sender 46 has a
guard literal 24663. The support check reconstructs **six compatible five-sets**
on one arm and **one** on the other, with intersecting the first six requiring
either of two vertices and the single set on the second requiring its singleton.
The supplied physical proof on the original parent therefore fits exactly the
meaning, not only a matching clause fingerprint.

The `wider.py` census computes these intersections, omits already-required
spokes and enumerates the actual two-element hitting sets. It returns unique
positive clauses (set semantics), while `check_supports.py` independently lists
all compatible fives for the 13 selected examples. Every example again shows
one group of six alternatives with a two-vertex hit and a singleton (rank 340
has 2 and 1 respectively, without changing its status as an actual example).
The regenerated JSON byte content matches the input archive and yields:

- **176,136** four-literal clauses;
- nonempty lists on **all 1,300** input rows.

A later independent run of `widecheck.py`, not only a repetition of saved totals,
also reproduces all 13 panel objects. It applies the older ternary clauses and
then prior direct encodings before testing each new false cube. Totals are
1,747 and 939—a real extra unit-propagation opportunity where older rules do
not already close these cubes.

## 4. What is actually certified about the four-literal cases

Only two retained positive examples have direct native proofs in this bundle:

| rank | clause | recorded conflicts |
| ---: | --- | ---: |
| 8 | `-24663 1056 2428 6024` | 105 |
| 340 | `-24652 3908 4832 6028` | 81 |

They had no prior propagation closure (`previous_direct_and_ternaries_up=false`)
and have a genuine native refutation of the false cube on the whole original
parent. The remaining **11** hash-bound queries are OPEN at 40,000 conflicts;
`widereplay.py` does not treat them as UNSAT and they receive no claim here.

Signed cases have 14 examples, consisting of 7 `mixed` plus 7 `both_negative`
records. All have **previous_ternaries_up=true**, i.e. prior propagation already
closes the tested false cube. The native proofs use the full original parent
and intended counterassignment, not merely a rewritten category label. These
certificates are useful witnesses of the counter-context, but this population
is not a fresh propagation advance comparable with the two wide examples.

There are **26,224 mixed** and **10,136 double-negative** signed candidates.
They use the fact that a vertex absent from **all** compatible five-sets makes
the negative spoke literal true. Obvious root-triangle exclusions are discarded
before those counts. The complete signed dataset also regenerates byte-
for-byte.

The candidate-independent search for other forced single spokes from linked
four/five supports emits **zero** plain and **zero** joint additions, hence zero
new singleton choices beyond those frozen triangle constraints. The separate
single-arm relaxed lookup yields empty output for every one of the 1,300 rows.
These negative claims are confined to the tested named-arm relaxations; they
do not assert a general no-existence theorem for all clauses.

## 5. Strict replay repair—what changed and what did not

The raw positive replay's earliest reported warnings include
`backward mode ignores deletion of (pseudo) unit clause [0]`. The raw checker
returns zero status and prints `s VERIFIED` amid warnings, so the stock
`-w`/substring check would accept them. My strict proxy failed on those outputs,
so the first supplied replay call did **not** get a blanket pass.

The transformation in [repair_replay.py](checks/repair_replay.py) is narrowly
defined:

1. parse the binary stream completely, accepting only `a` and `d` records;
2. retain **every `a` addition record**, with its literals and ordering;
3. omit only `d` deletion records;
4. preserve original SHA-256 digests and verify query hashes against the
   independently rebuilt original full-root parent and intended false cube;
5. replay with **`-i -U -W -t 600`**: binary input, RUP-only, warnings fatal,
   no `-w`.

Removing deletion instructions is a *strengthening* of a RUP check: it retains
more clauses in the database, so it can only help propagation and cannot
license a refutation that was not already valid. Each newly written proof gets
its own distinct hash; it is not mislabelled as the original byte stream.
Temporary or `.scratch` normalised files are not committed.

Result: **16/16 accepted**. Every complete normalised proof is consumed, each
call returns 0 with one exact `s VERIFIED`, zero warnings/errors, and `0 RAT
lemmas in core`. The provenance totals are:

- **431,370 original proof bytes**;
- **263,222 normalised strict proof bytes**.

This does not mean widening a bad argument was needed to save it. No actual
counterexample to any displayed rule was found. It means the original
`-w` reporting conceals warnings that must be dealt with explicitly instead of
being treated as a clean checker certificate.

## 6. Performance evidence and appropriate next interpretation

The supplied six-rank benchmark still produces **0/6 unrestricted completions
at 60,000 conflicts**. The prior-plus-positive policy and the policy augmented
with all four-literal additions are both open. The ranks alternate which policy
runs first, but this remains one seed-zero comparison, not a robust performance
evaluation. The attached older 800,000-conflict experiments also leave main
families unresolved under all policies.

Auxiliary pentagon choices in extended encodings are legitimate implicational
extensions: a real model can select the selectors for its realised supports,
and received selector units and clauses are original-parent logical
consequences, not guessed new models. Still, encoding length/clause volume is
no guarantee of better search.

The useful reading of this attachment is that it isolates a bigger, validated
**local cube-elimination family** with names indices and mechanically checked
support intersections. A subsequent experiment should add these clauses to the
same hash-bound parents, measure matched propagation and search time with more
than one seed/selection policy, and distinguish genuine pruning from version or
ordering effects. It need not start with the full 1,300-row sweep. The package
makes the inputs available, not a production recommendation.

## 7. Reproduction artifacts

- [2-compute.json](checks/2-compute.json): archive identity, exact census and
  screen totals, thirteen independent support cases, the eleven OPEN wide
  queries and initial warning receipts.
- [strict-clean-replay.json](checks/strict-clean-replay.json): all 16 clause,
  parent, query, original-proof-hash and normalised-proof-hash bindings plus
  checker results/full byte counts.
- [check-supports.out](checks/check-supports.out): 13 selected four-literal
  clauses and their actual compatible five-set counts.
- [repair_replay.py](checks/repair_replay.py): the source for the deletion-only
  transformation and strict `-U -W` checking.
- [2-compute.md](checks/2-compute.md): full commands and timing/provenance notes.

No production ledger or queue was updated, no further Ultramath run was started
or resumed, no original package input was edited, and no Lean kernel proof was
requested or claimed. The reported long-budget numbers are supplied metadata,
not new timed search runs by this reviewer.
