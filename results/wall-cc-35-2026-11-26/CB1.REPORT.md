# CB1 declared depth-two cube-and-conquer frontier

## Outcome

- Scope is exactly ten canonical CB1 rows: five in `15,14,14,14` followed by five in `15,15,14,13`. All 64-hex row IDs and key hashes are preserved below and in `cb1-frontier.json` / `frontier.tsv`.
- **10/10 plans prepared and audited; 40/40 declared cubes attempted by fresh leaf workers; 1 independently certified UNSAT leaf; 39 OPEN; 0 NOT_RUN; 0 SAT.**
- **0/10 whole rows closed. No whole-parent DRAT export was attempted or claimed.** No Ramsey bound, profile elimination, or inference from these finite unresolved subcases is made.
- Canonical selection SHA-256: `86188322ae02e4e25b6eafe83564acb9c3592d1ecf19213b7921b3920442302a`; frozen roster SHA-256: `d5641e1ba875bc4ec5fbe156d48585f610e877f5232de7181eb464d4ad4fa2bc`.

## Protocol and evidence boundaries

Every parent is the exact regenerated first-tier formula (`tables=True,total_critical=True,full_root=False`). Each plan uses `--depth 2 --arm-pair auto --arm-mode both`; no prohibited restrictions were added. `audit_plans.py` compared parent bytes to that recipe, checked roster identity/profile/branch/placement, hashed parent/working/CAS, and independently reconstructed all 40 two-literal ancestry cubes. There are three split nodes and four leaves per row, not merely a claimed leaf count.

The first pass was fresh `shared_conquer.py --no-reuse` in a new directory for each row, with 350000 conflicts per cube, 1000 tail conflicts, 300 search seconds and 600 checker seconds. All ten ended OPEN at conflict limits, not wall time. Their partial incremental streams were removed by the driver and are not evidence for any cube.

Every cube then used a fresh CaDiCaL 1.9.5 native subprocess through `wallcc.py resume --jobs 1 --proof eager --seconds 300 --conflicts 1000000 --check-seconds 600` on the same plan. All 39 OPEN outcomes are conflict-limit outcomes (native conflict counters can overshoot the requested limit slightly; exact values are in the TSV). No timeout/UNKNOWN is called UNSAT. No second identical-budget retry was run.

`wallcc.py verify --jobs 1 --check-seconds 600 --expect-sha256 PARENT_SHA` ran on every plan. It explicitly returned OPEN for all ten: nine rows had 4 OPEN and one had 1 VERIFIED_UNSAT + 3 OPEN. The separate final audit checked plan/receipt/cube/budget bindings, scanned the retained proof as ordinary binary DRAT, rebuilt the original-parent-plus-unit-cube formula, joined the matching `cas.drat` prefix, and invoked pinned ordinary `drat-trim -i -p -t 600 -w` (SHA `a9571deb08430a3d7f7a72074440f53e2ad48196dced50b146835052a18e9066`). The sole closed leaf passed. No `-C` output acceptance, IDRUP parsing, shared incomplete prefix, or search-CNF-only replay was promoted to proof.

No plan was cover-eligible for `export-drat`, so there are no parent proof bytes to report separately. OPEN leaf proofs and unfinished attempt directories are absent; valid CAS prefixes and the one valid leaf certificate are retained.

## Complete per-row trees and leaf outcomes

The common per-leaf worker budget below is 300 wall seconds, 1000000 requested conflicts, eager proof, and 600 checker seconds. Shared `result` is CaDiCaL's internal `false/true/null` result during the later discarded OPEN stream; it is not counted as per-leaf certification.

### `15,14,14,14`, row `076eafbfe47eece51caf59db5d7ba4837744555a7c06414346f24b6ab222e7df`

- Branch `0`; selection key SHA-256 `014793b41b77d72c747c373868d2670ed68a2df1170e5d0d58769eeaa269ddce`; plan directory `plans/15,14,14,14/076eafbfe47eece51caf59db5d7ba4837744555a7c06414346f24b6ab222e7df`.
- Parent SHA-256 `031c400998346ebc3bf743f4fe69a8ece6191da3b9df7197acf62ec4cb4092ce`; receipt plan ID `53e968911dc89c6848b541e3c3c3e38fe55f7bcad7d278b8b886f60a671fa66f`; working SHA-256 `0bfe8b36dac7c79cdb32349cd2153a41fe2fd51dae2aeae7a732a766dd024e82`; CAS SHA-256 `f3b19ba9893110a5e75a977c2ac1ff0918216abdff3d248bc41bfd5aa0d5f88e`. Formula: 18149 variables, 171963 parent clauses, 378 proof-derived cuts.
- Declared splits: `r=1605`, `r0=1798`, `r1=1609`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 65.469 s; output `shared-fresh/15,14,14,14/076eafbfe47eece51caf59db5d7ba4837744555a7c06414346f24b6ab222e7df`; receipt `shared-fresh/15,14,14,14/076eafbfe47eece51caf59db5d7ba4837744555a7c06414346f24b6ab222e7df/receipt.json`. Tail conflicts: 1000.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "076eafbfe47eece51caf59db5d7ba4837744555a7c06414346f24b6ab222e7df", "kind": "wall", "tier": "first"}, "parent_sha256": "031c400998346ebc3bf743f4fe69a8ece6191da3b9df7197acf62ec4cb4092ce", "processed": 4, "status": "OPEN"}`; log `logs/verify-076eafbfe47eece51caf59db5d7ba4837744555a7c06414346f24b6ab222e7df.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-1605,-1798]` | `null` / 350000 | 43.815 / 1000005 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-1605,1798]` | `null` / 350000 | 47.463 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[1605,-1609]` | `null` / 350002 | 44.112 / 1000003 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[1605,1609]` | `null` / 350001 | 43.829 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-1605,-1798]],["r01",[-1605,1798]],["r10",[1605,-1609]],["r11",[1605,1609]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,14,14,14`, row `66aec8853d00a8b94b856a1ab81d9dc96325c9caf2d518c685fcb419676f24e4`

- Branch `4`; selection key SHA-256 `014ed32611d7d6477ad09eecb1d1e2ed668d29ef8d4e2e113cbb2aee55c32494`; plan directory `plans/15,14,14,14/66aec8853d00a8b94b856a1ab81d9dc96325c9caf2d518c685fcb419676f24e4`.
- Parent SHA-256 `7a271bbce1cdf675ea0a68662e55954f64dd0e44b8468997abbf7f044f2864ba`; receipt plan ID `7358ee385cba0a17416796fcfcc6d90026c75254cf402de9d670f82bfaccfb2c`; working SHA-256 `dc99c7e0039d4a5831212b57c79bbec879155c3fbc08cb2c878287f3e2057b99`; CAS SHA-256 `9e61a26c628f007b251ea8afb610c388d5cbb9276d6b74159111e1685289c64a`. Formula: 12138 variables, 146122 parent clauses, 378 proof-derived cuts.
- Declared splits: `r=3240`, `r0=3244`, `r1=3244`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 61.523 s; output `shared-fresh/15,14,14,14/66aec8853d00a8b94b856a1ab81d9dc96325c9caf2d518c685fcb419676f24e4`; receipt `shared-fresh/15,14,14,14/66aec8853d00a8b94b856a1ab81d9dc96325c9caf2d518c685fcb419676f24e4/receipt.json`. Tail conflicts: 1000.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "66aec8853d00a8b94b856a1ab81d9dc96325c9caf2d518c685fcb419676f24e4", "kind": "wall", "tier": "first"}, "parent_sha256": "7a271bbce1cdf675ea0a68662e55954f64dd0e44b8468997abbf7f044f2864ba", "processed": 4, "status": "OPEN"}`; log `logs/verify-66aec8853d00a8b94b856a1ab81d9dc96325c9caf2d518c685fcb419676f24e4.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-3240,-3244]` | `null` / 350000 | 45.48 / 1000002 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-3240,3244]` | `null` / 350000 | 41.268 / 1000005 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[3240,-3244]` | `null` / 350001 | 44.678 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[3240,3244]` | `null` / 350000 | 46.702 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-3240,-3244]],["r01",[-3240,3244]],["r10",[3240,-3244]],["r11",[3240,3244]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,14,14,14`, row `e9e63f1b9b350e4a1899494597259a75a8e5d646eba16dcff4890abc9a3ef8e2`

- Branch `21`; selection key SHA-256 `015e3b49a7da6a013879ea5e54fe59e86df4e09f7a37d893a79d54d928b2d7cc`; plan directory `plans/15,14,14,14/e9e63f1b9b350e4a1899494597259a75a8e5d646eba16dcff4890abc9a3ef8e2`.
- Parent SHA-256 `f23a7300044f91ab4664c3a464ae0eb20d5ee75e25c27dd703e6d579ad13881b`; receipt plan ID `0128d624de1397d1d497e842d8e875200f2e5207126f90343fd9dd1f24e22797`; working SHA-256 `186032eb4ad9515ebc9d9589a14e56df329063e5ddde5088fecdf01fc8031c34`; CAS SHA-256 `f9fcc180ecbbae02fb05d55b6b1c4d5d6c7821b0178c4bec229659a87cbd54cd`. Formula: 18039 variables, 171741 parent clauses, 189 proof-derived cuts.
- Declared splits: `r=1609`, `r0=2377`, `r1=2729`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 66.361 s; output `shared-fresh/15,14,14,14/e9e63f1b9b350e4a1899494597259a75a8e5d646eba16dcff4890abc9a3ef8e2`; receipt `shared-fresh/15,14,14,14/e9e63f1b9b350e4a1899494597259a75a8e5d646eba16dcff4890abc9a3ef8e2/receipt.json`. Tail conflicts: 1002.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "e9e63f1b9b350e4a1899494597259a75a8e5d646eba16dcff4890abc9a3ef8e2", "kind": "wall", "tier": "first"}, "parent_sha256": "f23a7300044f91ab4664c3a464ae0eb20d5ee75e25c27dd703e6d579ad13881b", "processed": 4, "status": "OPEN"}`; log `logs/verify-e9e63f1b9b350e4a1899494597259a75a8e5d646eba16dcff4890abc9a3ef8e2.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-1609,-2377]` | `null` / 350001 | 43.614 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-1609,2377]` | `null` / 350000 | 43.772 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[1609,-2729]` | `null` / 350002 | 44.633 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[1609,2729]` | `null` / 350001 | 41.848 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-1609,-2377]],["r01",[-1609,2377]],["r10",[1609,-2729]],["r11",[1609,2729]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,14,14,14`, row `df1144681acb4939480417902dbee6d221d827821a36ce784e2d0664fb6a4d37`

- Branch `11`; selection key SHA-256 `01cc1be540ab816db52974655f93c254176af043b46d519fa078a365136d701a`; plan directory `plans/15,14,14,14/df1144681acb4939480417902dbee6d221d827821a36ce784e2d0664fb6a4d37`.
- Parent SHA-256 `0e8ea7f21f6a236664cb242990bcb16d480bb192a97a3dbbf3806ba7dd4ba906`; receipt plan ID `c81f573078b1d8d4e5b7aad973aeffee8d849910b3570e55292993dd8d2623d9`; working SHA-256 `2da0e112e8ee065fd068e115c699491d272efea65954182fbc553331fc7b1495`; CAS SHA-256 `f9fcc180ecbbae02fb05d55b6b1c4d5d6c7821b0178c4bec229659a87cbd54cd`. Formula: 17919 variables, 169468 parent clauses, 189 proof-derived cuts.
- Declared splits: `r=2373`, `r0=2549`, `r1=2362`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 64.335 s; output `shared-fresh/15,14,14,14/df1144681acb4939480417902dbee6d221d827821a36ce784e2d0664fb6a4d37`; receipt `shared-fresh/15,14,14,14/df1144681acb4939480417902dbee6d221d827821a36ce784e2d0664fb6a4d37/receipt.json`. Tail conflicts: 1000.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "df1144681acb4939480417902dbee6d221d827821a36ce784e2d0664fb6a4d37", "kind": "wall", "tier": "first"}, "parent_sha256": "0e8ea7f21f6a236664cb242990bcb16d480bb192a97a3dbbf3806ba7dd4ba906", "processed": 4, "status": "OPEN"}`; log `logs/verify-df1144681acb4939480417902dbee6d221d827821a36ce784e2d0664fb6a4d37.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-2373,-2549]` | `null` / 350000 | 45.187 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-2373,2549]` | `null` / 350000 | 46.879 / 1000003 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[2373,-2362]` | `null` / 350006 | 43.125 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[2373,2362]` | `null` / 350001 | 44.427 / 1000003 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-2373,-2549]],["r01",[-2373,2549]],["r10",[2373,-2362]],["r11",[2373,2362]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,14,14,14`, row `e6a695057cdd6066d1db2bb0ad3f7c643327db4e7ed28eca8079aae8ad5d817d`

- Branch `25`; selection key SHA-256 `01ebbaf19ba90e87c5998f9ed4855ea29befa0ddbce8633755ca48c5e2e46afa`; plan directory `plans/15,14,14,14/e6a695057cdd6066d1db2bb0ad3f7c643327db4e7ed28eca8079aae8ad5d817d`.
- Parent SHA-256 `6b9b57ec899ff3fc710d98694e731d844d9749077b1c8ccf88467b8bbe1e8e38`; receipt plan ID `1c0eea62d7496207373e8df1be2cd944ddb89cc901e71c1e622e4e710a6f34d6`; working SHA-256 `00b9194c742303b969441fca3ec10ad63b7bfd8283d460d71b75397a26e94056`; CAS SHA-256 `0bd43206d6d3733f397e52045406ecc15742442a6c23e44520c2776ee57167de`. Formula: 17919 variables, 169468 parent clauses, 189 proof-derived cuts.
- Declared splits: `r=2001`, `r0=2189`, `r1=1797`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 56.635 s; output `shared-fresh/15,14,14,14/e6a695057cdd6066d1db2bb0ad3f7c643327db4e7ed28eca8079aae8ad5d817d`; receipt `shared-fresh/15,14,14,14/e6a695057cdd6066d1db2bb0ad3f7c643327db4e7ed28eca8079aae8ad5d817d/receipt.json`. Tail conflicts: 1000.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "e6a695057cdd6066d1db2bb0ad3f7c643327db4e7ed28eca8079aae8ad5d817d", "kind": "wall", "tier": "first"}, "parent_sha256": "6b9b57ec899ff3fc710d98694e731d844d9749077b1c8ccf88467b8bbe1e8e38", "processed": 4, "status": "OPEN"}`; log `logs/verify-e6a695057cdd6066d1db2bb0ad3f7c643327db4e7ed28eca8079aae8ad5d817d.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-2001,-2189]` | `null` / 350000 | 41.289 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-2001,2189]` | `null` / 350000 | 45.461 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[2001,-1797]` | `null` / 350000 | 44.902 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[2001,1797]` | `null` / 350000 | 46.012 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-2001,-2189]],["r01",[-2001,2189]],["r10",[2001,-1797]],["r11",[2001,1797]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,15,14,13`, row `bffb4a76605d9b42605d91205d1ca31363d9de548cad952253bb575380e1f52e`

- Branch `1541`; selection key SHA-256 `0007c79c5cac390f19bb7143e90ede0d70bcfd0059a64f5cb83c6640ade9918b`; plan directory `plans/15,15,14,13/bffb4a76605d9b42605d91205d1ca31363d9de548cad952253bb575380e1f52e`.
- Parent SHA-256 `054b563be3e12df4ad953b1597d8e7c4b6cf19df9e926e83e561c7c3515b9a01`; receipt plan ID `932919b731abc78a9f27ee94204ce1e629f7fb36ecef536766b7099d23920cc2`; working SHA-256 `66ef02f564cf213c3c2e901bad0395d415cd85b9b3113c5bb899dd181a0479a1`; CAS SHA-256 `7051d1f7625873bd58afc82b41d090e60752fb96606362a008fcc94093421b6d`. Formula: 18497 variables, 173817 parent clauses, 357 proof-derived cuts.
- Declared splits: `r=4133`, `r0=4141`, `r1=4141`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 93.031 s; output `shared-fresh/15,15,14,13/bffb4a76605d9b42605d91205d1ca31363d9de548cad952253bb575380e1f52e`; receipt `shared-fresh/15,15,14,13/bffb4a76605d9b42605d91205d1ca31363d9de548cad952253bb575380e1f52e/receipt.json`. Tail conflicts: 1000.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "bffb4a76605d9b42605d91205d1ca31363d9de548cad952253bb575380e1f52e", "kind": "wall", "tier": "first"}, "parent_sha256": "054b563be3e12df4ad953b1597d8e7c4b6cf19df9e926e83e561c7c3515b9a01", "processed": 4, "status": "OPEN"}`; log `logs/verify-bffb4a76605d9b42605d91205d1ca31363d9de548cad952253bb575380e1f52e.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-4133,-4141]` | `null` / 350001 | 44.917 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-4133,4141]` | `null` / 350001 | 43.957 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[4133,-4141]` | `null` / 350001 | 42.448 / 1000002 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[4133,4141]` | `null` / 350002 | 42.282 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-4133,-4141]],["r01",[-4133,4141]],["r10",[4133,-4141]],["r11",[4133,4141]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,15,14,13`, row `3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c`

- Branch `1347`; selection key SHA-256 `00086fb2e0cc422d5db1c590617be2026e20b3c75994f34def7a629b9da78d6a`; plan directory `plans/15,15,14,13/3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c`.
- Parent SHA-256 `d27d34c0d8336997d545c76120e040ff1aa0f448ef362d443502372d4c1a1ff2`; receipt plan ID `4dea9e14284398299ce866b63783269de8129b62efcc438997f2aa1a665841fa`; working SHA-256 `64950cdc66a760e0ce59975b3244701e4c1ae81116b4f804cb35377ceaf4fcde`; CAS SHA-256 `036ec2b03282f64d5ccdc1336210ef9b4f565c07abbc04138971ad340a08a95f`. Formula: 18497 variables, 173817 parent clauses, 357 proof-derived cuts.
- Declared splits: `r=4262`, `r0=5104`, `r1=4645`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 56.401 s; output `shared-fresh/15,15,14,13/3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c`; receipt `shared-fresh/15,15,14,13/3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c/receipt.json`. Tail conflicts: 1000.
- Strict verify: `{"counts": {"OPEN": 3, "VERIFIED_UNSAT": 1}, "leaves": 4, "origin": {"id": "3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c", "kind": "wall", "tier": "first"}, "parent_sha256": "d27d34c0d8336997d545c76120e040ff1aa0f448ef362d443502372d4c1a1ff2", "processed": 4, "status": "OPEN"}`; log `logs/verify-3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-4262,-5104]` | `null` / 350006 | 46.515 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-4262,5104]` | `null` / 350000 | 52.898 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[4262,-4645]` | `null` / 350000 | 42.023 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[4262,4645]` | `false` / 0 | 0.262 / 1 | CERTIFIED (CHECKED_UNSAT + independent VERIFIED) | `plans/15,15,14,13/3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c/leaves/r11/leaf.drat`; SHA `1e605f06553a1152d358bccf16f49dcb7a4102da7ccb9d3adade9a2f662d3007`; 6707 bytes; replay log `logs/independent-leaf-3d443146013949bb1f01e907953c366c617e4178c4638cc2c8eb59d4e2745d1c-r11.log` |

**Whole-row result: OPEN_INCOMPLETE (1 certified, 3 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-4262,-5104]],["r01",[-4262,5104]],["r10",[4262,-4645]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,15,14,13`, row `0b7669c7d3213018b4b888b04251af8e64a443c7424fb63dbe99d25dfd1b5d5b`

- Branch `9`; selection key SHA-256 `000c4af71eea7fcde0920e621dab0322ce1d9a7d26451103d50e87573d822e12`; plan directory `plans/15,15,14,13/0b7669c7d3213018b4b888b04251af8e64a443c7424fb63dbe99d25dfd1b5d5b`.
- Parent SHA-256 `1f6cab2fd0e42508ba2289a5ff8573aa66cea031d51cd4bfb6caa49e2fcdfaf7`; receipt plan ID `223ded72b2ea9995dba3cf41bdb3a81bc2e1d2c505a348975d24a315eb6e18dc`; working SHA-256 `c07cda4d83f9c8243d33e07ae65e0b5cc8f26f475162e345608156fc6b030bc8`; CAS SHA-256 `036ec2b03282f64d5ccdc1336210ef9b4f565c07abbc04138971ad340a08a95f`. Formula: 18497 variables, 173817 parent clauses, 357 proof-derived cuts.
- Declared splits: `r=3545`, `r0=3541`, `r1=3698`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 91.024 s; output `shared-fresh/15,15,14,13/0b7669c7d3213018b4b888b04251af8e64a443c7424fb63dbe99d25dfd1b5d5b`; receipt `shared-fresh/15,15,14,13/0b7669c7d3213018b4b888b04251af8e64a443c7424fb63dbe99d25dfd1b5d5b/receipt.json`. Tail conflicts: 1000.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "0b7669c7d3213018b4b888b04251af8e64a443c7424fb63dbe99d25dfd1b5d5b", "kind": "wall", "tier": "first"}, "parent_sha256": "1f6cab2fd0e42508ba2289a5ff8573aa66cea031d51cd4bfb6caa49e2fcdfaf7", "processed": 4, "status": "OPEN"}`; log `logs/verify-0b7669c7d3213018b4b888b04251af8e64a443c7424fb63dbe99d25dfd1b5d5b.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-3545,-3541]` | `null` / 350002 | 60.835 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-3545,3541]` | `null` / 350000 | 58.303 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[3545,-3698]` | `null` / 350001 | 59.106 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[3545,3698]` | `null` / 350000 | 43.861 / 1000004 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-3545,-3541]],["r01",[-3545,3541]],["r10",[3545,-3698]],["r11",[3545,3698]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,15,14,13`, row `3bdc43804776da92a2ffe0d955849865f69e8296676c25e0a91079db2babc657`

- Branch `122`; selection key SHA-256 `001d14d345854bff16cc63412810982512d2117f339048a92667298a93c1b46b`; plan directory `plans/15,15,14,13/3bdc43804776da92a2ffe0d955849865f69e8296676c25e0a91079db2babc657`.
- Parent SHA-256 `62903d9be6d1c085821f18694d7a52674d2417918f558ecd7d7aa7d7c025ce88`; receipt plan ID `33e146aaf3ee9f800187bfb243a0ed6d20d5f310aa567f24598fcd6906f62762`; working SHA-256 `8f7e3736b87cfd119b3a8953e9c2dc26e706000843b2b3db4cb550959e7317e6`; CAS SHA-256 `036ec2b03282f64d5ccdc1336210ef9b4f565c07abbc04138971ad340a08a95f`. Formula: 18497 variables, 173817 parent clauses, 357 proof-derived cuts.
- Declared splits: `r=4129`, `r0=4768`, `r1=4886`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 92.486 s; output `shared-fresh/15,15,14,13/3bdc43804776da92a2ffe0d955849865f69e8296676c25e0a91079db2babc657`; receipt `shared-fresh/15,15,14,13/3bdc43804776da92a2ffe0d955849865f69e8296676c25e0a91079db2babc657/receipt.json`. Tail conflicts: 1001.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "3bdc43804776da92a2ffe0d955849865f69e8296676c25e0a91079db2babc657", "kind": "wall", "tier": "first"}, "parent_sha256": "62903d9be6d1c085821f18694d7a52674d2417918f558ecd7d7aa7d7c025ce88", "processed": 4, "status": "OPEN"}`; log `logs/verify-3bdc43804776da92a2ffe0d955849865f69e8296676c25e0a91079db2babc657.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-4129,-4768]` | `null` / 350002 | 44.029 / 1000000 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-4129,4768]` | `null` / 350002 | 60.593 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[4129,-4886]` | `null` / 350000 | 42.647 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[4129,4886]` | `null` / 350000 | 43.59 / 1000003 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-4129,-4768]],["r01",[-4129,4768]],["r10",[4129,-4886]],["r11",[4129,4886]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

### `15,15,14,13`, row `2bcaf5a123e1cc692fc353bb07c59c7279dcb62c9b2e42d98bf4d333258514e1`

- Branch `487`; selection key SHA-256 `002326b90de9983bf1e1194732a54a06949a2429de1ad69040f85a29956a372f`; plan directory `plans/15,15,14,13/2bcaf5a123e1cc692fc353bb07c59c7279dcb62c9b2e42d98bf4d333258514e1`.
- Parent SHA-256 `dbd02eab20d7a42879074dd8fda2c6c901cc86d2ccf4d9588f66f12a74b113f7`; receipt plan ID `6ecce5c34ce6d4cf29be7474bd8c4be87604ed5c6587444317ba10dde5a108c2`; working SHA-256 `1365f15a3f76ead9c1c01d63eab7984ee37c5d09d824b5932ce8c69b5d4941e1`; CAS SHA-256 `32002e22340bf2a6d76fe152d16e27b7e7458259714d26774cfdea4d1e23ea79`. Formula: 18387 variables, 173594 parent clauses, 189 proof-derived cuts.
- Declared splits: `r=1605`, `r0=2197`, `r1=2181`. The exact signed cube for each node is listed below; zero/one child signs are negative/positive respectively.
- Shared fresh pass: OPEN / conflict_limits, elapsed 96.913 s; output `shared-fresh/15,15,14,13/2bcaf5a123e1cc692fc353bb07c59c7279dcb62c9b2e42d98bf4d333258514e1`; receipt `shared-fresh/15,15,14,13/2bcaf5a123e1cc692fc353bb07c59c7279dcb62c9b2e42d98bf4d333258514e1/receipt.json`. Tail conflicts: 1001.
- Strict verify: `{"counts": {"OPEN": 4}, "leaves": 4, "origin": {"id": "2bcaf5a123e1cc692fc353bb07c59c7279dcb62c9b2e42d98bf4d333258514e1", "kind": "wall", "tier": "first"}, "parent_sha256": "dbd02eab20d7a42879074dd8fda2c6c901cc86d2ccf4d9588f66f12a74b113f7", "processed": 4, "status": "OPEN"}`; log `logs/verify-2bcaf5a123e1cc692fc353bb07c59c7279dcb62c9b2e42d98bf4d333258514e1.log`.

| Node | Exact cube | Shared result/conflicts | Leaf seconds/conflicts | Independently audited final status | Proof/replay binding |
|---|---|---:|---:|---|---|
| `r00` | `[-1605,-2197]` | `null` / 350000 | 60.32 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r01` | `[-1605,2197]` | `null` / 350002 | 52.782 / 1000002 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r10` | `[1605,-2181]` | `null` / 350000 | 43.717 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |
| `r11` | `[1605,2181]` | `null` / 350000 | 43.296 / 1000001 | OPEN / conflict_limit; unresolved, no proof retained | none |

**Whole-row result: OPEN_INCOMPLETE (0 certified, 4 OPEN, 0 NOT_RUN). Remaining cubes: `[["r00",[-1605,-2197]],["r01",[-1605,2197]],["r10",[1605,-2181]],["r11",[1605,2181]]]`. Export: NOT_ATTEMPTED_INCOMPLETE_COVER.**

## Retained artifacts and machine summary

- `cb1-frontier.json`: all plan bindings, full shared and leaf receipts, strict verification outputs, and independent final per-cube audit.
- `frontier.tsv`: 40-row flat frontier with full IDs, tree literals, exact cubes, both budgets' outcomes, proof hashes, replay paths and row verdict.
- `plan-audit.json`: exact independently reconstructed split trees and original parent/working/CAS hashes.
- `independent-leaf-audit.json`: exact per-leaf receipt bindings and the independent ordinary replay; `logs/` retains raw driver/checker output.
- Disk use and a file inventory are recorded separately in `retention.txt` and `artifact-sha256.tsv`. The campaign is far below the 40 GiB collective cap.
