# K58 representative-pair package: mathematical and symmetry-cover audit

## Judgment

**The package is mathematically useful as an unrestricted-row-root symmetry decision cover and as an exact local preprocessor. It is not, by itself, a mathematical reduction of the ordinary wall.** I independently established the complete local sorted table and preferred-pair existence cover by strict replay of all 608 local RUP certificates, checked the representative semantics on all 3,330 supplied local SAT witnesses, and checked the physical signed-unit/pentagon premises on all 11,585 rows.

**All 11,585 ordinary wall rows remain OPEN.** The reduction from 60,817,332 labeled cells to 3,604,436 preferred jobs is scheduling compression, not 57,212,896 newly closed mathematical cases and not a reduction in the number of OPEN wall rows. The handoff reports zero raw A/B closures and zero new D closures at 128 conflicts; those timeout/OPEN outcomes and C's sorted exclusions do not close any whole unrestricted row. Prior unsplit A/B/C and 1000-pattern experiments likewise supplied no established solver improvement.

I would **not spend a broad new K58 solver campaign on this evidence**. The correct limited use is the already-built root-level job cover and local exclusion table. Any additional solver expenditure needs its own small, fixed, matched cost/closure test with strict proof production; the reported D result gives no positive signal for scaling. There is no basis here for claiming a solver speedup.

## Inputs and private setup

I worked only in my extracted/private member copy and ran no K58 SAT search. `input_sha256.txt` records:

```
93055577ff1adb617949a66376c48940a3e1177a7874ff00bae7a2ed17c9386a  K58_wall_batch_handoff.md
10398532cfbccfa8fcc680f34308ad9465d71f976cbac56b117298ff3a08cae6  K58_40000_pattern_trials.tsv
c59d0dbbd8e2108ab0f376377a489f26897246f3ff3d971983ebd5b3523e387a  K58_wall_10k_batches.zip
```

The principal commands, from `.ultramath/smwy7kg2n/m4/`, were:

```sh
unzip -q K58_wall_10k_batches.zip -d extracted
(cd extracted/K58_wall_10k_batches && sh setup.sh)
extracted/K58_wall_10k_batches/.venv/bin/python strict_replay_local.py
extracted/K58_wall_10k_batches/.venv/bin/python audit_sorting_encoding.py
python3 audit_cover.py
python3 audit_root_pins.py
```

Setup used only the bundled offline Python 3.12 wheel and compiled the supplied checker source. No solver was invoked by my audit scripts. Standard output and output hashes are preserved in `*_stdout.txt` and `*_sha256.txt`.

## 1. What the local proofs certify

For arm size $n$, the local formula has one exactly-one-of-three variable group per arm edge, all monochromatic-triangle exclusions, and the signed two-color pentagon. `sorted_base(n)` additionally sorts the $n-5$ outside pentagon-word vectors lexicographically.

### Complete sorted table

For each $n\in\{11,12,13,14\}$ and every one of the 76 legal one-vertex words $z$, `cover_proofs.query` fixes the second sorted word to $z$ and adds one blocking clause for every corresponding retained SAT first word. Independently replaying its RUP proof shows that every sorted full arm coloring with second word $z$ has one of the listed first words. Conversely, I checked every listed full coloring: exact edge count and alphabet, every arm triangle, every fixed pentagon edge, sorted words, and its stated first two words.

The witness counts are

| $n$ | checked local SAT models | catalog preferred pairs |
| --- | ---: | ---: |
| 11 | 1,272 | 1,214 |
| 12 | 1,049 | 941 |
| 13 | 692 | 530 |
| 14 | 317 | 156 |
| total | **3,330** | **2,841** |

Every preferred catalog label occurs as the owner label of at least one checked witness. Thus the 304 sorted exclusions plus the 3,330 witnesses establish the complete local sorted classification, not merely the screen survivors.

### Complete preferred-pair existence cover

For each $(n,z)$, `preferred_proofs.instance` uses the sorted local arm formula, defines exact word/occurrence indicators, forbids every preferred unordered pair anywhere in the outside word multiset, and fixes the second sorted word to $z$. Its independently checked RUP refutation rules out a preferred-pair-free sorted arm with that second word. Since the 304 cases cover all possible second words, **every complete local arm coloring contains at least one preferred pair**. This conclusion does not rely on the catalog-learning search, its greedy rounds, or the finite witness pool.

### Strict replay actually performed

`strict_replay_local.py` regenerated every query with the supplied encoder, checked its receipt hash and every decompressed proof hash, and ran, sequentially with one worker:

```sh
drat-trim query.cnf proof.rup -i -U
```

There was deliberately no `-w`. Results in `strict_replay_local_stdout.txt` and `strict_local_replay_results.json`:

* **304/304 sorted proofs and 304/304 preferred proofs: `s VERIFIED`**;
* 608 regenerated query/proof hash pairs checked;
* 9,890,764 decompressed proof bytes;
* 26.979 seconds wall time;
* checker SHA-256 `a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066`.

The bundled `cover_proofs.rup()` itself appends `-w`, contrary to the requested replay policy. I did not use that helper for the checker invocation. `drat-trim` help says `-w` suppresses warnings, `-i` forces binary proof parsing, and `-U` allows only RUP additions.

These are **local arm proofs**, not 608 whole-row refutations. I did not independently replay all 42 full-parent physical proof injections in this direction.

## 2. Exact raw, sorted, and preferred semantics

Let $P_r$ be the unrestricted first-tier parent for row $r$, let $O=(o_0,\ldots,o_{m-1})$ be the outside vertices of its nominated arm, and let $W_\phi(o)$ be the five-digit word of physical coloring $\phi$.

* A **raw** job is $P_r$ plus the ten units $W(o_0)=w$, $W(o_1)=z$. It imposes no ordering or ownership constraint on the other outside words. Its refutation closes that raw restricted formula.
* A **sorted** job adds lexicographic nondecrease of the entire word list $(W(o_0),\ldots,W(o_{m-1}))$. Its first two entries really are the two smallest. Its refutation closes only that sorted restricted formula.
* A **preferred** job for catalog pair $p_j=(w,z)$ fixes those words on $o_0,o_1$, sorts only the tail $W(o_2),\ldots,W(o_{m-1})$, and asserts the ownership guard. The guard makes $p_j$ the lexicographically first preferred pair present anywhere in $O$. A preferred pair need not consist of the two smallest words.

In `representatives.py`, gates satisfy $g_i\Rightarrow g_{i-1}$ and $g_i\Rightarrow\neg\mathrm{Present}(p_i)$. For distinct words, presence means both occur; for an equal pair $(w,w)$, it means two outside vertices have word $w$. Owner $j$ assumes $g_{j-1}$ (when $j>0$) and $\neg g_j$. The ten physical pins ensure $p_j$ itself is present; $g_{j-1}$ excludes every earlier preferred pair. This implements the stated first-present-pair convention. Equal-word presence correctly uses all vertex pairs in the physical preferred extension, rather than only adjacent vertices.

`audit_sorting_encoding.py` exhaustively evaluated the actual one-adjacent-pair `sorted_base(7)` comparator for **59,049 ordered pairs of arbitrary three-color five-digit words**, with all 16 assignments of its four auxiliary variables. It accepted exactly the **29,646** nondecreasing pairs, with zero mismatches. Repetition of the same comparator construction sorts the longer lists.

## 3. Why the root cover transports, and where it stops

### Signed physical data: full 11,585-row check

`audit_root_pins.py` independently recomputed K58 edge variable numbers and inspected the frozen signed units. It passed on every row:

* $O$ has exactly $2(n-5)$ incident signed units: a positive root-color edge from $O$ to the root and a negative marked-color edge from the marked vertex to $O$. No other prescribed signed unit touches $O$.
* The nominated arm has size 11--14, is unnamed (`root_kinds[b] == '-'`), and is distinct from the marked arm.
* Word color 0 is the marked color. All **115,850** nominated pentagon edges match the local cycle/diagonal order and physical palette convention used by the local formula.
* Counts were 40, 628, 3,374 and 7,543 for sizes 11, 12, 13 and 14 respectively; all seven profiles were present. See `root_pin_audit_results.json`.

The K58 exactly-one and triangle clauses are invariant under every graph-vertex permutation. The checked pins are invariant under permutations fixing the signed pentagon. For the auxiliary predicates, `dense.py::marked_threshold` shows why an extension survives as well:

* vertices of the small unnamed nominated arm are not selected as sender centers in the first-tier (`full_root=False`) marked/total-critical predicates;
* where its outside vertices occur as candidates for senders in other arms, only the cardinality of selected candidate edges matters;
* `support_tables.py` skips an unnamed target arm (`kind == '-'`). Thus no named support table distinguishes individual members of $O$.

Consequently, an outside permutation preserves the full parent satisfiability condition, including the ability to choose the cardinality/support auxiliary variables. This is a semantic extension argument from the generator, not merely invariance of the ten exported physical pins.

### Decision-cover theorem at an unrestricted root

Take any physical parent solution. Restrict it to the nominated complete arm. The 304 preferred proofs give at least one preferred pair; choose the least present pair $p_j$. Rename a witnessing pair of vertices to $o_0,o_1$, orienting unequal words increasingly, and sort the remaining outside vertices by word. By the symmetry argument above, the renamed physical coloring still extends to the parent auxiliaries. It satisfies preferred job $p_j$ and its owner guard. Therefore:

> Strict refutations of **every** preferred job for a given row imply UNSAT of that row's unrestricted first-tier parent, and then close that whole row. A direct strict refutation of the unrestricted parent also closes it.

For a fixed complete arm coloring, the least present preferred pair is unique. However, there may be several vertex pairs implementing that same label: 33 of the 3,330 checked witnesses had more than one such vertex pair (one had four). The output is one **pair label**, not a unique vertex renaming.

### Raw-cell mapping is not unique

There is no generally valid existence-and-uniqueness function from an old raw two-star cell to one preferred representative. The canonical label depends on all other outside words, which the raw ten pins leave free.

The finite audit gives an explicit local-interface counterexample. For $n=11$, raw pair $(00000,02100)$ has two fully checked local arm colorings, with SHA-256 hashes

```
0e4cc953d4e0af7dc6daed9e25c5dd0f147bbf5bab14f589e39d388071dae8aa
b1f99fc86416bb9c863d85db4297a27afba67df0b55da76b554ff46592c328c9
```

whose earliest preferred labels are respectively $(00000,02001)$ and $(00000,02100)$. Both full model strings are in `cover_audit_results.json`. Across the supplied finite witness set, 15,251 represented $(n,\text{raw pair})$ keys have multiple preferred labels and 15,389 have multiple sorted labels. These counts are witness-set diagnostics, not an exhaustive arm census.

This many-to-many raw-interface relation **does not invalidate the root decision cover**: existence of a canonical full-coloring image and uniqueness of its pair label are all the UNSAT theorem needs. It does invalidate a literal claim that old raw cells are bijectively renamed into representatives or that one preferred-job refutation proves the corresponding raw job UNSAT. The preferred job has extra tail-order and owner constraints.

Likewise, “partition” should be read as disjoint canonical-label/orbit decision classes, not as a literal partition of every fixed physical parent solution. A noncanonical physical solution generally must be permuted before it satisfies a sorted or preferred naming formula.

### Root-only, not arbitrary under-cube transport

At the unrestricted row root, the above argument chooses the permutation separately for each solution. Under a pre-existing cube, that permutation must also preserve satisfaction of the cube (or an equivalent case-specific transport must be proved). Arbitrary physical cubes, including ten-pin raw cells, can distinguish $o_0,o_1$, so arbitrary permutations need not preserve them. The new representative cover is therefore not automatically a quotient of every saved under-cube frontier.

## 4. Counts, capacity observations, and remaining limits

The independently recomputed weighted preferred total is

$$
40(1214)+628(941)+3374(530)+7543(156)
=48{,}560+590{,}948+1{,}788{,}220+1{,}176{,}708
=\boxed{3{,}604{,}436}.
$$

This certifies queue arithmetic from roster arm sizes and catalogs. It does not close the rows those jobs cover.

`audit_cover.py` also exhaustively checked all $2^{15}=32{,}768$ two-colorings of $K_6$: none lacked a monochromatic triangle. Thus a color class in a three-color triangle-free complete graph has degree at most five, supporting the capacity-screen argument.

A minor wording issue is that the implemented outside capacities $(5,3,3)$ are valid upper bounds but not all tight. At a pentagon site, the marked vertex already supplies one color-0 neighbor, so outside color-0 capacity is at most **4**; there are already two cycle and two diagonal neighbors for colors 1 and 2, giving 3 each. Using 5 is conservative and does not threaten completeness or the local proofs. It should not be described as the exact maximum.

Finally, `cheap.py::certify` returns `UNSAT_SORTED_ARM` directly from the exact local table before constructing a separate full-parent proof. That status is a mathematically transportable local exclusion when the physical query and conventions are as audited, but it should not be confused with an individually stored full-row DRAT certificate, and it is not a whole-row closure.

## Artifact map

* `strict_replay_local.py`, `strict_replay_local_stdout.txt`, `strict_local_replay_results.json`: all 608 strict local replays.
* `audit_root_pins.py`, `audit_root_pins_stdout.txt`, `root_pin_audit_results.json`: complete-roster physical symmetry premises.
* `audit_cover.py`, `audit_cover_stdout.txt`, `cover_audit_results.json`: all 3,330 models, catalog ownership, raw non-uniqueness examples, and exhaustive $K_6$ check.
* `audit_sorting_encoding.py`, `audit_sorting_encoding_stdout.txt`, `sorting_encoding_audit_results.json`: exhaustive actual comparator semantics.
* Consolidated cryptographic hashes: `audit_artifacts_sha256.txt`.
