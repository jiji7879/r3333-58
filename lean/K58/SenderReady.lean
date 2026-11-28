import K58.TargetSuffix

/-!
# Sender-indexed readiness for the emitted K58 support steps (direction 3)

At each of the fifteen guarded senders 18..32 the K58 suffix emits one
`emittedSupportStep`.  Its guard variable is the output of the preceding
41-of-14 sender counter, its 112 selectors `12344+i` (resp. `12835+i`, ...)
index the emitted `targetSupports` catalogue, and its sixteen input atoms are
the first sixteen atoms of that same counter.  The step contributes the only
guarded content of those 1793 clauses per sender; the readiness obligation of
`K58.SemanticAssembly.ChainReady` is therefore exactly the physical bridge that
the repository still reports as open.

This file proves, for that emitted object:

* `senderStep_ready_iff` — at every sender the obligation is the *same*
  proposition: a true guard forces the 16-bit support vector to be one of the
  112 emitted masks.  One lemma covers senders 18..32; the senders differ only
  in `(oldTop, guard, newTop, atoms)`.
* `supportAudit_eq` — a kernel-checked audit that the emitted
  `targetSuffixSteps` really has exactly those fifteen support steps with those
  allocations, guards and atoms (extracted from the emitted clause lists
  themselves, not retyped from the source text).
* `catalogue_of_formulaSat` and `exists_extension_iff` — the emitted support
  clause set has *exactly* the catalogue semantics, in both directions.  So the
  open physical bridge is the whole obligation of the step: no further hidden
  coded premise, and no weaker one.
* `counter_semantics_not_shape` and `guard_alone_insufficient` — the catalogue
  proposition is **not** a consequence of the emitted counter's own semantics:
  a valuation can satisfy the 41-of-14 guard count and still carry a support
  vector outside the catalogue.  The physical `PinnedArm`/CAT content is
  indispensable, not bookkeeping.
* `coordinate_order_matters` and `three_element_not_catalogue` — the catalogue
  really constrains the slot order and the support size, so a wrong coordinate
  order or an off-catalogue mask is rejected rather than absorbed.

Nothing here is a physical premise.  `TriangleFree`, mutual root-arm
membership, the degree bounds `15 ≤ d ≤ 16` and both `PinnedArm`s stay
hypotheses of the caller; in particular no `ChainReady` instance, no equality
with a physical `Sends` event and no physical vertex is produced or assumed.
The residual mathematical obligation after this file is exactly
`CatalogueVec` at a true guard, which is the P4/C5 transport.
-/

namespace K58.SenderReady
open K58
open K58.SemanticAssembly
open K58.SequentialCounter
open K58.EncoderExtensions

set_option autoImplicit false

/-! ## The catalogue as the generator's 16-bit mask -/

/-- Bit `j` of catalogue entry `i`: `supportBit targetSupports` specialised to
the emitted `k = 112`. -/
def catalogueBit (i : Fin 112) (j : Nat) : Bool := supportBit targetSupports i j

set_option maxRecDepth 100000 in
theorem catalogue_size : targetSupports.length = 112 := by decide

set_option maxRecDepth 100000 in
/-- Independent re-derivation, from the emitted Lean list, of the reported
`96` four-element and `16` five-element split. -/
theorem catalogue_four_count :
    ((List.finRange 112).filter
      (fun i => (targetSupports.getD i.val []).length = 4)).length = 96 := by decide

set_option maxRecDepth 100000 in
theorem catalogue_five_count :
    ((List.finRange 112).filter
      (fun i => (targetSupports.getD i.val []).length = 5)).length = 16 := by decide

/-- A 16-bit support vector is one of the 112 emitted masks. -/
def CatalogueVec (x : Nat → Bool) : Prop :=
  ∃ i : Fin 112, ∀ j < 16, x j = catalogueBit i j

/-- The same predicate over `Fin 16`, the decidable form used by the negative
controls below. -/
def CatalogueVecFin (x : Fin 16 → Bool) : Prop :=
  ∃ i : Fin 112, ∀ j : Fin 16, x j = catalogueBit i j.val

theorem catalogueVec_iff_fin (x : Nat → Bool) :
    CatalogueVec x ↔ CatalogueVecFin (fun j => x j.val) := by
  constructor
  · rintro ⟨i, hi⟩
    exact ⟨i, fun j => hi j.val j.isLt⟩
  · rintro ⟨i, hi⟩
    exact ⟨i, fun j hj => hi ⟨j, hj⟩⟩

/-- The exact clause set of each emitted support step. -/
def catalogueCNF (g : Nat) (x : Nat → Nat) (sel : Fin 112 → Nat) : CNF :=
  emittedSupportFamilyCNF g 16 112 x sel catalogueBit (fun _ => true)

/-- The one shape shared by the fifteen emitted support steps; only the guard,
the sixteen input atoms, the allocation bounds and the proof arguments differ. -/
def senderStep (oldTop g newTop : Nat) (x : Nat → Nat) (sel : Fin 112 → Nat)
    (hg : g ≤ oldTop) (hnew : oldTop ≤ newTop)
    (hinp : ∀ j < 16, x j ≤ oldTop) (fresh : ∀ i, oldTop < sel i)
    (hinj : Function.Injective sel)
    (hb : VarsBelow (catalogueCNF g x sel) newTop) : ExtensionStep :=
  emittedSupportStep oldTop g 16 112 newTop x sel catalogueBit (fun _ => true)
    hg hnew hinp fresh hinj hb

/-- **Sender-indexed form of the open obligation.**  Readiness of a sender step
is the guard-true catalogue proposition — for every sender, with no extra
content and no sender-specific variation. -/
theorem senderStep_ready_iff (oldTop g newTop : Nat) (x : Nat → Nat)
    (sel : Fin 112 → Nat) (hg : g ≤ oldTop) (hnew : oldTop ≤ newTop)
    (hinp : ∀ j < 16, x j ≤ oldTop) (fresh : ∀ i, oldTop < sel i)
    (hinj : Function.Injective sel)
    (hb : VarsBelow (catalogueCNF g x sel) newTop) (v : Valuation) :
    (senderStep oldTop g newTop x sel hg hnew hinp fresh hinj hb).ready v ↔
      (v g = true → CatalogueVec (fun j => v (x j))) :=
  Iff.rfl

/-! ## The emitted clause set has exactly the catalogue semantics -/

/-- **Backward exactness.**  Satisfying the emitted support clause set at a true
guard forces a catalogue vector.  Injectivity of the selector map is not needed:
the main clause already names a witness selector. -/
theorem catalogue_of_formulaSat (g : Nat) (x : Nat → Nat) (sel : Fin 112 → Nat)
    {w : Valuation} (hg : w g = true)
    (hs : FormulaSat w (catalogueCNF g x sel)) :
    CatalogueVec (fun j => w (x j)) := by
  have hmain : ((false, g) :: (List.finRange 112).map (fun i => (true, sel i)))
      ∈ catalogueCNF g x sel := by
    unfold catalogueCNF emittedSupportFamilyCNF
    exact List.mem_append.mpr (Or.inr (by simp))
  obtain ⟨l, hl, hv⟩ := hs _ hmain
  rcases List.mem_cons.mp hl with rfl | hl
  · rw [hg] at hv
    exact absurd hv (by simp)
  · obtain ⟨i, -, rfl⟩ := List.mem_map.mp hl
    refine ⟨i, fun j hj => ?_⟩
    have hcl : [(false, sel i), (catalogueBit i j, x j)] ∈ catalogueCNF g x sel := by
      unfold catalogueCNF emittedSupportFamilyCNF emittedSupportImplications
      apply List.mem_append.mpr
      left
      apply List.mem_flatMap.mpr
      refine ⟨i, by simp, ?_⟩
      apply List.mem_map.mpr
      exact ⟨j, List.mem_filter.mpr ⟨List.mem_range.mpr hj, rfl⟩, rfl⟩
    obtain ⟨l', hl', hv'⟩ := hs _ hcl
    rcases List.mem_cons.mp hl' with hfirst | hrest
    · rw [hfirst] at hv'
      rw [hv] at hv'
      exact absurd hv' (by simp)
    · rcases List.mem_cons.mp hrest with hsecond | hempty
      · rw [hsecond] at hv'
        exact hv'
      · exact absurd hempty (by simp)

/-- **Forward direction**: the catalogue proposition is enough to extend any
valuation over the emitted support clauses. -/
theorem exists_extension_of_catalogue (v : Valuation) (g oldTop : Nat)
    (x : Nat → Nat) (sel : Fin 112 → Nat)
    (hg : g ≤ oldTop) (hinp : ∀ j < 16, x j ≤ oldTop) (fresh : ∀ i, oldTop < sel i)
    (hinj : Function.Injective sel)
    (h : v g = true → CatalogueVec (fun j => v (x j))) :
    ∃ w : Valuation, (∀ a ≤ oldTop, w a = v a) ∧ FormulaSat w (catalogueCNF g x sel) :=
  satisfiable_emittedSupportFamily v g 16 112 oldTop x sel catalogueBit (fun _ => true)
    hg hinp fresh hinj h

/-- **Exactness of the emitted support step.**  Over a fixed prefix, the support
clause set is satisfiable by extension if and only if the guard-true catalogue
proposition holds.  Hence the still-open physical bridge is the whole content of
the step: there is neither an additional coded obligation nor a weaker one. -/
theorem exists_extension_iff (v : Valuation) (g oldTop : Nat) (x : Nat → Nat)
    (sel : Fin 112 → Nat) (hg : g ≤ oldTop) (hinp : ∀ j < 16, x j ≤ oldTop)
    (fresh : ∀ i, oldTop < sel i) (hinj : Function.Injective sel) :
    (∃ w : Valuation, (∀ a ≤ oldTop, w a = v a) ∧ FormulaSat w (catalogueCNF g x sel)) ↔
      (v g = true → CatalogueVec (fun j => v (x j))) := by
  constructor
  · rintro ⟨w, hag, hs⟩ hgt
    have hwg : w g = true := by rw [hag g hg]; exact hgt
    obtain ⟨i, hi⟩ := catalogue_of_formulaSat g x sel hwg hs
    refine ⟨i, fun j hj => ?_⟩
    show v (x j) = catalogueBit i j
    rw [← hag (x j) (hinp j hj)]
    exact hi j hj
  · intro h
    exact exists_extension_of_catalogue v g oldTop x sel hg hinp fresh hinj h

/-! ## The fifteen emitted senders, audited from the emitted clause lists -/

/-- Last clause of an emitted family. -/
def lastClause (F : CNF) : List Literal := F.getD (F.length - 1) []

/-- Guard variable carried by the last clause (`¬ g ∨ …`). -/
def guardOf (F : CNF) : Nat := match lastClause F with
  | [] => 0
  | l :: _ => l.2

/-- The sixteen support atoms, read off the first sixteen implication clauses. -/
def firstAtoms (F : CNF) : List Nat :=
  (F.take 16).map (fun c => match c with
    | [] => 0
    | _ :: l :: _ => l.2
    | _ => 0)

/-- The variables at or below `top` occurring in a clause set, deduplicated and
sorted. -/
def inputAtomsOf (F : CNF) (top : Nat) : List Nat :=
  (((F.flatMap (fun c => c.map (fun l => l.2))).filter (fun v => v ≤ top)).eraseDups).insertionSort
    (· ≤ ·)

/-- Signature of every clause set in `targetSuffixSteps` of support-family size. -/
def supportAuditList : List (Nat × Nat × Nat × List Nat) :=
  (targetSuffixSteps.filter (fun s => s.clauses.length = 1793)).map
    (fun s => (s.oldTop, guardOf s.clauses, s.newTop, firstAtoms s.clauses))

/-- The allocation map used below, sender by sender 18..32. -/
def senderAlloc : List (Nat × Nat × Nat × List Nat) :=
  [(12343, 11965, 12455, [294, 514, 730, 942, 1150, 1354, 1554, 1750, 1942, 2130, 2314, 2494, 2670, 2842, 3010, 3174]),
   (12834, 12456, 12946, [298, 518, 734, 946, 1154, 1358, 1558, 1754, 1946, 2134, 2318, 2498, 2674, 2846, 3014, 3178]),
   (13325, 12947, 13437, [302, 522, 738, 950, 1158, 1362, 1562, 1758, 1950, 2138, 2322, 2502, 2678, 2850, 3018, 3182]),
   (13816, 13438, 13928, [306, 526, 742, 954, 1162, 1366, 1566, 1762, 1954, 2142, 2326, 2506, 2682, 2854, 3022, 3186]),
   (14307, 13929, 14419, [310, 530, 746, 958, 1166, 1370, 1570, 1766, 1958, 2146, 2330, 2510, 2686, 2858, 3026, 3190]),
   (14798, 14420, 14910, [314, 534, 750, 962, 1170, 1374, 1574, 1770, 1962, 2150, 2334, 2514, 2690, 2862, 3030, 3194]),
   (15289, 14911, 15401, [318, 538, 754, 966, 1174, 1378, 1578, 1774, 1966, 2154, 2338, 2518, 2694, 2866, 3034, 3198]),
   (15780, 15402, 15892, [322, 542, 758, 970, 1178, 1382, 1582, 1778, 1970, 2158, 2342, 2522, 2698, 2870, 3038, 3202]),
   (16271, 15893, 16383, [326, 546, 762, 974, 1182, 1386, 1586, 1782, 1974, 2162, 2346, 2526, 2702, 2874, 3042, 3206]),
   (16762, 16384, 16874, [330, 550, 766, 978, 1186, 1390, 1590, 1786, 1978, 2166, 2350, 2530, 2706, 2878, 3046, 3210]),
   (17253, 16875, 17365, [334, 554, 770, 982, 1190, 1394, 1594, 1790, 1982, 2170, 2354, 2534, 2710, 2882, 3050, 3214]),
   (17744, 17366, 17856, [338, 558, 774, 986, 1194, 1398, 1598, 1794, 1986, 2174, 2358, 2538, 2714, 2886, 3054, 3218]),
   (18235, 17857, 18347, [342, 562, 778, 990, 1198, 1402, 1602, 1798, 1990, 2178, 2362, 2542, 2718, 2890, 3058, 3222]),
   (18726, 18348, 18838, [346, 566, 782, 994, 1202, 1406, 1606, 1802, 1994, 2182, 2366, 2546, 2722, 2894, 3062, 3226]),
   (19217, 18839, 19329, [350, 570, 786, 998, 1206, 1410, 1610, 1806, 1998, 2186, 2370, 2550, 2726, 2898, 3066, 3230])]

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- **Kernel-checked audit of the emitted suffix.**  The clause lists of
`targetSuffixSteps` contain exactly these fifteen support families, with these
allocations, guards and atoms; nothing is retyped from the source text. -/
theorem supportAudit_eq : supportAuditList = senderAlloc := by
  decide

theorem sender_count : senderAlloc.length = 15 := by decide

theorem sender_guards : senderAlloc.map (fun p => p.2.1) =
    [11965, 12456, 12947, 13438, 13929, 14420, 14911, 15402, 15893, 16384,
     16875, 17366, 17857, 18348, 18839] := by decide

/-- **Kernel-checked selector audit.**  In every one of the fifteen emitted
support families the last clause is `¬ guard ∨ sel 0 ∨ … ∨ sel 111`, all
selectors are positive, and the selector variables are exactly
`oldTop+1 … oldTop+112`.  So the emitted support/selector identifiers are the
ones interpreted here, and the fifteen selector blocks are pairwise disjoint
because each block is followed by the next counter allocation. -/
def supportShapeAudit : Bool :=
  (targetSuffixSteps.filter (fun s => s.clauses.length = 1793)).all fun s =>
    match lastClause s.clauses with
    | [] => false
    | l :: rest =>
        (!l.1) && (rest.length = 112) && rest.all (fun m : Literal => m.1) &&
          (rest.map (fun m : Literal => m.2) = (List.range 112).map (fun i => s.oldTop + 1 + i))

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
theorem supportShapeAudit_eq :
    (targetSuffixSteps.filter (fun s => s.clauses.length = 1793)).all (fun s =>
      match lastClause s.clauses with
      | [] => false
      | l :: rest =>
          (!l.1) && (rest.length = 112) && rest.all (fun m : Literal => m.1) &&
            (rest.map (fun m : Literal => m.2) = (List.range 112).map (fun i => s.oldTop + 1 + i)))
      = true := by decide

/-- A row of `senderAlloc` read as `(oldTop, guard, newTop, atoms)`. -/
def oldTopOf (p : Nat × Nat × Nat × List Nat) : Nat := p.1
def newTopOf (p : Nat × Nat × Nat × List Nat) : Nat := p.2.2.1
def guardOfRow (p : Nat × Nat × Nat × List Nat) : Nat := p.2.1
def atomsOfRow (p : Nat × Nat × Nat × List Nat) : List Nat := p.2.2.2

/-- The fifteen selector blocks are pairwise disjoint: each block ends before
the next counter starts. -/
theorem sender_blocks_disjoint :
    (senderAlloc.zip (senderAlloc.drop 1)).all
      (fun q => newTopOf q.1 < oldTopOf q.2) = true := by decide

/-- Every sender allocates exactly 112 fresh selector variables. -/
theorem sender_stride : ∀ p ∈ senderAlloc, newTopOf p = oldTopOf p + 112 := by decide

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- **Corruption control for the audit.**  Changing one atom of one row makes the
audited signature differ from the emitted clause lists, so `supportAudit_eq` is
sensitive to a single-digit corruption and is not vacuous. -/
theorem supportAudit_corruption :
    supportAuditList ≠
      senderAlloc.set 0
        (12343, 11965, 12455, [294, 514, 730, 942, 1150, 1354, 1554, 1750, 1942,
          2130, 2314, 2494, 2670, 2842, 3010, 3175]) := by
  decide

/-! ## The two final counters count exactly these senders -/

/-- The clause set of the first final counter, `AtLeast(15,6)` at `19329`. -/
def finalCNF : CNF :=
  (targetSuffixSteps.filter (fun s => s.oldTop = 19329)).flatMap (fun s => s.clauses)

/-- The clause set of the second final counter, `AtLeast(31,6)` at `19383`. -/
def totalCNF : CNF :=
  (targetSuffixSteps.filter (fun s => s.oldTop = 19383)).flatMap (fun s => s.clauses)

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- **Kernel-checked arm audit.**  The final `AtLeast(15,6)` counts exactly the
fifteen guard variables `11965 … 18839` of senders 18..32, and the final
`AtLeast(31,6)` counts exactly those plus the sixteen earlier guards.  So the
fifteen support senders of this file are precisely the arm the emission singles
out, not an arbitrary subset. -/
theorem final_counters_inputs :
    inputAtomsOf finalCNF 19329 =
        ([11965, 12456, 12947, 13438, 13929, 14420, 14911, 15402, 15893, 16384,
          16875, 17366, 17857, 18348, 18839].insertionSort (· ≤ ·)) ∧
      inputAtomsOf totalCNF 19383 =
        ([6613, 6814, 7193, 7394, 7773, 8152, 8531, 8732, 9111, 9490, 9869, 10248,
          10449, 10828, 11207, 11586, 11965, 12456, 12947, 13438, 13929, 14420,
          14911, 15402, 15893, 16384, 16875, 17366, 17857, 18348,
          18839].insertionSort (· ≤ ·)) := by
  decide

/-! ## The indexed sender family: senders 18..32 in one theorem -/

/-- Row `k` of `senderAlloc`, sender `18 + k`. -/
def row (k : Fin 15) : Nat × Nat × Nat × List Nat := senderAlloc.get k

def rowOldTop (k : Fin 15) : Nat := (row k).1

def rowGuard (k : Fin 15) : Nat := (row k).2.1

def rowNewTop (k : Fin 15) : Nat := (row k).2.2.1

def rowAtomsList (k : Fin 15) : List Nat := (row k).2.2.2

def rowAtoms (k : Fin 15) : Nat → Nat := listAtoms (rowAtomsList k)

def rowSel (k : Fin 15) : Fin 112 → Nat := fun i => rowOldTop k + 1 + i.val

theorem row_guard_le_old (k : Fin 15) : rowGuard k ≤ rowOldTop k := by
  fin_cases k <;> decide

theorem row_new_eq (k : Fin 15) : rowNewTop k = rowOldTop k + 112 := by
  fin_cases k <;> decide

theorem row_old_le_new (k : Fin 15) : rowOldTop k ≤ rowNewTop k := by
  rw [row_new_eq]; omega

theorem row_atoms_length (k : Fin 15) : (rowAtomsList k).length = 16 := by
  fin_cases k <;> decide

theorem row_atoms_bound (k : Fin 15) (j : Nat) (hj : j < 16) :
    rowAtoms k j ≤ rowOldTop k := by
  fin_cases k <;> interval_cases j <;> decide

theorem row_sel_fresh (k : Fin 15) (i : Fin 112) : rowOldTop k < rowSel k i := by
  unfold rowSel; omega

theorem row_sel_injective (k : Fin 15) : Function.Injective (rowSel k) := by
  intro i j h
  apply Fin.ext
  unfold rowSel at h
  omega

theorem senderAlloc_get_mem (k : Fin 15) : senderAlloc.get k ∈ senderAlloc :=
  List.get_mem senderAlloc k

/-- **The whole sender family, indexed.**  For each `k : Fin 15` — sender
`18 + k`, guard `rowGuard k`, atoms `rowAtomsList k`, selectors
`rowOldTop k + 1 … rowOldTop k + 112` — the emitted support step's readiness is
the guard-true catalogue proposition.  The fifteen rows are exactly the emitted
ones by `supportAudit_eq`, so this is the sender 18..32 statement rather than a
schema for arbitrary data. -/
theorem sender_family_ready (k : Fin 15)
    (hb : VarsBelow (catalogueCNF (rowGuard k) (rowAtoms k) (rowSel k))
      (rowNewTop k)) (v : Valuation) :
    (senderStep (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k) (rowSel k)
      (by have := row_guard_le_old k; omega)
      (by have := row_old_le_new k; omega)
      (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb).ready v ↔
      (v (rowGuard k) = true → CatalogueVec (fun j => v (rowAtoms k j))) :=
  senderStep_ready_iff (rowOldTop k) (rowGuard k) (rowNewTop k) (rowAtoms k)
    (rowSel k) _ _ (row_atoms_bound k) (row_sel_fresh k) (row_sel_injective k) hb v

/-! ## Sender 18, exactly as emitted -/

/-- The sixteen support atoms of sender 18. -/
def atomsList18 : List Nat :=
  [294, 514, 730, 942, 1150, 1354, 1554, 1750, 1942, 2130, 2314, 2494, 2670, 2842, 3010, 3174]

/-- The twenty-five further atoms of sender 18's 41-of-14 guard counter. -/
def tailList18 : List Nat :=
  [3550, 3554, 3558, 3562, 3566, 3570, 3574, 3578, 3582, 3586, 3590, 3594, 3598,
   3602, 3606, 3610, 3614, 3618, 3622, 3626, 3630, 3634, 3638, 3642, 3646]

/-- All 41 input atoms of the guard counter whose output is `11965`. -/
def counterList18 : List Nat := atomsList18 ++ tailList18

def atoms18 : Nat → Nat := listAtoms atomsList18

def counterAtoms18 : Nat → Nat := listAtoms counterList18

def sel18 : Fin 112 → Nat := fun i => 12344 + i.val

theorem atomsList18_length : atomsList18.length = 16 := by decide

/-- Row `0` of the family is sender 18, with the atoms used above. -/
theorem row_zero : row 0 = (12343, 11965, 12455, atomsList18) := by decide

theorem counterList18_length : counterList18.length = 41 := by decide

theorem sender18_row : (12343, 11965, 12455, atomsList18) ∈ senderAlloc := by decide

theorem atoms18_bound (j : Nat) (hj : j < 16) : atoms18 j ≤ 12343 := by
  interval_cases j <;> decide

theorem atoms18_lt_guard (j : Nat) (hj : j < 16) : atoms18 j < 11965 := by
  interval_cases j <;> decide

theorem sel18_fresh (i : Fin 112) : 12343 < sel18 i := by
  unfold sel18; omega

theorem sel18_injective : Function.Injective sel18 := by
  intro i j h
  apply Fin.ext
  unfold sel18 at h
  omega

/-- **Sender 18 (`guard = 11965`), exactly as emitted.**  The ready proposition
of its support step is the guard-true catalogue proposition; the `VarsBelow`
argument of the emitted call is carried as a hypothesis, exactly as the emitted
file supplies it from `emittedSupport_varsBelow`. -/
theorem sender18_ready (hb : VarsBelow (catalogueCNF 11965 atoms18 sel18) 12455)
    (v : Valuation) :
    (senderStep 12343 11965 12455 atoms18 sel18 (by omega) (by omega)
      atoms18_bound sel18_fresh sel18_injective hb).ready v ↔
      (v 11965 = true → CatalogueVec (fun j => v (atoms18 j))) :=
  senderStep_ready_iff 12343 11965 12455 atoms18 sel18 _ _ atoms18_bound
    sel18_fresh sel18_injective hb v

/-! ## Negative controls: the catalogue proposition is not free -/

set_option maxRecDepth 100000 in
theorem catalogue_nonempty_all :
    ∀ i : Fin 112, ∃ j : Fin 16, catalogueBit i j = true := by decide

theorem catalogue_nonempty (i : Fin 112) : ∃ j : Fin 16, catalogueBit i j = true :=
  catalogue_nonempty_all i

/-- The empty support is not a catalogue vector. -/
theorem empty_not_catalogue : ¬ CatalogueVec (fun _ => false) := by
  rintro ⟨i, hi⟩
  obtain ⟨j, hj⟩ := catalogue_nonempty i
  have h := hi j.val j.isLt
  rw [show (fun _ : Nat => false) j.val = false from rfl] at h
  rw [← h] at hj
  exact Bool.false_ne_true hj

theorem not_catalogue_of_prefix_false (v : Valuation)
    (h : ∀ j < 16, v (atoms18 j) = false) :
    ¬ CatalogueVec (fun j => v (atoms18 j)) := by
  rintro ⟨i, hi⟩
  obtain ⟨j, hj⟩ := catalogue_nonempty i
  have h1 := h j.val j.isLt
  have h2 : v (atoms18 j.val) = catalogueBit i j.val := hi j.val j.isLt
  rw [h1] at h2
  rw [← h2] at hj
  exact Bool.false_ne_true hj

/-- The valuation of control 1: true only at the guard variable itself. -/
def guardOnlyModel : Valuation := fun a => a == 11965

theorem guardOnlyModel_true : guardOnlyModel 11965 = true := by decide

theorem guardOnlyModel_prefix_false (j : Nat) (hj : j < 16) :
    guardOnlyModel (atoms18 j) = false := by
  interval_cases j <;> decide

/-- **Control 1: the guard variable alone does not determine the shape.**  A
valuation with `v 11965 = true` and an empty support vector; so the ready
hypothesis is a genuine extra premise, not a tautology. -/
theorem guard_alone_insufficient :
    ∃ v : Valuation, v 11965 = true ∧ ¬ CatalogueVec (fun j => v (atoms18 j)) :=
  ⟨guardOnlyModel, guardOnlyModel_true,
    not_catalogue_of_prefix_false _ guardOnlyModel_prefix_false⟩

/-- The valuation of control 2: true exactly on the twenty-five non-support
atoms of the guard counter, plus the guard itself. -/
def counterModel : Valuation := fun a => tailList18.contains a || (a == 11965)

set_option maxRecDepth 100000 in
theorem counterModel_count :
    14 ≤ prefixCount (fun j => counterModel (counterAtoms18 j)) 41 := by
  decide

theorem counterModel_prefix_false (j : Nat) (hj : j < 16) :
    counterModel (atoms18 j) = false := by
  interval_cases j <;> decide

/-- **Control 2: the emitted counter's semantics does not imply the shape.**  A
valuation satisfies sender 18's 41-of-14 guard count and yet carries a support
vector outside the catalogue.  Hence the physical PinnedArm/CAT argument is
needed; the emitted guard counter cannot supply it. -/
theorem counter_semantics_not_shape :
    ∃ v : Valuation, 14 ≤ prefixCount (fun j => v (counterAtoms18 j)) 41 ∧
      ¬ CatalogueVec (fun j => v (atoms18 j)) :=
  ⟨counterModel, counterModel_count,
    not_catalogue_of_prefix_false _ counterModel_prefix_false⟩

/-! ## Auditing the 41-atom guard counter of sender 18 -/

/-- The clause set of the emitted counter step that produces guard `11965`. -/
def guardCNF18 : CNF :=
  (targetSuffixSteps.filter (fun s => s.oldTop = 11964 && s.newTop = 12343)).flatMap
    (fun s => s.clauses)

set_option maxRecDepth 1000000 in
set_option maxHeartbeats 4000000 in
/-- **Kernel-checked audit of the guard counter.**  The emitted counter clauses
that produce guard `11965` read exactly the forty-one listed input atoms from the
prefix `≤ 11964` (all other variables of that clause set are fresh auxiliaries
above `11965` and the guard itself).  So `counterList18` is the emitted input
list, not a recollection of it. -/
theorem guard18_inputs :
    inputAtomsOf guardCNF18 11964 = counterList18.insertionSort (· ≤ ·) := by
  decide

/-! ## What the emitted counter step does to the guard -/

theorem counterAtoms18_bound (i : Nat) (hi : i < 41) : counterAtoms18 i ≤ 11964 := by
  interval_cases i <;> decide

theorem counterAtoms18_ne_guard (i : Nat) (hi : i < 41) : counterAtoms18 i ≠ 11965 := by
  have := counterAtoms18_bound i hi; omega

/-- **The emitted counter step's own effect on the guard.**  If the 41-of-14
count holds at a valuation, the guard variable `11965` of sender 18 is set true
by the counter step while every variable at or below `11964` is preserved, and
the emitted counter clauses are satisfied.  This is the `setValue` half of
`K58.SemanticAssembly.freshGuardedCounterStep` specialised to the emitted
counter of sender 18. -/
theorem counter_guard_true (v : Valuation)
    (h : 14 ≤ prefixCount (fun j => v (counterAtoms18 j)) 41) :
    ∃ w : Valuation, (∀ a ≤ 11964, w a = v a) ∧ w 11965 = true ∧
      FormulaSat w (guardedAtLeastCNF 11965 counterAtoms18 41 14 11965) := by
  let v0 : Valuation := setValue v 11965 true
  have hv0 : v0 11965 = true := by simp [v0, setValue]
  have hpres : ∀ i < 41, v0 (counterAtoms18 i) = v (counterAtoms18 i) := by
    intro i hi
    have hne : counterAtoms18 i ≠ 11965 := counterAtoms18_ne_guard i hi
    simp [v0, setValue, hne]
  have hcount : 14 ≤ prefixCount (fun i => v0 (counterAtoms18 i)) 41 := by
    rw [prefixCount_congr_of_lt (fun i => v0 (counterAtoms18 i))
      (fun i => v (counterAtoms18 i)) 41 hpres]
    exact h
  obtain ⟨w, hag, hs⟩ := satisfiable_guardedAtLeast v0 11965 counterAtoms18 41 14
    11965 (by omega) (fun i hi => by have := counterAtoms18_bound i hi; omega)
    (fun _ => hcount)
  refine ⟨w, ?_, ?_, hs⟩
  · intro a ha
    rw [hag a (by omega)]
    simp [v0, setValue, show a ≠ 11965 by omega]
  · rw [hag 11965 le_rfl]; exact hv0

/-- **Control 2, made concrete.**  On the valuation of `counterModel` — which the
emitted counter step of sender 18 supplies with a true guard — the emitted
support clause set is *unsatisfiable* over the same prefix.  So the support step
adds real content beyond the counter, and the missing ingredient is exactly the
catalogue/shape premise. -/
theorem counterModel_support_refuted :
    ¬ ∃ w : Valuation, (∀ a ≤ 12343, w a = counterModel a) ∧
        FormulaSat w (catalogueCNF 11965 atoms18 sel18) := by
  rintro ⟨w, hag, hs⟩
  have hg : counterModel 11965 = true := by decide
  have hiff := (exists_extension_iff counterModel 11965 12343 atoms18 sel18
    (by omega) atoms18_bound sel18_fresh sel18_injective).mp ⟨w, hag, hs⟩
  exact not_catalogue_of_prefix_false _ counterModel_prefix_false (hiff hg)

/-- **The counter and support steps have no common model above `counterModel`.**
Any valuation agreeing with `counterModel` on the sender-18 region (guard and
support atoms) admits no extension over the emitted support clauses.  Together
with `counter_guard_true` this isolates the missing premise: the emitted counter
is satisfiable exactly where the emitted support step is not, unless the
catalogue/shape fact is supplied physically. -/
theorem counter_then_support_unsatisfiable (w : Valuation)
    (hw : ∀ a ≤ 11965, w a = counterModel a) :
    ¬ ∃ z : Valuation, (∀ a ≤ 12343, z a = w a) ∧
        FormulaSat z (catalogueCNF 11965 atoms18 sel18) := by
  rintro ⟨z, hag, hs⟩
  have hg : w 11965 = true := by rw [hw 11965 le_rfl]; decide
  have hiff := (exists_extension_iff w 11965 12343 atoms18 sel18
    (by omega) atoms18_bound sel18_fresh sel18_injective).mp ⟨z, hag, hs⟩
  refine not_catalogue_of_prefix_false w (fun j hj => ?_) (hiff hg)
  rw [hw (atoms18 j) (by have := atoms18_lt_guard j hj; omega)]
  exact counterModel_prefix_false j hj

/-- Swap the first two support slots of a catalogue entry. -/
def swap01 (i : Fin 112) (j : Nat) : Bool :=
  if j = 0 then catalogueBit i 1 else if j = 1 then catalogueBit i 0 else catalogueBit i j

set_option maxRecDepth 100000 in
/-- **Control 3: the slot order matters.**  Some catalogue entry, with its first
two slots exchanged, is not a catalogue vector; a wrongly ordered `PinnedArm`
coordinate map is therefore rejected, not silently absorbed. -/
theorem coordinate_order_matters :
    ∃ i : Fin 112, ∀ i' : Fin 112, ∃ j < 16, swap01 i j ≠ catalogueBit i' j := by
  decide

set_option maxRecDepth 100000 in
/-- **Control 4: the support size is constrained.**  The three-element support
`{2,4,6}`, a subset of catalogue entry `[0,2,4,6]`, is not a catalogue vector,
so off-catalogue masks are refused. -/
theorem three_element_not_catalogue :
    ¬ CatalogueVec (fun j => [2, 4, 6].contains j) := by
  rw [catalogueVec_iff_fin]
  unfold CatalogueVecFin
  decide

/-! ## Axiom check -/

#print axioms K58.SenderReady.senderStep_ready_iff
#print axioms K58.SenderReady.catalogue_of_formulaSat
#print axioms K58.SenderReady.exists_extension_iff
#print axioms K58.SenderReady.supportAudit_eq
#print axioms K58.SenderReady.supportShapeAudit_eq
#print axioms K58.SenderReady.supportAudit_corruption
#print axioms K58.SenderReady.guard18_inputs
#print axioms K58.SenderReady.final_counters_inputs
#print axioms K58.SenderReady.sender_blocks_disjoint
#print axioms K58.SenderReady.sender_family_ready
#print axioms K58.SenderReady.row_zero
#print axioms K58.SenderReady.sender18_ready
#print axioms K58.SenderReady.guard_alone_insufficient
#print axioms K58.SenderReady.counter_semantics_not_shape
#print axioms K58.SenderReady.counter_guard_true
#print axioms K58.SenderReady.counter_then_support_unsatisfiable
#print axioms K58.SenderReady.coordinate_order_matters
#print axioms K58.SenderReady.three_element_not_catalogue

end K58.SenderReady
