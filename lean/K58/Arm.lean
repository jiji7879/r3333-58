/-
K58 supplement (swarm smwr0lr3q, member m8): the arm structure of a critical
neighbourhood.

* `sum_inter_nbr` : the double count that splits a colour class by the colour of
  the edge to another vertex of that class;
* `sender_split` : L3 -- a sender inside a colour class meets each *other* colour
  class of the centre in exactly 4 or 5 points, with at most one 4;
* `arm_degree_partition` : inside a 15-arm every vertex has arm-internal colour
  degrees a permutation of (5,5,4); inside a 14-arm they are at most 5 with sum
  13, hence a permutation of (5,4,4) or of (5,5,3).
-/
import K58.Mixture
import K58.Corollaries
import K58.DegreeCap

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

theorem mem_nbr {G : EdgeCol V 4} {i j : V} {a : Fin 4} :
    j ∈ nbr G i a ↔ j ≠ i ∧ G.col i j = a := by
  simp [nbr]

theorem nbr_symm_mem (G : EdgeCol V 4) {r a : V} {c : Fin 4} (ha : a ∈ nbr G r c) :
    r ∈ nbr G a c := by
  rw [mem_nbr] at ha ⊢
  exact ⟨ha.1.symm, by rw [G.symm a r]; exact ha.2⟩

/-- The colour-`c` class of `a` meets the colour-`c` class of `r` trivially when
`a` itself lies in the colour-`c` class of `r`. -/
theorem inter_nbr_self_colour_empty (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    (c : Fin 4) (ha : a ∈ nbr G r c) : (nbr G a c) ∩ (nbr G r c) = ∅ := by
  rw [Finset.eq_empty_iff_forall_notMem]
  intro y hy
  obtain ⟨h1, h2⟩ := Finset.mem_inter.mp hy
  have hcol : G.col a y = c := (mem_nbr.mp h1).2
  have hne : a ≠ y := ((mem_nbr.mp h1).1).symm
  exact nbr_indep G h r c a ha y h2 hne hcol

/-- The pairwise disjointness of the colour classes of `u` inside a class of `x`. -/
theorem pairwiseDisjoint_inter_nbr (G : EdgeCol V 4) (x u : V) (c : Fin 4)
    (S : Finset (Fin 4)) :
    (S : Set (Fin 4)).PairwiseDisjoint (fun f => (nbr G x c) ∩ (nbr G u f)) := by
  intro f _ g _ hfg
  show Disjoint ((nbr G x c) ∩ (nbr G u f)) ((nbr G x c) ∩ (nbr G u g))
  rw [Finset.disjoint_left]
  intro v hv hv'
  obtain ⟨-, hvf⟩ := Finset.mem_inter.mp hv
  obtain ⟨-, hvg⟩ := Finset.mem_inter.mp hv'
  exact hfg ((mem_nbr.mp hvf).2.symm.trans (mem_nbr.mp hvg).2)

/-- **The double count.** If `u` is a colour-`c` neighbour of `x`, then the other
colour-`c` neighbours of `x` are partitioned by the colour of the edge joining
them to `u`. -/
theorem sum_inter_nbr (G : EdgeCol V 4) (x u : V) (c : Fin 4) (hu : u ∈ nbr G x c) :
    ∑ f : Fin 4, ((nbr G x c) ∩ (nbr G u f)).card = (nbr G x c).card - 1 := by
  have hunion : (Finset.univ : Finset (Fin 4)).biUnion (fun f => (nbr G x c) ∩ (nbr G u f))
      = (nbr G x c).erase u := by
    ext v
    constructor
    · intro hv
      rw [Finset.mem_biUnion] at hv
      obtain ⟨f, -, hvf⟩ := hv
      obtain ⟨hvx, hvu⟩ := Finset.mem_inter.mp hvf
      exact Finset.mem_erase.mpr ⟨(mem_nbr.mp hvu).1, hvx⟩
    · intro hv
      rw [Finset.mem_erase] at hv
      obtain ⟨hvu, hvx⟩ := hv
      rw [Finset.mem_biUnion]
      refine ⟨G.col u v, Finset.mem_univ _, ?_⟩
      exact Finset.mem_inter.mpr ⟨hvx, mem_nbr.mpr ⟨hvu, rfl⟩⟩
  have hcard := Finset.card_biUnion (pairwiseDisjoint_inter_nbr G x u c Finset.univ)
  rw [hunion, Finset.card_erase_of_mem hu] at hcard
  exact hcard.symm

/-- The same double count with the vanishing colour `c` removed. -/
theorem sum_inter_nbr_ne (G : EdgeCol V 4) (h : TriangleFree G) (x u : V) (c : Fin 4)
    (hu : u ∈ nbr G x c) :
    ∑ f ∈ Finset.univ.filter (fun f : Fin 4 => f ≠ c),
      ((nbr G x c) ∩ (nbr G u f)).card = (nbr G x c).card - 1 := by
  have hunion : (Finset.univ.filter (fun f : Fin 4 => f ≠ c)).biUnion
        (fun f => (nbr G x c) ∩ (nbr G u f)) = (nbr G x c).erase u := by
    ext v
    constructor
    · intro hv
      rw [Finset.mem_biUnion] at hv
      obtain ⟨f, -, hvf⟩ := hv
      obtain ⟨hvx, hvu⟩ := Finset.mem_inter.mp hvf
      exact Finset.mem_erase.mpr ⟨(mem_nbr.mp hvu).1, hvx⟩
    · intro hv
      rw [Finset.mem_erase] at hv
      obtain ⟨hvu, hvx⟩ := hv
      have hnc : G.col u v ≠ c := by
        intro hc
        have hmem : v ∈ (nbr G u c) ∩ (nbr G x c) :=
          Finset.mem_inter.mpr ⟨mem_nbr.mpr ⟨hvu, hc⟩, hvx⟩
        rw [inter_nbr_self_colour_empty G h x u c hu] at hmem
        exact absurd hmem (Finset.notMem_empty v)
      rw [Finset.mem_biUnion]
      refine ⟨G.col u v, ?_, ?_⟩
      · rw [Finset.mem_filter]
        exact ⟨Finset.mem_univ _, hnc⟩
      · exact Finset.mem_inter.mpr ⟨hvx, mem_nbr.mpr ⟨hvu, rfl⟩⟩
  have hcard := Finset.card_biUnion
    (pairwiseDisjoint_inter_nbr G x u c (Finset.univ.filter (fun f : Fin 4 => f ≠ c)))
  rw [hunion, Finset.card_erase_of_mem hu] at hcard
  exact hcard.symm

/-- A counting bound: if a sum of at most three terms, each at most 5, is at
least 14, then every term is at least 4. -/
theorem le_of_sum_ge_of_bound {α : Type*} [DecidableEq α] (S : Finset α) (F : α → ℕ) (f : α)
    (hf : f ∈ S) (hcard : S.card ≤ 3) (hle : ∀ g ∈ S, F g ≤ 5) (hsum : 14 ≤ ∑ g ∈ S, F g) :
    4 ≤ F f := by
  have h1 : F f + ∑ g ∈ S.erase f, F g = ∑ g ∈ S, F g := Finset.add_sum_erase S F hf
  have h2 : ∑ g ∈ S.erase f, F g ≤ (S.erase f).card * 5 := by
    calc ∑ g ∈ S.erase f, F g ≤ ∑ g ∈ S.erase f, 5 :=
          Finset.sum_le_sum (fun g hg => hle g (Finset.mem_erase.mp hg).2)
      _ = (S.erase f).card * 5 := Finset.sum_const_nat (fun g _ => rfl)
  have h3 : (S.erase f).card ≤ 2 := by
    have h4 := Finset.card_erase_of_mem hf
    omega
  omega

/-- The set of colours other than `c` has three elements. -/
theorem card_filter_ne_three (c : Fin 4) :
    (Finset.univ.filter (fun f : Fin 4 => f ≠ c)).card ≤ 3 := by
  rw [show (Finset.univ.filter (fun f : Fin 4 => f ≠ c)) = Finset.univ.erase c from by
    ext x; simp [Finset.mem_erase, and_comm]]
  rw [Finset.card_erase_of_mem (Finset.mem_univ c)]
  simp

/-- **L3, the 4/5 split.** A vertex `a` of the colour-`c` class of `r` whose
colour-`c` degree is at least 15 meets each other colour class of `r` in exactly
4 or 5 points, and at most one of them in 4. -/
theorem sender_split (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4) (a : V)
    (ha : a ∈ nbr G r c) (hs : 15 ≤ (nbr G a c).card) (f : Fin 4) (hf : f ≠ c) :
    4 ≤ ((nbr G a c) ∩ (nbr G r f)).card ∧ ((nbr G a c) ∩ (nbr G r f)).card ≤ 5 := by
  have hr : r ∈ nbr G a c := nbr_symm_mem G ha
  have hsum : 14 ≤ ∑ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
      ((nbr G a c) ∩ (nbr G r g)).card := by
    rw [sum_inter_nbr_ne G h a r c hr]
    omega
  have hfS : f ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c) := by
    rw [Finset.mem_filter]
    exact ⟨Finset.mem_univ _, hf⟩
  have hle : ∀ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
      ((nbr G a c) ∩ (nbr G r g)).card ≤ 5 := by
    intro g hg
    exact mixture G h a r c g (Finset.mem_filter.mp hg).2.symm
  exact ⟨le_of_sum_ge_of_bound _ _ f hfS (card_filter_ne_three c) hle hsum, hle f hfS⟩

/-- **The arm degree partition.** Inside the colour-`c` class of a vertex `r` of
cardinality 15, every point `a` has at most five neighbours of each other colour
inside that class and the three counts sum to 14: they are a permutation of
(5,5,4). -/
theorem arm_degree_partition (G : EdgeCol V 4) (h : TriangleFree G) (r a : V) (c : Fin 4)
    (ha : a ∈ nbr G r c) (h15 : (nbr G r c).card = 15) (f : Fin 4) (hf : f ≠ c) :
    4 ≤ ((nbr G a f) ∩ (nbr G r c)).card ∧ ((nbr G a f) ∩ (nbr G r c)).card ≤ 5 := by
  have hsum : 14 ≤ ∑ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
      ((nbr G a g) ∩ (nbr G r c)).card := by
    rw [show (∑ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
          ((nbr G a g) ∩ (nbr G r c)).card)
        = ∑ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
          ((nbr G r c) ∩ (nbr G a g)).card from
        Finset.sum_congr rfl (fun g _ => by rw [Finset.inter_comm])]
    rw [sum_inter_nbr_ne G h r a c ha, h15]
  have hfS : f ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c) := by
    rw [Finset.mem_filter]
    exact ⟨Finset.mem_univ _, hf⟩
  have hle : ∀ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
      ((nbr G a g) ∩ (nbr G r c)).card ≤ 5 := by
    intro g hg
    exact arm_part_le_five G h r c ha g (Finset.mem_filter.mp hg).2
  exact ⟨le_of_sum_ge_of_bound _ _ f hfS (card_filter_ne_three c) hle hsum, hle f hfS⟩

end K58

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

theorem card_filter_eq_sum_ite {α : Type*} (s : Finset α) (p : α → Prop) [DecidablePred p] :
    (s.filter p).card = ∑ x ∈ s, (if p x then 1 else 0) := by
  rw [Finset.card_eq_sum_ones, Finset.sum_filter]

/-- The colour-`c` neighbours of a point of the colour-`c` class of `r` are `r`
together with its colour-`c` neighbours outside that class (minus `r`). -/
theorem nbr_eq_insert (G : EdgeCol V 4) (h : TriangleFree G) (r a : V) (c : Fin 4)
    (ha : a ∈ nbr G r c) :
    nbr G a c
      = insert r (((Finset.univ \ nbr G r c) \ {r}).filter (fun y => G.col a y = c)) := by
  ext y
  constructor
  · intro hy
    rw [mem_nbr] at hy
    by_cases hyr : y = r
    · rw [hyr]; exact Finset.mem_insert_self _ _
    · refine Finset.mem_insert_of_mem (Finset.mem_filter.mpr ⟨?_, hy.2⟩)
      rw [Finset.mem_sdiff, Finset.mem_sdiff]
      refine ⟨⟨Finset.mem_univ _, ?_⟩, by simpa using hyr⟩
      intro hyA
      have hmem : y ∈ (nbr G a c) ∩ (nbr G r c) :=
        Finset.mem_inter.mpr ⟨mem_nbr.mpr ⟨hy.1, hy.2⟩, hyA⟩
      rw [inter_nbr_self_colour_empty G h r a c ha] at hmem
      exact absurd hmem (Finset.notMem_empty y)
  · intro hy
    rcases Finset.mem_insert.mp hy with hyr | hyf
    · rw [hyr]; exact nbr_symm_mem G ha
    · obtain ⟨hyX, hcol⟩ := Finset.mem_filter.mp hyf
      rw [Finset.mem_sdiff, Finset.mem_sdiff] at hyX
      obtain ⟨⟨-, hyA⟩, hyr⟩ := hyX
      exact mem_nbr.mpr ⟨by rintro rfl; exact hyA ha, hcol⟩

/-- The interface identity: the colour-`c` degree surplus of the colour-`c` class
of `r` equals the number of colour-`c` edges from that class to the vertices
outside it and outside `r`. -/
theorem interface_count (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4) :
    ∑ a ∈ nbr G r c, (deg G a c - 1)
      = ∑ y ∈ (Finset.univ \ nbr G r c) \ {r},
          ((nbr G y c) ∩ (nbr G r c)).card := by
  have stepA : ∀ a ∈ nbr G r c, deg G a c - 1
      = ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, (if G.col a y = c then 1 else 0) := by
    intro a ha
    have hins := nbr_eq_insert G h r a c ha
    have hnot : r ∉ ((Finset.univ \ nbr G r c) \ {r}).filter (fun y => G.col a y = c) := by
      intro hm
      obtain ⟨hmX, -⟩ := Finset.mem_filter.mp hm
      rw [Finset.mem_sdiff, Finset.mem_singleton] at hmX
      exact hmX.2 rfl
    have hcard : (nbr G a c).card
        = (((Finset.univ \ nbr G r c) \ {r}).filter (fun y => G.col a y = c)).card + 1 := by
      rw [hins, Finset.card_insert_of_notMem hnot]
    rw [nbr_card] at hcard
    have h2 := card_filter_eq_sum_ite ((Finset.univ \ nbr G r c) \ {r})
      (fun y => G.col a y = c)
    omega
  have stepB : ∀ y ∈ (Finset.univ \ nbr G r c) \ {r},
      ((nbr G y c) ∩ (nbr G r c)).card
        = ∑ a ∈ nbr G r c, (if G.col y a = c then 1 else 0) := by
    intro y hy
    have hyX : y ∉ nbr G r c := (Finset.mem_sdiff.mp (Finset.mem_sdiff.mp hy).1).2
    have hset : (nbr G y c) ∩ (nbr G r c)
        = (nbr G r c).filter (fun a => G.col y a = c) := by
      ext a
      constructor
      · intro ha
        obtain ⟨h1, h2⟩ := Finset.mem_inter.mp ha
        exact Finset.mem_filter.mpr ⟨h2, (mem_nbr.mp h1).2⟩
      · intro ha
        obtain ⟨haA, hcol⟩ := Finset.mem_filter.mp ha
        refine Finset.mem_inter.mpr ⟨mem_nbr.mpr ⟨?_, hcol⟩, haA⟩
        rintro rfl
        exact hyX haA
    rw [hset, card_filter_eq_sum_ite]
  calc ∑ a ∈ nbr G r c, (deg G a c - 1)
      = ∑ a ∈ nbr G r c, ∑ y ∈ (Finset.univ \ nbr G r c) \ {r},
          (if G.col a y = c then 1 else 0) :=
        Finset.sum_congr rfl stepA
    _ = ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, ∑ a ∈ nbr G r c,
          (if G.col a y = c then 1 else 0) := Finset.sum_comm
    _ = ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, ∑ a ∈ nbr G r c,
          (if G.col y a = c then 1 else 0) := by
        refine Finset.sum_congr rfl ?_
        intro y _
        exact Finset.sum_congr rfl (fun a _ => by rw [G.symm a y])
    _ = ∑ y ∈ (Finset.univ \ nbr G r c) \ {r},
          ((nbr G y c) ∩ (nbr G r c)).card := by
        refine Finset.sum_congr rfl ?_
        intro y hy
        exact (stepB y hy).symm

/-- Every member of a sending arm contributes at least 14 to the interface. -/
theorem interface_sender_lower (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4)
    (hsend : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card) :
    14 * (nbr G r c).card
      ≤ ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, ((nbr G y c) ∩ (nbr G r c)).card := by
  rw [← interface_count G h r c]
  calc 14 * (nbr G r c).card = ∑ _a ∈ nbr G r c, 14 := by
        rw [Finset.sum_const_nat (fun a _ => rfl), Nat.mul_comm]
    _ ≤ ∑ a ∈ nbr G r c, (deg G a c - 1) := by
        refine Finset.sum_le_sum ?_
        intro a ha
        have := hsend a ha
        rw [← nbr_card]
        omega

/-- Each outside vertex sees at most `|N_c(r)|` points of the arm in colour `c`. -/
theorem interface_upper (G : EdgeCol V 4) (r : V) (c : Fin 4) :
    ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, ((nbr G y c) ∩ (nbr G r c)).card
      ≤ ((Finset.univ \ nbr G r c) \ {r}).card * (nbr G r c).card := by
  calc ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, ((nbr G y c) ∩ (nbr G r c)).card
      ≤ ∑ _y ∈ (Finset.univ \ nbr G r c) \ {r}, (nbr G r c).card := by
        refine Finset.sum_le_sum ?_
        intro y _
        exact Finset.card_le_card (Finset.inter_subset_right)
    _ = ((Finset.univ \ nbr G r c) \ {r}).card * (nbr G r c).card :=
        Finset.sum_const_nat (fun a _ => rfl)

end K58

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- **The interface budget of a sending arm.** If every point of a 15-arm sends,
then the arm's colour-`c` edges to the rest of the board number between 210 and
225. -/
theorem interface_sender_bounds (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4)
    (h15 : (nbr G r c).card = 15) (hsend : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card) :
    210 ≤ ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, ((nbr G y c) ∩ (nbr G r c)).card
      ∧ ∑ y ∈ (Finset.univ \ nbr G r c) \ {r}, ((nbr G y c) ∩ (nbr G r c)).card ≤ 225 := by
  constructor
  · have h1 := interface_sender_lower G h r c hsend
    rw [h15] at h1
    omega
  · rw [← interface_count G h r c]
    calc ∑ a ∈ nbr G r c, (deg G a c - 1) ≤ ∑ _a ∈ nbr G r c, 15 := by
          refine Finset.sum_le_sum ?_
          intro a _
          have hcap := deg_le_sixteen G h a c
          omega
      _ = (nbr G r c).card * 15 := Finset.sum_const_nat (fun a _ => rfl)
      _ = 225 := by rw [h15]

/-- The arm of a vertex of a `K_58` leaves `58 - 1 - 15 = 42` vertices outside. -/
theorem interface_outside_card (G : EdgeCol V 4) (r : V) (c : Fin 4)
    (hV : Fintype.card V = 58) (h15 : (nbr G r c).card = 15) :
    ((Finset.univ \ nbr G r c) \ {r}).card = 42 := by
  have hrn : r ∉ nbr G r c := by
    intro hm
    exact (mem_nbr.mp hm).1 rfl
  have hsub : nbr G r c ⊆ (Finset.univ : Finset V) := Finset.subset_univ _
  have h1 : ((Finset.univ : Finset V) \ nbr G r c).card = 58 - 15 := by
    rw [Finset.card_sdiff_of_subset hsub, Finset.card_univ, hV, h15]
  have h2 : ({r} : Finset V) ⊆ (Finset.univ : Finset V) \ nbr G r c := by
    intro x hx
    rw [Finset.mem_singleton] at hx
    subst hx
    exact Finset.mem_sdiff.mpr ⟨Finset.mem_univ _, hrn⟩
  rw [Finset.card_sdiff_of_subset h2, h1, Finset.card_singleton]

end K58

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- Inside a 15-arm the three arm-internal colour degrees of any point sum to 14. -/
theorem arm_degree_sum_fifteen (G : EdgeCol V 4) (h : TriangleFree G) (r a : V) (c : Fin 4)
    (ha : a ∈ nbr G r c) (h15 : (nbr G r c).card = 15) :
    ∑ f ∈ Finset.univ.filter (fun f : Fin 4 => f ≠ c),
      ((nbr G a f) ∩ (nbr G r c)).card = 14 := by
  rw [show (∑ f ∈ Finset.univ.filter (fun f : Fin 4 => f ≠ c),
        ((nbr G a f) ∩ (nbr G r c)).card)
      = ∑ f ∈ Finset.univ.filter (fun f : Fin 4 => f ≠ c),
        ((nbr G r c) ∩ (nbr G a f)).card from
      Finset.sum_congr rfl (fun f _ => by rw [Finset.inter_comm])]
  rw [sum_inter_nbr_ne G h r a c ha, h15]

/-- Inside a 14-arm the three arm-internal colour degrees of any point sum to 13. -/
theorem arm_degree_sum_fourteen (G : EdgeCol V 4) (h : TriangleFree G) (r a : V) (c : Fin 4)
    (ha : a ∈ nbr G r c) (h14 : (nbr G r c).card = 14) :
    ∑ f ∈ Finset.univ.filter (fun f : Fin 4 => f ≠ c),
      ((nbr G a f) ∩ (nbr G r c)).card = 13 := by
  rw [show (∑ f ∈ Finset.univ.filter (fun f : Fin 4 => f ≠ c),
        ((nbr G a f) ∩ (nbr G r c)).card)
      = ∑ f ∈ Finset.univ.filter (fun f : Fin 4 => f ≠ c),
        ((nbr G r c) ∩ (nbr G a f)).card from
      Finset.sum_congr rfl (fun f _ => by rw [Finset.inter_comm])]
  rw [sum_inter_nbr_ne G h r a c ha, h14]

/-- **L3, second clause.** At most one of the three other arms is met in 4 points. -/
theorem sender_split_at_most_one_four (G : EdgeCol V 4) (h : TriangleFree G) (r : V)
    (c : Fin 4) (a : V) (ha : a ∈ nbr G r c) (hs : 15 ≤ (nbr G a c).card)
    (f g : Fin 4) (hf : f ≠ c) (hg : g ≠ c) (hfg : f ≠ g)
    (hf4 : ((nbr G a c) ∩ (nbr G r f)).card = 4) :
    ((nbr G a c) ∩ (nbr G r g)).card ≠ 4 := by
  intro hg4
  have hr : r ∈ nbr G a c := nbr_symm_mem G ha
  have hsum : 14 ≤ ∑ x ∈ Finset.univ.filter (fun x : Fin 4 => x ≠ c),
      ((nbr G a c) ∩ (nbr G r x)).card := by
    rw [sum_inter_nbr_ne G h a r c hr]
    omega
  have hle : ∀ x ∈ Finset.univ.filter (fun x : Fin 4 => x ≠ c),
      ((nbr G a c) ∩ (nbr G r x)).card ≤ 5 := by
    intro x hx
    exact mixture G h a r c x (Finset.mem_filter.mp hx).2.symm
  have hfS : f ∈ Finset.univ.filter (fun x : Fin 4 => x ≠ c) := by
    rw [Finset.mem_filter]; exact ⟨Finset.mem_univ _, hf⟩
  have hgS : g ∈ Finset.univ.filter (fun x : Fin 4 => x ≠ c) := by
    rw [Finset.mem_filter]; exact ⟨Finset.mem_univ _, hg⟩
  have hgS' : g ∈ (Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f := by
    rw [Finset.mem_erase]
    exact ⟨Ne.symm hfg, hgS⟩
  have h1 : ((nbr G a c) ∩ (nbr G r f)).card
      + ∑ x ∈ (Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f,
          ((nbr G a c) ∩ (nbr G r x)).card
      = ∑ x ∈ Finset.univ.filter (fun x : Fin 4 => x ≠ c),
          ((nbr G a c) ∩ (nbr G r x)).card :=
    Finset.add_sum_erase (Finset.univ.filter (fun x : Fin 4 => x ≠ c))
      (fun x => ((nbr G a c) ∩ (nbr G r x)).card) hfS
  have h2 : ((nbr G a c) ∩ (nbr G r g)).card
      + ∑ x ∈ ((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f).erase g,
          ((nbr G a c) ∩ (nbr G r x)).card
      = ∑ x ∈ (Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f,
          ((nbr G a c) ∩ (nbr G r x)).card :=
    Finset.add_sum_erase ((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f)
      (fun x => ((nbr G a c) ∩ (nbr G r x)).card) hgS'
  have hcard1 : ((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f).card ≤ 2 := by
    have := Finset.card_erase_of_mem hfS
    have hc := card_filter_ne_three c
    omega
  have hcard2 : (((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f).erase g).card ≤ 1 := by
    have := Finset.card_erase_of_mem hgS'
    omega
  have hb : ∑ x ∈ ((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f).erase g,
      ((nbr G a c) ∩ (nbr G r x)).card ≤ 5 := by
    calc ∑ x ∈ ((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f).erase g,
          ((nbr G a c) ∩ (nbr G r x)).card
        ≤ ∑ _x ∈ ((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f).erase g, 5 := by
          refine Finset.sum_le_sum ?_
          intro x hx
          exact hle x ((Finset.mem_erase.mp (Finset.mem_erase.mp hx).2).2)
      _ = (((Finset.univ.filter (fun x : Fin 4 => x ≠ c)).erase f).erase g).card * 5 :=
          Finset.sum_const_nat (fun a _ => rfl)
    omega
  omega

end K58

namespace K58

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- The sharper counting bound: a sum of at most three terms bounded by 5 that is
at least 15 forces every term to be 5. -/
theorem le_of_sum_ge_of_bound_five {α : Type*} [DecidableEq α] (S : Finset α) (F : α → ℕ)
    (f : α) (hf : f ∈ S) (hcard : S.card ≤ 3) (hle : ∀ g ∈ S, F g ≤ 5)
    (hsum : 15 ≤ ∑ g ∈ S, F g) : 5 ≤ F f := by
  have h1 : F f + ∑ g ∈ S.erase f, F g = ∑ g ∈ S, F g := Finset.add_sum_erase S F hf
  have h2 : ∑ g ∈ S.erase f, F g ≤ (S.erase f).card * 5 := by
    calc ∑ g ∈ S.erase f, F g ≤ ∑ g ∈ S.erase f, 5 :=
          Finset.sum_le_sum (fun g hg => hle g (Finset.mem_erase.mp hg).2)
      _ = (S.erase f).card * 5 := Finset.sum_const_nat (fun g _ => rfl)
  have h3 : (S.erase f).card ≤ 2 := by
    have h4 := Finset.card_erase_of_mem hf
    omega
  omega

/-- **The 16-arm balance.** Every point of a class of 16 points has exactly five
neighbours of each other colour inside it. -/
theorem arm_degree_sixteen (G : EdgeCol V 4) (h : TriangleFree G) (r a : V) (c : Fin 4)
    (ha : a ∈ nbr G r c) (h16 : (nbr G r c).card = 16) (f : Fin 4) (hf : f ≠ c) :
    ((nbr G a f) ∩ (nbr G r c)).card = 5 := by
  have hsum : 15 ≤ ∑ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
      ((nbr G a g) ∩ (nbr G r c)).card := by
    rw [show (∑ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
          ((nbr G a g) ∩ (nbr G r c)).card)
        = ∑ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
          ((nbr G r c) ∩ (nbr G a g)).card from
        Finset.sum_congr rfl (fun g _ => by rw [Finset.inter_comm])]
    rw [sum_inter_nbr_ne G h r a c ha, h16]
  have hle : ∀ g ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c),
      ((nbr G a g) ∩ (nbr G r c)).card ≤ 5 := by
    intro g hg
    exact arm_part_le_five G h r c ha g (Finset.mem_filter.mp hg).2
  have hfS : f ∈ Finset.univ.filter (fun g : Fin 4 => g ≠ c) := by
    rw [Finset.mem_filter]; exact ⟨Finset.mem_univ _, hf⟩
  have hge := le_of_sum_ge_of_bound (Finset.univ.filter (fun g : Fin 4 => g ≠ c))
    (fun g => ((nbr G a g) ∩ (nbr G r c)).card) f hfS
    (card_filter_ne_three c) hle (by omega)
  have hlef : ((nbr G a f) ∩ (nbr G r c)).card ≤ 5 := hle f hfS
  exact le_antisymm hlef (le_of_sum_ge_of_bound_five (Finset.univ.filter (fun g : Fin 4 => g ≠ c))
    (fun g => ((nbr G a g) ∩ (nbr G r c)).card) f hfS (card_filter_ne_three c) hle hsum)

/-- The three colours other than `c` number exactly three. -/
theorem card_filter_ne_eq_three (c : Fin 4) :
    (Finset.univ.filter (fun f : Fin 4 => f ≠ c)).card = 3 := by
  rw [show (Finset.univ.filter (fun f : Fin 4 => f ≠ c)) = Finset.univ.erase c from by
    ext x; simp [Finset.mem_erase, and_comm]]
  rw [Finset.card_erase_of_mem (Finset.mem_univ c)]
  simp

/-- At most one of at most three terms bounded by 5 is exactly 4 when the sum is
at least 14. -/
theorem at_most_one_four_of_sum {α : Type*} [DecidableEq α] (S : Finset α) (F : α → ℕ)
    (hcard : S.card ≤ 3) (hle : ∀ g ∈ S, F g ≤ 5) (hsum : 14 ≤ ∑ g ∈ S, F g)
    (f g : α) (hf : f ∈ S) (hg : g ∈ S) (hfg : f ≠ g) (hf4 : F f = 4) : F g ≠ 4 := by
  intro hg4
  have hgS' : g ∈ S.erase f := Finset.mem_erase.mpr ⟨Ne.symm hfg, hg⟩
  have h1 : F f + ∑ x ∈ S.erase f, F x = ∑ x ∈ S, F x := Finset.add_sum_erase S F hf
  have h2 : F g + ∑ x ∈ (S.erase f).erase g, F x = ∑ x ∈ S.erase f, F x :=
    Finset.add_sum_erase (S.erase f) F hgS'
  have hc2 : ((S.erase f).erase g).card ≤ 1 := by
    have h3 := Finset.card_erase_of_mem hf
    have h4 := Finset.card_erase_of_mem hgS'
    omega
  have hb : ∑ x ∈ (S.erase f).erase g, F x ≤ 5 := by
    calc ∑ x ∈ (S.erase f).erase g, F x ≤ ∑ _x ∈ (S.erase f).erase g, 5 :=
          Finset.sum_le_sum (fun x hx => hle x (Finset.mem_erase.mp (Finset.mem_erase.mp hx).2).2)
      _ = ((S.erase f).erase g).card * 5 := Finset.sum_const_nat (fun a _ => rfl)
    omega
  omega

/-- In a 15-arm every point is *light* in exactly one other colour. -/
theorem arm_light_exists_and_unique (G : EdgeCol V 4) (h : TriangleFree G) (r a : V)
    (c : Fin 4) (ha : a ∈ nbr G r c) (h15 : (nbr G r c).card = 15) :
    ∃ f : Fin 4, f ≠ c ∧ ((nbr G a f) ∩ (nbr G r c)).card = 4 ∧
      ∀ g : Fin 4, g ≠ c → ((nbr G a g) ∩ (nbr G r c)).card = 4 → g = f := by
  classical
  set S := Finset.univ.filter (fun g : Fin 4 => g ≠ c) with hSdef
  have hS3 : S.card = 3 := card_filter_ne_eq_three c
  have hsum : ∑ g ∈ S, ((nbr G a g) ∩ (nbr G r c)).card = 14 := by
    rw [show (∑ g ∈ S, ((nbr G a g) ∩ (nbr G r c)).card)
        = ∑ g ∈ S, ((nbr G r c) ∩ (nbr G a g)).card from
        Finset.sum_congr rfl (fun g _ => by rw [Finset.inter_comm])]
    rw [show S = Finset.univ.filter (fun g : Fin 4 => g ≠ c) from hSdef,
      sum_inter_nbr_ne G h r a c ha, h15]
  have hle : ∀ g ∈ S, ((nbr G a g) ∩ (nbr G r c)).card ≤ 5 := by
    intro g hg
    exact arm_part_le_five G h r c ha g (Finset.mem_filter.mp hg).2
  have hge : ∀ g ∈ S, 4 ≤ ((nbr G a g) ∩ (nbr G r c)).card := by
    intro g hg
    exact (arm_degree_partition G h r a c ha h15 g (Finset.mem_filter.mp hg).2).1
  -- existence: if no term is 4, all three are 5 and the sum is 15, not 14
  have hex : ∃ f ∈ S, ((nbr G a f) ∩ (nbr G r c)).card = 4 := by
    by_contra hc
    have h45 : ∀ g ∈ S, ((nbr G a g) ∩ (nbr G r c)).card = 4
        ∨ ((nbr G a g) ∩ (nbr G r c)).card = 5 := by
      intro g hg
      have h1 := hge g hg
      have h2 := hle g hg
      rcases Nat.lt_or_ge ((nbr G a g) ∩ (nbr G r c)).card 5 with h | h
      · exact Or.inl (le_antisymm (Nat.lt_succ_iff.mp h) h1)
      · exact Or.inr (le_antisymm h2 h)
    have h5 : ∀ g ∈ S, ((nbr G a g) ∩ (nbr G r c)).card = 5 := by
      intro g hg
      rcases h45 g hg with h | h
      · exact absurd h (fun h4 => hc ⟨g, hg, h4⟩)
      · exact h
    have hsum15 : ∑ g ∈ S, ((nbr G a g) ∩ (nbr G r c)).card = S.card * 5 :=
      Finset.sum_const_nat h5
    rw [hS3] at hsum15
    omega
  obtain ⟨f, hfS, hf4⟩ := hex
  refine ⟨f, (Finset.mem_filter.mp hfS).2, hf4, ?_⟩
  intro g hg hg4
  by_contra hne
  exact at_most_one_four_of_sum S (fun x => ((nbr G a x) ∩ (nbr G r c)).card)
    (by rw [hS3]) hle (by omega) f g hfS (by rw [Finset.mem_filter]; exact ⟨Finset.mem_univ _, hg⟩)
    (Ne.symm hne) hf4 hg4

end K58
