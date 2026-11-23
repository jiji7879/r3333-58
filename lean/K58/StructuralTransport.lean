import K58.CachedPlacement

namespace K58

private theorem edge_swap (u v : ℕ) (c : Fin 4) (b : Bool) :
    ColourUnit.ofEdge u v c b = ColourUnit.ofEdge v u c b := by
  simp only [ColourUnit.ofEdge,min_comm u v,max_comm u v]

private theorem relabel_edge (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (u v : Fin 58) (c : Fin 4) (b : Bool) :
    (ColourUnit.ofEdge u.val v.val c b).relabel e p =
    ColourUnit.ofEdge (e u).val (e v).val (p c) b := by
  have h (i : Fin 58) : Fin.ofNat 58 i.val = i := Fin.ext (Nat.mod_eq_of_lt i.isLt)
  rcases le_total u.val v.val with huv | hvu
  · simp [ColourUnit.relabel,ColourUnit.ofEdge,min_eq_left huv,max_eq_right huv]
  · change ColourUnit.ofEdge (e (Fin.ofNat 58 (min u.val v.val))).val
      (e (Fin.ofNat 58 (max u.val v.val))).val (p c) b = _
    rw [min_eq_right hvu,max_eq_left hvu,h,h,edge_swap]

private theorem block_member {n : ℕ} (f : Fin n → Fin 58) (t : Bool) (a : Fin 4) (u : ColourUnit) :
    u ∈ blockUnits (fun i => (f i).val) t a ↔
      ∃ i j, i ≠ j ∧ ColourUnit.ofEdge (f i).val (f j).val (a.succAbove ((template n t).col i j)) = u := by
  constructor
  · intro h
    obtain ⟨i,_,hi⟩ := List.mem_flatMap.mp h
    obtain ⟨j,hj,he⟩ := List.mem_map.mp hi
    exact ⟨i,j,(of_decide_eq_true (List.mem_filter.mp hj).2).ne,he⟩
  · rintro ⟨i,j,h,he⟩
    rcases lt_or_gt_of_ne h with hlt | hgt
    · exact List.mem_flatMap.mpr ⟨i,List.mem_finRange _,List.mem_map.mpr
        ⟨j,List.mem_filter.mpr ⟨List.mem_finRange _,decide_eq_true hlt⟩,he⟩⟩
    · have he' : ColourUnit.ofEdge (f j).val (f i).val (a.succAbove ((template n t).col j i)) = u := by
        rw [(template n t).symm j i,edge_swap,he]
      exact List.mem_flatMap.mpr ⟨j,List.mem_finRange _,List.mem_map.mpr
        ⟨i,List.mem_filter.mpr ⟨List.mem_finRange _,decide_eq_true hgt⟩,he'⟩⟩

private theorem block_transport {n m : ℕ} (f : Fin n → Fin 58) (g : Fin m → Fin 58)
    (t s : Bool) (a b : Fin 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (z : Fin n ≃ Fin m) (labels : ∀ i, e (f i) = g (z i))
    (edges : ∀ i j, i ≠ j → p (a.succAbove ((template n t).col i j)) =
      b.succAbove ((template m s).col (z i) (z j))) :
    (blockUnits (fun i => (g i).val) s b).toFinset =
      (blockUnits (fun i => (f i).val) t a).toFinset.image (fun u => u.relabel e p) := by
  ext u
  simp only [Finset.mem_image,List.mem_toFinset,block_member]
  constructor
  · rintro ⟨i,j,h,rfl⟩
    let x := z.symm i
    let y := z.symm j
    have hn : x ≠ y := z.symm.injective.ne h
    refine ⟨_,⟨x,y,hn,rfl⟩,?_⟩
    simp only [relabel_edge,labels,edges x y hn,x,y,Equiv.apply_symm_apply]
  · rintro ⟨_,⟨i,j,hn,rfl⟩,rfl⟩
    exact ⟨z i,z j,z.injective.ne hn,by rw [relabel_edge,labels,labels,edges i j hn]⟩

private def hits {n : ℕ} (f : Fin n → Fin 58) (w : Fin 58) : Bool :=
  (List.finRange n).any fun i => (f i).val == w.val

private theorem star_member {n : ℕ} (q : Fin 58) (a : Fin 4) (f : Fin n → Fin 58) (u : ColourUnit) :
    u ∈ starUnitList q.val a f ↔ ∃ w : Fin 58, w ≠ 0 ∧ w ≠ q ∧
      ColourUnit.ofEdge q.val w.val a (hits f w) = u := by
  constructor
  · intro h
    obtain ⟨v,hv,he⟩ := List.mem_map.mp h
    obtain ⟨hr,hn⟩ := List.mem_filter.mp hv
    let w : Fin 58 := ⟨v,List.mem_range.mp hr⟩
    have hn' : v ≠ 0 ∧ v ≠ q.val := by simpa using hn
    exact ⟨w,fun h => hn'.1 (congrArg Fin.val h),fun h => hn'.2 (congrArg Fin.val h),he⟩
  · rintro ⟨w,h0,hq,he⟩
    exact List.mem_map.mpr ⟨w.val,List.mem_filter.mpr ⟨List.mem_range.mpr w.isLt,by
      simpa using And.intro (fun h => h0 (Fin.ext h)) (fun h => hq (Fin.ext h))⟩,he⟩

private theorem hits_transport {n m : ℕ} (f : Fin n → Fin 58) (g : Fin m → Fin 58)
    (e : Equiv.Perm (Fin 58)) (z : Fin n ≃ Fin m) (labels : ∀ i, e (f i) = g (z i)) (w : Fin 58) :
    hits f w = hits g (e w) := by
  apply Bool.eq_iff_iff.mpr
  simp only [hits,List.any_eq_true,List.mem_finRange,true_and,beq_iff_eq,← Fin.ext_iff]
  constructor
  · rintro ⟨i,rfl⟩
    exact ⟨z i,(labels i).symm⟩
  · rintro ⟨j,hj⟩
    refine ⟨z.symm j,e.injective ?_⟩
    rwa [labels, z.apply_symm_apply]

private theorem star_transport {n m : ℕ} (f : Fin n → Fin 58) (g : Fin m → Fin 58)
    (q : Fin 58) (a : Fin 4) (e : Equiv.Perm (Fin 58)) (p : Equiv.Perm (Fin 4))
    (z : Fin n ≃ Fin m) (h0 : e 0 = 0) (labels : ∀ i, e (f i) = g (z i)) :
    (starUnitList (e q).val (p a) g).toFinset =
      (starUnitList q.val a f).toFinset.image (fun u => u.relabel e p) := by
  ext u
  simp only [Finset.mem_image,List.mem_toFinset,star_member]
  constructor
  · rintro ⟨w,hw,hq,rfl⟩
    let v := e.symm w
    have hv : e v = w := e.apply_symm_apply _
    have hn0 : v ≠ 0 := fun h => hw (hv.symm.trans ((congrArg e h).trans h0))
    have hnq : v ≠ q := fun h => hq (hv.symm.trans (congrArg e h))
    refine ⟨_,⟨v,hn0,hnq,rfl⟩,?_⟩
    rw [relabel_edge,hits_transport f g e z labels v,hv]
  · rintro ⟨_,⟨w,h0w,hqw,rfl⟩,rfl⟩
    refine ⟨e w,fun h => h0w (e.injective (h.trans h0.symm)),e.injective.ne hqw,?_⟩
    rw [relabel_edge,hits_transport f g e z labels w]

/-- One aligned permutation of the second template transports both its internal
edges and its entire signed star. The root-unit equality is independent of placement. -/
theorem transport_of_alignment {A B : ExpandedCase} (e : Equiv.Perm (Fin 58))
    (p : Equiv.Perm (Fin 4)) (z : Fin A.key.secondSize ≃ Fin B.key.secondSize)
    (rootEdges : (rootUnitList A.key.plan).toFinset.image (fun u => u.relabel e p) =
      (rootUnitList B.key.plan).toFinset)
    (h0 : e 0 = 0) (hq : e (caseMark A) = caseMark B) (ha : p A.key.arm = B.key.arm)
    (edges : ∀ i j, i ≠ j → p (A.key.arm.succAbove ((template _ A.key.secondTwisted).col i j)) =
      B.key.arm.succAbove ((template _ B.key.secondTwisted).col (z i) (z j)))
    (labels : ∀ i, e (A.marked i) = B.marked (z i)) : UnitTransport A B e p := by
  have av : (caseMark A).val = blockLabel A.key.plan A.key.arm A.key.markPosition := slotLabel_val _ _ _
  have bv : (caseMark B).val = blockLabel B.key.plan B.key.arm B.key.markPosition := slotLabel_val _ _ _
  have star := star_transport A.marked B.marked (caseMark A) A.key.arm e p z h0 labels
  rw [hq,ha,av,bv] at star
  simp only [UnitTransport,caseUnits,caseUnitList,List.toFinset_append,Finset.image_union,rootEdges,
    ← block_transport _ _ _ _ _ _ e p z labels edges, ← star]

/-- A finite tuple encoded in low-to-high digits of a natural number. -/
def packedValue (w width i : ℕ) : ℕ := (w >>> (width*i)) % (2^width)

def packedMap (n width w : ℕ) [NeZero n] (i : Fin n) : Fin n := Fin.ofNat n (packedValue w width i.val)

noncomputable def packedPerm (n width w inverse : ℕ) [NeZero n]
    (h : ∀ i : Fin n, packedValue inverse width (packedMap n width w i).val = i.val) : Equiv.Perm (Fin n) :=
  Equiv.ofBijective (packedMap n width w) (Finite.injective_iff_bijective.mp (fun i j he =>
    Fin.ext ((h i).symm.trans ((congrArg (fun x : Fin n => packedValue inverse width x.val) he).trans (h j)))))

def packedLabels {n : ℕ} (w : ℕ) (i : Fin n) : Fin 58 := Fin.ofNat 58 (packedValue w 6 i.val)

structure Marking (f : CaseKey) where
  labels : Fin f.secondSize → Fin 58
  injective : Function.Injective labels
  rootBound : f.rootPosition < f.secondSize
  rootZero : labels ⟨_,rootBound⟩ = 0
  markBound : f.markPosition < plannedDegree f.plan f.arm

def packedMarking (f : CaseKey) (w inverse : ℕ) (hr : f.rootPosition < f.secondSize)
    (hm : f.markPosition < plannedDegree f.plan f.arm)
    (hi : ∀ i : Fin f.secondSize, packedValue inverse 4 (packedLabels w i).val = i.val)
    (hz : packedLabels w (⟨f.rootPosition,hr⟩ : Fin f.secondSize) = 0) : Marking f :=
  ⟨packedLabels w,fun i j h => Fin.ext ((hi i).symm.trans ((congrArg (fun x : Fin 58 =>
    packedValue inverse 4 x.val) h).trans (hi j))),hr,hz,hm⟩

def Marking.asCase {f : CaseKey} (M : Marking f) (v : Fin 3 → ℕ) : ExpandedCase :=
  ⟨f.atPlacement v,M.labels,M.injective,M.rootBound,M.rootZero,M.markBound⟩

private theorem PlacementTables.sources {f : CaseKey} (T : PlacementTables f) (c : Fin 3) :
    (T.table c).1 = supportAt f ⟨_,T.rootBound⟩ (f.arm.succAbove c) := by
  let r : Fin f.secondSize := ⟨_,T.rootBound⟩
  let b := f.arm.succAbove c
  let src := supportAt f r b
  have ht : (supportChoices f b src).bind (fun ws => some (src,ws)) = some (T.table c) := T.exactTable c
  cases hc : supportChoices f b src with
  | none => simp [hc] at ht
  | some ws =>
    have he : (src,ws) = T.table c := by simpa [hc] using ht
    exact congrArg Prod.fst he.symm

def PlacementTables.matches {f : CaseKey} (T : PlacementTables f) (v : Fin 3 → ℕ) (M : Marking f) : Bool :=
  (List.finRange 3).all fun c =>
    let (src,ws) := T.table c
    match ws[v c]? with
    | none => false
    | some word => decide (src.zip (word.map (blockLabel f.plan (f.arm.succAbove c))) =
        src.map (fun x => (x,(M.labels x).val)))

theorem PlacementTables.expand_marking {f : CaseKey} (T : PlacementTables f)
    (v : Fin 3 → ℕ) (M : Marking f) (h : T.matches v M = true) :
    expandKey (f.atPlacement v) = some (M.asCase v) := by
  apply expandKey_of_labels f v M.rootBound M.markBound M.labels M.injective M.rootZero
  intro c
  have test := List.all_eq_true.mp h c (List.mem_finRange _)
  obtain ⟨src,ws,ht⟩ : ∃ src ws, T.table c = (src,ws) := ⟨_,_,rfl⟩
  have srcEq := T.sources c
  rw [ht] at srcEq
  change src = _ at srcEq
  subst src
  have tables := T.exactTable c
  rw [ht] at tables
  change (match (T.table c).2[v c]? with
    | none => false
    | some word => decide ((T.table c).1.zip (word.map (blockLabel f.plan (f.arm.succAbove c))) =
      (T.table c).1.map (fun x => (x,(M.labels x).val)))) = true at test
  rw [ht] at test
  cases hw : ws[v c]? with
  | none => simp [hw] at test
  | some word => exact ⟨ws,word,tables,hw,by simpa [hw] using test⟩

def keyMark (f : CaseKey) : Fin 58 := Fin.ofNat 58 (blockLabel f.plan f.arm f.markPosition)

/-- Fixed part of a transport, valid for every placement in these families. -/
structure Alignment (f g : CaseKey) where
  host : Equiv.Perm (Fin 58)
  palette : Equiv.Perm (Fin 4)
  localMap : Fin f.secondSize ≃ Fin g.secondSize
  rootEdges : (rootUnitList f.plan).toFinset.image (fun u => u.relabel host palette) =
    (rootUnitList g.plan).toFinset
  root : host 0 = 0
  mark : host (keyMark f) = keyMark g
  arm : palette f.arm = g.arm
  edges : ∀ i j, i ≠ j → palette (f.arm.succAbove ((template _ f.secondTwisted).col i j)) =
    g.arm.succAbove ((template _ g.secondTwisted).col (localMap i) (localMap j))

theorem root_transport_of_bits {P Q : Plan} {e : Equiv.Perm (Fin 58)} {p : Equiv.Perm (Fin 4)}
    (h : unitBits ((rootUnitList P).map (fun u => u.relabel e p)) = unitBits (rootUnitList Q)) :
    (rootUnitList P).toFinset.image (fun u => u.relabel e p) = (rootUnitList Q).toFinset := by
  ext u
  have hh := congrArg (fun n : ℕ => n.testBit u.bitIndex = true) h
  simpa only [Finset.mem_image,List.mem_toFinset,List.mem_map,unitBits_member] using Iff.of_eq hh

theorem covered_aligned {f g : CaseKey} {v w : Fin 3 → ℕ} (T : PlacementTables f) (U : PlacementTables g)
    (M : Marking f) (N : Marking g) (a : Alignment f g) (hj : g.atPlacement w ∈ frozenKeys)
    (hm : T.matches v M = true) (hn : U.matches w N = true)
    (labels : ∀ i, a.host (M.labels i) = N.labels (a.localMap i)) : CoveredKey (f.atPlacement v) := by
  right
  intro A hA
  have hc := T.expand_marking v M hm
  rw [hc] at hA
  cases hA
  exact ⟨_,hj,_,U.expand_marking w N hn,a.host,a.palette,transport_of_alignment a.host a.palette
    a.localMap a.rootEdges a.root a.mark a.arm a.edges labels⟩

end K58
