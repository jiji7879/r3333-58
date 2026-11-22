/-
K58 supplement (swarm smwrfgma5, member m5): the *restriction* half of the
conditional theorem on the 28-vertex two-arm instance.

Statement proved here.  Let `G` be a triangle-free 4-colouring of the complete
graph on a 58-point type `V`, let `r : V` have a colour-`c` class `A = nbr G r c`
of size 15, and suppose the branch hypotheses hold:

* every point of `A` sends, `15 ≤ |nbr G a c|` (fully sending);
* every vertex outside `A ∪ {r}` sees exactly five points of `A` in colour `c`
  (uniform), `|nbr G y c ∩ A| = 5`.

Then:

* `exact_degree`   : `|nbr G a c| = 15` for every `a ∈ A`   (interface is tight);
* `word_part_indep` : the parts `M_f(x) = nbr G x f ∩ A` contain no `f`-edge
  of `A`  -- the per-slot independence clause of the instance;
* `pair_disjoint`  : if `col x y = f` then `M_f(x) ∩ M_f(y) = ∅` -- the pair
  clause of the instance;
* `root_colour_free` : inside `nbr G r b` there is no colour-`b` edge -- the
  root-colour clause;
* `arm_triangle_free` : no monochromatic triangle inside a colour class of `r`
  -- the arm-triangle clause;
* `coverage_le`    : for `b ≠ c`, `d ≠ c`, `b ≠ d`, each `a ∈ A` is counted at
  most 14 times in colour `c` by the two arms `nbr G r b`, `nbr G r d` -- the
  column-sum clause of the 14+14 instance (`≤ 14`, never `= 14`: with 28 slots
  and five `c`s per slot only 140 incidences exist, so `= 14` on 15 columns
  would be unsatisfiable outright).

`two_arm_restriction` is the conjunction of all six, i.e. literally the clause
families of the encoder `.ultramath/smwr8io45/m6/pairlevel.py` specialised to
`nB = 14, nC = 0, nD = 14` with `coverage = "atmost14"` and `arm_triangles`
on.  Hence: if that CNF is unsatisfiable, no branch object exists with an arm
`A` whose internal colouring is the one the CNF was built from.
-/
import K58.Arm

namespace K58
namespace TwoArm

variable {V : Type*} [Fintype V] [DecidableEq V]

/-! ### Per-slot clauses -/

/-- **Part independence.**  If `a`, `a'` are two points of the word arm `A` both
joined to the outside vertex `x` in colour `f`, then the edge `aa'` does not have
colour `f` -- otherwise `x a a'` is a monochromatic triangle.  Note the statement
is for *every* `f : Fin 4`, including `f = c`. -/
theorem word_part_indep (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4) :
    ∀ (x : V) (f : Fin 4) (a a' : V), x ∉ nbr G r c → a ∈ nbr G r c →
      a' ∈ nbr G r c → a ≠ a' → G.col x a = f → G.col x a' = f → G.col a a' ≠ f := by
  intro x f a a' hx ha ha' haa' h1 h2 hc
  have hxa : x ≠ a := fun e => hx (e ▸ ha)
  have hxa' : x ≠ a' := fun e => hx (e ▸ ha')
  exact h x a a' hxa haa' hxa' ⟨by rw [h1, h2], by rw [h2, hc]⟩

/-- **Pair disjointness.**  If the edge `xy` has colour `f`, the two `f`-parts of
`x` and `y` inside the word arm are disjoint -- otherwise a common point `a`
gives the monochromatic triangle `x y a`. -/
theorem pair_disjoint (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4) :
    ∀ (x y a : V) (f : Fin 4), x ≠ y → x ∉ nbr G r c → y ∉ nbr G r c →
      a ∈ nbr G r c → G.col x y = f → G.col x a = f → G.col y a = f → False := by
  intro x y a f hxy hx hy ha hxyf hxa hya
  have hax : x ≠ a := fun e => hx (e ▸ ha)
  have hay : y ≠ a := fun e => hy (e ▸ ha)
  exact h x y a hxy hay hax ⟨by rw [hxyf, hxa], by rw [hxa, hya]⟩

/-- **Root colour free inside an arm.**  A colour class of `r` carries no edge of
its own colour. -/
theorem root_colour_free (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (b : Fin 4) :
    ∀ x ∈ nbr G r b, ∀ y ∈ nbr G r b, x ≠ y → G.col x y ≠ b :=
  fun x hx y hy hxy => nbr_indep G h r b x hx y hy hxy

/-- **Arm triangle-freeness.**  No triple inside a colour class of `r` is
monochromatic (in any colour). -/
theorem arm_triangle_free (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (b : Fin 4) :
    ∀ x ∈ nbr G r b, ∀ y ∈ nbr G r b, ∀ z ∈ nbr G r b, x ≠ y → y ≠ z → x ≠ z →
      ¬ (G.col x y = G.col x z ∧ G.col x z = G.col y z) :=
  fun x _ y _ z _ hxy hyz hxz => h x y z hxy hyz hxz

/-! ### The interface is exactly tight -/

/-- **The uniform fully-sending branch saturates the interface.**  With
`|A| = 15`, `|V| = 58`, every point of the arm sending and every outside vertex
seeing exactly five arm points in colour `c`, every point of the arm has
colour-`c` degree exactly 15.  (Lower bound `interface_sender_lower`, upper bound
the uniformity; equality termwise because the arm has 15 points.) -/
theorem exact_degree (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4)
    (hV : Fintype.card V = 58) (hA : (nbr G r c).card = 15)
    (hsend : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card)
    (hunif : ∀ y, y ∈ (Finset.univ \ nbr G r c) \ {r} →
      ((nbr G y c) ∩ (nbr G r c)).card = 5) :
    ∀ a ∈ nbr G r c, (nbr G a c).card = 15 := by
  have hX : ((Finset.univ \ nbr G r c) \ {r}).card = 42 :=
    interface_outside_card G r c hV hA
  have hsum5 : ∑ y ∈ (Finset.univ \ nbr G r c) \ {r},
      ((nbr G y c) ∩ (nbr G r c)).card = 210 := by
    rw [Finset.sum_congr rfl (fun y hy => hunif y hy),
      Finset.sum_const_nat (fun y _ => rfl), hX]
  have hcount := interface_count G h r c
  rw [hsum5] at hcount
  have hle : ∀ a ∈ nbr G r c, (14 : ℕ) ≤ deg G a c - 1 := by
    intro a ha
    have hs := hsend a ha
    rw [nbr_card] at hs
    omega
  have hconst : ∑ a ∈ nbr G r c, (14 : ℕ) = 210 := by
    rw [Finset.sum_const_nat (fun a _ => rfl), hA]
  have heq : ∀ a ∈ nbr G r c, deg G a c - 1 = 14 := by
    have h := (Finset.sum_eq_sum_iff_of_le hle).mp ?_
    · intro a ha; exact (h a ha).symm
    · rw [hconst, hcount]
  intro a ha
  have h1 := heq a ha
  have h2 : 1 ≤ deg G a c := by
    have hs := hsend a ha
    rw [nbr_card] at hs
    omega
  rw [nbr_card]
  omega

/-- **The column-sum clause of the two-arm instance.**  With the branch
hypotheses, every point `a` of the word arm is joined in colour `c` to at most 14
vertices of the two word-carrying arms `nbr G r b`, `nbr G r d`
(`b, d ≠ c`, `b ≠ d`).  The value 14 is `|nbr G a c| - 1`: the remaining
colour-`c` neighbour of `a` is `r`, and `a` has no colour-`c` neighbour inside
the arm itself. -/
theorem coverage_le (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c b d : Fin 4)
    (hb : b ≠ c) (hd : d ≠ c) (_hbd : b ≠ d)
    (hV : Fintype.card V = 58) (hA : (nbr G r c).card = 15)
    (hsend : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card)
    (hunif : ∀ y, y ∈ (Finset.univ \ nbr G r c) \ {r} →
      ((nbr G y c) ∩ (nbr G r c)).card = 5)
    (a : V) (ha : a ∈ nbr G r c) :
    (((nbr G r b) ∪ (nbr G r d)).filter (fun x => G.col x a = c)).card ≤ 14 := by
  have hdeg : (nbr G a c).card = 15 := exact_degree G h r c hV hA hsend hunif a ha
  have hra : r ∈ nbr G a c := nbr_symm_mem G ha
  -- the filtered set is a subset of `nbr G a c` with `r` removed
  have hsub : ((nbr G r b) ∪ (nbr G r d)).filter (fun x => G.col x a = c)
      ⊆ (nbr G a c).erase r := by
    intro x hx
    rw [Finset.mem_filter] at hx
    obtain ⟨hxU, hxc⟩ := hx
    rw [Finset.mem_erase]
    rw [Finset.mem_union] at hxU
    have hxr : x ≠ r := by
      rcases hxU with hxb | hxd
      · exact (mem_nbr.mp hxb).1
      · exact (mem_nbr.mp hxd).1
    have hxnc : x ∉ nbr G r c := by
      rcases hxU with hxb | hxd
      · intro hc'
        have h1 : G.col r x = b := (mem_nbr.mp hxb).2
        have h2 : G.col r x = c := (mem_nbr.mp hc').2
        exact hb (by rw [← h1, h2])
      · intro hc'
        have h1 : G.col r x = d := (mem_nbr.mp hxd).2
        have h2 : G.col r x = c := (mem_nbr.mp hc').2
        exact hd (by rw [← h1, h2])
    have hxa : x ≠ a := by
      intro e
      exact hxnc (e ▸ ha)
    refine ⟨hxr, ?_⟩
    rw [mem_nbr]
    exact ⟨hxa, by rw [G.symm a x]; exact hxc⟩
  have hcard : ((nbr G a c).erase r).card = 14 := by
    rw [Finset.card_erase_of_mem hra, hdeg]
  have := Finset.card_le_card hsub
  omega

/-! ### The bundle -/

/-- **The restriction theorem.**  All the clause families of the 28-vertex
two-arm instance hold for the word data of a genuine branch object. -/
theorem two_arm_restriction (G : EdgeCol V 4) (h : TriangleFree G) (r : V) (c : Fin 4)
    (hV : Fintype.card V = 58) (hA : (nbr G r c).card = 15)
    (hsend : ∀ a ∈ nbr G r c, 15 ≤ (nbr G a c).card)
    (hunif : ∀ y, y ∈ (Finset.univ \ nbr G r c) \ {r} →
      ((nbr G y c) ∩ (nbr G r c)).card = 5) :
    -- (0) the interface is tight
    (∀ a ∈ nbr G r c, (nbr G a c).card = 15) ∧
    -- (1) five `c`-entries per word
    (∀ x, x ∈ (Finset.univ \ nbr G r c) \ {r} →
      ((nbr G x c) ∩ (nbr G r c)).card = 5) ∧
    -- (2) per-slot part independence
    (∀ (x : V) (f : Fin 4) (a a' : V), x ∉ nbr G r c → a ∈ nbr G r c →
      a' ∈ nbr G r c → a ≠ a' → G.col x a = f → G.col x a' = f → G.col a a' ≠ f) ∧
    -- (3) pair disjointness
    (∀ (x y a : V) (f : Fin 4), x ≠ y → x ∉ nbr G r c → y ∉ nbr G r c →
      a ∈ nbr G r c → G.col x y = f → G.col x a = f → G.col y a = f → False) ∧
    -- (4) the arm colour is not used inside the arm
    (∀ (b : Fin 4), b ≠ c → ∀ x ∈ nbr G r b, ∀ y ∈ nbr G r b, x ≠ y → G.col x y ≠ b) ∧
    -- (5) no monochromatic triangle inside an arm
    (∀ (b : Fin 4) (x y z : V), x ∈ nbr G r b → y ∈ nbr G r b → z ∈ nbr G r b →
      x ≠ y → y ≠ z → x ≠ z →
      ¬ (G.col x y = G.col x z ∧ G.col x z = G.col y z)) ∧
    -- (6) column sums at most 14 over the two arms
    (∀ (b d : Fin 4), b ≠ c → d ≠ c → b ≠ d → ∀ a ∈ nbr G r c,
      (((nbr G r b) ∪ (nbr G r d)).filter (fun x => G.col x a = c)).card ≤ 14) := by
  refine ⟨exact_degree G h r c hV hA hsend hunif,
    fun x hx => hunif x hx,
    fun x f a a' hx ha ha' haa' h1 h2 => word_part_indep G h r c x f a a' hx ha ha' haa' h1 h2,
    fun x y a f hxy hx hy ha hxyf hxa hya =>
      pair_disjoint G h r c x y a f hxy hx hy ha hxyf hxa hya,
    fun b _ x hx y hy hxy => root_colour_free G h r b x hx y hy hxy,
    fun b x y z hx hy hz hxy hyz hxz => arm_triangle_free G h r b x hx y hy z hz hxy hyz hxz,
    fun b d hb hd hbd a ha => coverage_le G h r c b d hb hd hbd hV hA hsend hunif a ha⟩

end TwoArm
end K58
