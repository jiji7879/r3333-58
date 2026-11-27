PROVED — only the stated finite implication on the supplied signed parent. No
whole representative, pivot branch, wall row, K58 model or Ramsey bound is
established by this certificate.

# Certified trigger exclusion on signed case 0

## 1. Exact statement and literal scope

The verified input is `K58_case0_24_patterns.zip`, SHA-256
`22d87d5245ea80b8459d3ce40698a745aea9cf6f1c611606cc490cba9a19706e`.
Its parent decompresses to 19,218 variables and 178,823 clauses with SHA-256
`ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`.
This is byte-identical to the previously audited signed parent. All 244
manifest entries pass, and all 236 `.rup` proof files are unique, referenced
and content-addressed by their own proof digests.

Let $P$ denote that entire parent, not a 30-vertex projection. It contains
all 1653 edge-colour clauses, 9918 pairwise at-most-one clauses, and 123424
negative monochromatic-triangle clauses. A terminal query is always this
whole parent plus explicit units or case-blocking clauses; it is never the
strengthened `branch-h` file from the earlier two-site package.

For an edge $(a,b)$ on vertices ordered lexicographically among 0–57, its
colour-$k$ variable follows the physical indexing rule $4i+1+k$. The audit
reconstructed that map and checked:

$$
E_{31,13,0}=2721,\qquad E_{42,13,1}=2766,
$$

and $(E_{31,42,0},E_{31,42,1},E_{31,42,2},E_{31,42,3})=(5249,5250,5251,5252)$.
The trigger is $T=(E_{31,13,0}\land E_{42,13,1})$.

The established consequence is precisely

$$
P\models \neg E_{31,13,0}\lor\neg E_{42,13,1},
$$

or, in words, **on this one signed parent it is impossible for both trigger
assumptions to hold**. The shipped file `conditional-clauses.cnf` has the
correct byte content:

```text
p cnf 19218 1
-2721 -2766 0
```

No stronger result follows for an owner with a different signed parent or for
the ordinary row without a separate semantic transfer argument.

## 2. Proof by the checked finite case analysis

The previous 24-word OPEN set is reused exactly, not redefined. Its pivot-0
list is

```text
0001 0301 0311 1001 1310 3130 3310
```

and its pivot-3 list is

```text
0103 0300 0303 0330 1103 1300 1301 1303 1313 1330 3001 3011 3110 3131 3300 3303 3330
```

The stored predecessor branch-cover queries match the prior conditional
frontier byte-for-byte. Their proof bytes are also identical to the old
`.rup.gz` contents, as are the raw compressed-parent bytes. The result is a
real extension of the previously audited 12-closure/24-OPEN state, not an
incorrect recollection of it.

The argument is a complete disjunction cover, not an inference from local
models or timeouts:

1. **Choose the original pivot colour.** Since each physical edge has exactly
   one colour in $P$, the pivot has one of colours 0,1,2,3. Two supplied
   full-parent refutations eliminate 1 and 2 and are tied to the correct event
   children. Colours 0 and 3 remain conditional cases, but are not closed
   unconditionally.
2. **Choose one of the 24 words.** For each $h\in\{0,3\}$, the earlier
   full-parent cover proof shows that under pivot $h$ and $T$, the four word
   edges must give one of the 7 or 17 listed words. It uses blocking clauses
   for every listed word on the complete signed formula.
3. **Choose an arm alternative.** Each word has an exhaustive arm-cover proof
   under its pivot/trigger/word units. The 14 physically ordered arm vertices
   are 31–44, so a complete assignment has $\binom{14}{2}=91$ edge colours.
   Each listed alternative contains 91 digits in $\{0,1,2,3\}$. Altogether
   these are 69 alternatives for pivot 0 and 148 for pivot 3, **217** in all.
   The proof of each cover certifies that no alternative has been omitted.
4. **Refute every alternative.** Four words close directly:
   $(0,\mathtt{0311})$, $(3,\mathtt{0103})$, $(3,\mathtt{0330})$ and
   $(3,\mathtt{3131})$. All **203 other** arm alternatives close separately
   with the full parent plus their arm units. The full K14 arm already contains
   the pivot and four word edges, so repeated units can occur; these are
   harmless duplicates, not a shift in edge numbering or an extra assumption
   of another arm.
5. **Close the trigger case.** Every case under $P\land T$ is now refuted.
   Hence $P\land T$ is unsatisfiable, which is exactly the asserted binary
   clause. No full-parent model or countermodel is either needed or found.

The previous unsplit 24-word cover under $T$ also replays and matches the
earlier query/proof bytes. It records the same pivot-independent prior
frontier. The **new** work is the exhaustive arm subdivision of all 24
remaining words, not merely recycling old OPEN records.

## 3. No missing verifier-only branch in this dataset

Although `replay.py` supports deeper colour splits and `forced_groups`, this
particular input uses **zero** active forced groups and **zero** deeper splits.
Every reconstructed arm node is a direct `CLOSED` terminal. Therefore this
result never promotes a guarded disjunction into unsupported conjunctive
unit assumptions and never silently skips an OPEN subtree.

The `OPEN` records from earlier rounds are not counted here as evidence. The
24 current word cases and all 217 arm alternatives are terminated by explicit
proofs. `open-leaves.tsv` is exactly its header, with zero data rows, and the
independently reconstructed list of unresolved cases is empty.

## 4. Independent replay, receipts and reproducing scripts

The official verifier was executed after freshly compiling the bundled
checker, through a proxy that removes `-w`, adds a checker timeout, requires
return code 0 and one exact `s VERIFIED`, and rejects any warning.

There are **236 distinct expected queries and 236 strict successful calls**:

| component | calls |
| --- | ---: |
| old pivot-1/2 eliminations | 2 |
| old pivot-0/3 word covers | 2 |
| old pivot-free 24-word frontier | 1 |
| new 24 arm-cover proofs | 24 |
| new direct word refutations | 4 |
| new arm refutations | 203 |
| **total** | **236** |

Checker time was 115.724 seconds. Independent analysis of every raw output
shows that **all 236** also satisfy:

- proof byte count read equals the complete proof file length;
- exactly one status line, `s VERIFIED`;
- no `WARNING`, no `ERROR`;
- `0 RAT lemmas in core`, consistent with RUP-only checking.

The coordinator's separate [DAG checker](checks/independent_audit.py), not an
import of `replay.py`, reconstructed every one of the 236 expected queries
and proof digests from $P$, the physical edge map and the case data. It compared
these exact receipts to the strict execution, re-derived the full K58 clause
core, checked the old predecessor proof bytes, and performed **2,113 passed
assertions**. Its report is [checks/2-compute.json](checks/2-compute.json).

A units-only control query, which is satisfiable by construction, rejects a
genuine arm proof with return code 1 and no verified line. The genuine proof
cut halfway also rejects, with return code 1 and no verified line. These are
actual discriminating tests, not tiny tail changes that can remain valid.
See [checks/negative-controls.json](checks/negative-controls.json).
The packaged `-w` substring acceptance is not relied upon.

## 5. Precisely what was not proved

- The parent itself is not refuted and no full K58 model was generated.
- Neither unconditional physical pivot branch 0 nor 3 is closed. Only their
  cases **under both trigger assumptions** have been closed.
- Representative 0 as a whole is not excluded, nor is any other one of the
  46 variants from the previous single row.
- Nothing transfers the binary clause automatically to all 11,585 wall rows
  or changes a production ledger status.
- No Ramsey-number statement is proved and no production search was started.
- The evidence is a finite case analysis backed by native RUP proof replay,
  not a standalone DRAT refutation of $P+T$ or a Lean kernel theorem. No new
  Lean formalisation was introduced during this audit.

The result should therefore be cited as **a certified conditional binary
clause on the selected signed case-0 representative**, with an independently
replayed and complete 24-pattern/217-arm proof, not as a wall-closure or a
proof of $R(3,3,3,3)\le58$.
