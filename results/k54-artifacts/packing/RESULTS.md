# Job A (swarm smwn8rsmo, member m2): the crossing-cut theorem's finite inputs, verified

Route taken: **the theorem side**, not the eligibility side.  I do not test
tightness of the stored parts of size 5, 6, 7 (that is d1's object); I verify the
*other* half of the crossing-cut chain, namely the one-template capacity table of
sizes 1..4 and the four-point packing bound `4 / 4 / 3` that lifts the edge count
`56` of `work/k54cut/README.md` to `61 / 61 / 62`.

Everything below is re-derived by my own encoder (`pack/enc.py`); the handoff's
`saturated.py`, `all_singletons.py`, `pack_four.py`, `four_bounds.py` and
`cap.cpp` are never imported or executed, and nothing in the archive is written.
For the 39 refutations the handoff ships, my encoder reproduces its CNF bytes
exactly (byte-identical on all 39 of them), which is what makes its DRAT
proofs apply.

## Result

| claim of `work/k54cut/README.md` | verdict | evidence |
|---|---|---|
| every 1-set of the 14 template positions is tight (at most 1 outsider has its whole c-support there) | holds: 14/14 | `capacity.json`, 14 CNFs, DRATs in `proofs/cap1-*` |
| every 2-set is tight (at most 2) | holds: 91/91 | `proofs/cap2-*` |
| every 3-set is tight (at most 3) | holds: 364/364 | `proofs/cap3-*` |
| 989 of the 1001 four-sets are tight (at most 4), the other 12 have capacity 5 | holds: 989 tight, 12 at 5, and the 12 are exactly `results/saturated4.json` (277, 550, 1162, 2121, 4388, 4417, 5154, 5192, 8724, 8834, 10257, 10376) | `proofs/cap4-*`, `proofs/cap6-*` (6 outsiders in a four-set refuted for all 12) |
| at most 4 / 4 / 3 outsiders can have *exactly* four c-neighbours at pole 0 / 2 / 4 | holds, and each bound is attained (4, 4, 3) | `direct.json`: 3 UNSAT CNFs with DRAT, 6 SAT CNFs with clause-checked models |
| the capacities are exact, not just upper bounds (k outsiders inside a k-set are realizable, 4 inside every four-set) | holds: 1470 SAT controls, models checked | `exactness.json` |
| the 39 stored mask-set refutations behind that bound | all 39 replay: `s VERIFIED` against my rebuilt CNF, and each re-solves UNSAT | `replay.json` |
| the enumeration that turns them into `4 / 4 / 3` | recomputed: `overall = 4,4,3`, per-position `limits` match, `allowed` = the exceptional masks avoiding the pole, witness models satisfy their CNF | `enum_check.json` |
| "each exceptional set occurs at most once" (the implicit multiplicity step of the enumeration) | holds: 25 UNSAT certificates (13 singleton witnesses + two outsiders of the same exceptional four-support, for every exceptional mask and every pole it avoids) | `multiplicity.json`, `proofs/dup-*` |

Consequences, with the arithmetic spelled out.  In the theorem's `M` we have
`|M| = 13`, every `|S(w)| >= 4` (three-point capacities above), and at most
`overall` members have `|S(w)| = 4` (packing bound above, pole 0/2: 4, pole 4: 3).
Hence

  * pole 0 and pole 2: `sum |S(w)| >= 4*4 + 5*9 = 61`,
  * pole 4: `sum |S(w)| >= 4*3 + 5*10 = 62`,

against the `55 = 6*7 + 13` upper bound, instead of the handoff's weaker
`56 = 9*4 + 4*5`.  The strengthened edge bound is therefore certified, and the
packing bound is tight (models attain it).

Also checked: the handoff's Lean file reproduces here — `lean formal/CrossCut.lean`
with Lean 4.33.1 prints `'R3333.CrossCut.forcedRectangle' depends on axioms:
[propext, Classical.choice, Quot.sound]`, so the counting half (`56 > 55`
contradiction) is machine-checked and axiom-clean.

## What this does *not* verify, and which links the theorem actually needs

Reading the theorem's proof against the capacities, the chain uses exactly four
kinds of finite input:

1. `|L| <= 13`: one-point capacity on the A template — **verified here**.
2. `|M| <= |B1| + |B2| = 13`: tightness of the two *parts themselves*, sizes 6
   and 7 — **not verified here** (d1's object).
3. Hall's condition for the representative columns: for every `R` contained in a
   part, at most `|R|` outsiders have their B-support inside `R` — i.e. tightness
   of *every* subset of *each* part, sizes 1..7 — **not verified here**.
4. `|S(w)| >= 4` and the four-support count: **verified here**.

So the eligibility claim itself still rests on (2) and (3).  Worth flagging for
whoever finishes pole 0: Hall needs *all* subsets of a part, not a sample and not
only the parts themselves, so a single non-tight subset anywhere inside a part
refutes eligibility of that partition — sampling cannot close it.

## Reproduce

    cd .ultramath/smwn8rsmo/m2/pack
    sh run_all.sh          # ~3 min, 4 cores idle

Each script is independent and re-runnable; every UNSAT answer carries a CaDiCaL
DRAT that `work/k54/build/drat-trim` accepts (`s VERIFIED`, exit 0), every SAT
answer a model re-checked clause by clause against the same CNF.  All instances
have at most 32 vertices and are decided in under a second.

## Scale of the evidence

3043 CNF instances: 1549 UNSAT (every one with a stored, verified DRAT: 1470 in
`proofs/cap*`, 37 in `proofs/dup-*`/`proofs/cap4-*`, 3 in `proofs/direct-*`, plus
the 39 archive proofs replayed in place) and 1494 SAT (models checked clause by
clause).  Proof store: 20 MB gzipped.  Peak RSS measured with `/usr/bin/time -v`:
67 MB (`direct.py`), 65 MB (`capacity.py`) — no memory pressure at any point.  The
archive's own `sha256sum -c SHA256SUMS` verifies 132/132 files, so the bytes the
replays consumed are the bytes that were published.

## Files

* `enc.py` — independent encoder.  Two modes: prescribed c-support (the handoff's
  packing instances) and free c-support inside an allowed set (occupancy), plus an
  exactly-k mode used for the direct packing bound.
* `capacity.py` / `capacity.json` — the 1..4-set capacity table, 1470 entries with
  CNF sha256 and status.
* `direct.py` / `direct.json` — the single-instance certification of `4 / 4 / 3`.
* `replay.py` / `replay.json` — the 39 archive refutations, CNF sha256 + proof
  sha256 + `drat-trim` verdict + independent re-solve.
* `enum_check.py` / `enum_check.json` — recomputation of `overall`, `limits`,
  `allowed`, and the witness models.
* `multiplicity.py` / `multiplicity.json` — the multiplicity certificates and the
  capacity-4 / capacity-5 controls.
* `exactness.py` / `exactness.json` — 1470 SAT controls showing every capacity
  value is exact (so the UNSAT side is not an artefact of the encoding).
* `model_semantics.py` — reads supports back out of the models of the exactly-k
  CNF (thirteen distinct singletons, r four-supports, none containing the pole).
* `proofs/` — gzipped DRAT proofs; `MANIFEST.sha256` — hashes of all of the above.
* `CrossCut.lean` — copy of the handoff's Lean file, compiled here.
