import K58.TargetParent

open K58
open K58.SemanticAssembly
open Classical

set_option maxRecDepth 1000000

/-- Executable Boolean version of `VarsBelow` for a finite CNF. -/
def varsBelowBool (F : CNF) (top : Nat) : Bool :=
  F.all fun c => c.all fun l => decide (l.2 ≤ top)

theorem varsBelow_of_bool (F : CNF) (top : Nat)
    (h : varsBelowBool F top = true) : VarsBelow F top := by
  intro c hc l hl
  have hc' := List.all_eq_true.mp h c hc
  exact of_decide_eq_true (List.all_eq_true.mp hc' l hl)

/-- The maximum rank for a fixed smaller endpoint is monotone up to `56`.
The extra allowance `56-u` is exactly the number of remaining columns. -/
private theorem rankMaxMono {a b : Nat} (hab : a ≤ b) (hb : b ≤ 56) :
    ((List.range a).map (fun i => 57-i)).sum + (56-a) ≤
    ((List.range b).map (fun i => 57-i)).sum + (56-b) := by
  induction b with
  | zero =>
      have ha : a = 0 := Nat.eq_zero_of_le_zero hab
      subst a
      exact le_rfl
  | succ b ih =>
      by_cases heq : a = b + 1
      · subst a; rfl
      · have ha : a ≤ b := by omega
        calc
          _ ≤ ((List.range b).map (fun i => 57-i)).sum + (56-b) := ih ha (by omega)
          _ ≤ ((List.range (b+1)).map (fun i => 57-i)).sum + (56-(b+1)) := by
            simp only [List.range_succ, List.map_append, List.map_singleton,
              List.sum_append, List.sum_singleton]
            omega

/-- The largest sorted host-pair rank is exactly `(56,57) ↦ 1652`. -/
theorem hostLexRank_le_of_sorted {u v : Nat} (hu : u < 57) (hv : v < 58)
    (huv : u < v) : hostLexRank u v ≤ 1652 := by
  have hm := rankMaxMono (a := u) (b := 56) (by omega) (by rfl)
  have he : hostLexRank 56 57 = 1652 := by rfl
  unfold hostLexRank at he ⊢
  omega

/-- The four DIMACS variables of every genuine host edge stay below the suffix. -/
theorem hostVar_le_of_host_edge {u v : Nat} (hu : u < 58) (hv : v < 58)
    (hne : u ≠ v) (c : Fin 4) : hostVar u v c ≤ 6612 := by
  rcases lt_or_gt_of_ne hne with huv | hvu
  · have hr := hostLexRank_le_of_sorted (u := u) (v := v) (by omega) hv huv
    have hc := c.isLt
    simp only [hostVar, min_eq_left (Nat.le_of_lt huv), max_eq_right (Nat.le_of_lt huv)]
    omega
  · have hr := hostLexRank_le_of_sorted (u := v) (v := u) (by omega) hu hvu
    have hc := c.isLt
    simp only [hostVar, min_eq_right (Nat.le_of_lt hvu), max_eq_left (Nat.le_of_lt hvu)]
    omega

/-- Every label in the four root arms is a genuine host vertex. -/
theorem blockLabel_lt_of_key (k : CaseKey) (a : Fin 4) (i : Nat)
    (hi : i < plannedDegree k.plan a) : blockLabel k.plan a i < 58 := by
  have hp := k.planIndex.isLt
  fin_cases a <;> interval_cases h : k.planIndex.val <;>
    norm_num [CaseKey.plan, plans, blockLabel, plannedDegree, h] at hi ⊢ <;> omega

private theorem hostVar_ofEdge_le {u v : Nat} (hu : u < 58) (hv : v < 58)
    (hne : u ≠ v) (c : Fin 4) (b : Bool) :
    hostVar (ColourUnit.ofEdge u v c b).u (ColourUnit.ofEdge u v c b).v c ≤ 6612 := by
  rcases le_total u v with huv | hvu
  · simpa only [ColourUnit.ofEdge, min_eq_left huv, max_eq_right huv] using
      hostVar_le_of_host_edge hu hv hne c
  · simpa only [ColourUnit.ofEdge, min_eq_right hvu, max_eq_left hvu] using
      hostVar_le_of_host_edge hv hu hne.symm c

private theorem blockUnits_hostVar_le {n : Nat} (vertices : Fin n → Nat)
    (hvert : ∀ i, vertices i < 58)
    (hinj : ∀ i j, i ≠ j → vertices i ≠ vertices j)
    (t : Bool) (a : Fin 4) {u : ColourUnit}
    (hu : u ∈ blockUnits vertices t a) : hostVar u.u u.v u.colour ≤ 6612 := by
  obtain ⟨i, _, hi⟩ := List.mem_flatMap.mp hu
  obtain ⟨j, hj, rfl⟩ := List.mem_map.mp hi
  have hij : i ≠ j := ne_of_lt (of_decide_eq_true (List.mem_filter.mp hj).2)
  exact hostVar_ofEdge_le (hvert i) (hvert j) (hinj i j hij) _ _

private theorem rootUnit_hostVar_le (k : CaseKey) {u : ColourUnit}
    (hu : u ∈ rootUnitList k.plan) : hostVar u.u u.v u.colour ≤ 6612 := by
  unfold rootUnitList at hu
  rw [List.mem_append] at hu
  rcases hu with hu | hu
  · obtain ⟨a, _, hu⟩ := List.mem_flatMap.mp hu
    obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hu
    apply hostVar_ofEdge_le (by omega) (blockLabel_lt_of_key k a i (List.mem_range.mp hi))
    simp only [blockLabel]
    omega
  · obtain ⟨a, _, hu⟩ := List.mem_flatMap.mp hu
    have hvert (i : Fin (plannedDegree k.plan a)) : blockLabel k.plan a i.val < 58 :=
      blockLabel_lt_of_key k a i.val i.isLt
    have hinj (i j : Fin (plannedDegree k.plan a)) (hij : i ≠ j) :
        blockLabel k.plan a i.val ≠ blockLabel k.plan a j.val := by
      intro he
      apply hij
      apply Fin.ext
      simp only [blockLabel] at he
      omega
    split at hu
    · exact blockUnits_hostVar_le _ hvert hinj false a hu
    · exact blockUnits_hostVar_le _ hvert hinj true a hu
    · simp at hu

private theorem caseUnit_hostVar_le (C : ExpandedCase) {u : ColourUnit}
    (hu : u ∈ caseUnitList C) : hostVar u.u u.v u.colour ≤ 6612 := by
  simp only [caseUnitList, List.mem_append] at hu
  rcases hu with (hu | hu) | hu
  · exact rootUnit_hostVar_le C.key hu
  · exact blockUnits_hostVar_le _ (fun i => (C.marked i).isLt)
      (fun i j hij h => C.marked_injective.ne hij (Fin.ext h)) _ _ hu
  · obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hu
    obtain ⟨hv, hn⟩ := List.mem_filter.mp hv
    have hn' : v ≠ 0 ∧ v ≠ blockLabel C.key.plan C.key.arm C.key.markPosition := by
      simpa using hn
    exact hostVar_ofEdge_le
      (blockLabel_lt_of_key C.key C.key.arm C.key.markPosition C.mark_in_range)
      (List.mem_range.mp hv) hn'.2.symm _ _

/-- Every frozen signed-unit variable lies in the physical tier.  The proof
never evaluates the support-embedding computation hidden in `expandKey`. -/
theorem targetUnit_varsBelow : VarsBelow targetUnitCNF 6612 := by
  unfold targetUnitCNF
  split
  · intro c hc
    simp at hc
  · rename_i C hC
    intro c hc l hl
    obtain ⟨u, hu, rfl⟩ := List.mem_map.mp hc
    have hu' : u ∈ caseUnitList C := by simpa using hu
    have hl' : l = (u.positive, hostVar u.u u.v u.colour) := List.mem_singleton.mp hl
    subst l
    exact caseUnit_hostVar_le C hu'

private theorem edgeExactlyOne_varsBelow {u v : Nat} (hu : u < 58) (hv : v < 58)
    (hne : u ≠ v) : VarsBelow (edgeExactlyOne u v) 6612 := by
  intro c hc l hl
  unfold edgeExactlyOne at hc
  rw [List.mem_append] at hc
  rcases hc with hc | hc
  · have hc' : c = (List.range 4).map (fun d => (true, hostVar u v (Fin.ofNat 4 d))) :=
      List.mem_singleton.mp hc
    subst c
    obtain ⟨d, _, rfl⟩ := List.mem_map.mp hl
    exact hostVar_le_of_host_edge hu hv hne _
  · obtain ⟨d, _, hc⟩ := List.mem_flatMap.mp hc
    obtain ⟨e, _, hc⟩ := List.mem_map.mp hc
    have hc' : [(false, hostVar u v (Fin.ofNat 4 d)),
        (false, hostVar u v (Fin.ofNat 4 e))] = c := hc
    subst c
    simp only [List.mem_cons, List.not_mem_nil, or_false] at hl
    rcases hl with rfl | rfl <;> exact hostVar_le_of_host_edge hu hv hne _

private theorem triangleExclusions_varsBelow {u v w : Nat}
    (hu : u < 58) (hv : v < 58) (hw : w < 58)
    (huv : u ≠ v) (huw : u ≠ w) (hvw : v ≠ w) :
    VarsBelow (triangleExclusions u v w) 6612 := by
  intro c hc l hl
  unfold triangleExclusions at hc
  obtain ⟨d, _, hc⟩ := List.mem_map.mp hc
  have hc' : [(false, hostVar u v (Fin.ofNat 4 d)),
      (false, hostVar u w (Fin.ofNat 4 d)),
      (false, hostVar v w (Fin.ofNat 4 d))] = c := hc
  subst c
  simp only [List.mem_cons, List.not_mem_nil, or_false] at hl
  rcases hl with rfl | rfl | rfl
  · exact hostVar_le_of_host_edge hu hv huv _
  · exact hostVar_le_of_host_edge hu hw huw _
  · exact hostVar_le_of_host_edge hv hw hvw _

/-- All exactly-one and triangle-exclusion clauses use only the physical tier. -/
theorem hostBase_varsBelow : VarsBelow hostBaseCNF 6612 := by
  intro c hc l hl
  unfold hostBaseCNF at hc
  rw [List.mem_append] at hc
  rcases hc with hc | hc
  · obtain ⟨p, hp, hc⟩ := List.mem_flatMap.mp hc
    unfold hostPairs at hp
    obtain ⟨u, hu, hp⟩ := List.mem_flatMap.mp hp
    obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hp
    have huv : u < v := of_decide_eq_true (List.mem_filter.mp hv).2
    exact edgeExactlyOne_varsBelow (List.mem_range.mp hu)
      (List.mem_range.mp (List.mem_filter.mp hv).1) huv.ne c hc l hl
  · obtain ⟨t, ht, hc⟩ := List.mem_flatMap.mp hc
    unfold hostTriplesExact at ht
    obtain ⟨u, hu, ht⟩ := List.mem_flatMap.mp ht
    obtain ⟨v, hv, ht⟩ := List.mem_flatMap.mp ht
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp ht
    have huv : u < v := of_decide_eq_true (List.mem_filter.mp hv).2
    have hvw : v < w := of_decide_eq_true (List.mem_filter.mp hw).2
    exact triangleExclusions_varsBelow (List.mem_range.mp hu)
      (List.mem_range.mp (List.mem_filter.mp hv).1)
      (List.mem_range.mp (List.mem_filter.mp hw).1)
      huv.ne (huv.trans hvw).ne hvw.ne c hc l hl

/-- Every physical-tier base and signed-unit variable is at most `6612`. -/
theorem targetBase_varsBelow : VarsBelow (hostBaseCNF ++ targetUnitCNF) 6612 := by
  intro c hc l hl
  rw [List.mem_append] at hc
  exact hc.elim (fun h => hostBase_varsBelow c h l hl) (fun h => targetUnit_varsBelow c h l hl)

#print axioms targetUnit_varsBelow
#print axioms hostBase_varsBelow
#print axioms targetBase_varsBelow


/-- Prefix sums in the host lexicographic order are monotone (also past `57`). -/
private theorem prefixMono {a b : Nat} (hab : a ≤ b) :
    ((List.range a).map (fun i => 57-i)).sum ≤
    ((List.range b).map (fun i => 57-i)).sum := by
  induction b with
  | zero =>
      have ha : a = 0 := Nat.eq_zero_of_le_zero hab
      subst a
      exact le_rfl
  | succ b ih =>
      by_cases heq : a = b+1
      · subst a; rfl
      · have ha : a ≤ b := by omega
        calc
          _ ≤ ((List.range b).map (fun i => 57-i)).sum := ih ha
          _ ≤ ((List.range (b+1)).map (fun i => 57-i)).sum := by
            simp only [List.range_succ, List.map_append, List.map_singleton,
              List.sum_append, List.sum_singleton]
            omega

private theorem rank_lt_prefixSucc {u v : Nat} (hu : u < 57) (hv : v < 58)
    (huv : u < v) : hostLexRank u v <
      ((List.range (u+1)).map (fun i => 57-i)).sum := by
  simp only [hostLexRank, List.range_succ, List.map_append, List.map_singleton,
    List.sum_append, List.sum_singleton]
  omega

/-- The lexicographic rank is injective on sorted genuine host pairs. -/
theorem hostLexRank_inj_sorted {u v u' v' : Nat}
    (hu : u < 58) (hv : v < 58) (hu' : u' < 58) (hv' : v' < 58)
    (huv : u < v) (hu'v' : u' < v')
    (hr : hostLexRank u v = hostLexRank u' v') : u = u' ∧ v = v' := by
  have huu : u = u' := by
    by_contra hne
    rcases lt_or_gt_of_ne hne with hlt | hgt
    · have ha := rank_lt_prefixSucc (u := u) (v := v) (by omega) hv huv
      have hb := prefixMono (a := u+1) (b := u') (by omega)
      have hc : ((List.range u').map (fun i => 57-i)).sum ≤ hostLexRank u' v' := by
        unfold hostLexRank
        omega
      omega
    · have ha := rank_lt_prefixSucc (u := u') (v := v') (by omega) hv' hu'v'
      have hb := prefixMono (a := u'+1) (b := u) (by omega)
      have hc : ((List.range u).map (fun i => 57-i)).sum ≤ hostLexRank u v := by
        unfold hostLexRank
        omega
      omega
  subst u'
  refine ⟨rfl, ?_⟩
  unfold hostLexRank at hr
  omega

/-- A `hostVar` code has at most one sorted genuine-edge representation. -/
theorem hostVar_inj_sorted {u v u' v' : Fin 58} (huv : u < v) (hu'v' : u' < v')
    {c c' : Fin 4} (he : hostVar u v c = hostVar u' v' c') :
    u = u' ∧ v = v' ∧ c = c' := by
  have huv' : u.val < v.val := huv
  have hu'v'' : u'.val < v'.val := hu'v'
  simp only [hostVar, min_eq_left huv'.le, max_eq_right huv'.le,
    min_eq_left hu'v''.le, max_eq_right hu'v''.le] at he
  have hr : hostLexRank u v = hostLexRank u' v' := by
    have hc := c.isLt
    have hc' := c'.isLt
    omega
  have hp := hostLexRank_inj_sorted u.isLt v.isLt u'.isLt v'.isLt huv hu'v' hr
  have hcval : c.val = c'.val := by
    have hc := c.isLt
    have hc' := c'.isLt
    omega
  exact ⟨Fin.ext hp.1, Fin.ext hp.2, Fin.ext hcval⟩

/-- A sorted genuine-edge representation of one DIMACS variable. -/
structure HostVarRep (a : Nat) where
  u : Fin 58
  v : Fin 58
  colour : Fin 4
  sorted : u < v
  encode : hostVar u v colour = a

/-- Canonical physical valuation after the common host and palette permutations.
Variables outside the genuine sorted-edge range are irrelevant and default false. -/
noncomputable def realizedValuation (G : EdgeCol (Fin 58) 4)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) : Valuation :=
  fun a => if h : Nonempty (HostVarRep a) then
    let r := Classical.choice h
    decide (G.col (e r.u) (e r.v) = p r.colour)
  else false

/-- The representation choice in `realizedValuation` is irrelevant on host edges. -/
theorem realizedValuation_hostVar (G : EdgeCol (Fin 58) 4)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    {u v : Fin 58} (huv : u < v) (c : Fin 4) :
    realizedValuation G e p (hostVar u v c) = decide (G.col (e u) (e v) = p c) := by
  unfold realizedValuation
  split
  · rename_i h
    let r := Classical.choice h
    change decide (G.col (e r.u) (e r.v) = p r.colour) = _
    have hr : hostVar r.u r.v r.colour = hostVar u v c := r.encode
    have hi := hostVar_inj_sorted r.sorted huv hr
    change r.u = u ∧ r.v = v ∧ r.colour = c at hi
    rw [hi.1, hi.2.1, hi.2.2]
  · rename_i h
    exact (h ⟨⟨u,v,c,huv,rfl⟩⟩).elim

/-- The same evaluation rule on either orientation of a genuine edge. -/
theorem realizedValuation_hostVar_unsorted (G : EdgeCol (Fin 58) 4)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    {u v : Fin 58} (hne : u ≠ v) (c : Fin 4) :
    realizedValuation G e p (hostVar u v c) = decide (G.col (e u) (e v) = p c) := by
  rcases lt_or_gt_of_ne hne with huv | hvu
  · exact realizedValuation_hostVar G e p huv c
  · have hcode : hostVar u v c = hostVar v u c := by
      have h : v.val < u.val := hvu
      simp only [hostVar, min_eq_right h.le, max_eq_left h.le,
        min_eq_left h.le, max_eq_right h.le]
    calc
      realizedValuation G e p (hostVar u v c) = realizedValuation G e p (hostVar v u c) :=
        congrArg (realizedValuation G e p) hcode
      _ = decide (G.col (e v) (e u) = p c) := realizedValuation_hostVar G e p hvu c
      _ = decide (G.col (e u) (e v) = p c) := by rw [G.symm (e v) (e u)]

#print axioms hostVar_inj_sorted
#print axioms realizedValuation_hostVar


private theorem finOfNat_val (c : Fin 4) : Fin.ofNat 4 c.val = c :=
  Fin.ext (Nat.mod_eq_of_lt c.isLt)

private theorem finOfNat_ne_of_lt {a b : Nat} (ha : a < 4) (hb : b < 4)
    (hab : a ≠ b) : Fin.ofNat 4 a ≠ Fin.ofNat 4 b := by
  intro he
  have hev := congrArg Fin.val he
  have hav : (Fin.ofNat 4 a).val = a := Nat.mod_eq_of_lt ha
  have hbv : (Fin.ofNat 4 b).val = b := Nat.mod_eq_of_lt hb
  omega

/-- The physical valuation satisfies the generator's exact exactly-one family. -/
theorem formulaSat_edgeExactlyOne (G : EdgeCol (Fin 58) 4)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    {u v : Fin 58} (huv : u < v) :
    FormulaSat (realizedValuation G e p) (edgeExactlyOne u v) := by
  intro c hc
  unfold edgeExactlyOne at hc
  rw [List.mem_append] at hc
  rcases hc with hc | hc
  · let d : Fin 4 := p.symm (G.col (e u) (e v))
    have hd : G.col (e u) (e v) = p d := (p.apply_symm_apply (G.col (e u) (e v))).symm
    have hc' : c = (List.range 4).map (fun a => (true, hostVar u v (Fin.ofNat 4 a))) :=
      List.mem_singleton.mp hc
    subst c
    refine ⟨(true, hostVar u v d), ?_, ?_⟩
    · exact List.mem_map.mpr ⟨d.val, List.mem_range.mpr d.isLt, by rw [finOfNat_val]⟩
    · simp [realizedValuation_hostVar G e p huv, hd]
  · obtain ⟨a, ha, hc⟩ := List.mem_flatMap.mp hc
    obtain ⟨b, hb, hc⟩ := List.mem_map.mp hc
    have hab : a < b := of_decide_eq_true (List.mem_filter.mp hb).2
    have hc' : [(false, hostVar u v (Fin.ofNat 4 a)),
        (false, hostVar u v (Fin.ofNat 4 b))] = c := hc
    subst c
    by_cases ha' : G.col (e u) (e v) = p (Fin.ofNat 4 a)
    · have hne : Fin.ofNat 4 a ≠ Fin.ofNat 4 b :=
        finOfNat_ne_of_lt (by have := List.mem_range.mp ha; omega)
          (by have := List.mem_range.mp (List.mem_filter.mp hb).1; omega) hab.ne
      have hb' : G.col (e u) (e v) ≠ p (Fin.ofNat 4 b) := by
        intro hb'
        exact hne (p.injective (ha'.symm.trans hb'))
      simp only [Fin.ofNat_eq_cast] at hb'
      refine ⟨(false, hostVar u v (Fin.ofNat 4 b)), by simp, ?_⟩
      simp [realizedValuation_hostVar G e p huv, Fin.ofNat_eq_cast, hb']
    · simp only [Fin.ofNat_eq_cast] at ha'
      refine ⟨(false, hostVar u v (Fin.ofNat 4 a)), by simp, ?_⟩
      simp [realizedValuation_hostVar G e p huv, Fin.ofNat_eq_cast, ha']

/-- Triangle-freeness after the same host permutation satisfies every emitted
four-colour exclusion clause, in its exact list position. -/
theorem formulaSat_triangleExclusions (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    {u v w : Fin 58} (huv : u < v) (hvw : v < w) :
    FormulaSat (realizedValuation G e p) (triangleExclusions u v w) := by
  have huw : u < w := huv.trans hvw
  have ht := hG (e u) (e v) (e w) (e.injective.ne huv.ne)
    (e.injective.ne hvw.ne) (e.injective.ne huw.ne)
  intro c hc
  unfold triangleExclusions at hc
  obtain ⟨d, hd, hc⟩ := List.mem_map.mp hc
  have hc' : [(false, hostVar u v (Fin.ofNat 4 d)),
      (false, hostVar u w (Fin.ofNat 4 d)),
      (false, hostVar v w (Fin.ofNat 4 d))] = c := hc
  subst c
  by_cases huv' : G.col (e u) (e v) = p (Fin.ofNat 4 d)
  · by_cases huw' : G.col (e u) (e w) = p (Fin.ofNat 4 d)
    · have hvw' : G.col (e v) (e w) ≠ p (Fin.ofNat 4 d) := by
        intro hvw'
        exact ht ⟨huv'.trans huw'.symm, huw'.trans hvw'.symm⟩
      simp only [Fin.ofNat_eq_cast] at hvw'
      refine ⟨(false, hostVar v w (Fin.ofNat 4 d)), by simp, ?_⟩
      simp [realizedValuation_hostVar G e p hvw, Fin.ofNat_eq_cast, hvw']
    · simp only [Fin.ofNat_eq_cast] at huw'
      refine ⟨(false, hostVar u w (Fin.ofNat 4 d)), by simp, ?_⟩
      simp [realizedValuation_hostVar G e p huw, Fin.ofNat_eq_cast, huw']
  · simp only [Fin.ofNat_eq_cast] at huv'
    refine ⟨(false, hostVar u v (Fin.ofNat 4 d)), by simp, ?_⟩
    simp [realizedValuation_hostVar G e p huv, Fin.ofNat_eq_cast, huv']

/-- The complete physical host base follows from just triangle-freeness. -/
theorem hostBase_satisfiable (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) :
    FormulaSat (realizedValuation G e p) hostBaseCNF := by
  intro c hc
  unfold hostBaseCNF at hc
  rw [List.mem_append] at hc
  rcases hc with hc | hc
  · obtain ⟨q, hq, hc⟩ := List.mem_flatMap.mp hc
    unfold hostPairs at hq
    obtain ⟨u, hu, hq⟩ := List.mem_flatMap.mp hq
    obtain ⟨v, hv, rfl⟩ := List.mem_map.mp hq
    have huv : u < v := of_decide_eq_true (List.mem_filter.mp hv).2
    let uf : Fin 58 := ⟨u, List.mem_range.mp hu⟩
    let vf : Fin 58 := ⟨v, List.mem_range.mp (List.mem_filter.mp hv).1⟩
    exact formulaSat_edgeExactlyOne G e p (u := uf) (v := vf) huv c hc
  · obtain ⟨t, ht, hc⟩ := List.mem_flatMap.mp hc
    unfold hostTriplesExact at ht
    obtain ⟨u, hu, ht⟩ := List.mem_flatMap.mp ht
    obtain ⟨v, hv, ht⟩ := List.mem_flatMap.mp ht
    obtain ⟨w, hw, rfl⟩ := List.mem_map.mp ht
    have huv : u < v := of_decide_eq_true (List.mem_filter.mp hv).2
    have hvw : v < w := of_decide_eq_true (List.mem_filter.mp hw).2
    let uf : Fin 58 := ⟨u, List.mem_range.mp hu⟩
    let vf : Fin 58 := ⟨v, List.mem_range.mp (List.mem_filter.mp hv).1⟩
    let wf : Fin 58 := ⟨w, List.mem_range.mp (List.mem_filter.mp hw).1⟩
    exact formulaSat_triangleExclusions G hG e p (u := uf) (v := vf) (w := wf)
      huv hvw c hc

#print axioms hostBase_satisfiable


/-- `RealizesCase` with its two shared permutations exposed. -/
def RealizesCaseAt (G : EdgeCol (Fin 58) 4) (C : ExpandedCase)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4)) : Prop :=
  ∀ u ∈ caseUnits C, ∃ i j : Fin 58, i.val = u.u ∧ j.val = u.v ∧ i ≠ j ∧
    (G.col (e i) (e j) = p u.colour ↔ u.positive = true)

/-- Every sorted frozen signed unit agrees with its physical realization. -/
theorem targetUnit_satisfiable_of_expanded (G : EdgeCol (Fin 58) 4)
    (C : ExpandedCase) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (hC : expandKey targetKey = some C) (hr : RealizesCaseAt G C e p) :
    FormulaSat (realizedValuation G e p) targetUnitCNF := by
  unfold targetUnitCNF
  rw [hC]
  intro c hc
  obtain ⟨u, hu, rfl⟩ := List.mem_map.mp hc
  have hu' : u ∈ caseUnitList C := by simpa using hu
  obtain ⟨i,j,hi,hj,hij,hcol⟩ := hr u (List.mem_toFinset.mpr hu')
  refine ⟨(u.positive, hostVar u.u u.v u.colour), by simp, ?_⟩
  rw [← hi, ← hj, realizedValuation_hostVar_unsorted G e p hij]
  cases hp : u.positive
  · have hn : G.col (e i) (e j) ≠ p u.colour := by
      intro he
      have ht := hcol.mp he
      simp [hp] at ht
    simp [hn]
  · have he : G.col (e i) (e j) = p u.colour := hcol.mpr (by simp [hp])
    simp [he]

/-- Both physical base premises follow from a triangle-free expanded-row model. -/
theorem targetBase_satisfiable_of_expanded (G : EdgeCol (Fin 58) 4)
    (hG : TriangleFree G) (C : ExpandedCase)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (hC : expandKey targetKey = some C) (hr : RealizesCaseAt G C e p) :
    FormulaSat (realizedValuation G e p) (hostBaseCNF ++ targetUnitCNF) :=
  (formulaSat_append _ _ _).mpr
    ⟨hostBase_satisfiable G hG e p, targetUnit_satisfiable_of_expanded G C e p hC hr⟩

/-- Existence form for the complete ordinary physical base and signed units. -/
theorem targetBase_satisfiable_of_realizesKey (G : EdgeCol (Fin 58) 4)
    (hG : TriangleFree G) (hk : RealizesKey G targetKey) :
    ∃ v : Valuation, FormulaSat v (hostBaseCNF ++ targetUnitCNF) := by
  obtain ⟨C,hC,e,p,hr⟩ := hk
  exact ⟨realizedValuation G e p, targetBase_satisfiable_of_expanded G hG C e p hC hr⟩

/-- Exact whole-parent assembly with the former `hbase` and `hvars` obligations
closed.  The suffix readiness is still required and is not asserted here. -/
theorem targetParent_satisfiable_of_expanded_ready (G : EdgeCol (Fin 58) 4)
    (hG : TriangleFree G) (C : ExpandedCase)
    (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (hC : expandKey targetKey = some C) (hr : RealizesCaseAt G C e p)
    (hready : ChainReady 6612 (realizedValuation G e p) targetSuffixSteps) :
    ∃ w : Valuation, (∀ a ≤ 6612, w a = realizedValuation G e p a) ∧
      FormulaSat w targetParentCNF :=
  targetParent_satisfiable_of_ready (realizedValuation G e p)
    (targetBase_satisfiable_of_expanded G hG C e p hC hr)
    targetBase_varsBelow hready

#print axioms targetUnit_satisfiable_of_expanded
#print axioms targetBase_satisfiable_of_realizesKey
#print axioms targetParent_satisfiable_of_expanded_ready
