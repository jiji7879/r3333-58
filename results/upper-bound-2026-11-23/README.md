# Upper bounds on `U+V`: exact on all five boards, and they close nothing

Swarm `smwu1x5uy`, first two results. Question asked: can `U+V` be bounded above, and would that
close a row?

## The answer, in one table

| row (branch) | board floor (short-spoke) | board ceiling (attained) | ceiling witness |
| --- | ---: | ---: | --- |
| 14 `ec075047186a` | 19 | **32** | (15,17) |
| 59 `8a40a4423925` | 19 | **38** | (18,20) |
| 62 `652553307655` | **21** | **40** | (20,20) |
| 282 `f4f7ef740f40` | 19 | **33** | (17,16) |
| 286 `dd05194bd9aa` | 19 | **35** on (14,5), 30 on (5,14) | (17,18) |

All ten witnesses re-checked here from the definition: triangle-free, every frozen pin respected
(224–234 pins per board), counts recomputed.

## The exact maximum on branch 62, proved by hand

`U <= 20` and `V <= 20` on branch 62's `(14,5)` board, so `U+V <= 40`, and `(20,20)` is attained —
so the maximum is exactly 40.

Proof, every step checked here: all 105 pairs inside `A` and all 15 root-`A` pairs are pinned, so the
colour-1 graph `G` on `A` is fixed. The colour-1 neighbourhood `M = N_1(16)` has 16 vertices and
**all 120 pairs inside `M` are pinned to a colour other than 1** (the judge's first check missed this
by looking only for negative colour-1 literals; the row pins are positive). For a pentagon vertex
`z`, its colour-1 neighbours in `A` lie in `F = A \ M = {2,3,5,7,9,10,11,12,13,14}` — the triangle
`16-z-a` forbids colour 1 from `a` to `z` when `a` is colour-1 adjacent to 16 — and that set is
independent in `G`, since a colour-1 edge inside it would close a monochromatic triangle at `z`.
`G[F]` is 3-regular on ten vertices with **independence number exactly 4** (brute force over all
subsets). Hence `|S_z| <= 4` for each of the five pentagon vertices, and `U <= 20`, symmetrically
`V <= 20`.

**Pins-free bound, every row and board**: `U, V <= 25` and `U+V <= 50`. The binding side is the
pentagon, not `A`: each pentagon vertex has at most five colour-1 neighbours in `A`, because `A`
omits colour 0 internally and six would give a two-coloured `K_6`. (An earlier 75 in the swarm's
brief counted 15 `A`-vertices at five spokes each and is withdrawn — it is not the binding side.)

## The ceiling is an instance fact at 58 vertices, not only a board argument (m6)

m3's proof caps the value on the 35-vertex board. m6 closes it at full-row scale: **`U+V >= 41` is
UNSAT on the 58-vertex pin-relaxation of branch 62**, with a DRAT certificate. The judge reproduced
it end to end — CNF hash `d4a4e3d9…` matches the manifest, kissat returns UNSATISFIABLE in 9.1 s, the
proof it emits is 24,416,206 bytes with SHA-256 `fb5bed1b…` (byte-identical to the recorded proof),
and `drat-trim` accepts it in 7.9 s.

So on branch 62 the row satisfies **`21 <= U+V <= 40`** as an instance, and 40 is not merely the
board maximum — it is the row maximum.

**The board tops do not lift.** Fixing the bundle's `(18,18)` colouring or either `(20,20)`
colouring, the 44-vertex CNF is UNSAT. So no colouring attaining the top extends, and the true
realisable range is a proper subrange of `[21, 40]` — which is now a concrete question rather than a
guess.

**Symmetry**: the `(14,5)` board has exactly **725,760 = 9! x 2** automorphisms, enumerated
exhaustively, and a verified isomorphism `(14,5) -> (5,14)` exchanging colours 2 and 3 transports
every witness and exclusion between the two orientations.

## What this settles

**No upper bound provable from these boards can close any of the five rows.** Closure needs
`U+V <= 18` (one below the floor); every board the floor is certified from already attains at least
32, and monotonicity extends that to every larger board. So the board-level route is dead for
closure in both directions, on all five rows, and the remaining hope for any of them is a full-row
statement.

## Open

- `U+V = 19` exactly, on all four non-62 rows: OPEN at 250 s each.
- `U+V >= 39` on row 59 (150 s), `>= 36` on 286 (40 s), `>= 33` on 14 (90 s): OPEN.
- Row 59's 44-vertex `(14,14)` board: neither model nor refutation at 600 s.
- The full rows: OPEN, and the bundle reports no measured speedup from any of these cuts.
