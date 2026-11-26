# Review of `K58_0404_shared_frontier` and `K58_Tatarevic_transfer`

Date: 2026-11-26 (audit phase 2).

## Bottom line

Both packages are useful, but neither adds a newly closed frozen row to the current OPEN set.

- The shared-frontier bundle independently supports **256 exclusions among 726 selector assignments**.
  The exact remaining **470** assignments and strengthened CNF reproduce byte-for-byte.
  The unrestricted 0404 row remains OPEN.
- The Tatarevic package validates a real deletion-and-lift transfer on four source rows, plus one
  fallback search and its reuse on a second row. All **26** source/core/parent replay checks passed.
  These six IDs were already certified in the owner's full-cover release, so this is independent
  validation and proof reuse, **not six new closures**.
- The full 20,166-row K60-to-K58 crosswalk has been checked against the primary K60 source table,
  but exact unchanged-unit reuse on the current **1,288-row retry tail gives zero candidates**.
  There is no further reduction to claim from the retained donors at this point.

Finally, no new upper bound or result `R(3,3,3,3) <= 58` is established.

## Evidence checked

### Source archives and primary data

- `K58_0404_shared_frontier.zip`:
  `e55dc45515f7f7e33dcfe41c5e1f1b5a2838e0a226cb96e129ae5478b7fec448`.
- `K58_Tatarevic_transfer.zip`:
  `6ec5de4493c2bff1c2554087c313fe49471fd51904b1167e6363cd50edd852e5`.

Every entry in both packages' `SHA256SUMS` passed.

The public primary bundle was also downloaded from the pinned revision
`milostatarevic/r3333-upper-bound@6c3f2fd0386335321801fa4079397d4a4c1962f3`:

| object | bytes | SHA-256 |
|---|---:|---|
| `k60-formal-evidence.tar.gz` | 226,891,893 | `5bfa1c13c51b18bf486e0f22511852547df8417790575160e02bd5f2ca7550df` |
| `e.tsv` | 569,844,540 | `55eb8435e9820495bfcf5257c4e7ace8cc432694cb6d4576759287491df66a22` |
| `lean-base.body` | 2,856,586 | `3df2e9629912cab4af3b64826970c86c1f93ebadd2a381e91ec2079f5dfe9da2` |

The downloader's index checks and independently recomputed hashes agree.

### 0404 shared frontier

All **38 nonempty DRAT certificates** replayed as `s VERIFIED` using the supplied ordinary full-row
query for each proof's exact subset of assigned selectors. The independent checker then recomputed:

| quantity | value |
|---|---:|
| total selector assignments | 726 |
| newly excluded assignments | 256 |
| retained assignments | 470 |
| retained at $H=10$ | 135 |
| retained at $H=11$ | 229 |
| retained at $H=12$ | 91 |
| retained at $H=13$ | 14 |
| retained at $H=14$ | 1 |
| ordinary parent SHA-256 | `1e3ac049b4170d8d77fbc09374c8966f1822c49ca7e57f03cc9f3e3c3f4fd261` |
| exported residual SHA-256 | `d9430644e9a833d8bd88c0be46f4b9ab8e96ce94cf90339b115677922196a65e` |
| exported variables/clauses | 20,389 / 223,091 |

The strengthened CNF contains **every clause of the known ordinary row parent** plus 38,717 extra
clauses. Its ordinary parent has hash
`a062b827b34fa73ccd610b2a932e007e48ba217d85c7dea00f9a1a73dbdb62fe`.
No ordinary clause was lost. The extra clauses and auxiliary selector variables belong to this
particular hypothesis encoding: **$H\ge10$ in the reported partial-contact definition**.
They must not be silently converted into a new global $H(r)=w(r)$ or perfect-balance assumption.
The row's first clause set itself is not proof of its semantic bridge, and the ordinary full row
is not closed by 256 refutations among 726 hypotheses.

Replay output: [full-replay.log](../shared-frontier-audit-2026-11-26/full-replay.log).

### Crosswalk completeness

For all **20,166** records, the independent verifier checked:

1. exactly 20,166 distinct frozen row IDs, matching the November 22 OPEN roster (83,360 current
   triple-15 raw rows include other statuses as well);
2. participant metadata (`family`, `placement`, `charge`) against the frozen ledger;
3. source-owner and source-offset identity in the downloaded primary `e.tsv`;
4. the map's 58-vertex image being a bijection after deleting vertices 13 and 14;
5. validity of the four-colour permutation;
6. **exact equality of all translated signed pins to those of the frozen row**.

Owner totals agree: **13,005 E_TTT / 5,982 E_UTT / 1,030 E_UUT / 149 E_UUU**.

This is structural deletion and literal mapping, not template-family matching. The source table
uses exactly the same signed pins under the retained permutation; a matching map is a precise
combinatorial completion requirement, not evidence satisfying that requirement.

Log: [local-audit.log](../transfer-audit-2026-11-26/local-audit.log).

### The six retained K58 certificates

For the four K60 source cases and the two fallback cases the verifier checked:

- every prototype/source proof byte and receipt hash;
- the filtered signed unit set against the actual frozen family;
- that each extracted source core contains only source clauses;
- that deleted vertices are absent from the used core;
- exact literal renaming of that core to the K58 core;
- proper physical host/triangle clauses and per-row pins;
- byte-identical reconstruction of first and retry parent CNFs;
- real empty-clause DRAT replays on each source/core/parent formula.

The results were `s VERIFIED` on all **26 checks**:

| case prefix | source result | verified core size / pins | first and retry parent proofs |
|---|---|---:|---|
| `2cad8d149de7` | K60 `TTT:131:48:3` | 50 vertices | both `s VERIFIED` |
| `2eea7d578d80` | K60 `TTT:117:43:3` | 48 | both `s VERIFIED` |
| `38bd7b456e04` | K60 `TTT:117:42:3` | 35 | both `s VERIFIED` |
| `c17143277f24` | K60 `TTT:113:44:3` | 35 | both `s VERIFIED` |
| `3d366579cb84` | K58 shared CaDiCaL fallback | 285 unit pins | both `s VERIFIED` |
| `4f94a88e7c76` | unchanged fallback reuse | 285 | both `s VERIFIED` |

These are verified statements about individual case refutations, not about all 20,166 maps. Nor is
it a transfer of a name-based relaxation from `E` to `K58`: exact units and physical proof inputs
were replayed separately.

The owners' current release already lists all six as CERTIFIED with `full_root=true`. The independently
reconstructed retry recipes reproduce their hashes; the local verification therefore independently
upholds and binds the same objects without double-counting them.

### Current-tail reuse check

An actual unchanged proof requires at least the donor core's signed units to be contained in the
candidate row's pins. Full row metadata and each unit-lit set were compared against the release's
1,288 currently OPEN `(15,15,15,12)` rows, using all four K60 donor proofs and the fallback donor.

Result:

```text
tail rows 1288 exact unchanged-unit candidates 0
```

No solver verdict is inferred from that necessary subset test failing. It only says these specific
retained proofs cannot close another current tail row unchanged. If one wants more reuse closures,
the next routes are fresh K60 refutations with eligible free vertices left to delete, or new shared
cores whose pin set is compatible with the actual tail. There is no honest basis for extrapolating
six validated refutations to another coverage percentage.

## Usability next steps

- Use the preserved transfer mechanism when solving a new source case: create/check the deletion
  map, lift any orphan vertex variables into a fresh auxiliary range, and replay on exact first and
  retry parents rather than accepting a same-family template result.
- Keep candidate/proof stores intact. As m2's submission demonstrated, retaining only hashes and
  removing DRATs prevents independent certification.
- In generic reuse, freeze the candidate ID, every input and proof hash, the signed pin map, the
  deletion set, each target parent hash, and the checker verdict. A timeout remains OPEN.
- The 0404 parent is an exact stronger hypothesis, not the whole unrestricted proof obligation;
  further coverage should use the 470 retained selector assignments or new structural cuts rather
  than confuse it with an eliminated root.
- The source 217 MB archive remains available locally when coherent fresh source computations are
  needed; it is not a reason to start an unbounded global solver sweep on a small shared VM.

## What was not established

- No current OPEN tail row is refuted by the retained donor proofs.
- No complete 0404 row or profile is closed.
- No 20,166-way K60 replication was run or required: the package already preserved the six local
  certificates; replay alone establishes them.
- No blanket raw-versus-folded-ledger equality is used. Older OPEN subsets, current release statuses,
  and the present wall are kept distinct.
- The auxiliary filenames are not proof of their intended meaning. Each DRAT must be checked against
  its proper CNF, as evidenced by why source, lifted-core, and first/retry parent audiences were
  distinguished during this audit.
