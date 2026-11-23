import K58.Frontier
import K58.Marking
import Mathlib.Data.Fin.Tuple.Reflection

namespace K58

private def perm4 : Fin 24 → Fin 4 → Fin 4 := ![
  ![0, 1, 2, 3],
  ![0, 1, 3, 2],
  ![0, 2, 1, 3],
  ![0, 2, 3, 1],
  ![0, 3, 1, 2],
  ![0, 3, 2, 1],
  ![1, 0, 2, 3],
  ![1, 0, 3, 2],
  ![1, 2, 0, 3],
  ![1, 2, 3, 0],
  ![1, 3, 0, 2],
  ![1, 3, 2, 0],
  ![2, 0, 1, 3],
  ![2, 0, 3, 1],
  ![2, 1, 0, 3],
  ![2, 1, 3, 0],
  ![2, 3, 0, 1],
  ![2, 3, 1, 0],
  ![3, 0, 1, 2],
  ![3, 0, 2, 1],
  ![3, 1, 0, 2],
  ![3, 1, 2, 0],
  ![3, 2, 0, 1],
  ![3, 2, 1, 0]
]

private theorem perm4_bij : ∀ i, Function.Bijective (perm4 i) := by decide

/-- Witnesses indexed by the degree profile and the four chosen template bits. -/
private def kindChoice : Fin 11 → Fin 16 → Fin 41 × Fin 24 := ![
  ![(1, 0), (0, 0), (1, 0), (0, 0), (1, 0), (0, 0), (1, 0), (0, 0), (1, 0), (0, 0), (1, 0), (0, 0), (1, 0), (0, 0), (1, 0), (0, 0)],
  ![(4, 0), (3, 0), (3, 6), (2, 0), (4, 0), (3, 0), (3, 6), (2, 0), (4, 0), (3, 0), (3, 6), (2, 0), (4, 0), (3, 0), (3, 6), (2, 0)],
  ![(8, 0), (7, 0), (7, 6), (6, 0), (7, 12), (6, 2), (6, 8), (5, 0), (8, 0), (7, 0), (7, 6), (6, 0), (7, 12), (6, 2), (6, 8), (5, 0)],
  ![(10, 0), (9, 0), (10, 0), (9, 0), (10, 0), (9, 0), (10, 0), (9, 0), (10, 0), (9, 0), (10, 0), (9, 0), (10, 0), (9, 0), (10, 0), (9, 0)],
  ![(14, 0), (12, 0), (13, 0), (11, 0), (14, 0), (12, 0), (13, 0), (11, 0), (14, 0), (12, 0), (13, 0), (11, 0), (14, 0), (12, 0), (13, 0), (11, 0)],
  ![(18, 0), (16, 0), (17, 0), (15, 0), (18, 0), (16, 0), (17, 0), (15, 0), (18, 0), (16, 0), (17, 0), (15, 0), (18, 0), (16, 0), (17, 0), (15, 0)],
  ![(24, 0), (21, 0), (23, 0), (20, 0), (23, 2), (20, 2), (22, 0), (19, 0), (24, 0), (21, 0), (23, 0), (20, 0), (23, 2), (20, 2), (22, 0), (19, 0)],
  ![(27, 0), (26, 0), (26, 6), (25, 0), (27, 0), (26, 0), (26, 6), (25, 0), (27, 0), (26, 0), (26, 6), (25, 0), (27, 0), (26, 0), (26, 6), (25, 0)],
  ![(30, 0), (29, 0), (29, 6), (28, 0), (30, 0), (29, 0), (29, 6), (28, 0), (30, 0), (29, 0), (29, 6), (28, 0), (30, 0), (29, 0), (29, 6), (28, 0)],
  ![(36, 0), (34, 0), (34, 6), (32, 0), (35, 0), (33, 0), (33, 6), (31, 0), (36, 0), (34, 0), (34, 6), (32, 0), (35, 0), (33, 0), (33, 6), (31, 0)],
  ![(40, 0), (39, 0), (39, 6), (38, 0), (39, 12), (38, 2), (38, 8), (37, 0), (40, 0), (39, 0), (39, 6), (38, 0), (39, 12), (38, 2), (38, 8), (37, 0)]
]

private def bitCode (k : Fin 4 → Bool) : Fin 16 :=
  ⟨(if k 0 then 1 else 0) + (if k 1 then 2 else 0) +
    (if k 2 then 4 else 0) + (if k 3 then 8 else 0), by split_ifs <;> decide⟩

private def profAt (i : Fin 11) := degreeProfiles58[i.val]'(by exact i.isLt)
private def planAt (i : Fin 41) := plans[i.val]'(by exact i.isLt)

private def hasKind (P : Plan) (a : Fin 4) (k : Bool) : Prop :=
  P.kinds.toList[a.val]? = some (if k then 'T' else 'U')

private instance (P : Plan) (a : Fin 4) (k : Bool) : Decidable (hasKind P a k) := by
  unfold hasKind; infer_instance

private theorem kindChoice_ok : ∀ (i : Fin 11) (k : Fin 4 → Bool) (a : Fin 4),
    let row := kindChoice i (bitCode k)
    let P := planAt row.1
    let b := perm4 row.2 a
    plannedDegree P a = (profAt i)[b.val]?.getD 0 ∧
      (15 ≤ plannedDegree P a → hasKind P a (k b)) := by decide

/-- A balanced root has a single plan and a single colour permutation
simultaneously matching the degrees, the pinned kinds, and the reached threshold. -/
theorem root_plan_with_kinds (G : EdgeCol (Fin 58) 4) (hG : TriangleFree G) :
    ∃ r, w G r ≤ H G r ∧ ∃ P ∈ plans, ∃ σ : Equiv.Perm (Fin 4),
      (∀ a, deg G r (σ a) = plannedDegree P a) ∧
      (∀ a, 15 ≤ plannedDegree P a → ∃ t : Bool,
        P.kinds.toList[a.val]? = some (if t then 'T' else 'U') ∧
        PinnedArm G r (σ a) (plannedDegree P a) t) ∧
      ∃ a, plannedThreshold P a ≤ armSenders G r (σ a) := by
  classical
  obtain ⟨r, hr⟩ := exists_root G
  obtain ⟨τ, hτ⟩ := root_degree_profile G hG r
  obtain ⟨i, hi⟩ := List.mem_iff_get.mp hτ
  let profileIndex : Fin 11 := i
  have hlist : profAt profileIndex =
      [deg G r (τ 0), deg G r (τ 1), deg G r (τ 2), deg G r (τ 3)] := hi
  have value (b : Fin 4) : (profAt profileIndex)[b.val]?.getD 0 = deg G r (τ b) := by
    rw [hlist]
    fin_cases b <;> rfl
  have pins (b : Fin 4) : ∃ t : Bool, 15 ≤ deg G r (τ b) →
      PinnedArm G r (τ b) (deg G r (τ b)) t := by
    by_cases h : 15 ≤ deg G r (τ b)
    · have cap := deg_le_sixteen G hG r (τ b)
      obtain ⟨t, ht⟩ := critical_arm_pinned G hG r (τ b) (by omega)
      exact ⟨t, fun _ => ht⟩
    · exact ⟨false, fun h' => (h h').elim⟩
  choose k hk using pins
  let row := kindChoice profileIndex (bitCode k)
  let π := Equiv.ofBijective (perm4 row.2) (perm4_bij row.2)
  let P := planAt row.1
  let σ := π.trans τ
  have hP : P ∈ plans := List.getElem_mem _
  have hrow (a : Fin 4) : plannedDegree P a = deg G r (σ a) ∧
      (15 ≤ plannedDegree P a → hasKind P a (k (π a))) := by
    simpa only [P, σ, π, row, Equiv.trans_apply, Equiv.ofBijective_apply, value] using
      kindChoice_ok profileIndex k a
  have hp (a : Fin 4) := (hrow a).1.symm
  obtain ⟨a, ha, _⟩ := normalized_plan_arm_reaches G r hr σ P hP hp
  refine ⟨r, hr, P, hP, σ, hp, ?_, a, ha⟩
  intro b hb
  refine ⟨k (π b), (hrow b).2 hb, ?_⟩
  rw [(hrow b).1] at hb ⊢
  exact hk (π b) hb

end K58
