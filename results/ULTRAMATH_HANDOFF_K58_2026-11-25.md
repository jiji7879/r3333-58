# K58 wall campaign: Ultramath handoff

Status date: 2026-11-25, including runs `smwvpsb38`, `smwvx4uzm`, and `smww1ulor`.

## Executive status

- **No complete frozen row or profile has been closed.**
- **`R(3,3,3,3) ≤ 58` is not proved.** This work does not move the established published bound.
- Target for the current push: **140 OPEN rows** of profile `(16,16,13,12)`: 70 TU, 56 TT, and 14 UU, with charge split 14/70/56 for charges 1/4/7. Check these statuses against the release-folding ledger, not the older raw case-ledger status field.
- Hard exclusion: **do not work specifically on profile `(15,14,14,14)`**. Never enable perfect balance for the target profile: root degrees include 16 and 12. Use the `balance.py` CLI without `--balance`, or explicit `balance=False`.
- Scores so far: **21 accepted reports** across the three swarms (7 + 8 + 6). Acceptances include rigorous structural results, exact finite certificates, and precisely scoped negative boundaries; they are not all refutations.

## Most useful current artifacts

### Reciprocal C&C on charge-7 TU row 0404

Root row:
`0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296`,
`(16,16,13,12)`, TU--, arm 1, charge 7, placement `[4,0,0]`.

Augmented root: `results/cc-reciprocal-0404-2026-11-25/root.cnf`,
SHA `aa23de814810dc2b5515955a0aa318eab72df81c4541006fde253b39c48d2b44`.
This is the common-pair reciprocal child plus independently proved mixed cap-8 clauses, **not the whole row**.

Current merged coverage tree: `results/cc-reciprocal-0404-2026-11-25/continuation/tree.json`.
It has 25 nodes and 13 terminal leaves. The nine verified leaves are
`n002,n005,n006,n009,n014,n016,n018,n019,n021`; all were independently decompressed,
hash-checked, and replayed through drat-trim `s VERIFIED` in
`pilot/JUDGE_REPLAY.log` and `continuation/JUDGE_CONTINUATION_REPLAY.log`.
The only open terminal leaves are **`n017,n022,n024,n025`** at depth 6.
The original `n012` branch is completely closed.

Coverage is exact Boolean splitting $C \mapsto (C\land x) \lor (C\land \lnot x)$: **both** leaves must be closed; proof reuse does not change it. Closing the entire current terminal frontier would refute **only the augmented reciprocal child** of this one row.

### Measured controller experiment

`tools/cc/policy_reciprocal.py` offers an opt-in policy that probes both polarities
before branching, priorities fast checked UNSAT children then propagation pressure,
and reuses verified probes as leaves. It introduces **no new constraints**.
`tools/cc/continue_reciprocal.py` accepts this with
`--leaf-prefix policy_reciprocal.PolicyPilot` and budget controls
`--probe-vars N --probe-seconds N`.
`results/cc-reciprocal-0404-2026-11-25/POLICY_EXPERIMENT.md` records the short
end-to-end smoke trial. This is tested plumbing, not yet a demonstrated speedup.

## Main mathematical tools

1. **Exact mixed two-arm clone maximum**. `.ultramath/smwvx4uzm/m1/PROOF.md`,
   `ClonePair16.lean`, and `work/embedding-certificate/physical_manifest.json`.
   For full pinned root+16+16 objects, mixed T/U or U/T permits at most **8** exact-one-spoke clones. Both >=9 CNFs replay DRAT UNSAT; both exact 8-clone physical models check. Equal U/U and T/T permit 16. The older 29-vertex reduced-interface cap 12 is superseded **for the full object by 8**, not contradicted.

2. **Reciprocity exactly characterised at this root**.
   `.ultramath/smwvx4uzm/m6/ReciprocalTwo16.lean`: with root degrees `(16,16,13,12)`,
   `Reciprocal G` iff every vertex's critical colours are `{0,1}`, with no extra global
   at-least-two-critical premise. Degree shapes and handshake parity supply extra pinned 16-arms. Reciprocity is **not** derived merely from `H=w` without additional argument.

3. **Global residual-flow identities**. `.ultramath/smwvpsb38/m4/` and
   `.ultramath/smwvx4uzm/m5/ResidualCycle.lean`: `inOne-outOne=H-w`, balanced residual arcs lie on nonempty directed closed walks, every residual arc has a directed return path, and a balanced root is inactive in both directions or active in both. Outgoing at root use colours 0/1; incoming use 2/3.

4. **Deficiency conservation and exact inactive flags**.
   `.ultramath/smww1ulor/m1/BalanceDeficiency.lean` and
   `.ultramath/smww1ulor/m1/RootProfile.lean`:
   `H + (critical shortfall) = w + (noncritical surplus)`.
   At `(16,16,13,12)`: `H=32+β-α`, balanced `α=β<=25`, activity iff `α=β>0`,
   strictness iff `α<β`, requiring a critical point in at least one small arm.
   **β>0 is a 25-way disjunction**, not a witness in each small arm.

5. **Flags cover reciprocal AND inactive children**.
   `.ultramath/smww1ulor/m7/InactiveCoverage.lean`, `build_inactive_L2.py`,
   `build_generic.py`: at critical palette `{0,1}`, residual inactivity is exactly 32 positive + 25 negative root-edge flags. Full reciprocity makes every vertex residual-inactive, hence satisfies those same flags. The marked-free formula `.ultramath/smww1ulor/m7/gen-L4.cnf` (827,570 clauses,
   SHA `715597e0bdb9d2131a909b8bcbde6ec1768b98cf7608be17991ca92c7bebcbd7`)
   covers both cases across **all 70 TU rows**, without balance/reciprocity assumptions.

6. **Support and interface geometry**.
   - `.ultramath/smwvpsb38/m5/SmallSupportC4.lean` and `small_support_c4.py`: critical supports are C4-free in either residual colour, including unclassified 11–14 arms. Do not confuse C4-free with P4/C5 **without** requiring support size 4/5; the exact finite equivalence was checked separately.
   - `.ultramath/smwvx4uzm/m3/CrossSupport.lean` and `CrossSupportTotals.lean`: pointwise joins at most 2,2,1 and aggregate join totals `(2m,2m,m)` for every pinned 15/16 star, without receiving-template hypotheses.
   - `.ultramath/smwvpsb38/m2/Clone16.lean` and `.ultramath/smwvx4uzm/m7/CloneWords.lean`: exact-one star cloning, centre uniqueness, and clone-pair colours.
   - `.ultramath/smwvx4uzm/m4/Interface16.lean`: `2|Z|-16 ≤ Σ_{y∈Z}|N_a(y)∩A|`, hence at least 66 arm/off-centre incidences at K58.
   - `.ultramath/smww1ulor/m5/lean/ArmSixteen.lean`: direct 5-regularity of any 16-arm, no T/U classification; discharges familyC at a 16-receiver. U16 unique four-support centres vs explicit T16 counterexample: `.ultramath/smwvx4uzm/m4/Support16Colours.lean` and `PinnedUSupport.lean`.

7. **Five-way pins-only coverage**.
   `.ultramath/smww1ulor/m2/lean/RootFiveWay.lean` and `AUDIT.md`.
   `physical_root_four_way` assumes `w(r) ≤ H(r)` and therefore, without a separate root premise, its four siblings are not exhaustive for **pins only**.
   At the anchor, `w=32` while the row CNF's marked-arm charge supplies only H≥7.
   A complete pins-only closure must additionally cover `H(r)≤31` or derive/route
   `H(r)≥32`. The collision-free builder is `build_branch5.py`; every auxiliary starts above `parent.nv`, root-edge accounting uses `needed=14`.
   **This is not itself a proof that the global cover is unsound.** Cover-level routing to different strict/nondeficit roots is a separate issue.

## Exact delimitations, not refutations

- `.ultramath/smww1ulor/m6/Core33.lean` and `PROOF.md`: an explicit symmetric triangle-free 33-vertex model satisfying all 303 frozen root-arm units and necessary >=4 projected cross-floors. It does **not** represent actual criticality: those other two off-core degree parts are missing. Three terms `(4,4,4)` give only degree 13; criticality requires off-arm sum >=14, i.e. `(4,5,5)` or `(5,5,5)`.
- `.ultramath/smww1ulor/m8/REPORT.md`: the same necessary-projection delimitation including all 32 projected 4/5 C4-free supports and no rigidity threshold. Again, `H,w,criticality/tickets` are not actually evaluated in the two-arm world.
- `.ultramath/smww1ulor/m5/REPORT.md` and `lean/ArmSixteen.lean`: exact-family/sibling hash reconstruction, but the inactive arithmetic has no slack. `(5,5,5)` and all `(4,5,5)` placements stay feasible. A bare two-arm count is not a way forward.
- `.ultramath/smwvpsb38/m6/REPORT.md`: 239,662 accepted RUP clauses and 288,681 chained additions replay `s DERIVATION`, **not `s VERIFIED`**, because no empty clause occurs. The closest sibling's strengthened row stayed UNKNOWN.
- `.ultramath/smwvx4uzm/m8/REPORT.md`: same-profile transfer also produced no empty clause. Compact donor cores retain 161–162 source-only units. Dependency reduction with missing target geometry is required, rather than more accepted-clause accretion.
- Shell-job completion messages by themselves are not mathematical evidence; only the independently replayed DRAT logs certify leaves.

## Acceptance/verification status by swarm

### `smwvpsb38` (seven accepted)

m7 common critical pair; m3 one-critical reduction; m5 small-arm C4 constraint/encoder;
m2 pinned 16 one-spoke clone theorem; m8 certified 35-hole PARTIAL K58 model and local capped-fill UNSAT;
m4 exact residual/ticket framework; m6 negative sibling-transfer boundary.

### `smwvx4uzm` (eight accepted)

m6 exact reciprocal common-pair equivalence and parity-forced pinned arms;
m4 interface bound and exact U16 four-support centre vs explicit T counterexample;
m7 exact clone pair-colour interface and tight K33 limits;
m2 independent full template/guard/unit and mixed-interface audit;
m5 balanced residual return paths, root split, saturation and physical countermodels;
m1 exact full mixed two-arm cap 8;
m3 exact cross-support local and aggregate totals;
m8 checked negative same-profile transfer.

### `smww1ulor` (six accepted)

m1 exact deficiency/strict/activity identity (two documentation corrections checked);
m6 correct necessary-floor two-arm delimitation;
m2 five-way pins-only split and deficient-root builder;
m5 exact reconstruction and classification-free arm regularity/familyC;
m8 corrected root-local necessary-projection delimitation;
m7 compact shared reciprocal/inactive flags and exact C4-free support-shape encoding.

## What not to repeat

- Do **not** repeat root-only dumb CDCL sweeps, generic transfer accumulation, full labelled T/U mapping expansions, or the four inactive support-pattern leaves that all timed out.
- Do **not** accept a tiny unit-propagation UNSAT as progress without checking for accidental self-pair literals or colliding auxiliaries. Prior false UNSATs came from an invalid self-edge and a variable/pin collision and were correctly rejected.
- Do not claim all vertices are critical merely because three projected parts each have >=4; three parts summing to 12 yield degree 13.
- Do not rely on degree-only perfect-balance assumptions or disagreement-free generic C&C; each added strengthening must reproduce parent hashes and exact coverage hypotheses.
- Do not use raw case-ledger OPEN as a synonym for folded current OPEN. Raw totals and current release totals differ.
- Do not delete prior proof artifacts. Use only local scratch for new computations and include CNF/DRAT hashes in every receipt.

## Next useful obligations

1. Complete the four reciprocal frontier leaves only if cheap enough, with independently replayed DRAT. Otherwise preserve the exact partial frontier honestly.
2. Use marked-free gen-L4 for adaptive binary coverage on reciprocal+inactive 70-row behaviour only; it does **not** cover strict/mixed/deficient branches or other template kinds.
3. Produce genuinely global active/strict/small-arm coupling, not another necessary local support-floor projection.
4. If seeking full-row claim, account for the nondeficit-root premise and the deficient H≤31 case explicitly or prove the precise global root-routing that discharges it.
5. Compare the new measured C&C polarity policy against the unmodified controller. Keep it only if equal budgets give a reproducible reduction in work/coverage or new verified leaves.

## Update — supplied pentagon and four-row certificates audited

The statements above describe the state before the two newly supplied attachments.

1. **The reciprocal/common-pair root of row 0404 is now independently certified UNSAT.**
   The supplied pentagon certificate was replayed in full in 24.75 s: all seven finite
   pentagon refutations, the degree-counter proof, the core proof, the exact root,
   `n025`/`n026`/`n027`, and both native solver traces. The root hash is the same
   `aa23de81…` recorded above. Thus the old four-leaf residual frontier and further
   reciprocal C&C on this root are superseded; the root itself is closed. This is one
   reciprocal branch of one frozen row, not a full row/profile closure or a new bound.
   See `pentagon-n025-audit-2026-11-25/AUDIT.md` and its replay log. Do not apply the
   conclusion to active/inactive without a new colour/vertex map: their 57 flags are
   not the same nine degree premises used here.

2. **The four-row degree/ticket result remains conditional on missing proof archives.**
   All bundle hashes passed; its scope check reproduced 2,151/2,142 words and the
   claimed coverage, four conditional native capstones checked, and two fresh sample
   DRAT refutations (smallest grid and 66-entry `K15` blocker) were generated. The two
   certificate bundles `K58_degree_certificates_1.zip` and `_2.zip` containing the
   518 traces (1,861,878,149 bytes total) were not attached. Their complete replay and
   the inherited queue's certification are required before accepting `d_0(q)<=14` or
   the four reciprocal exclusions. The connectivity/common-critical-palette and Hall
   path/ticket arguments themselves are sound. See
   `four-row-ticket-audit-2026-11-25/AUDIT.md`.

3. **m3/d9's `Classified 15` certificate was rejected pending repair.** The documented
   independence filter is not implemented in any shipped Python file, final per-graph
   DRAT files were deleted rather than retained for independent replay, and its
   67,219-clause prose should read 67,894, matching the fresh registry rebuild. The
   `RealizesFamily` root-floor and 64-digit reciprocal-hash corrections were verified.
   `Classified 16` did pass a fresh full 71-second regeneration: all 388 terminal
   certificates replayed, with identical per-graph hashes and 72 = 12 U + 60 T.
   See `m3-classification-audit-2026-11-25/REVIEW.md`.
