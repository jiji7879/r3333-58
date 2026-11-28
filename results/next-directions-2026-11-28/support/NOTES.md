# Direction 1 — finite support catalogue + physical-to-coded transport in Lean (K58)

**Integrated direction and checked claims.** The accepted source is in
`lean/K58/SupportCatalogue.lean`, `lean/K58/SupportTransport.lean`, and the exact
emitted readiness/audit companion is `lean/K58/SenderReady.lean`. All use real
physical neighbour sets and the production `targetSupports`. Only the local
import prefix was changed during integration. See `build.txt` for the root
build and permitted axiom output.

**Remaining obligations.** `PinnedArm` and pinning to the exact emitted root
coordinates remain hypotheses. No emitted atom order has been identified with
that pinning, no coded guard has been equated with physical `Sends`, and no
`ChainReady` theorem follows. The catalogue and two-sided readiness statements
are proved; the physical instantiation is consequently conditional.

The original report follows. Its reproduction paths and module names refer to
the member directory. The original source-root offsets resolve correctly here;
only the sender-18 transcription check now reads the integrated Lean module.

Base tree: repository HEAD `e43e78e` ("Prioritize new directions from Ramsey literature").
While this ran, another member committed `012c7a2` (adds `lean/K58/CAT58.lean`,
`lean/K58/Attachment.lean` only).  My build imports `K58.Support` and
`K58.TargetSuffix`; neither changed, so the statements below are against
unmodified production sources.  No repository file, frozen ledger, order entry,
production encoding default or other member's directory was touched.  All my
artefacts are in this directory.

## Result in one line

22 kernel-checked Lean theorems (today's set; standard axioms only) do two
things.  They pin down the emitted catalogue *exactly* (both directions:
`catalogue_iff`, `112 = 96 P4 + 16 C5`, marked colour 1, path colour 2, T16),
and they carry a physical colouring at any arm-1 support event of the retained
parent — `sender = 18 … 32`, guards `11965 … 18839` — to the **exact emitted
`ready` proposition** of `K58.SemanticAssembly.emittedSupportStep`
(`emittedSupportStep_ready_shape` is `rfl`, so no new predicate is introduced).

## What is proved (all `[propext, Classical.choice, Quot.sound]`)

`K58SupportCatalogue.lean`

* `targetSupports_length : targetSupports.length = 112`,
  `targetSupports_four_count = 96`, `targetSupports_five_count = 16`,
  `targetSupports_nodup`.
* `catalogue_sound` — every one of the 112 emitted masks is marked-colour
  independent and has cardinality 4 or 5 (`patternNat_indep`, `patternNat_card`).
* `p4_complete` — the K60 `p4_complete` port: for all `a b d e : Fin 16`, the six
  T16 colour relations of a colour-1 path `a-b-d-e` with colour-2 diagonals give
  `inCatalogue {a,b,d,e} = true`.
* `c5_check` / `c5_complete` — the K60 `support_check` port: every 5-element
  marked-colour independent subset of the 16 T16 coordinates is one of the 16
  five-element entries.
* `four_check` / `catalogue_complete` / `catalogue_iff` — the **exact**
  membership characterisation (both directions), in set form: for
  `S ⊆ Fin 16` with `S.card ∈ {4,5}`,
  `inCatalogue S = true ↔ indep0 S ∧ (S.card = 4 → pathDegrees S = true)`,
  where `pathDegrees` says the local-colour-1 degree sequence is `1,1,2,2`
  (`localDeg`).  The forward direction on the emitted list is
  `catalogue_sound` + `patternNat_pathDegrees`.  So the catalogue is *not* "all
  marked-independent 4/5-sets" (that would be 120+16) and *not* "all colour-1
  paths" — it is exactly the intersection, which is what the physical transport
  supplies.
* Six checked negative controls (see below).

`K58SupportTransport.lean`

* `support_mask_mem` — the transport theorem (statement quoted below).
* `support_mask_mem_of_pinned` — same with `PinnedArm G r 0 16 true`.
* `ready_of_mask`, `ready_at_guard`, `sender18_ready` — the emitted `ready`
  proposition at `g = 11965` (sender 18) and at an arbitrary guard.
* `emittedSupportStep_ready_shape` — `rfl` lemma: the `ready` field of the
  production constructor *is* the proposition discharged here (`n = 16`,
  `k = 112`, `allowed = supportBit targetSupports`).  No new semantic predicate
  is introduced.
* `local_colour` — the palette bridge: physical `0.succAbove d` ↔ local `d`, so
  physical 1 = local marked 0, physical 2 = local path 1, physical 3 = local 2.
* `support_mask_mem_of_deg` — the degree form: with the order-`n` template
  classification as a hypothesis, `deg G q 1 = n` (`n = 15 ∨ n = 16`) replaces
  `PinnedArm G q 1 n t` via `K58.pin_of_named_classification`, leaving the root
  pinning as the only other premise.  This is exactly where the memo's
  `15 ≤ d ≤ 16` enters; the classification is *not* proved here.

Exact statement of the transport theorem (from the file):

```lean
theorem support_mask_mem (G : EdgeCol V 4) (hG : TriangleFree G) (q r : V)
    (hqr_ne : q ≠ r) (hqr : G.col q r = 1) {n : ℕ} {t : Bool} (hn : n = 15 ∨ n = 16)
    (hsender : PinnedArm G q 1 n t) (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y))) :
    ∃ i : Fin 112, ∀ j : Fin 16,
      (decide (G.col q (er.symm j).val = 1)) = supportBit targetSupports i j
```

Shape of the proof (each step is a real deduction, none assumed):

1. `pinned_support_shape G q r 1 hn hsender hr_mem 0 1` gives
   `SupportShape G (arm G q 1 ∩ arm G r 0) 2` — the physical support is a
   colour-**2** P4 or C5, because `(1 : Fin 4).succAbove 0 = 0` and
   `(1 : Fin 4).succAbove 1 = 2`.
2. `m = 4` branch: the four template positions give a colour-2 path
   `0-1-2-3`; the three diagonals are *not* colour 2 (SupportShape iff), *not*
   colour 0 (triangle at the root `r`), *not* colour 1 (triangle at the sender
   `q`), hence colour 3, i.e. local colour 2.  `p4_complete` then applies.
3. `m = 5` branch: the support has cardinality 5 and is marked-colour
   independent (triangle at `q`); `c5_complete` then applies.  No cycle-shape
   hypothesis is needed there, which is a *checked* property of the T16
   template, not an assumption.
4. The root pinning `er` converts the physical support into a `Finset (Fin 16)`
   whose colour-1/2 degrees are those of the physical colour 2/3 edges.

## What is NOT proved (explicit residual obligations)

1. **The two `PinnedArm` hypotheses are hypotheses.**  `PinnedArm G q 1 n t`
   encodes `15 ≤ deg G q 1 ≤ 16` plus the critical-template classification; that
   is the still-open "candidate/112-support criticality" obligation, not
   something a SAT counter supplies.
2. **The emitted coordinate order is a hypothesis.**  `er` + `hroot` say the
   frozen emission enumerates the root's arm 0 in a `T16` colour-isomorphic
   order.  Identifying the production atom list with that order (the memo's
   "mask/name bridge") is *not* proved here: `sender18Atoms` is transcribed from
   the emitter, and the theorem is stated relative to `er`.
3. Nothing here says a coded guard *is* a physical `Sends` event, that vertex 17
   plus the 15 coded support sets exhaust the physical senders, or that
   `ChainReady` holds.  The two final floor counters (6-of-15, 6-of-31) are
   untouched.
4. No UNSAT/upper-bound claim, no change to 51 ≤ R_4(3) ≤ 62.

## Negative / rejecting controls (all kernel-checked in `K58SupportCatalogue`)

| control | content |
|---|---|
| `control_indep_not_member` | `{0,2,9,11}` is marked-independent but its colour-1 edges form a 4-cycle; not an entry.  So independence alone is insufficient (independent 4-sets: 120, entries: 96). |
| `control_path_with_marked_edge` | `{0,1,2,5}` is a T16 colour-1 path `0-2-1-5` but contains the marked colour-0 edge `01`; not an entry. |
| `control_wrong_path_colour` | `{0,1,4,8}` is a colour-**2** path with no colour-1 edge ("either remaining colour" shortcut); not an entry. |
| `control_single_bit` | `{0,2,4,6}` and `{0,2,4,7}` are entries; `{0,2,4,8}` is not. |
| `control_five_needs_indep` | `{0,1,4,8,12}` is not an entry and is not marked-independent (the five-set branch really uses the hypothesis). |
| `control_t16_not_u16` | `{0,2,4,6}` is an entry and a T16 colour-1 path, but under U16 its colour-1 edges are only `02, 46` (a matching).  The emitted list is T16-specific: the U16 shape family is a proper subset (80 of 96 four-sets, verified in `catalogue-semantics.json`). |

## Independent non-Lean checks (`python3`, no solver, no network)

* `check_catalogue_semantics.py` → `catalogue-semantics.json`:
  re-derives the catalogue from `lean/K58/Templates.lean`'s `dc`/`trade`/`swap01`
  and reproduces `targetSupports` **order-exactly** (96 four-sets in
  lexicographic order, then 16 five-sets); the reproduced template equals the
  frozen generator's `named_template(16,"T",0)`; independent 4-sets = 120 ≠ 96,
  independent 5-sets = 16 = the entries; controls: U16 4-family = 80, wrong path
  colour = 672, wrong size (T15) = 492.
* `align_controls.py` → `align-controls.json`: 192 ordered tuple witnesses for
  the `p4_complete` hypothesis, whose underlying sets are exactly the 96
  four-element entries; the 24 marked-independent-but-not-P4 4-sets; U16
  ordered-P4 sets = 80, all inside the catalogue (so U/T are not interchangeable
  but U is not a superset either).
* `check_sender18_transcription.py` → `sender18-transcription.json`: the Lean
  literal `sender18Atoms` equals the emitter's first support atom list
  byte-for-byte (so the transcription is machine-compared, not hand-asserted).
* `check_emitted_events.py` → `emitted-events.json`: the production suffix has
  exactly **15** support events, guards
  `11965 12456 12947 13438 13929 14420 14911 15402 15893 16384 16875 17366 17857 18348 18839`,
  every one `n = 16`, `k = 112`, 16 distinct atoms, and each atom list is the
  leading 16 atoms of the immediately preceding guarded counter.  31 counters:
  4 × AtLeast(30,10) + 27 × AtLeast(41,14), then native 6-of-15 and 6-of-31.
  This is the inventory `ready_at_guard` is meant to instantiate; it does not
  prove the coordinate bridge (item 2 above).

## Reproduce

```sh
cd .ultramath/smx06hpp8/m1
python3 check_catalogue_semantics.py
python3 align_controls.py
python3 check_emitted_events.py
python3 check_sender18_transcription.py
bash build.sh          # lean -j1 -o ... K58SupportCatalogue, K58SupportTransport, Axioms
```

`build.sh` sets `LEAN_PATH="$PWD:$REPO_ROOT/lean:$LEAN_PATH"` and reuses the
repository's existing `lean/K58/*.olean`; it writes only `*.olean` files inside
this directory (never into `lean/`).  Toolchain: Lean 4.33.1 (the repository's
pinned version), `lean` + fully built Mathlib on `LEAN_PATH`.

Axiom receipt (`Axioms.lean` output) — 22 theorems, all
`[propext, Classical.choice, Quot.sound]` except `ready_of_mask` (`[propext]`).
No `sorry`, `admit`, `native_decide` or custom axiom occurs in either file
(`grep -n "sorry\|admit\|native_decide"` returns nothing).  The finite checks
use `decide +kernel`, i.e. kernel reduction, not compiled `native_decide`.

## File hashes

`hashes.txt` (sha256) covers both Lean sources, `Axioms.lean`, this note, the
four JSON receipts and the four scripts; `build-receipt.json` repeats the Lean
hashes together with the verbatim axiom output and the exit code.  Hashes are
not quoted here, so that no stale copy can drift from `hashes.txt`.
