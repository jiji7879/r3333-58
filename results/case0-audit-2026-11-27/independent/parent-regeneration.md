# K58 case 0 — parent regeneration and representation audit (direction C)

## Verdict

**PASS, with exact scoped identity.** At repository HEAD `1fa1a9115af7b93b6f3131e75a2a70a26289e764`, two deterministic encoder runs regenerated the supplied decompressed `parent.cnf.gz` byte-for-byte. One used a private source/data-only extraction of the recipe archive; the other used `.scratch/review-attachments-v1/audited-K58`. There were **zero solver calls, zero proof-checker calls, and empty stderr**. No new search or SAT model was used.

The attachment is the **base first-tier revised representative CNF**, not the current strengthened export that appends the stored root exclusions.

## 1. Exact representation

| CNF | Variables | Clauses | Bytes | SHA-256 |
| --- | ---: | ---: | ---: | --- |
| Ordinary first-tier row (`tables=true`, `total_critical=true`, `full_root=false`) | 18,387 | 173,594 | 3,323,477 | `160f9fb6c60638443c50d79e4fcaa64e6cdb6460db32fc61406d269a938bec00` |
| **Attached/regenerated base representative** | **19,218** | **178,823** | **3,423,661** | **`ae90931dc6cd482105153dd720209e602bbfc7cc0915e18c6e87023ee2659931`** |
| Strengthened export (base plus 23 stored `root.forbidden` negative units) | 19,218 | 178,846 | 3,423,845 | `d69970e19ddadfad5057ffaf8ffbd1354f957a4003852dc2b6b8aeff63cb3004` |

The representative adds 5,218 ownership clauses and 11 signed cube units to the ordinary row: `173594 + 5218 + 11 = 178823`. The strengthened form adds another 23 clauses. This direction reconstructed that form but **did not replay the separate campaign proofs for those 23 exclusions**.

Raw identity is stronger than a hash-only comparison: the complete reconstructed bytes equal both `revised.export(row,pair)` and the attached decompressed parent. The independently written DIMACS append serialization also agrees exactly.

## 2. Queue, guard, and physical binding

The frozen live queue has 983,774 entries. Its index-0 interval gives:

- row `00032f347903758c89e2187f30f0e1c07aecb21bd27c149fb43aef0ccdb60f0d`;
- arm 14, revised owner rank 0, pair `00000/01022`, profile `15,15,14,13`, symmetry order 1;
- palette `[1,0,3]`, missing physical color 2, first-tier recipe;
- pentagon `[31,32,35,33,34]`, nominated outside vertices `[36,37]`, remaining `[38,39,40,41,42,43,44]`;
- full physical arm order `[31,32,35,33,34,36,37,38,39,40,41,42,43,44]`.

The exact physical spoke pins are

```text
5226 5326 5602 5422 5514 5230 5329 5606 5428 5520
```

and the sole owner literal is `-19172`; together they reproduce `guard.owner_cube` and `guard.owner_gates` exactly. Local pivot `[0,11]` maps to physical edge `(31,42)`. Both the physical host map and the independent lexicographic edge-index calculation produce variables `[5249,5250,5251,5252]`. The locally surviving colors `[1,2]` map through palette `[1,0,3]` to physical colors `[0,3]`; missing physical color 2 is not part of that three-color local palette.

### Historical `search_query` caveat

The physical-color-1 proof query is the **base plus `5250`**, SHA-256 `84ba8a7e6bb372c0d5e6c4485bee7e47c8ca5081277f4f8d8beabbe0d1fee33f`. The current strengthened parent plus `5250` instead hashes to `41f37720b4b189df8dc43a854733c53c86dc71a721bebacb58fa8c3424eca891`, which is **not** the event's archived `search_query` (`7b3910a5331ded5cf2108dd04f225ca5075a9d44a636b0c8a1017d297385cc25`). The supplied case package does not include the producer source needed to identify that historical query further, so this audit does not guess its construction.

## 3. Source/recipe binding and initialized overlays

`guard.recipe` equals the actual `K58_adaptive_wall_solver.zip` SHA-256 `3324b778ea425dbcd48a3c7f19a38812820066d769581569f318b61108837b75`.

The pristine run strictly matched all **59 selected root/engine Python sources and required case-data files** against that archive. Only those source/data files were privately extracted; no bundled executable was extracted or run.

The audited initialized tree is **not pristine archive bytes**. Of the 76 checked source/data paths, 48 matched, 11 common files differed, and 17 audit/verification files were additional. Therefore the report does not describe the initialized tree as an untouched recipe extraction. Independently running both representations and obtaining identical complete CNFs avoids relying on a manual claim that the overlays are semantically irrelevant. Exact per-file overlay hashes are recorded in `evidence/comparison.json`.

Input package identities measured here are:

- case ZIP: `f08ec771eaf99c31d22cbe4d364ccd0ca80365f41a1395e1a152d067aabcf192`;
- attached `parent.cnf.gz` compressed bytes: `aceef062c0f8b511a96c10f39265c02cd25333cd101000a6c0493568a5d5a380`.

The established binary identity is the **decompressed DIMACS stream**. The event archives no independent original gzip-stream digest beyond the included copy, and matching deterministic source bytes does not authenticate an original native executable, producer, execution date, or event head.

## 4. Discriminating controls

All controls passed during both reconstruction runs:

1. Selecting the next valid revised rank (rank 1, pair `00000/22010`) produced a different CNF, SHA-256 `ba5edb2f3e09dc65bdcd4e1c65c6ef996a957a24344f0a62e112640269adf17f`.
2. Flipping the owner gate from `-19172` to `19172` was distinguished by the exact cube and complete-CNF comparisons.
3. The base and strengthened parents were distinguished by complete bytes, digest, and the 23-clause difference.

These are negative identity controls, not SAT/UNSAT experiments.

## 5. Reproduction and artifacts

From this member directory:

```bash
ROOT="$(git rev-parse --show-toplevel)"
AUD="$ROOT/.scratch/review-attachments-v1/audited-K58"
PYTHONDONTWRITEBYTECODE=1 "$AUD/.venv/bin/python" -B run_regeneration.py \
  --python "$AUD/.venv/bin/python"
```

- `audit_parent.py`: queue/guard checks, independent serialization, reconstruction, and controls.
- `run_regeneration.py`: safe source/data-only extraction and pristine/audited cross-check.
- `evidence/comparison.json`: combined result and initialized-overlay details.
- `evidence/pristine/summary.json` and `evidence/audited/summary.json`: detailed independent results.
- `evidence/pristine/regenerated-base.cnf.gz` and `evidence/audited/regenerated-base.cnf.gz`: regenerated artifacts; their decompressed bytes are identical.
- `evidence/pristine-manifest.json`: exact private source/data extraction manifest.

## Scope

This is a deterministic parent/source audit only. It establishes no refinement to one survivor, no whole-parent, wall-row, or Ramsey closure, and no runtime comparison. Strict RUP/LRAT replay belongs to the separate proof-replay direction. Recipe reproducibility and an archived event-head hash are not cryptographic producer authentication.
