# K58 case 0 — direction B audit

## Verdict

**Pass for the three supplied signed-CNF refutations, subject to the scope below.** After inspecting the sources, I compiled the bundled `drat-trim.c` unchanged and replayed every original binary proof directly with `-i -U`, never `-w`. Each positive run had exit status 0, exactly one `s VERIFIED` status line, zero warning occurrences, and empty stderr. The supplied default Python/LRAT path also passed with no warnings. Discriminating native and Python negative controls were rejected as intended.

This is proof checking, not a new K58 search or a Ramsey-bound result.

## Inputs and source inspection

* ZIP SHA-256: `f08ec771eaf99c31d22cbe4d364ccd0ca80365f41a1395e1a152d067aabcf192`.
* `parent.cnf.gz` SHA-256: `aceef062c0f8b511a96c10f39265c02cd25333cd101000a6c0493568a5d5a380`.
* Decompressed parent SHA-256: `ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`; 3,423,661 bytes, 19,218 variables, 178,823 clauses and physical clause lines.
* `drat-trim.c` SHA-256: `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`; compiled with `cc -O2`, with empty compiler stdout/stderr.
* `verify.py` SHA-256: `62caee6bf2831845be9326c07f2f438cead558c10e20811f4227427b12741ec9`.
* `event.json` SHA-256: `af30cc194054c79a93b063d78087c0ec5ef1dbec4d37244239a163c6b20efda2`.

The C help and option dispatcher establish that `-i` forces binary proof parsing, `-U` permits only RUP additions, and **`-w` suppresses warnings**. The supplied `native_replay` uses `-i -w -U` and tests `b"s VERIFIED" in checked.stdout`. That optional path therefore does **not** implement the coordinator contract. I did not execute it. My direct runner counts normalized CR/LF-delimited status lines, requires the sole status to be exactly `s VERIFIED`, counts warnings in both output streams, and requires empty stderr.

## Exact signed queries

I independently decompressed the parent, changed only the DIMACS clause count, and appended the displayed signed unit clauses. The pivot formula gives edge index 1312 and variables `[5249,5250,5251,5252]`, agreeing with the event. Hashes are over the exact query bytes.

| Query | Appended units | SHA-256 |
|---|---|---|
| color0 | `5249 0` | `25bb3d2500487ee87ccde7c41274538ac484344a42b301b54b9d99036ff0a5e5` |
| color1 | `5250 0` | `84ba8a7e6bb372c0d5e6c4485bee7e47c8ca5081277f4f8d8beabbe0d1fee33f` |
| color2 | `5251 0` | `858216a74117455646e51880ca1392e957da8800ccb95f5189870d67007ad83c` |
| color3 | `5252 0` | `7aedd43ca0cd6ea1be6a5219abd17c72160807bcc4c2b95936741b7dfdbf6bee` |
| cover | `-5249 0`, `-5252 0` | `30163e3ddaefb8241137b19bcdceafc7d1c9facfb85f0c76a239d53c71923a70` |

The child queries have 178,824 clauses; the cover query has 178,825. Only color1, color2, and cover have supplied proofs and were natively replayed.

The color1 event also names `search_query = 7b3910a5331ded5cf2108dd04f225ca5075a9d44a636b0c8a1017d297385cc25`; that is not the native proof input. The replay binds its RUP to the event's reconstructed `query = 84ba8a7e…` bytes above.

## Native RUP replay and proof identities

Command form for every positive and control was:

```text
work/drat-trim QUERY PROOF -i -U
```

| Claim | Original binary RUP SHA-256 | Binary additions / deletions | Matching LRAT SHA-256 | Strict native result |
|---|---|---:|---|---|
| color1 | `7bb85210d29faa078a357ecc0da28e51cb9d58ed0c5a48eaec7d201284acc6b4` | 36 / 77 | `767d2ea4b9817eb5a204c790a95bbe130fb1cb6e56a2fce1dfebac393254534f` | exit 0; one `s VERIFIED`; 0 warnings; empty stderr |
| color2 | `ffe9aaeaa2a2d5048174df0b80599ef0197ec024c4b051bc9860cff58ef7f9f3` | 1 / 0 | `0664efa14bd9864d81cdb10d64b791fc03c1e7db64199f4d69b4bedf054635c3` | same |
| cover | `67229c09284239f78229d4920d7527495a2ccaca3775e262d11d8754ec161d66` | 38 / 0 | `1c2452e0738c29a3a84b223484e221ebb4196ca2d6acd399fd18bab9209d1613` | same |

The color1 file includes deletion instructions despite its `.rup` suffix; `-U` restricts the **additions** to RUP. All three native reports say zero RAT lemmas in core. The optimized LRAT counts need not equal raw binary addition counts: the Python checker accepts 36, 1, and 35 additions respectively. Color2's single binary addition is the empty clause, and the signed query is unsatisfiable by unit propagation.

### Native negative controls

| Control | Observed outcome | Why it discriminates |
|---|---|---|
| Empty addition alone against color1 query | exit 1, `s NOT VERIFIED`, 0 warnings | Learned steps are necessary; an arbitrary empty-clause claim is not accepted. |
| Empty addition alone against cover query | exit 1, `s NOT VERIFIED`, 0 warnings | Same check on the two-guard query. |
| Original color2 proof against the parent **without** `+5251` | exit 1, `s NOT VERIFIED`, 0 warnings | The exact signed guard matters; the empty proof is not portable to the unsigned parent. |
| Color1 proof with its last nonempty lemma removed | exit 1, `s NOT VERIFIED`, 0 warnings | A targeted corruption of the actual proof is detected. |
| Valid cover proof plus trailing `x` | exit 0 and `s VERIFIED`, **1 warning** | Exit/status alone is insufficient. The strict zero-warning gate rejects this; warning suppression would hide the required signal. |

Dropping only a redundant final empty record was explored but is **not** called a negative control: such a prefix can remain a valid refutation. This is why the final suite uses the targeted controls above.

## Supplied standalone Python/LRAT checker

Running `python3 package/K58_case0/verify.py` (without `--native`) exited 0, emitted no warnings or stderr, and printed:

```text
VERIFIED color 1 (36 RUP additions)
VERIFIED color 2 (1 RUP additions)
VERIFIED cover (35 RUP additions)
{"index": 0, "pivot": [31, 42], "excluded": [1, 2], "unresolved": [0, 3], "archived_parent": "OPEN_UNKNOWN"}
```

Source review found no non-stdlib dependency in the default path. For each proposed clause it negates the clause, follows the cited unit/conflict chain over original clauses and earlier accepted additions, and requires the final derived clause to be empty. It supports textual RUP additions with positive clause hints, not arbitrary LRAT deletions or RAT proofs. Omitting deletions is sound here because retained clauses remain available; it can be less efficient, not an inference of new clauses.

The control suite rejected all 11 intended negatives: missing guards for all three proofs, reversing the color2 guard, a changed final conflict hint, dropping each proof's final LRAT record, an empty-clause claim on a satisfiable toy CNF, a unit chain with a missing propagation link, and an unknown hint. Positive toy refutations using two complementary units and a three-clause propagation chain were accepted as independently expected.

Pitfalls:

* Unknown or missing learned clause IDs can leak raw `KeyError` instead of the explicit `require`/`ValueError` failures. Missing-guard controls exhibited this too. Callers must treat an unhandled exception/nonzero exit as rejection; this is an API robustness issue, not an observed unsound acceptance.
* The `.lrat` hashes are not fields in the event; the event's `proof` identities bind the original `.rup` bytes. The direct native replay is therefore important for binding those archived RUPs, while the hashes above identify the companion LRAT files exactly.
* The optional native helper's warning suppression and substring status test must not replace the strict runner.

## Scope and non-claims

The checks establish refutations of the exact CNFs `parent ∧ 5250`, `parent ∧ 5251`, and `parent ∧ -5249 ∧ -5252`. With the displayed pivot mapping, the first two exclude colors 1 and 2; the third excludes a model in which both colors 0 and 3 are false. Together they establish the stated **color 0 or color 3** consequence for a model of this supplied parent.

They do not refute or solve either color0/color3 child, show a unique survivor, close the parent, authenticate the producer, validate the live queue's 983,774 entries, or establish whole-parent/wall-row/Ramsey closure. I did not regenerate the parent, determine base-versus-strengthened provenance, independently recount the queue, infer a SAT model, or run any fresh search. The event-head hash is not producer authentication. Raw elapsed times and archived status names were not used as proof evidence.

## Reproduce

From this member directory, after source inspection:

```bash
bash run_all.sh
```

The script verifies the two source hashes, compiles the C checker, runs `audit.py`, runs `python_controls.py`, and runs the supplied default Python path. `run_all.sh` completed with exit 0. Detailed commands, output hashes, raw stdout/stderr, mutation hashes, and exceptions are in `outputs/native_manifest.json`, `outputs/native_summary.json`, and `outputs/python_controls.json`; native output streams are `outputs/native_*.txt`. Mutants and toy proofs are in `controls/`.
