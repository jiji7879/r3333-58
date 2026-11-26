# Reciprocal C&C frontier — independent audit

The accepted result is the reduction of the named augmented reciprocal formula
to **three explicit, still-open cubes**. It does not close a frozen row or any
other ticket branch.

## Root and exact coverage

- Frozen row: `0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296`.
- Root formula: `results/cc-reciprocal-0404-2026-11-25/root.cnf`, SHA-256
  `aa23de814810dc2b5515955a0aa318eab72df81c4541006fde253b39c48d2b44`.
- It has 305,513 variables and 834,101 clauses. The target root is one augmented
  reciprocal/common-critical-pair CNF with a mixed cap-8 clone interface; it is
  not an unqualified statement about every TU row.

`audit_tree.py` independently reconstructed every leaf CNF from the root body
and cube. It verified 343 nodes/172 leaves, and that every internal node has
children `C AND x` and `C AND NOT x` with consistent cube prefixes and parent
links. The terminal counts are **169 certified leaves and three open leaves**.
All 9 pilot and 155 inline compressed proof files were located and checked by
compressed and decompressed SHA-256. All five external raw CNF/proof pairs were
also checked by SHA-256. These checks bind the claimed proofs to the claimed
CNFs. `artifacts-audit.json` and `leaf-audit.json` contain the per-leaf ledger.

## Open leaves

| leaf | cube length | CNF SHA-256 |
| --- | ---: | --- |
| `r5_n025b2-019` | 21 | `f167b31790d3cf5605887648fd2a9df2799bc0791b4041cfeb17ea10db6c9dda` |
| `c485-022` | 20 | `3159be40996f1c23766d7e25f489f6a1a2ef0e634882330331a74afa0f9ef4f7` |
| `c485_029-033` | 12 | `fa9b361846ae5d5ee644d048c6c36227e825b11db8d0a336a2b884c2b2c70c62` |

These are the exact residual cubes in `merged-tree.json`, not a new theorem that
the full row is unsatisfiable. The first two each contain one positive clone
selector; the third pins only 12 selectors. They must not be paraphrased as all
32 selectors false, or as physical clone-freeness.

## Fresh verification and the clone models

A fresh `drat-trim` verification of the retained external
585,308,080-byte proof against its rebuilt 834,125-clause CNF returned
`s VERIFIED` in **347.168 seconds**. The complete checker output is retained in
`external-c485_028.log`. The other stored certificates retain their successful
verification receipts: this audit did not rerun all 155 inline DRATs one by one,
so its independent fresh replay count is one external proof in addition to the
earlier pilot replays.

Both mixed-orientation 33-vertex zero-clone models were independently checked:
all 46,560 clauses and all 5,456 triangles pass, and no vertex has exactly one
arm-coloured spoke (`clone0-check.json`). Five or six ordinary colour-0 edges
are not clones: a clone has **exactly one** such edge. These examples delimit a
clone-lower-bound argument for that 33-vertex object; they are not K58 models.
