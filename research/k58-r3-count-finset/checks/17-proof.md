# Proved theorem 17: exact clean proof sources

This is the complete Lean argument reviewed for the all-sender R3 goal,
including the non-vacuous physical mask, agreeing-atom valuations,
and the explicit auxiliary-guard vacuity audit. Sequential counter
soundness is not assumed; the count remains an explicit hypothesis.

## `lean/K58/CountedSenderReady.lean`

~~~lean
import K58.CounterNeighboursAudit2
import K58.ClassifiedBridge
import K58.SequentialCounter
import K58.PhysicalGuard

/-! Count-driven physical geometry at all fifteen retained senders.

`K58.R3Counter` decodes the exact counter inputs and constructs a genuine
physical neighbour finset.  `K58.EmittedBridge.hclass_classified` supplies the
literal-colour order-15/16 critical classification.  This module combines them:
no neighbour set `W`, its premises, or a separate `hclass` argument is needed.

The main results are the physical catalogue mask and its transport to any
valuation agreeing on the sixteen physical atoms.  Bare `ready` at
`realizedValuation` is retained below for continuity and is independently
shown in `PhysicalGuard` to be vacuous because the auxiliary counter guards
have the value `false` there.  None of this asserts `ChainReady`, a complete
exact-root/key bridge, a reverse guarded-counter soundness theorem, or a Ramsey
bound improvement. -/

open K58
open K58.SequentialCounter
open K58.SenderReady
open K58.SemanticAssembly
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

/-- Every audited emitted 41-of-14 count makes the corresponding emitted
support step ready at the physical valuation, using the actual imported
order-15/16 classification.  The four `W` hypotheses and extra `hclass` of the
former bridge are removed; root and sender host-coordinate identifications
remain explicit. -/
theorem emitted_sender_step_ready_of_emitted_count_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) := by
  rw [emittedCounterAtoms_eq k] at hcount
  exact emitted_sender_step_ready_of_counter_count G hG e p hp1 k q r hqr_ne hqr
    hq hzero hcount hclass_classified er hroot hcoord hb

/-- **Non-vacuous physical endpoint.** The actual emitted count determines a
catalogue mask, not merely the vacuous `ready` proposition at a guard-false
physical valuation.  The neighbour set comes from the audited input atoms and
the real classification is applied to its critical arm. -/
theorem exists_catalogue_mask_of_emitted_count_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val) :
    ∃ i : Fin 112, ∀ j : Fin 16,
      realizedValuation G e p (rowAtoms k j.val) = supportBit targetSupports i j.val := by
  rw [emittedCounterAtoms_eq k] at hcount
  obtain ⟨W, hW, hrW, hcard⟩ := exists_neighbour_finset_spec G e p hp1 k q r hq hzero hcount
  have hlo := deg_ge_fifteen_of_counter_count G e p hp1 k q r hqr_ne hqr hq hzero hcount
  obtain ⟨-, hhi, t, ht⟩ := sender_pinned_of_count_of_classification G hG q r hqr_ne hqr W hW hrW hcard
  have hdeg : deg G q 1 = 15 ∨ deg G q 1 = 16 := by omega
  exact emitted_mask_of_pinned G hG e p hp1 k q r hqr_ne hqr hq hdeg ht er hroot hcoord

/-- **Non-vacuous mask at an arbitrary valuation.** If `v` agrees with the
physical valuation on all sixteen genuine support atoms, then `v`'s support
vector is exactly one of the 112 emitted catalogue entries.  Unlike the bare
physical `.ready` proposition, this constrains genuine bits and is true even if
`v`'s auxiliary guard is true. -/
theorem catalogueVec_of_atom_agreement_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (v : Valuation)
    (hv : ∀ j < 16, v (rowAtoms k j) = realizedValuation G e p (rowAtoms k j)) :
    CatalogueVec (fun j => v (rowAtoms k j)) := by
  obtain ⟨i, hi⟩ := exists_catalogue_mask_of_emitted_count_classified G hG e p hp1 k q r
    hqr_ne hqr hq hzero hcount er hroot hcoord
  refine ⟨i, fun j hj => ?_⟩
  show v (rowAtoms k j) = catalogueBit i j
  rw [hv j hj]
  exact hi ⟨j, hj⟩

/-- **Non-vacuous emitted readiness.** Readiness is proved at every valuation
that agrees on the sixteen physical support atoms, not merely at the original
physical valuation whose auxiliary guard is false.  The physical count and
geometry remain hypotheses; sequential exactness of the emitted counter is not
silently inferred from agreement on those atoms. -/
theorem senderStep_ready_of_atom_agreement_classified
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val =
        (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k))
    (v : Valuation)
    (hv : ∀ j < 16, v (rowAtoms k j) = realizedValuation G e p (rowAtoms k j)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready v := by
  rw [sender_family_ready k hb]
  intro _
  exact catalogueVec_of_atom_agreement_classified G hG e p hp1 k q r hqr_ne hqr hq hzero
    hcount er hroot hcoord v hv

#print axioms K58.R3Counter.exists_catalogue_mask_of_emitted_count_classified
#print axioms K58.R3Counter.catalogueVec_of_atom_agreement_classified
#print axioms K58.R3Counter.senderStep_ready_of_atom_agreement_classified
#print axioms K58.R3Counter.emitted_sender_step_ready_of_emitted_count_classified

end K58.R3Counter

~~~

## `lean/K58/CounterNeighbours.lean`

~~~lean
/-
K58 R3 component: the audited 41-atom decoder for all fifteen guarded senders.

Swarm `smx0gue0b`, member m7, direction C.  Commit 5a5cef9.

WHAT THIS FILE DOES

`K58.EmittedBridge.emitted_sender_step_ready_of_count` derives the emitted
support readiness at a sender from an *assumed* finite set `W` of physical
colour-1 neighbours of the sender (`hW`, `hrW`, `hcard : 14 <= W.card`).  R3
asks for such a `W` to be *derived* from the emitted 41-of-14 counter, whose
semantics is `14 <= prefixCount (fun i => v (x i)) 41`.

The obstruction is that the counter's atoms are DIMACS host variables, not
physical vertices.  This file removes that obstruction for all fifteen senders
18..32, exactly and auditably:

* `emittedCounterListAll` transcribes the fifteen 41-atom input lists of the
  emitted `freshGuardedCounterStepAuto ... 41 14 ...` blocks of
  `K58.TargetSuffix.targetSuffixSteps` (parsed from the source by
  `decode_check.py`, not retyped by hand).
* `counter_list_decode` : all fifteen lists are *exactly*
  `j |-> hostVar (1+j) (18+k) one` for `j < 16` followed by
  `i |-> hostVar (18+k) (33+i) one` for `i < 25`.
* `counter_inputs_audit` : the variables at or below each counter's own
  `oldTop` that the emitted clause set actually reads are exactly those 41
  atoms.  So the decode is checked against the emitted clauses, not against a
  guess: the atom list is used to *rebuild* the clause family and the clause
  family is read back.
* `endpoint_*` : the 25+16 = 41 non-sender labels are `1..16 u 33..57`; none is
  the sender label `18+k` (nonloop), none is `0` (root, given `e 0 = r`), and
  none is an arm-1 label `17..32` -- the precise general form of
  `counter18_avoids_fin`, for every sender and not only sender 18.
* `exists_neighbour_finset` : from the emitted count at
  `realizedValuation G e p` and the two labelling facts `e (18+k) = q`,
  `e 0 = r`, it produces a genuine `Finset (Fin 58)` of physical colour-1
  neighbours of `q`, of cardinality exactly the counter count, excluding the
  root, with no duplicates and no diagonal.  The only physical input is that
  the sender/root emit labels are the physical sender/root; the only palette
  input is the gauge `p one = 1`.
* `deg_ge_fifteen_of_counter_count` and
  `emitted_sender_step_ready_of_counter_count` : the two consumers, i.e. the
  current bridge with `W`, `hW`, `hrW`, `hcard` replaced by the emitted count.

`e 0 = r` is not an extra mathematical restriction: it is a labelling
convention.  `exists_perm_with_zero_image` proves that any `e` with
`e (18+k) = q` can be replaced by one that also sends `0` to `r`.

No `sorry`, no `admit`, no `native_decide`, no new axiom.
-/
import K58.EmittedBridge
import Mathlib.Data.List.GetD

open K58
open K58.SenderReady
open K58.SemanticAssembly
open K58.SequentialCounter
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

/-! ## 1. The fifteen emitted 41-atom counter inputs, transcribed -/

/-- The emitted input atoms of the fifteen arm-1 counters, row by row for
senders `18 .. 32`.  Extracted from the `freshGuardedCounterStepAuto ... 41 14`
blocks of `K58.TargetSuffix.targetSuffixSteps` by `decode_check.py`. -/
def emittedCounterListAll : List (List Nat) := [
    [294, 514, 730, 942, 1150, 1354, 1554, 1750, 1942, 2130, 2314, 2494, 2670, 2842, 3010, 3174, 3550, 3554, 3558, 3562, 3566, 3570, 3574, 3578, 3582, 3586, 3590, 3594, 3598, 3602, 3606, 3610, 3614, 3618, 3622, 3626, 3630, 3634, 3638, 3642, 3646],
    [298, 518, 734, 946, 1154, 1358, 1558, 1754, 1946, 2134, 2318, 2498, 2674, 2846, 3014, 3178, 3702, 3706, 3710, 3714, 3718, 3722, 3726, 3730, 3734, 3738, 3742, 3746, 3750, 3754, 3758, 3762, 3766, 3770, 3774, 3778, 3782, 3786, 3790, 3794, 3798],
    [302, 522, 738, 950, 1158, 1362, 1562, 1758, 1950, 2138, 2322, 2502, 2678, 2850, 3018, 3182, 3850, 3854, 3858, 3862, 3866, 3870, 3874, 3878, 3882, 3886, 3890, 3894, 3898, 3902, 3906, 3910, 3914, 3918, 3922, 3926, 3930, 3934, 3938, 3942, 3946],
    [306, 526, 742, 954, 1162, 1366, 1566, 1762, 1954, 2142, 2326, 2506, 2682, 2854, 3022, 3186, 3994, 3998, 4002, 4006, 4010, 4014, 4018, 4022, 4026, 4030, 4034, 4038, 4042, 4046, 4050, 4054, 4058, 4062, 4066, 4070, 4074, 4078, 4082, 4086, 4090],
    [310, 530, 746, 958, 1166, 1370, 1570, 1766, 1958, 2146, 2330, 2510, 2686, 2858, 3026, 3190, 4134, 4138, 4142, 4146, 4150, 4154, 4158, 4162, 4166, 4170, 4174, 4178, 4182, 4186, 4190, 4194, 4198, 4202, 4206, 4210, 4214, 4218, 4222, 4226, 4230],
    [314, 534, 750, 962, 1170, 1374, 1574, 1770, 1962, 2150, 2334, 2514, 2690, 2862, 3030, 3194, 4270, 4274, 4278, 4282, 4286, 4290, 4294, 4298, 4302, 4306, 4310, 4314, 4318, 4322, 4326, 4330, 4334, 4338, 4342, 4346, 4350, 4354, 4358, 4362, 4366],
    [318, 538, 754, 966, 1174, 1378, 1578, 1774, 1966, 2154, 2338, 2518, 2694, 2866, 3034, 3198, 4402, 4406, 4410, 4414, 4418, 4422, 4426, 4430, 4434, 4438, 4442, 4446, 4450, 4454, 4458, 4462, 4466, 4470, 4474, 4478, 4482, 4486, 4490, 4494, 4498],
    [322, 542, 758, 970, 1178, 1382, 1582, 1778, 1970, 2158, 2342, 2522, 2698, 2870, 3038, 3202, 4530, 4534, 4538, 4542, 4546, 4550, 4554, 4558, 4562, 4566, 4570, 4574, 4578, 4582, 4586, 4590, 4594, 4598, 4602, 4606, 4610, 4614, 4618, 4622, 4626],
    [326, 546, 762, 974, 1182, 1386, 1586, 1782, 1974, 2162, 2346, 2526, 2702, 2874, 3042, 3206, 4654, 4658, 4662, 4666, 4670, 4674, 4678, 4682, 4686, 4690, 4694, 4698, 4702, 4706, 4710, 4714, 4718, 4722, 4726, 4730, 4734, 4738, 4742, 4746, 4750],
    [330, 550, 766, 978, 1186, 1390, 1590, 1786, 1978, 2166, 2350, 2530, 2706, 2878, 3046, 3210, 4774, 4778, 4782, 4786, 4790, 4794, 4798, 4802, 4806, 4810, 4814, 4818, 4822, 4826, 4830, 4834, 4838, 4842, 4846, 4850, 4854, 4858, 4862, 4866, 4870],
    [334, 554, 770, 982, 1190, 1394, 1594, 1790, 1982, 2170, 2354, 2534, 2710, 2882, 3050, 3214, 4890, 4894, 4898, 4902, 4906, 4910, 4914, 4918, 4922, 4926, 4930, 4934, 4938, 4942, 4946, 4950, 4954, 4958, 4962, 4966, 4970, 4974, 4978, 4982, 4986],
    [338, 558, 774, 986, 1194, 1398, 1598, 1794, 1986, 2174, 2358, 2538, 2714, 2886, 3054, 3218, 5002, 5006, 5010, 5014, 5018, 5022, 5026, 5030, 5034, 5038, 5042, 5046, 5050, 5054, 5058, 5062, 5066, 5070, 5074, 5078, 5082, 5086, 5090, 5094, 5098],
    [342, 562, 778, 990, 1198, 1402, 1602, 1798, 1990, 2178, 2362, 2542, 2718, 2890, 3058, 3222, 5110, 5114, 5118, 5122, 5126, 5130, 5134, 5138, 5142, 5146, 5150, 5154, 5158, 5162, 5166, 5170, 5174, 5178, 5182, 5186, 5190, 5194, 5198, 5202, 5206],
    [346, 566, 782, 994, 1202, 1406, 1606, 1802, 1994, 2182, 2366, 2546, 2722, 2894, 3062, 3226, 5214, 5218, 5222, 5226, 5230, 5234, 5238, 5242, 5246, 5250, 5254, 5258, 5262, 5266, 5270, 5274, 5278, 5282, 5286, 5290, 5294, 5298, 5302, 5306, 5310],
    [350, 570, 786, 998, 1206, 1410, 1610, 1806, 1998, 2186, 2370, 2550, 2726, 2898, 3066, 3230, 5314, 5318, 5322, 5326, 5330, 5334, 5338, 5342, 5346, 5350, 5354, 5358, 5362, 5366, 5370, 5374, 5378, 5382, 5386, 5390, 5394, 5398, 5402, 5406, 5410]
]


/-- Row `k`: the 41 emitted input atoms of the counter that produces the guard
of sender `18 + k`. -/
def emittedCounterList (k : Fin 15) : List Nat := emittedCounterListAll.get k

/-- The emitted counter of sender `18 + k` read as an input-variable map, i.e.
exactly the `x` of the emitted `freshGuardedCounterStep`. -/
def emittedCounterAtoms (k : Fin 15) : Nat → Nat := listAtoms (emittedCounterList k)

/-- The emitted counter clause set of sender `18 + k`, recovered from the
emitted suffix by its allocation `(oldTop, newTop)`. -/
def counterCNF (k : Fin 15) : CNF :=
  (targetSuffixSteps.filter
    (fun s => s.newTop = rowOldTop k && s.oldTop = rowOldTop k - 379)).flatMap
    (fun s => s.clauses)

/-! ## 2. The decoded form of the same 41 atoms -/

/-- The emit label of the sender of row `k`. -/
def senderFin (k : Fin 15) : Fin 58 := ⟨18 + k.val, by omega⟩

/-- Emit label `0`, the root label used by the physical coordinate map. -/
def zeroFin : Fin 58 := ⟨0, by omega⟩

/-- The non-sender endpoint of slot `i < 41`: the root arm-0 labels `1 .. 16`
for the first sixteen slots, the far labels `33 .. 57` for the other
twenty-five.  Note the label set does not depend on the sender. -/
def endpoint (i : Nat) : Nat := if i < 16 then 1 + i else 33 + (i - 16)

theorem endpoint_lt (i : Nat) (hi : i < 41) : endpoint i < 58 := by
  unfold endpoint; split <;> omega

/-- Slot `i` as an emit label. -/
def endpointFin (i : Fin 41) : Fin 58 := ⟨endpoint i.val, endpoint_lt i.val i.isLt⟩

/-- The decoded atom of slot `i` of sender `18 + k`: the colour-1 host edge
between the endpoint and the sender.  Defaults to `0` outside the 41 slots,
which is the emitted default of `listAtoms` as well. -/
def counterAtoms (k : Fin 15) (i : Nat) : Nat :=
  if i < 41 then hostVar (endpoint i) (18 + k.val) one else 0

theorem counterAtoms_of_lt (k : Fin 15) (i : Nat) (hi : i < 41) :
    counterAtoms k i = hostVar (endpoint i) (18 + k.val) one := by
  simp only [counterAtoms, if_pos hi]

theorem counterAtoms_of_ge (k : Fin 15) (i : Nat) (hi : 41 ≤ i) :
    counterAtoms k i = 0 := by
  simp only [counterAtoms, if_neg (Nat.not_lt.mpr hi)]

/-- The decoded 41-atom list of sender `18 + k`. -/
def counterList (k : Fin 15) : List Nat := (List.range 41).map (counterAtoms k)

/-- `getD` of a mapped range is the map itself, with the emitted default `0`
matching the decoder's own default outside the 41 slots. -/
theorem getD_map_range {n : Nat} (f : Nat → Nat) (hf : ∀ i, n ≤ i → f i = 0) (i : Nat) :
    ((List.range n).map f).getD i 0 = f i := by
  by_cases hi : i < n
  · rw [List.getD_eq_getElem (l := (List.range n).map f) (d := 0) (n := i)
      (by simpa using hi), List.getElem_map, List.getElem_range]
  · rw [List.getD_eq_default (l := (List.range n).map f) (d := 0) (n := i)
      (by simpa using hi), hf i (by omega)]

/-! ## 3. The decode, checked against the transcribed emitted lists -/

set_option maxRecDepth 100000 in
/-- **Atom decode, all fifteen senders.**  The fifteen emitted 41-atom lists are
exactly the decoded host-variable edges: the sixteen edges `(1+j, 18+k)` in
colour 1 followed by the twenty-five edges `(18+k, 33+i)` in colour 1. -/
theorem emittedCounterList_decode (k : Fin 15) :
    emittedCounterList k = counterList k := by
  fin_cases k <;> decide

/-- The emitted counter's input map is the decoded map. -/
theorem emittedCounterAtoms_eq (k : Fin 15) : emittedCounterAtoms k = counterAtoms k := by
  funext i
  rw [emittedCounterAtoms, emittedCounterList_decode k]
  exact getD_map_range (counterAtoms k) (counterAtoms_of_ge k) i

/-! ## 4. The 41 non-sender labels: nonloop, not the root, not arm 1 -/

theorem endpoint_injective_on (a b : Fin 41) (h : endpoint a.val = endpoint b.val) :
    a = b := by
  have ha := a.isLt
  have hb := b.isLt
  unfold endpoint at h
  split at h <;> split at h <;> omega

theorem endpointFin_injective : Function.Injective endpointFin := by
  intro a b h
  refine endpoint_injective_on a b ?_
  have := congrArg Fin.val h
  simpa [endpointFin] using this

/-- **No emitted edge is a loop.**  The endpoint label is never the sender
label `18 + k`. -/
theorem endpointFin_ne_sender (k : Fin 15) (i : Fin 41) :
    endpointFin i ≠ senderFin k := by
  intro h
  have hv : endpoint i.val = 18 + k.val := by
    have := congrArg Fin.val h
    simpa [endpointFin, senderFin] using this
  have hi := i.isLt
  have hk := k.isLt
  unfold endpoint at hv
  split at hv <;> omega

/-- **The root is not an endpoint**: label `0` is outside `1..16 u 33..57`. -/
theorem endpointFin_ne_zero (i : Fin 41) : endpointFin i ≠ zeroFin := by
  intro h
  have hv : endpoint i.val = 0 := by
    have := congrArg Fin.val h
    simpa [endpointFin, zeroFin] using this
  have hi := i.isLt
  unfold endpoint at hv
  split at hv <;> omega

/-- **No endpoint is an arm-1 sibling** `17 .. 32`: the general form of
`K58.EmittedBridge.counter18_avoids_fin` for every sender. -/
theorem endpointFin_ne_arm1 (i : Fin 41) (s : Fin 16) :
    endpointFin i ≠ (⟨17 + s.val, by omega⟩ : Fin 58) := by
  intro h
  have hv : endpoint i.val = 17 + s.val := by
    have := congrArg Fin.val h
    simpa [endpointFin] using this
  have hi := i.isLt
  have hs := s.isLt
  unfold endpoint at hv
  split at hv <;> omega

/-- The full label range of the 41 endpoints. -/
theorem endpoint_range (i : Fin 41) :
    (1 ≤ endpoint i.val ∧ endpoint i.val ≤ 16) ∨
      (33 ≤ endpoint i.val ∧ endpoint i.val ≤ 57) := by
  have hi := i.isLt
  unfold endpoint
  split <;> omega

/-- The endpoint of a slot is not the endpoint of another slot: the 41 decoded
atoms are 41 distinct physical edges. -/
theorem endpointFin_ne_of_ne {a b : Fin 41} (h : a ≠ b) : endpointFin a ≠ endpointFin b :=
  fun he => h (endpointFin_injective he)

/-! ## 5. The physical value of each decoded atom -/

theorem counterAtoms_eq_hostVar (k : Fin 15) (i : Fin 41) :
    counterAtoms k i.val = hostVar (endpointFin i) (senderFin k) one := by
  rw [counterAtoms_of_lt k i.val i.isLt]
  rfl

/-- **The physical meaning of a decoded counter atom.**  Under the repository's
`realizedValuation` the atom of slot `i` is the statement "the edge from the
endpoint `e (endpoint i)` to the physical sender `e (18+k)` has physical colour
`p 1`". -/
theorem eval_counterAtoms (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (p : Equiv.Perm (Fin 4)) (k : Fin 15) (i : Fin 41) :
    realizedValuation G e p (counterAtoms k i.val) =
      decide (G.col (e (endpointFin i)) (e (senderFin k)) = p one) := by
  rw [counterAtoms_eq_hostVar]
  exact realizedValuation_hostVar_unsorted G e p (endpointFin_ne_sender k i) one

/-- A true atom is a physical colour-1 edge out of the sender. -/
theorem colour_one_of_true (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1) (k : Fin 15) (i : Fin 41)
    (h : realizedValuation G e p (counterAtoms k i.val) = true) :
    G.col (e (senderFin k)) (e (endpointFin i)) = 1 := by
  rw [eval_counterAtoms] at h
  have h' := of_decide_eq_true h
  rw [hp1] at h'
  exact (G.symm (e (senderFin k)) (e (endpointFin i))).trans h'

/-! ## 6. `prefixCount` at the full length is a cardinality -/

theorem prefixCount_eq_sum (b : Nat → Bool) (n : Nat) :
    prefixCount b n = ∑ i : Fin n, if b i.val = true then 1 else 0 := by
  induction n with
  | zero => simp [prefixCount]
  | succ n ih =>
    rw [prefixCount, ih, Fin.sum_univ_castSucc]
    by_cases h : b n = true <;> simp [h]

/-- The emitted counter's own semantics, as a finite cardinality: the number of
true atoms among the 41. -/
theorem prefixCount_eq_card (b : Nat → Bool) (n : Nat) :
    prefixCount b n = (Finset.univ.filter (fun i : Fin n => b i.val = true)).card := by
  rw [prefixCount_eq_sum, Finset.card_eq_sum_ones, Finset.sum_filter]

/-! ## 7. R3: a genuine Finset of physical colour-1 neighbours -/

/-- **R3 for every guarded sender.**  Let `G` be a physical four-colouring of
`K58`, `e` the host permutation with `e (18+k) = q` and `e 0 = r`, and `p` the
palette permutation with gauge `p 1 = 1`.  If the emitted 41-of-14 counter of
sender `18+k` holds at the physical valuation, then the true atoms give a
genuine finite set of physical colour-1 neighbours of `q`: every element is
adjacent to `q` in colour 1, `q` itself is excluded (no loops), the root `r` is
excluded, no element is counted twice (the 41 edges are distinct), and the
cardinality is exactly the counter count. -/
theorem exists_neighbour_finset (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1) (k : Fin 15) (q r : Fin 58)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (counterAtoms k i)) 41) :
    ∃ W : Finset (Fin 58),
      W.card = prefixCount (fun i => realizedValuation G e p (counterAtoms k i)) 41 ∧
      14 ≤ W.card ∧
      (∀ x ∈ W, x ≠ q ∧ G.col q x = 1) ∧
      r ∉ W ∧
      (∀ i : Fin 41, realizedValuation G e p (counterAtoms k i.val) = true →
        e (endpointFin i) ∈ W) := by
  classical
  set S : Finset (Fin 41) :=
    Finset.univ.filter
      (fun i : Fin 41 => realizedValuation G e p (counterAtoms k i.val) = true) with hS
  set W : Finset (Fin 58) := S.image (fun i : Fin 41 => e (endpointFin i)) with hWdef
  have hinj : Function.Injective (fun i : Fin 41 => e (endpointFin i)) :=
    fun a b h => endpointFin_injective (e.injective h)
  have hWcard : W.card = S.card := Finset.card_image_of_injective S hinj
  have hScard : S.card =
      prefixCount (fun i => realizedValuation G e p (counterAtoms k i)) 41 := by
    rw [hS, prefixCount_eq_card]
  refine ⟨W, ?_, ?_, ?_, ?_, ?_⟩
  · rw [hWcard, hScard]
  · rw [hWcard, hScard]
    exact hcount
  · intro x hx
    rw [hWdef] at hx
    obtain ⟨i, hi, rfl⟩ := Finset.mem_image.mp hx
    have htrue : realizedValuation G e p (counterAtoms k i.val) = true :=
      (Finset.mem_filter.mp hi).2
    refine ⟨?_, ?_⟩
    · intro h
      have h2 : e (endpointFin i) = e (senderFin k) := by rw [h, hq]
      exact endpointFin_ne_sender k i (e.injective h2)
    · rw [← hq]
      exact colour_one_of_true G e p hp1 k i htrue
  · intro hr
    rw [hWdef] at hr
    obtain ⟨i, -, hi⟩ := Finset.mem_image.mp hr
    have h2 : e zeroFin = e (endpointFin i) := by rw [hzero, hi]
    exact endpointFin_ne_zero i (e.injective h2).symm
  · intro i hi
    rw [hWdef]
    exact Finset.mem_image.mpr
      ⟨i, Finset.mem_filter.mpr ⟨Finset.mem_univ _, hi⟩, rfl⟩

/-- **R3 in the shape the current bridge consumes.**  Same hypotheses; the
conclusion is the triple `(W, hW, hrW, hcard)` that
`K58.EmittedBridge.emitted_sender_step_ready_of_count` assumes. -/
theorem exists_neighbour_finset_spec (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58))
    (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1) (k : Fin 15) (q r : Fin 58)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (counterAtoms k i)) 41) :
    ∃ W : Finset (Fin 58), (∀ x ∈ W, x ≠ q ∧ G.col q x = 1) ∧ r ∉ W ∧ 14 ≤ W.card := by
  obtain ⟨W, -, hcard, hW, hrW, -⟩ := exists_neighbour_finset G e p hp1 k q r hq hzero hcount
  exact ⟨W, hW, hrW, hcard⟩

/-- The counter count at the emitted atoms (the objects that occur in
`K58.TargetSuffix.targetSuffixSteps`) is the same count. -/
theorem exists_neighbour_finset_emitted (G : EdgeCol (Fin 58) 4)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (emittedCounterAtoms k i)) 41) :
    ∃ W : Finset (Fin 58),
      (∀ x ∈ W, x ≠ q ∧ G.col q x = 1) ∧ r ∉ W ∧ 14 ≤ W.card := by
  have hfun : (fun i => realizedValuation G e p (emittedCounterAtoms k i)) =
      (fun i => realizedValuation G e p (counterAtoms k i)) := by
    funext i
    rw [emittedCounterAtoms_eq]
  have hcount' : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (counterAtoms k i)) 41 := by
    rw [← hfun]
    exact hcount
  exact exists_neighbour_finset_spec G e p hp1 k q r hq hzero hcount'

/-! ## 8. Consumers: the degree bound and the current bridge -/

/-- **The emitted counter forces the sender's colour-1 degree up to 15.**  This
is `K58.EmittedBridge.deg_ge_of_counted` with its set `W` derived rather than
assumed. -/
theorem deg_ge_fifteen_of_counter_count (G : EdgeCol (Fin 58) 4)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (counterAtoms k i)) 41) :
    15 ≤ deg G q 1 := by
  obtain ⟨W, hW, hrW, hcard⟩ :=
    exists_neighbour_finset_spec G e p hp1 k q r hq hzero hcount
  exact EmittedBridge.deg_ge_of_counted G q r hqr_ne hqr W hW hrW hcard

/-- **The current emitted bridge with the finite set derived.**  Compared with
`K58.EmittedBridge.emitted_sender_step_ready_of_count`, the parameters
`W`, `hW`, `hrW` and `hcard` are gone; in their place are the emitted counter
count `hcount` and the labelling fact `e 0 = r`.  Everything else -- the
triangle-free physical colouring, the palette gauge, the sender/root label
identifications, the order-15/16 classification, the root arm-0 pinning in the
emitted coordinates, the coherence `hcoord` and the `VarsBelow` bound -- is
carried unchanged. -/
theorem emitted_sender_step_ready_of_counter_count (G : EdgeCol (Fin 58) 4)
    (hG : TriangleFree G) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (hp1 : p one = 1) (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r)
    (hqr : G.col q r = 1) (hq : e (senderFin k) = q) (hzero : e zeroFin = r)
    (hcount : 14 ≤ prefixCount
      (fun i => realizedValuation G e p (counterAtoms k i)) 41)
    (hclass : ∀ n : ℕ, n = 15 ∨ n = 16 → ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j))
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) := by
  obtain ⟨W, hW, hrW, hcard⟩ :=
    exists_neighbour_finset_spec G e p hp1 k q r hq hzero hcount
  exact EmittedBridge.emitted_sender_step_ready_of_count G hG e p hp1 k q r hqr_ne hqr
    hq W hW hrW hcard hclass er hroot hcoord hb

/-- **The labelling `e 0 = r` is free.**  Given any host permutation `e` sending
the sender label `18+k` to `q`, and any root `r ≠ q`, there is a host
permutation that also sends label `0` to `r`.  So the extra labelling hypothesis
of the theorems above is never a restriction on the physical configuration. -/
theorem exists_perm_with_zero_image (e : Equiv.Perm (Fin 58)) (k : Fin 15)
    (q r : Fin 58) (hq : e (senderFin k) = q) (hqr : q ≠ r) :
    ∃ e' : Equiv.Perm (Fin 58), e' (senderFin k) = q ∧ e' zeroFin = r := by
  classical
  have h0ne : e zeroFin ≠ e (senderFin k) := by
    intro h
    have h0 : zeroFin = senderFin k := e.injective h
    have hv : (0 : Nat) = 18 + k.val := by
      have := congrArg Fin.val h0
      simpa [zeroFin, senderFin] using this
    have hk := k.isLt
    omega
  have hqe : q ≠ e zeroFin := by
    rw [hq] at h0ne
    exact fun h => h0ne h.symm
  refine ⟨e.trans (Equiv.swap (e zeroFin) r), ?_, ?_⟩
  · rw [Equiv.trans_apply, hq, Equiv.swap_apply_def, if_neg hqe, if_neg hqr]
  · rw [Equiv.trans_apply, Equiv.swap_apply_def, if_pos rfl]

/-! ## 9. Axiom audit -/

#print axioms K58.R3Counter.getD_map_range
#print axioms K58.R3Counter.emittedCounterList_decode
#print axioms K58.R3Counter.emittedCounterAtoms_eq
#print axioms K58.R3Counter.endpointFin_injective
#print axioms K58.R3Counter.endpointFin_ne_sender
#print axioms K58.R3Counter.endpointFin_ne_zero
#print axioms K58.R3Counter.endpointFin_ne_arm1
#print axioms K58.R3Counter.endpoint_range
#print axioms K58.R3Counter.eval_counterAtoms
#print axioms K58.R3Counter.colour_one_of_true
#print axioms K58.R3Counter.prefixCount_eq_sum
#print axioms K58.R3Counter.prefixCount_eq_card
#print axioms K58.R3Counter.exists_neighbour_finset
#print axioms K58.R3Counter.exists_neighbour_finset_spec
#print axioms K58.R3Counter.exists_neighbour_finset_emitted
#print axioms K58.R3Counter.deg_ge_fifteen_of_counter_count
#print axioms K58.R3Counter.emitted_sender_step_ready_of_counter_count
#print axioms K58.R3Counter.exists_perm_with_zero_image

end K58.R3Counter

~~~

## `lean/K58/CounterNeighboursAudit0.lean`

~~~lean
/-
K58 R3, direction C (swarm smx0gue0b, member m7): clause-level audit of the
41-atom decoder, senders 18..32.

`K58.R3Counter.counterAtoms` reads the emitted counter's 41 atoms as the
colour-1 host edges `(1+j, 18+k)` (j<16) and `(18+k, 33+i)` (i<25).  Here that
reading is checked against the emitted clause set itself: the variables at or
below each counter's own `oldTop` occurring in the emitted
`freshGuardedCounterStepAuto ... 41 14 ...` clauses are exactly those 41 atoms.

Each `decide` is a full kernel re-evaluation of one emitted counter CNF
(743 clauses, 2593 literals), ~15 s and ~4.5 GB peak, so the fifteen are split
into three files to keep one elaboration cheap.  No sorry, no native_decide,
no new axiom.
-/
import K58.CounterNeighbours

open K58
open K58.SenderReady
open K58.SemanticAssembly
open K58.SequentialCounter
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `18`: the clauses read exactly the decoded atoms. -/
theorem audit_0 :
    inputAtomsOf (counterCNF ⟨0, by decide⟩) (rowOldTop ⟨0, by decide⟩ - 379) =
      (counterList ⟨0, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `19`: the clauses read exactly the decoded atoms. -/
theorem audit_1 :
    inputAtomsOf (counterCNF ⟨1, by decide⟩) (rowOldTop ⟨1, by decide⟩ - 379) =
      (counterList ⟨1, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `20`: the clauses read exactly the decoded atoms. -/
theorem audit_2 :
    inputAtomsOf (counterCNF ⟨2, by decide⟩) (rowOldTop ⟨2, by decide⟩ - 379) =
      (counterList ⟨2, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `21`: the clauses read exactly the decoded atoms. -/
theorem audit_3 :
    inputAtomsOf (counterCNF ⟨3, by decide⟩) (rowOldTop ⟨3, by decide⟩ - 379) =
      (counterList ⟨3, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `22`: the clauses read exactly the decoded atoms. -/
theorem audit_4 :
    inputAtomsOf (counterCNF ⟨4, by decide⟩) (rowOldTop ⟨4, by decide⟩ - 379) =
      (counterList ⟨4, by decide⟩).insertionSort (· ≤ ·) := by
  decide

end K58.R3Counter

~~~

## `lean/K58/CounterNeighboursAudit1.lean`

~~~lean
/-
K58 R3, direction C (swarm smx0gue0b, member m7): clause-level audit of the
41-atom decoder, senders 18..32.

`K58.R3Counter.counterAtoms` reads the emitted counter's 41 atoms as the
colour-1 host edges `(1+j, 18+k)` (j<16) and `(18+k, 33+i)` (i<25).  Here that
reading is checked against the emitted clause set itself: the variables at or
below each counter's own `oldTop` occurring in the emitted
`freshGuardedCounterStepAuto ... 41 14 ...` clauses are exactly those 41 atoms.

Each `decide` is a full kernel re-evaluation of one emitted counter CNF
(743 clauses, 2593 literals), ~15 s and ~4.5 GB peak, so the fifteen are split
into three files to keep one elaboration cheap.  No sorry, no native_decide,
no new axiom.
-/
import K58.CounterNeighboursAudit0

open K58
open K58.SenderReady
open K58.SemanticAssembly
open K58.SequentialCounter
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `23`: the clauses read exactly the decoded atoms. -/
theorem audit_5 :
    inputAtomsOf (counterCNF ⟨5, by decide⟩) (rowOldTop ⟨5, by decide⟩ - 379) =
      (counterList ⟨5, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `24`: the clauses read exactly the decoded atoms. -/
theorem audit_6 :
    inputAtomsOf (counterCNF ⟨6, by decide⟩) (rowOldTop ⟨6, by decide⟩ - 379) =
      (counterList ⟨6, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `25`: the clauses read exactly the decoded atoms. -/
theorem audit_7 :
    inputAtomsOf (counterCNF ⟨7, by decide⟩) (rowOldTop ⟨7, by decide⟩ - 379) =
      (counterList ⟨7, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `26`: the clauses read exactly the decoded atoms. -/
theorem audit_8 :
    inputAtomsOf (counterCNF ⟨8, by decide⟩) (rowOldTop ⟨8, by decide⟩ - 379) =
      (counterList ⟨8, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `27`: the clauses read exactly the decoded atoms. -/
theorem audit_9 :
    inputAtomsOf (counterCNF ⟨9, by decide⟩) (rowOldTop ⟨9, by decide⟩ - 379) =
      (counterList ⟨9, by decide⟩).insertionSort (· ≤ ·) := by
  decide

end K58.R3Counter

~~~

## `lean/K58/CounterNeighboursAudit2.lean`

~~~lean
/-
K58 R3, direction C (swarm smx0gue0b, member m7): clause-level audit of the
41-atom decoder, senders 18..32.

`K58.R3Counter.counterAtoms` reads the emitted counter's 41 atoms as the
colour-1 host edges `(1+j, 18+k)` (j<16) and `(18+k, 33+i)` (i<25).  Here that
reading is checked against the emitted clause set itself: the variables at or
below each counter's own `oldTop` occurring in the emitted
`freshGuardedCounterStepAuto ... 41 14 ...` clauses are exactly those 41 atoms.

Each `decide` is a full kernel re-evaluation of one emitted counter CNF
(743 clauses, 2593 literals), ~15 s and ~4.5 GB peak, so the fifteen are split
into three files to keep one elaboration cheap.  No sorry, no native_decide,
no new axiom.
-/
import K58.CounterNeighboursAudit1

open K58
open K58.SenderReady
open K58.SemanticAssembly
open K58.SequentialCounter
open K58.EmittedBridge

set_option autoImplicit false

namespace K58.R3Counter

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `28`: the clauses read exactly the decoded atoms. -/
theorem audit_10 :
    inputAtomsOf (counterCNF ⟨10, by decide⟩) (rowOldTop ⟨10, by decide⟩ - 379) =
      (counterList ⟨10, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `29`: the clauses read exactly the decoded atoms. -/
theorem audit_11 :
    inputAtomsOf (counterCNF ⟨11, by decide⟩) (rowOldTop ⟨11, by decide⟩ - 379) =
      (counterList ⟨11, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `30`: the clauses read exactly the decoded atoms. -/
theorem audit_12 :
    inputAtomsOf (counterCNF ⟨12, by decide⟩) (rowOldTop ⟨12, by decide⟩ - 379) =
      (counterList ⟨12, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `31`: the clauses read exactly the decoded atoms. -/
theorem audit_13 :
    inputAtomsOf (counterCNF ⟨13, by decide⟩) (rowOldTop ⟨13, by decide⟩ - 379) =
      (counterList ⟨13, by decide⟩).insertionSort (· ≤ ·) := by
  decide


set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- Emitted counter of sender `32`: the clauses read exactly the decoded atoms. -/
theorem audit_14 :
    inputAtomsOf (counterCNF ⟨14, by decide⟩) (rowOldTop ⟨14, by decide⟩ - 379) =
      (counterList ⟨14, by decide⟩).insertionSort (· ≤ ·) := by
  decide

/-! ## The audit for all fifteen senders -/

/-- **Clause-level audit of the decoder.**  For every sender `18+k` (`k : Fin 15`)
the emitted 41-of-14 counter clause set reads exactly the decoded forty-one
atoms at or below its own `oldTop`. -/
theorem counter_inputs_audit (k : Fin 15) :
    inputAtomsOf (counterCNF k) (rowOldTop k - 379) =
      (counterList k).insertionSort (· ≤ ·) := by
  fin_cases k
  · exact audit_0
  · exact audit_1
  · exact audit_2
  · exact audit_3
  · exact audit_4
  · exact audit_5
  · exact audit_6
  · exact audit_7
  · exact audit_8
  · exact audit_9
  · exact audit_10
  · exact audit_11
  · exact audit_12
  · exact audit_13
  · exact audit_14

#print axioms K58.R3Counter.counter_inputs_audit

end K58.R3Counter

~~~

## `lean/K58/ClassifiedBridge.lean`

~~~lean
/- Kernel-checked literal-colour critical-template classification.

Adapted from m4 / swarm smx0gue0b / direction d5.

The `hclass` hypothesis of `sender_pinned_of_count` and of
`emitted_sender_step_ready_of_count` is *proved*, not assumed, from
`K58.classified_15` / `K58.classified_16` (the pinned R4333Lean catalogue
completeness results) plus the two template palette-symmetry theorems.
It remains intentionally separate from the physical count-to-neighbour step.
-/
import K58.EmittedBridge
import K58.Classification
import K58.Palette

set_option autoImplicit false

namespace K58.EmittedBridge

open K58
open K58.SenderReady
open K58.SemanticAssembly

/-- Colour-permutation elimination: `Classified n` (template up to vertex *and
colour* relabelling) plus colour symmetry of the template gives the template up
to vertex relabelling alone.  `K58.Marking.named_of_palette` is the private
version of this argument; this one is public and stated for reuse. -/
theorem named_of_classified {n : ℕ} (hc : Classified n)
    (hp : ∀ t (p : Equiv.Perm (Fin 3)), ∃ e : Equiv.Perm (Fin n),
      ∀ i j, i ≠ j → (template n t).col (e i) (e j) = p ((template n t).col i j)) :
    ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j) := by
  intro C hC
  obtain ⟨t, v, p, hv⟩ := hc C hC
  obtain ⟨e, he⟩ := hp t p
  exact ⟨t, v.trans e, fun i j hij => (hv i j hij).trans (he _ _ (v.injective.ne hij)).symm⟩

/-- Order 15 in literal host colours. -/
theorem named_15 :
    ∀ C : EdgeCol (Fin 15) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin 15), ∀ i j, i ≠ j →
        C.col i j = (template 15 t).col (e i) (e j) :=
  named_of_classified classified_15 palette_15

/-- Order 16 in literal host colours. -/
theorem named_16 :
    ∀ C : EdgeCol (Fin 16) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin 16), ∀ i j, i ≠ j →
        C.col i j = (template 16 t).col (e i) (e j) :=
  named_of_classified classified_16 (fun t p => by
    obtain ⟨e, -, he⟩ := palette_16_fixing t p 0
    exact ⟨e, he⟩)

/-- **The `hclass` hypothesis of the bridge, discharged.**  Type copied verbatim
from the source of `sender_pinned_of_count`. -/
theorem hclass_classified :
    ∀ n : ℕ, n = 15 ∨ n = 16 → ∀ C : EdgeCol (Fin n) 3, TriangleFree C →
      ∃ t : Bool, ∃ e : Equiv.Perm (Fin n), ∀ i j, i ≠ j →
        C.col i j = (template n t).col (e i) (e j) := by
  intro n hn
  rcases hn with rfl | rfl
  · exact named_15
  · exact named_16

/-- `sender_pinned_of_count` without the classification hypothesis. -/
theorem sender_pinned_of_count_of_classification (G : EdgeCol (Fin 58) 4)
    (hG : TriangleFree G) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (W : Finset (Fin 58)) (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1) (hrW : r ∉ W)
    (hcard : 14 ≤ W.card) :
    Sends G q r ∧ deg G q 1 ≤ 16 ∧ ∃ t : Bool, PinnedArm G q 1 (deg G q 1) t :=
  sender_pinned_of_count G hG q r hqr_ne hqr W hW hrW hcard hclass_classified

/-- `emitted_sender_step_ready_of_count` without the classification hypothesis:
same statement, one argument fewer. -/
theorem emitted_sender_step_ready_of_count_of_classification
    (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) (hp1 : p one = 1)
    (k : Fin 15) (q r : Fin 58) (hqr_ne : q ≠ r) (hqr : G.col q r = 1)
    (hq : e ⟨18 + k.val, by omega⟩ = q)
    (W : Finset (Fin 58)) (hW : ∀ x ∈ W, x ≠ q ∧ G.col q x = 1) (hrW : r ∉ W)
    (hcard : 14 ≤ W.card)
    (er : ↥(arm G r 0) ≃ Fin 16)
    (hroot : ∀ x y : ↥(arm G r 0), x ≠ y →
      G.col x.val y.val = (0 : Fin 4).succAbove ((template 16 true).col (er x) (er y)))
    (hcoord : ∀ j : Fin 16, e ⟨1 + j.val, by omega⟩ = (er.symm j).val)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) :=
  emitted_sender_step_ready_of_count G hG e p hp1 k q r hqr_ne hqr hq
    W hW hrW hcard hclass_classified er hroot hcoord hb

#print axioms K58.EmittedBridge.named_of_classified
#print axioms K58.EmittedBridge.named_15
#print axioms K58.EmittedBridge.named_16
#print axioms K58.EmittedBridge.hclass_classified
#print axioms K58.EmittedBridge.sender_pinned_of_count_of_classification
#print axioms K58.EmittedBridge.emitted_sender_step_ready_of_count_of_classification

end K58.EmittedBridge

~~~

## `lean/K58/PhysicalGuard.lean`

~~~lean
import K58.EmittedBridge

/-! Why bare emitted-step readiness at the physical valuation is vacuous.

The ordinary physical valuation has values only for genuine host edges. The
auxiliary sender guards lie above the physical tier. Consequently they are
false at `realizedValuation`, and a guarded-true implication is true whether
or not the geometric premises or emitted counts hold.  This does not invalidate
the neighbour finsets, degree bounds, or physical catalogue masks; it says that
those masks, or agreement of all sixteen support atoms with a non-vacuous
valuation, are the meaningful statements. -/

open K58
open K58.SenderReady
open K58.SemanticAssembly

set_option autoImplicit false

namespace K58.PhysicalGuard

/-- A variable strictly above the physical tier has no `HostVarRep`. -/
theorem realizedValuation_eq_false_of_gt
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    {a : Nat} (h : 6612 < a) : realizedValuation G e p a = false := by
  unfold realizedValuation
  split
  · rename_i hh
    obtain ⟨rep⟩ := hh
    have hne : (rep.u : Nat) ≠ (rep.v : Nat) := by
      simp only [ne_eq]
      exact ne_of_lt rep.sorted
    have hle := hostVar_le_of_host_edge rep.u.isLt rep.v.isLt hne rep.colour
    rw [rep.encode] at hle
    omega
  · rfl

/-- Every retained auxiliary counter guard lies above the physical tier. -/
theorem rowGuard_gt (k : Fin 15) : 6612 < rowGuard k := by
  fin_cases k <;> decide

/-- The guard of any emitted sender is false at the physical valuation. -/
theorem realizedValuation_rowGuard
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (k : Fin 15) : realizedValuation G e p (rowGuard k) = false :=
  realizedValuation_eq_false_of_gt G e p (rowGuard_gt k)

/-- Explicit vacuity check: bare readiness at the original physical valuation
holds with no triangle-freeness, root pinnings, classification, or count.
The useful results instead concern the mask or agree-on-atoms valuations. -/
theorem senderStep_ready_at_realized_valuation
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (k : Fin 15)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k)) (rowNewTop k)) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready
      (realizedValuation G e p) := by
  rw [sender_family_ready k hb]
  intro hg
  rw [realizedValuation_rowGuard G e p k] at hg
  exact absurd hg Bool.false_ne_true

/-- The repaired, non-vacuous valuation premise is satisfiable even with a
true auxiliary guard.  The physical support atoms differ from the guard,
so changing that one auxiliary variable does not alter their physical bits. -/
theorem exists_guard_true_of_atom_agreement
    (G : EdgeCol (Fin 58) 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (k : Fin 15) :
    ∃ v : Valuation,
      (∀ j < 16, v (rowAtoms k j) = realizedValuation G e p (rowAtoms k j)) ∧
      v (rowGuard k) = true := by
  let v : Valuation := fun a =>
    if a = rowGuard k then true else realizedValuation G e p a
  refine ⟨v, ?_, ?_⟩
  · intro j hj
    have hne : rowAtoms k j ≠ rowGuard k := by
      have hle : rowAtoms k j ≤ 6612 := by
        rw [EmittedBridge.rowAtoms_val k ⟨j, hj⟩]
        simpa only [Fin.val_mk] using
          (hostVar_le_of_host_edge (u := 1 + j) (v := 18 + k.val)
            (by omega) (by have := k.isLt; omega) (by omega) EmittedBridge.one)
      have hgt := rowGuard_gt k
      omega
    simp [v, hne]
  · simp [v]

#print axioms K58.PhysicalGuard.exists_guard_true_of_atom_agreement
#print axioms K58.PhysicalGuard.realizedValuation_eq_false_of_gt
#print axioms K58.PhysicalGuard.rowGuard_gt
#print axioms K58.PhysicalGuard.realizedValuation_rowGuard
#print axioms K58.PhysicalGuard.senderStep_ready_at_realized_valuation

end K58.PhysicalGuard

~~~
