# K58_case0 direction-A audit: formulas, guard, ledger and continuation

## Outcome

**PASS for exact formula/guard/head/queue semantics, with an explicit authentication and closure boundary.** Repository HEAD was `1fa1a9115af7b93b6f3131e75a2a70a26289e764`. I independently regenerated all four child queries and the cover query from the supplied parent, matched every archived hash, reconstructed the guard from the campaign records, and passed seven byte/head negative controls plus unit-propagation and queue-policy controls.

I did not run a solver, infer a SAT model, execute the supplied verifier, or compile a checker. The three proof **verdicts** belong to direction B; `CLOSED` strings below are archived labels, not a substitute for replay. Parent regeneration/provenance belongs to direction C. Consequently, the logical implications below are stated conditional on independent acceptance of the three refutations, not on the status text.

The ZIP SHA-256 is `f08ec771eaf99c31d22cbe4d364ccd0ca80365f41a1395e1a152d067aabcf192`. The decompressed parent is 3,423,661 bytes, 19,218 variables and 178,823 clauses, SHA-256 `ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`.

## 1. Pivot, guard and exact signed bytes

For zero-based vertices, unordered edges are numbered by `itertools.combinations(range(58),2)`. Both direct enumeration and the closed formula give

$$i(31,42)=31(116-31-1)/2+42-31-1=1312,$$

so physical colors 0--3 have variables $4i+1+c = 5249,5250,5251,5252$. The parent contains the at-least-one clause as clause 9185 and all six pairwise at-most-one clauses as 9186--9191.

The live roster's index 0 resolves independently to row `00032f347903758c89e2187f30f0e1c07aecb21bd27c149fb43aef0ccdb60f0d`, arm 14, revised rank 0, pair `00000/01022`, profile `[15,15,14,13]`. The recomputed row ID, physical binding and recipe archive all match. The recipe archive SHA-256 is `3324b778ea425dbcd48a3c7f19a38812820066d769581569f318b61108837b75`.

The local-to-physical vertex list is `[31,32,35,33,34,36,37,38,39,40,41,42,43,44]`; local pivot `[0,11]` is therefore physical `(31,42)`. Palette `[1,0,3]` maps to literals `[5250,5249,5252]`. Thus local open branches 1 and 2 correspond to physical colors 0 and 3, not event colors 1 and 2.

The physical owner cube, including the rank-0 gate, is exactly

```text
5226 5326 5602 5422 5514 5230 5329 5606 5428 5520 -19172
```

The first ten literals are recomputed from the two nominated stars and palette. Gates are allocated last and contiguously: 47 revised pairs and 19,218 final variables put the first gate at $19218-47+1=19172$; rank 0 negates it. These eleven literals are also exactly the parent's final eleven unit clauses.

### Reconstructed queries

Each query preserves the parent body byte-for-byte, increments the header count and appends the displayed units in the displayed order. Generated CNFs are in `results/queries/`.

| Claim | Appended units | Query SHA-256 | Archived status |
|---|---|---|---|
| physical color 0 | `5249` | `25bb3d2500487ee87ccde7c41274538ac484344a42b301b54b9d99036ff0a5e5` | `OPEN_UNKNOWN` |
| physical color 1 | `5250` | `84ba8a7e6bb372c0d5e6c4485bee7e47c8ca5081277f4f8d8beabbe0d1fee33f` | `CLOSED` |
| physical color 2 | `5251` | `858216a74117455646e51880ca1392e957da8800ccb95f5189870d67007ad83c` | `CLOSED` |
| physical color 3 | `5252` | `7aedd43ca0cd6ea1be6a5219abd17c72160807bcc4c2b95936741b7dfdbf6bee` | `OPEN_UNKNOWN` |
| cover | `-5249`, then `-5252` | `30163e3ddaefb8241137b19bcdceafc7d1c9facfb85f0c76a239d53c71923a70` | `CLOSED` |

RUP byte identities also match: color 1 `7bb85210d29faa078a357ecc0da28e51cb9d58ed0c5a48eaec7d201284acc6b4` (958 bytes), color 2 `ffe9aaeaa2a2d5048174df0b80599ef0197ec024c4b051bc9860cff58ef7f9f3` (2 bytes), cover `67229c09284239f78229d4920d7527495a2ccaca3775e262d11d8754ec161d66` (378 bytes). These are identity checks; direction B supplies replay controls.

The query parent is the **base representative**. Independently adding the 23 stored root exclusions in physical coordinates produces the distinct 178,846-clause strengthened parent `d69970e19ddadfad5057ffaf8ffbd1354f957a4003852dc2b6b8aeff63cb3004`; the two strengthened local branches have hashes `f7e6f5b2cb5a95bf65c16c730f7c4e10bd359b3d413d031bcbf9dd180dd5ff8d` and `e85234ab42705601f1b83a2e6127ecb89dea669ba78865f35ea57e47815ece7a`. None is the attached parent or an event child query.

Only physical color 1 has separate `search_query: 7b3910a5331ded5cf2108dd04f225ca5075a9d44a636b0c8a1017d297385cc25`. No corresponding CNF or independently checkable execution transcript is included, and it is not any reconstructed query above. It must not be silently identified with either the proof input or a strengthened search formula. Conflict caps, statuses and elapsed fields are likewise committed historical metadata, not fresh execution evidence.

## 2. Precise logical consequence and non-consequences

Let $P$ be the base parent and $x_c$ its physical color-$c$ pivot literal. Once independently checked, the three refutations establish

$$P\land x_1\equiv\bot,\qquad P\land x_2\equiv\bot,\qquad P\land\neg x_0\land\neg x_3\equiv\bot.$$

The last statement alone is equivalent to $P\models x_0\lor x_3$: **every** parent model uses color 0 or color 3 on `(31,42)`. Using exact-oneness and the two child refutations on the same 19,218-variable space gives the stronger model-set identity

$$M(P)=M(P\land x_0)\;\dot\cup\;M(P\land x_3).$$

No parent model is lost by retaining **both** open child queries. But neither open child is decided SAT or UNSAT. The evidence does not prove a unique survivor, does not make the parent UNSAT, and yields no whole-parent, wall-row or Ramsey closure. `OPEN_UNKNOWN` is not promoted to a terminal result.

As an independent sign check, unit propagation on the base derives `-5251` after 1,932 assignments; adding `+5251` reaches a conflict at clause 16,594, whereas base-only and `-5251` controls do not conflict. Non-conflict is not a model or SAT claim. This used only propagation, no branching.

## 3. Continuation and queue arithmetic

I independently summed all 11,585 contiguous live-roster records and obtained the frozen total **983,774**, matching `event.live`. Under the repository's `queue_refine.decide` rule, a complete cover with two open children has the following behavior:

- capacity 1 or 2 (including the parent's slot): `KEEP_PARENT_QUEUED`, delta 0;
- capacity at least 3: `EXPAND_ALL_OPEN_CHILDREN`, delta +1;
- never `REPLACE_WITH_ONE_OPEN_CHILD` for this event;
- an incomplete-cover control retains the parent even with one open child; a zero-open abstract control closes its node.

If this event alone were expanded with sufficient capacity, its hypothetical total would be 983,775. That is a policy calculation, **not a recorded queue mutation**. The supplied record has `continuations: []`, `mode: "lazy"` and `state: "OPEN_UNKNOWN"`; no successor artifact or live-queue modification was made or inferred. The case0 package supplies no event-producer implementation that would justify extending the label `lazy` into stronger scheduler semantics.

## 4. Event-head integrity versus producer authentication

Independently reproducing the supplied verifier's head computation matches:

$$H=\operatorname{SHA256}(\mathrm{canonicalJSON}([\mathrm{PREDECESSOR},event,state,live,continuations])\,\|\,\mathrm{LF})$$

with sorted keys and compact separators `(',', ':')`, predecessor `33eff43a97ada9bda78eb5a4f744fc019c421492a767ac0a89784f76a364283c`, and result `5f6644251423ebb5207722ee641d08a93696703dac1df4cfbb56e58fbc7d4d9e`.

Changing `live` gives `8aa0ef17b573eabb70fbc522a962f438c336ee41efed47cee8f10628f130f435`; inserting a continuation gives `db97affd8038ada2ce5c283d002f811cb267e3fbed060b41e7cb9f34eee8793b`, so both fields are actually committed. A changed pivot with a freely recomputed head gives `9352b42ef612587f4bdeedb5c4ae714cd3ac474ec9e200fb2b601bac2baa7b05`; no key or secret is needed.

Therefore this is an **unsigned hash commitment, not cryptographic producer authentication**. The predecessor and expected head are constants in the same package, and no signed external anchor or predecessor record is supplied. Against an externally pinned expected head it detects content changes; it does not establish producer, timestamp or historical execution. It commits the event/status/guard/query/proof fields, not the ZIP/gzip containers, README, `verify.py`, C source or LRAT filenames/bytes. Even though head and roster checks pass, unexecuted historical statistics and the separate `search_query` remain unauthenticated metadata.

## 5. Negative controls and reproduction

The seven recorded controls distinguish wrong physical pivot `(31,43)` (`5253..5256`), wrong cover signs (hash `c5348f9d…`), reversed but logically equivalent cover-unit order (different byte hash `9aaa7959…`), live and continuation tampering, an unsigned replacement head, and one-bit RUP mutation (hash mismatch only, not a claimed proof replay). Queue controls specifically reject the unique-survivor interpretation of two open branches.

From my member directory:

```bash
python3 audit_case0_semantics.py \
  --package attachment/K58_case0 \
  --campaign ../../../.scratch/review-attachments-v1/audited-K58 \
  --recipe-archive ../../../attachments/let-s-try-and-rbdv/K58_adaptive_wall_solver.zip \
  --zip ../../../attachments/let-s-try-and-rbdv/K58_case0.zip \
  --repository-head 1fa1a9115af7b93b6f3131e75a2a70a26289e764 \
  --out results
```

Successful output is in `run.log` and `results/summary.json`; full identities and controls are in `results/audit.json`. `source-sha256.txt`, `artifact-sha256.txt` and `SOURCE_INSPECTION.md` bind the inspected sources and outputs. Fresh solver searches: **0**. No coordinator, campaign or repository source was modified.
