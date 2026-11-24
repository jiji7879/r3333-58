# The campaign–Wesley crosswalk confirms the 115 classification independently

File: `K58_campaign_Wesley_crosswalk.tsv` (18.6 KB), 345 rows.

## Its structure

| field | content |
| --- | --- |
| `campaign_role_zero_based` | 0–331, the campaign's 332 roles |
| `Wesley_type_one_based` | 1–115, the literature classes |
| `Wesley_symbol_for_zero` | which of the three colours is the arm colour |
| `rooted_cover_count`, `partition_covers`, … | per-role cover data |
| `Wesley_vertex_to_campaign_vertex_zero_based` | a 14-point vertex correspondence |

## It agrees exactly with an independent computation

The judge computed the `S_3` colour orbits of the campaign's 332 types by exact isomorphism (VF2 with
edge-colour matching) and found **115 classes: 102 of size 3 and 13 of size 2**. The crosswalk gives
the same structure from the other side:

| quantity | crosswalk | judge's computation |
| --- | ---: | ---: |
| classes | 115 Wesley types | **115** |
| (type, colour) pairs | 345 = 115·3 | 345 |
| campaign roles | 332 = 345 − 13 | **332** |
| duplicated roles | 13 | 13 orbits of size 2 |

and the sharpest test, which passes exactly: **all 13 size-2 orbits contain exactly one
crosswalk-duplicated role, and both members of each orbit share the same Wesley type.** The 13
duplicated roles are

```
6, 7, 19, 20, 62, 63, 75, 90, 154, 162, 248, 315, 328
```

each listed under two different symbols of one type — precisely the colour symmetry that makes its
orbit short.

## Why this is worth having

1. **It is an external check on our own alphabet.** The classification the campaign uses is confirmed
   by an independently compiled document, not merely self-consistent.
2. **It supplies vertex-level correspondences**, so the downloadable Wesley representatives map into
   campaign coordinates. Anyone wanting to work in the 115-class language can do so without
   recomputing the transport.
3. **It settles the unit question.** 345 (type, symbol) slots collapse to 332 roles because the 13
   symmetric classes identify two of their three colour choices; the census therefore has to be run
   per (class, colour), which is exactly what the one-arm cover census does.
