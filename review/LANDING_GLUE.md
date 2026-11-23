# Landing the gluing/transport bundle into the main tree

Bundle: `attachments/let-s-try-and-wcbj/R3333_K58_Lean_gluing_and_transport.zip`.
Stage 1 of the campaign's obligations ("land the gluing bundle"): fold the bundle's
`K58` modules and its generated replay tree into `lean/`, so that
`K58.Replay.frozenCover` is a kernel-checked object in this repository and not only
in a worktree built from an older base.

`K58.Replay.frozenCover : K58.FrozenCover` says the 113,179 frozen keys are
realized by the raw cover and its transports.  **It does not say that any case is
refuted.**  Ruling out the frozen cases remains the open problem (31,751 rows are
OPEN in `results/ledger-2026-11-22.tsv.gz`, including all 381 of the
`(15,14,14,14)` rows this session is working on).

## What the bundle verified before the landing

At its own base `e62d8ab` (24 commits behind the tree it was landed on), the
previous session ran its `build.sh` (catalogue + 45 K58 modules) and then deleted
every `.stamp` in the generated tree and rebuilt all 1,588 replay modules from
source: 0 cached, exit 0.  The transcript prints
`'K58.Replay.frozenCover'` and `'K58.Replay.rawTransportCover'` with axioms
`[propext, Classical.choice, Quot.sound]`, and `K58.frozenKeys_length :
frozenKeys.length = 113179` (axioms `[propext, Quot.sound]`).

## What changed in the landing, and why

* **`K58.Arm` was already taken.**  The bundle's `Arm.lean` (the pinned-arm
  interface: `PinnedArm`, `pin_of_named_classification`, `marked_sender`) is a
  *different module* from this tree's `K58.Arm` (the arm-structure lemmas
  `sender_split`, `arm_degree_partition`).  The bundle's file is landed as
  `K58.ArmPinned`, and its only two importers (`MarkBreadth`, `Support`) are
  repointed.  This is the one real conflict; the other three files that exist in
  both trees differ only in comments (`Main`, `Templates`) or are the audit list
  (`Check`), which is merged.
* **The build order is derived, not hand-written.**  `order.txt` is a topological
  order of the `import K58.*` edges over the 60 modules (a script, not a list
  someone maintained).  The bundle's own list had `Arm` before `Templates`, which
  the merged tree cannot do.
* **`ReplayGen/` is a build artefact.**  The 1,588 generated modules (56 MB of
  Lean) are produced by `replay/generate_replay.py` from the handoff ZIP and the
  500 KB transport certificate, so only the generator, its inputs and the driver
  are committed.  `ReplayCheck.lean` audits the two replay theorems and is built
  only in the `--replay` path, because it needs the generated tree.

## What was measured on the merged tree

* The library compiles: 60 modules, exit 0 (`.scratch/land/build3.log`).  The first
  pass stopped at `Check` because `order.txt` had been derived from the *old*
  `Check.lean`; the order is now recomputed from the merged file, and `build.sh`
  skips a module only when its `.olean` is newer than its source and than every
  `.olean` of the K58 modules it imports.
* `replay/check_build.py` on the merged tree: **143 registered declarations, 143
  distinct declarations with axiom records, every list a subset of
  `[propext, Classical.choice, Quot.sound]`**, no placeholder in the sources.
* **The bundle's checker had to be repaired first.**  It rejected this tree with
  `unpermitted proof token in lean/K58/Interface.lean`, because that file's comment
  header names `sorry` and `native_decide`; the check was a substring search over
  the raw file.  It now strips Lean comments (nested `/- -/` honoured) and string
  literals and matches the three tokens as words.  The repair was tested both
  ways: a comment mentioning all three passes, and a planted
  `theorem planted : True := by sorry` is still rejected.  This is an erratum in
  the handover tooling of the same family as `review/ERRATA.md`: a checker that
  cannot run on a tree whose documentation mentions the words it forbids.
* The replay (1,588 generated modules) is rebuilt from source in
  `.scratch/land/lean/replay/ReplayGen/`; its result is recorded in the commit that
  lands `ReplayCheck.lean`.

## What this landing does not do

No frozen case is closed, no bound moves.  `K58.Replay.frozenCover` certifies the
cover object and its 113,179 keys, not any refutation.
