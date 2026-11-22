/-
K58: the exchange residue at the `(15,14,14,14)` profile (swarm `smwrzh71x`,
member m2, direction d3).

The K59 exchange lemma transfers at 16-sets with a 15-core (`exchange_sixteen`)
and fails at 15-sets with a 14-core (`exchange_fifteen`): there the conclusion is
a disjunction, because the colour-degree vector of a core point inside a
colour-0-independent 15-set is only a permutation of `(5,5,4)` and not of
`(5,5,5)`.

This file makes the residue *exact* rather than disjunctive:

* `residue_pattern`   — a 13-count core pattern is a permutation of `(5,5,3)` or
                        of `(5,4,4)`, and nothing else;
* `residue_forced`    — a core point whose pattern is a permutation of `(5,5,3)`
                        has *one* admissible spoke colour, so the two spokes
                        agree there;
* `residue_two_way`   — two distinct admissible spoke colours force the pattern
                        `(4,4,5)`: the point is "free";
* `exists_complement` — at a core of size `mu <= 13` *every* core pattern is
                        completable: the residue is locally vacuous, i.e. its
                        incremental content is confined to codegree `>= 14`;
* `residue_arms`      — the profile corollary: if two senders' classes share a
                        14-core and their exclusive points lie in different arms
                        (different colours from the root), then the two counts
                        are 4 and every nonzero count is at least 4, so the
                        shared part is split `(4,4,5)` over the arms with the
                        exclusive points in the two 4-arms.

`exchange_sixteen` and `exchange_fifteen` are member m6's theorems from swarm
`smwridmzp` (same proofs); they are carried here, under their own statements, so
that the repository build contains them.
-/
import K58.Mixture

open scoped BigOperators

namespace K58

namespace Residue

variable {V : Type*} [Fintype V] [DecidableEq V]

/-- `S` carries no colour-0 edge, i.e. `S` is independent in the colour-0 graph. -/
def ZeroFree (G : EdgeCol V 4) (S : Finset V) : Prop :=
  ∀ x ∈ S, ∀ y ∈ S, x ≠ y → G.col x y ≠ 0

/-- Points of `S` joined to `z` in colour `c` (the caller keeps `z ∉ S`). -/
noncomputable def cntS (G : EdgeCol V 4) (z : V) (S : Finset V) (c : Fin 4) : ℕ :=
  (S.filter (fun u => G.col z u = c)).card

/-- **The colour-degree bound.**  In a triangle-free 4-colouring, if `S` carries
no colour-0 edge and `z ∉ S`, then `z` has at most five colour-`c` neighbours in
`S` for `c ≠ 0`: six of them would be 2-coloured by the two colours other than
`0` and `c`, contradicting `R(3,3) = 6`. -/
theorem cntS_le_five (G : EdgeCol V 4) (h : TriangleFree G) (z : V) (S : Finset V)
    (hzS : z ∉ S) (hS : ZeroFree G S) (c : Fin 4) (hc : c ≠ 0) : cntS G z S c ≤ 5 := by
  by_contra hle
  simp only [not_le] at hle
  obtain ⟨T, hTS, hTcard⟩ :=
    Finset.exists_subset_card_eq (show 6 ≤ cntS G z S c by omega)
  have hT6 : T.card = 6 := hTcard
  have hmem : ∀ p ∈ T, p ∈ S ∧ G.col z p = c := by
    intro p hp
    have hp' : p ∈ S.filter (fun u => G.col z u = c) := hTS hp
    simpa only [Finset.mem_filter] using hp'
  have hpT : ∀ p ∈ T, p ≠ z := fun p hp => by
    have := (hmem p hp).1
    exact fun hh => hzS (hh ▸ this)
  have hne : ∀ p ∈ T, ∀ q ∈ T, p ≠ q → G.col p q ≠ 0 ∧ G.col p q ≠ c := by
    intro p hp q hq hpq
    refine ⟨hS p (hmem p hp).1 q (hmem q hq).1 hpq, ?_⟩
    intro hc'
    exact h z p q (Ne.symm (hpT p hp)) hpq (Ne.symm (hpT q hq))
      ⟨by rw [(hmem p hp).2, (hmem q hq).2], by rw [(hmem q hq).2, hc']⟩
  let φ : {c' : Fin 4 // c' ≠ 0 ∧ c' ≠ c} ≃ Fin 2 :=
    Fintype.equivFinOfCardEq (card_ne_ne (Ne.symm hc))
  let G2 : EdgeCol ↥T 2 :=
    { col := fun p q =>
        if hpq : p = q then 0
        else φ ⟨G.col p.1 q.1, (hne p.1 p.2 q.1 q.2 (fun hh => hpq (Subtype.ext hh))).1,
                                  (hne p.1 p.2 q.1 q.2 (fun hh => hpq (Subtype.ext hh))).2⟩
      symm := by
        intro p q
        by_cases hpq : p = q
        · subst hpq; simp
        · have hqp : q ≠ p := Ne.symm hpq
          rw [dif_neg hpq, dif_neg hqp]
          congr 1
          exact Subtype.ext (G.symm p.1 q.1) }
  have h2 : TriangleFree G2 := by
    intro p q r hpq hqr hpr hmono
    have hpq' : ¬ (p = q) := hpq
    have hqr' : ¬ (q = r) := hqr
    have hpr' : ¬ (p = r) := hpr
    simp only [G2, dif_neg hpq', dif_neg hqr', dif_neg hpr'] at hmono
    have e1 : G.col p.1 q.1 = G.col p.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.1)
      simpa using hh
    have e2 : G.col p.1 r.1 = G.col q.1 r.1 := by
      have hh := congrArg Subtype.val (φ.injective hmono.2)
      simpa using hh
    have hpq2 : p.1 ≠ q.1 := fun hh => hpq (Subtype.ext hh)
    have hqr2 : q.1 ≠ r.1 := fun hh => hqr (Subtype.ext hh)
    have hpr2 : p.1 ≠ r.1 := fun hh => hpr (Subtype.ext hh)
    exact h p.1 q.1 r.1 hpq2 hqr2 hpr2 ⟨e1, e2⟩
  exact two_colour_six G2 (by simp [Fintype.card_coe, hT6]) h2

/-- Inserting a point adds one to exactly the matching colour count. -/
theorem cntS_insert (G : EdgeCol V 4) (z a : V) (S : Finset V)
    (haS : a ∉ S) (c : Fin 4) :
    cntS G z (insert a S) c = cntS G z S c + (if G.col z a = c then 1 else 0) := by
  unfold cntS
  rw [Finset.filter_insert]
  by_cases hcol : G.col z a = c
  · rw [if_pos hcol, if_pos hcol, Finset.card_insert_of_notMem]
    simp only [Finset.mem_filter, haS, false_and, not_false_eq_true]
  · rw [if_neg hcol, if_neg hcol, Nat.add_zero]

/-- The four colour counts of `z` into `S` add up to `|S|`. -/
theorem sum_cntS (G : EdgeCol V 4) (z : V) (S : Finset V) :
    cntS G z S 0 + cntS G z S 1 + cntS G z S 2 + cntS G z S 3 = S.card := by
  have h1 : ∀ c : Fin 4, cntS G z S c = ∑ u ∈ S, (if G.col z u = c then 1 else 0) := by
    intro c
    rw [cntS, Finset.card_eq_sum_ones, Finset.sum_filter]
  have h3 : ∀ u : V, (∑ c : Fin 4, (if G.col z u = c then 1 else 0)) = 1 := by
    intro u
    rw [Finset.sum_eq_single (G.col z u)]
    · simp
    · intro b _ hb
      simp [show ¬ (G.col z u = b) from fun hh => hb hh.symm]
    · simp
  calc cntS G z S 0 + cntS G z S 1 + cntS G z S 2 + cntS G z S 3
      = ∑ c : Fin 4, cntS G z S c := by rw [Fin.sum_univ_four]
    _ = ∑ c : Fin 4, ∑ u ∈ S, (if G.col z u = c then 1 else 0) :=
        Finset.sum_congr rfl (fun c _ => h1 c)
    _ = ∑ u ∈ S, ∑ c : Fin 4, (if G.col z u = c then 1 else 0) := Finset.sum_comm
    _ = ∑ _u ∈ S, (1 : ℕ) := Finset.sum_congr rfl (fun u _ => h3 u)
    _ = S.card := by rw [Finset.sum_const, smul_eq_mul, mul_one]

/-- A subset of a colour-0-free set is colour-0-free. -/
theorem zeroFree_subset {G : EdgeCol V 4} {S T : Finset V} (hT : ZeroFree G T)
    (hST : S ⊆ T) : ZeroFree G S :=
  fun x hx y hy hxy => hT x (hST hx) y (hST hy) hxy

/-- Every non-zero colour of `Fin 4` is `1`, `2` or `3`. -/
lemma fin4_ne_zero (c : Fin 4) (hc : c ≠ 0) : c = 1 ∨ c = 2 ∨ c = 3 := by
  fin_cases c
  · exact absurd rfl hc
  · exact Or.inl rfl
  · exact Or.inr (Or.inl rfl)
  · exact Or.inr (Or.inr rfl)

/-- Arithmetic of the 16/15 exchange: three colour counts at most five summing to
fourteen pin down the colour whose count is four. -/
theorem arith_sixteen (f : Fin 4 → ℕ) (h0 : f 0 = 0) (hsum : f 0 + f 1 + f 2 + f 3 = 14)
    (hle : ∀ c, f c ≤ 5) (c1 c2 : Fin 4) (hc1 : c1 ≠ 0) (hc2 : c2 ≠ 0)
    (h1 : f c1 + 1 ≤ 5) (h2 : f c2 + 1 ≤ 5) : c1 = c2 := by
  have e1 := hle 1
  have e2 := hle 2
  have e3 := hle 3
  by_contra hne
  rcases fin4_ne_zero c1 hc1 with rfl | rfl | rfl <;>
    rcases fin4_ne_zero c2 hc2 with rfl | rfl | rfl <;>
    first | exact absurd rfl hne | omega

/-- Arithmetic of the 15/14 exchange: three colour counts at most five summing to
thirteen leave a two-way choice exactly at the two counts equal to four. -/
theorem arith_fifteen (f : Fin 4 → ℕ) (h0 : f 0 = 0) (hsum : f 0 + f 1 + f 2 + f 3 = 13)
    (hle : ∀ c, f c ≤ 5) (c1 c2 : Fin 4) (hc1 : c1 ≠ 0) (hc2 : c2 ≠ 0)
    (h1 : f c1 + 1 ≤ 5) (h2 : f c2 + 1 ≤ 5) :
    c1 = c2 ∨ (f c1 = 4 ∧ f c2 = 4) := by
  rcases eq_or_ne c1 c2 with h | hne
  · exact Or.inl h
  · right
    have e1 := hle 1
    have e2 := hle 2
    have e3 := hle 3
    constructor
    · by_contra h4
      rcases fin4_ne_zero c1 hc1 with rfl | rfl | rfl <;>
        rcases fin4_ne_zero c2 hc2 with rfl | rfl | rfl <;>
        first | exact absurd rfl hne | omega
    · by_contra h4
      rcases fin4_ne_zero c1 hc1 with rfl | rfl | rfl <;>
        rcases fin4_ne_zero c2 hc2 with rfl | rfl | rfl <;>
        first | exact absurd rfl hne | omega

/-! ### The residue, exactly -/

/-- **A core pattern at codegree 14 is a permutation of `(5,5,3)` or of
`(5,4,4)`** — nothing else occurs, because three counts are at most five and sum
to thirteen. -/
theorem residue_pattern (f : Fin 4 → ℕ) (h0 : f 0 = 0)
    (hsum : f 0 + f 1 + f 2 + f 3 = 13) (hle : ∀ c, f c ≤ 5) :
    (f 1 = 3 ∨ f 2 = 3 ∨ f 3 = 3) ∨ (4 ≤ f 1 ∧ 4 ≤ f 2 ∧ 4 ≤ f 3) := by
  have e1 := hle 1
  have e2 := hle 2
  have e3 := hle 3
  by_cases h1 : f 1 = 3
  · exact Or.inl (Or.inl h1)
  by_cases h2 : f 2 = 3
  · exact Or.inl (Or.inr (Or.inl h2))
  by_cases h3 : f 3 = 3
  · exact Or.inl (Or.inr (Or.inr h3))
  right
  omega

/-- **The residue forces the spoke at a `(5,5,3)` point**: if the core pattern has
a count of three and a colour is admissible at `z` (raising it keeps every count
at most five), then that colour *is* the three-count colour.  Hence the two
spokes agree at such a core point. -/
theorem residue_forced (f : Fin 4 → ℕ) (h0 : f 0 = 0)
    (hsum : f 0 + f 1 + f 2 + f 3 = 13) (hle : ∀ c, f c ≤ 5)
    (c1 c2 : Fin 4) (hc1 : c1 ≠ 0) (hc2 : c2 ≠ 0)
    (h1 : f c1 + 1 ≤ 5) (h2 : f c2 + 1 ≤ 5) (hthree : f c1 = 3) : c2 = c1 := by
  rcases arith_fifteen f h0 hsum hle c1 c2 hc1 hc2 h1 h2 with h | ⟨h, -⟩
  · exact h.symm
  · omega

/-- **Two distinct admissible spoke colours force the pattern `(4,4,5)`.**  At
such a core point both spokes are the two four-count colours. -/
theorem residue_two_way (f : Fin 4 → ℕ) (h0 : f 0 = 0)
    (hsum : f 0 + f 1 + f 2 + f 3 = 13) (hle : ∀ c, f c ≤ 5)
    (c1 c2 : Fin 4) (hc1 : c1 ≠ 0) (hc2 : c2 ≠ 0)
    (h1 : f c1 + 1 ≤ 5) (h2 : f c2 + 1 ≤ 5) (hne : c1 ≠ c2) :
    f c1 = 4 ∧ f c2 = 4 := by
  rcases arith_fifteen f h0 hsum hle c1 c2 hc1 hc2 h1 h2 with h | h
  · exact absurd h hne
  · exact h

/-- **The residue is locally vacuous at every core of size at most thirteen.**
Given a core pattern `f` at a point `z` (no colour-0 count, every count at most
five, total `mu - 1` for a core of size `mu ≤ 13`), there is an assignment `w` of
the exclusive `15 - mu` points to colours that completes `f` to a permutation of
`(5,5,4)`.  So no core pattern below codegree 14 is refused by counting, and the
residue's incremental content is confined to codegree `14` and `15`. -/
theorem exists_complement (f : Fin 4 → ℕ) (h0 : f 0 = 0) (mu : ℕ) (hmu1 : 1 ≤ mu)
    (hsum : f 1 + f 2 + f 3 = mu - 1) (hle : ∀ c, f c ≤ 5) (hmu : mu ≤ 13) :
    ∃ w : Fin 4 → ℕ, w 0 = 0 ∧ (∑ c, w c = 15 - mu) ∧
      (∀ c, c ≠ 0 → 4 ≤ f c + w c ∧ f c + w c ≤ 5) := by
  have h13 : f 1 + f 2 + f 3 ≤ 12 := by omega
  have h1 := hle 1
  have h2 := hle 2
  have h3 := hle 3
  rcases Nat.lt_or_ge (f 1) 5 with hlt | hge
  · -- colour 1 is the four-slot
    refine ⟨![0, 4 - f 1, 5 - f 2, 5 - f 3], by simp, ?_, ?_⟩
    · rw [Fin.sum_univ_four]
      simp
      omega
    · intro c hc
      fin_cases c
      · exact absurd rfl hc
      · simp; omega
      · simp; omega
      · simp; omega
  · have h1' : f 1 = 5 := by omega
    rcases Nat.lt_or_ge (f 2) 5 with hlt | hge
    · refine ⟨![0, 5 - f 1, 4 - f 2, 5 - f 3], by simp, ?_, ?_⟩
      · rw [Fin.sum_univ_four]
        simp
        omega
      · intro c hc
        fin_cases c
        · exact absurd rfl hc
        · simp; omega
        · simp; omega
        · simp; omega
    · have h2' : f 2 = 5 := by omega
      refine ⟨![0, 5 - f 1, 5 - f 2, 4 - f 3], by simp, ?_, ?_⟩
      · rw [Fin.sum_univ_four]
        simp
        omega
      · intro c hc
        fin_cases c
        · exact absurd rfl hc
        · simp; omega
        · simp; omega
        · simp; omega

/-! ### The two exchange forms -/

/-- **Lemma A** (the K59 exchange lemma, at 16/15, valid in any triangle-free
4-colouring of a complete graph — no use of the order): if `P` has 15 points and
both `P ∪ {a}` and `P ∪ {b}` carry no colour-0 edge, then every `z ∈ P` sees the
same colour on `za` and on `zb`. -/
theorem exchange_sixteen (G : EdgeCol V 4) (h : TriangleFree G) (P : Finset V) (a b z : V)
    (hPcard : P.card = 15) (haP : a ∉ P) (hbP : b ∉ P) (hz : z ∈ P)
    (hX : ZeroFree G (insert a P)) (hY : ZeroFree G (insert b P)) :
    G.col z a = G.col z b := by
  have hzS : z ∉ P.erase z := Finset.notMem_erase z P
  have hSP : P.erase z ⊆ P := Finset.erase_subset z P
  have hS0 : ZeroFree G (P.erase z) := zeroFree_subset hX (fun x hx => Finset.mem_insert_of_mem (hSP hx))
  have hScard : (P.erase z).card = 14 := by
    rw [Finset.card_erase_of_mem hz, hPcard]
  have haS : a ∉ P.erase z := fun hh => haP (hSP hh)
  have hbS : b ∉ P.erase z := fun hh => hbP (hSP hh)
  have hza : z ≠ a := fun hh => haP (hh ▸ hz)
  have hzb : z ≠ b := fun hh => hbP (hh ▸ hz)
  have hzSa : z ∉ insert a (P.erase z) := by
    simp only [Finset.mem_insert, not_or]
    exact ⟨hza, hzS⟩
  have hzSb : z ∉ insert b (P.erase z) := by
    simp only [Finset.mem_insert, not_or]
    exact ⟨hzb, hzS⟩
  have hXa : ZeroFree G (insert a (P.erase z)) :=
    zeroFree_subset (S := insert a (P.erase z)) (T := insert a P) hX (by
    intro x hx
    simp only [Finset.mem_insert, Finset.mem_erase] at hx ⊢
    tauto)
  have hYb : ZeroFree G (insert b (P.erase z)) :=
    zeroFree_subset (S := insert b (P.erase z)) (T := insert b P) hY (by
    intro x hx
    simp only [Finset.mem_insert, Finset.mem_erase] at hx ⊢
    tauto)
  have hzero : ∀ u ∈ P.erase z, G.col z u ≠ 0 := by
    intro u hu
    exact hX z (Finset.mem_insert_of_mem hz) u (Finset.mem_insert_of_mem (hSP hu))
      (fun hh => hzS (hh ▸ hu))
  have hf0 : cntS G z (P.erase z) 0 = 0 := by
    rw [cntS, Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
    intro u hu
    simp only [Finset.mem_filter] at hu
    exact hzero u hu.1 hu.2
  have hsum : cntS G z (P.erase z) 0 + cntS G z (P.erase z) 1 +
      cntS G z (P.erase z) 2 + cntS G z (P.erase z) 3 = 14 := by
    rw [sum_cntS, hScard]
  have hfle : ∀ c : Fin 4, cntS G z (P.erase z) c ≤ 5 := by
    intro c
    by_cases hc : c = 0
    · subst hc; rw [hf0]
      omega
    · exact cntS_le_five G h z (P.erase z) hzS hS0 c hc
  have hplus : ∀ c : Fin 4, cntS G z (P.erase z) c + (if G.col z a = c then 1 else 0) ≤ 5 := by
    intro c
    by_cases hc : c = 0
    · subst hc; rw [hf0]; split <;> omega
    · rw [← cntS_insert G z a (P.erase z) haS c]
      exact cntS_le_five G h z (insert a (P.erase z)) hzSa hXa c hc
  have hplusb : ∀ c : Fin 4, cntS G z (P.erase z) c + (if G.col z b = c then 1 else 0) ≤ 5 := by
    intro c
    by_cases hc : c = 0
    · subst hc; rw [hf0]; split <;> omega
    · rw [← cntS_insert G z b (P.erase z) hbS c]
      exact cntS_le_five G h z (insert b (P.erase z)) hzSb hYb c hc
  have hca : G.col z a ≠ 0 := hX z (Finset.mem_insert_of_mem hz) a (Finset.mem_insert_self a P)
    (fun hh => haP (hh ▸ hz))
  have hcb : G.col z b ≠ 0 := hY z (Finset.mem_insert_of_mem hz) b (Finset.mem_insert_self b P)
    (fun hh => hbP (hh ▸ hz))
  have h1 : cntS G z (P.erase z) (G.col z a) + 1 ≤ 5 := by
    have := hplus (G.col z a)
    rwa [if_pos rfl] at this
  have h2 : cntS G z (P.erase z) (G.col z b) + 1 ≤ 5 := by
    have := hplusb (G.col z b)
    rwa [if_pos rfl] at this
  exact arith_sixteen _ hf0 hsum hfle _ _ hca hcb h1 h2

/-- **Lemma B** (the true statement at 15/14): with a common 14-core the exchange
forces equality at every core point whose common count is a permutation of
`(5,5,3)`, and a two-way choice elsewhere; the conclusion is only a disjunction. -/
theorem exchange_fifteen (G : EdgeCol V 4) (h : TriangleFree G) (P : Finset V) (a b z : V)
    (hPcard : P.card = 14) (haP : a ∉ P) (hbP : b ∉ P) (hz : z ∈ P)
    (hX : ZeroFree G (insert a P)) (hY : ZeroFree G (insert b P)) :
    G.col z b = G.col z a ∨
      (cntS G z (P.erase z) (G.col z a) = 4 ∧ cntS G z (P.erase z) (G.col z b) = 4) := by
  have hzS : z ∉ P.erase z := Finset.notMem_erase z P
  have hSP : P.erase z ⊆ P := Finset.erase_subset z P
  have hS0 : ZeroFree G (P.erase z) := zeroFree_subset hX (fun x hx => Finset.mem_insert_of_mem (hSP hx))
  have hScard : (P.erase z).card = 13 := by
    rw [Finset.card_erase_of_mem hz, hPcard]
  have haS : a ∉ P.erase z := fun hh => haP (hSP hh)
  have hbS : b ∉ P.erase z := fun hh => hbP (hSP hh)
  have hza : z ≠ a := fun hh => haP (hh ▸ hz)
  have hzb : z ≠ b := fun hh => hbP (hh ▸ hz)
  have hzSa : z ∉ insert a (P.erase z) := by
    simp only [Finset.mem_insert, not_or]
    exact ⟨hza, hzS⟩
  have hzSb : z ∉ insert b (P.erase z) := by
    simp only [Finset.mem_insert, not_or]
    exact ⟨hzb, hzS⟩
  have hXa : ZeroFree G (insert a (P.erase z)) :=
    zeroFree_subset (S := insert a (P.erase z)) (T := insert a P) hX (by
    intro x hx
    simp only [Finset.mem_insert, Finset.mem_erase] at hx ⊢
    tauto)
  have hYb : ZeroFree G (insert b (P.erase z)) :=
    zeroFree_subset (S := insert b (P.erase z)) (T := insert b P) hY (by
    intro x hx
    simp only [Finset.mem_insert, Finset.mem_erase] at hx ⊢
    tauto)
  have hzero : ∀ u ∈ P.erase z, G.col z u ≠ 0 := by
    intro u hu
    exact hX z (Finset.mem_insert_of_mem hz) u (Finset.mem_insert_of_mem (hSP hu))
      (fun hh => hzS (hh ▸ hu))
  have hf0 : cntS G z (P.erase z) 0 = 0 := by
    rw [cntS, Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
    intro u hu
    simp only [Finset.mem_filter] at hu
    exact hzero u hu.1 hu.2
  have hsum : cntS G z (P.erase z) 0 + cntS G z (P.erase z) 1 +
      cntS G z (P.erase z) 2 + cntS G z (P.erase z) 3 = 13 := by
    rw [sum_cntS, hScard]
  have hfle : ∀ c : Fin 4, cntS G z (P.erase z) c ≤ 5 := by
    intro c
    by_cases hc : c = 0
    · subst hc; rw [hf0]
      omega
    · exact cntS_le_five G h z (P.erase z) hzS hS0 c hc
  have hplus : ∀ c : Fin 4, cntS G z (P.erase z) c + (if G.col z a = c then 1 else 0) ≤ 5 := by
    intro c
    by_cases hc : c = 0
    · subst hc; rw [hf0]; split <;> omega
    · rw [← cntS_insert G z a (P.erase z) haS c]
      exact cntS_le_five G h z (insert a (P.erase z)) hzSa hXa c hc
  have hplusb : ∀ c : Fin 4, cntS G z (P.erase z) c + (if G.col z b = c then 1 else 0) ≤ 5 := by
    intro c
    by_cases hc : c = 0
    · subst hc; rw [hf0]; split <;> omega
    · rw [← cntS_insert G z b (P.erase z) hbS c]
      exact cntS_le_five G h z (insert b (P.erase z)) hzSb hYb c hc
  have hca : G.col z a ≠ 0 := hX z (Finset.mem_insert_of_mem hz) a (Finset.mem_insert_self a P)
    (fun hh => haP (hh ▸ hz))
  have hcb : G.col z b ≠ 0 := hY z (Finset.mem_insert_of_mem hz) b (Finset.mem_insert_self b P)
    (fun hh => hbP (hh ▸ hz))
  have h1 : cntS G z (P.erase z) (G.col z a) + 1 ≤ 5 := by
    have := hplus (G.col z a)
    rwa [if_pos rfl] at this
  have h2 : cntS G z (P.erase z) (G.col z b) + 1 ≤ 5 := by
    have := hplusb (G.col z b)
    rwa [if_pos rfl] at this
  have := arith_fifteen _ hf0 hsum hfle _ _ hca hcb h1 h2
  rcases this with hh | hh
  · exact Or.inl hh.symm
  · exact Or.inr hh

/-! ### The profile corollary -/

/-- **The arm-typed residue at the profile.**  Let two 0-critical vertices `a`,
`b` of colour-0 degree 15 have `N_0(a) ∩ N_0(b) = P` of size 14, let `r ∈ P` be
the root (so the colours of the two exclusive points from `r` are their arm
colours), and suppose those two colours differ.  Then both core counts at `r`
are 4 and every non-zero count is at least 4, so the shared part `P \ {r}` has
arm split `(4,4,5)`: four points in each of the two arms of the exclusive points
and five in the third.  Equivalently, the two senders' 4-arms are each other's
arms.

Consequently a 14-overlap of two senders whose exclusive points lie in different
arms cannot be the clone completion of the exchange: the clone reads
`col r a = col r b`. -/
theorem residue_arms (G : EdgeCol V 4) (h : TriangleFree G) (P : Finset V) (r a b : V)
    (hPcard : P.card = 14) (hr : r ∈ P) (haP : a ∉ P) (hbP : b ∉ P)
    (hX : ZeroFree G (insert a P)) (hY : ZeroFree G (insert b P))
    (hne : G.col r a ≠ G.col r b) :
    cntS G r (P.erase r) (G.col r a) = 4 ∧ cntS G r (P.erase r) (G.col r b) = 4 ∧
      (∀ c : Fin 4, c ≠ 0 → 4 ≤ cntS G r (P.erase r) c) := by
  have hra : r ≠ a := fun hh => haP (hh ▸ hr)
  have hrb : r ≠ b := fun hh => hbP (hh ▸ hr)
  have hca : G.col r a ≠ 0 :=
    hX r (Finset.mem_insert_of_mem hr) a (Finset.mem_insert_self a P) (fun hh => hra hh)
  have hcb : G.col r b ≠ 0 :=
    hY r (Finset.mem_insert_of_mem hr) b (Finset.mem_insert_self b P) (fun hh => hrb hh)
  have hrz : r ∉ P.erase r := Finset.notMem_erase r P
  have hScard : (P.erase r).card = 13 := by
    rw [Finset.card_erase_of_mem hr, hPcard]
  have hS0 : ZeroFree G (P.erase r) :=
    zeroFree_subset hX (fun x hx => Finset.mem_insert_of_mem (Finset.erase_subset r P hx))
  have hf0 : cntS G r (P.erase r) 0 = 0 := by
    rw [cntS, Finset.card_eq_zero, Finset.eq_empty_iff_forall_notMem]
    intro u hu
    simp only [Finset.mem_filter] at hu
    exact hX r (Finset.mem_insert_of_mem hr) u
      (Finset.mem_insert_of_mem (Finset.erase_subset r P hu.1))
      (fun hh => hrz (hh ▸ hu.1)) hu.2
  have hsum : cntS G r (P.erase r) 0 + cntS G r (P.erase r) 1 +
      cntS G r (P.erase r) 2 + cntS G r (P.erase r) 3 = 13 := by
    rw [sum_cntS, hScard]
  have hle : ∀ c : Fin 4, cntS G r (P.erase r) c ≤ 5 := by
    intro c
    by_cases hc : c = 0
    · subst hc; rw [hf0]; omega
    · exact cntS_le_five G h r (P.erase r) hrz hS0 c hc
  -- admissibility of the two spokes at r
  have hplusA : cntS G r (P.erase r) (G.col r a) + 1 ≤ 5 := by
    have hins : cntS G r (insert a (P.erase r)) (G.col r a) =
        cntS G r (P.erase r) (G.col r a) + 1 := by
      rw [cntS_insert G r a (P.erase r) (fun hh => haP (Finset.erase_subset r P hh))]
      simp
    rw [← hins]
    refine cntS_le_five G h r (insert a (P.erase r)) ?_ ?_ _ hca
    · intro hh
      rcases Finset.mem_insert.mp hh with h | h
      · exact hra h
      · exact (Finset.mem_erase.mp h).1 rfl
    · refine zeroFree_subset (G := G) (T := insert a P) hX ?_
      intro x hx
      simp only [Finset.mem_insert, Finset.mem_erase] at hx ⊢
      tauto
  have hplusB : cntS G r (P.erase r) (G.col r b) + 1 ≤ 5 := by
    have hins : cntS G r (insert b (P.erase r)) (G.col r b) =
        cntS G r (P.erase r) (G.col r b) + 1 := by
      rw [cntS_insert G r b (P.erase r) (fun hh => hbP (Finset.erase_subset r P hh))]
      simp
    rw [← hins]
    refine cntS_le_five G h r (insert b (P.erase r)) ?_ ?_ _ hcb
    · intro hh
      rcases Finset.mem_insert.mp hh with h | h
      · exact hrb h
      · exact (Finset.mem_erase.mp h).1 rfl
    · refine zeroFree_subset (G := G) (T := insert b P) hY ?_
      intro x hx
      simp only [Finset.mem_insert, Finset.mem_erase] at hx ⊢
      tauto
  have main := exchange_fifteen G h P a b r hPcard haP hbP hr hX hY
  rcases main with heq | ⟨ha4, hb4⟩
  · exact absurd heq.symm hne
  refine ⟨ha4, hb4, ?_⟩
  intro c hc
  rcases residue_pattern (cntS G r (P.erase r)) hf0 hsum hle with h3 | hall
  · -- a three-count colour: it is the unique admissible one, so both spokes are it
    exfalso
    have key : ∀ c1 c2 : Fin 4, c1 ≠ 0 → c2 ≠ 0 →
        cntS G r (P.erase r) c1 + 1 ≤ 5 → cntS G r (P.erase r) c2 + 1 ≤ 5 →
        cntS G r (P.erase r) c1 = 3 → c2 = c1 :=
      fun c1 c2 h1 h2 e1 e2 h3 => residue_forced _ hf0 hsum hle c1 c2 h1 h2 e1 e2 h3
    rcases h3 with h3 | h3 | h3
    · have e := key 1 (G.col r a) (by decide) hca (by omega) hplusA h3
      have f := key 1 (G.col r b) (by decide) hcb (by omega) hplusB h3
      exact hne (e.trans f.symm)
    · have e := key 2 (G.col r a) (by decide) hca (by omega) hplusA h3
      have f := key 2 (G.col r b) (by decide) hcb (by omega) hplusB h3
      exact hne (e.trans f.symm)
    · have e := key 3 (G.col r a) (by decide) hca (by omega) hplusA h3
      have f := key 3 (G.col r b) (by decide) hcb (by omega) hplusB h3
      exact hne (e.trans f.symm)
  · rcases fin4_ne_zero c hc with rfl | rfl | rfl
    · exact hall.1
    · exact hall.2.1
    · exact hall.2.2

end Residue

end K58
