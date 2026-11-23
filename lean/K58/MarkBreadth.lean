import K58.MarkClasses
import K58.Frontier
import K58.ArmPinned

namespace K58

/-- Mark representatives appearing in the frozen ledger, indexed by plan and
arm. Equal (size,kind) arms use the marks of the first arm of that type. -/
def ledgerMarks : Fin 41 → Fin 4 → List ℕ := ![
  ![[5], [0], [0], [0]],
  ![[0], [0], [0], [0]],
  ![[0, 1, 2, 4, 5, 6, 7, 9], [0, 1, 2, 4, 5, 6, 7, 9], [], []],
  ![[0, 1, 2, 4, 5, 7, 9], [0, 1, 2], [], []],
  ![[0, 1, 2], [0, 1, 2], [], []],
  ![[0, 6], [0, 6], [0, 6], []],
  ![[0, 1, 2, 4], [0, 1, 2, 4], [], []],
  ![[0, 2, 4, 6], [], [], []],
  ![[1], [1], [1], []],
  ![[0], [0], [0], []],
  ![[0], [0], [0], []],
  ![[0], [0, 1, 4], [], []],
  ![[0], [0, 1], [], []],
  ![[0], [0, 1, 4], [], []],
  ![[0], [0, 1], [], []],
  ![[0], [0, 1, 2, 4, 5, 7], [], []],
  ![[0], [0, 1, 2], [], []],
  ![[0], [0, 1, 2, 4, 5, 7], [], []],
  ![[0], [0, 1, 2], [], []],
  ![[], [0, 1, 2], [0, 1, 2], []],
  ![[], [0, 1, 2, 4, 7, 9], [], []],
  ![[0], [], [], []],
  ![[], [0, 1, 2], [0, 1, 2], []],
  ![[], [0, 1, 2, 4, 7, 9], [], []],
  ![[], [0, 1], [0, 1], []],
  ![[0], [0], [], []],
  ![[0], [0], [], []],
  ![[0], [0], [], []],
  ![[0], [0], [], []],
  ![[0], [0], [], []],
  ![[0], [0], [], []],
  ![[], [], [0, 2, 4], []],
  ![[], [], [0, 1], []],
  ![[], [], [0, 1, 2, 4, 5, 7], []],
  ![[0], [], [], []],
  ![[], [], [0, 2, 4], []],
  ![[], [], [0, 1], []],
  ![[0], [0], [0], []],
  ![[0], [0], [], []],
  ![[0], [], [], []],
  ![[0], [0], [0], []]
]

/-- Positions that have a retained representative in their allowed orbit. -/
def covered15 (P : Plan) (a : Fin 4) (marks : List ℕ) : Finset (Fin 15) :=
  Finset.univ.filter fun x =>
    ∃ y ∈ positionOrbit15 (planTag P a) (P.kinds.toList[a.val]? == some 'T') x, y.val ∈ marks

def markBreadth (P : Plan) (a : Fin 4) (marks : List ℕ) : ℕ :=
  if plannedDegree P a = 15 then (covered15 P a marks).card
  else if 0 ∈ marks then plannedDegree P a else 0

set_option maxHeartbeats 0 in
set_option maxRecDepth 100000 in
theorem ledger_mark_breadth : ∀ (i : Fin 41) (a : Fin 4),
    let P := plans[i.val]'(by exact i.isLt)
    plannedThreshold P a ≤ plannedDegree P a →
      plannedDegree P a - plannedThreshold P a + 1 ≤ markBreadth P a (ledgerMarks i a) := by
  decide +kernel

/-- In a labelled 15-arm reaching the specified plan threshold, some sender can
be carried to a retained mark by a palette respecting the other three arm tags. -/
theorem reached15_has_retained_mark (i : Fin 41) (a : Fin 4)
    (G : EdgeCol (Fin 58) 4) (r : Fin 58) (A : Fin 4)
    (e : ↥(arm G r A) ≃ Fin 15)
    (P : Plan) (hP : P = plans[i.val]'(by exact i.isLt))
    (hn : plannedDegree P a = 15) (hd : deg G r A = plannedDegree P a)
    (ht : plannedThreshold P a ≤ armSenders G r A) :
    ∃ q : ↥(arm G r A), Sends G q.val r ∧ ∃ y : Fin 15, y.val ∈ ledgerMarks i a ∧
      PositionOrbit (planTag P a) (P.kinds.toList[a.val]? == some 'T') (e q) y := by
  let marks := ledgerMarks i a
  let cov := covered15 P a marks
  let g : Fin 15 ↪ Fin 58 := e.symm.toEmbedding.trans ⟨Subtype.val, Subtype.val_injective⟩
  let M := cov.map g
  have hM : M ⊆ arm G r A := by
    intro v hv
    obtain ⟨x, _, rfl⟩ := Finset.mem_map.mp hv
    exact (e.symm x).property
  have hfeas := ht.trans (arm_senders_le_deg G r A)
  rw [hd] at hfeas
  have hb : plannedDegree P a - plannedThreshold P a + 1 ≤ markBreadth P a marks := by
    subst P
    exact ledger_mark_breadth i a hfeas
  have hcard : deg G r A - plannedThreshold P a + 1 ≤ M.card := by
    simpa only [hd, M, Finset.card_map, cov, markBreadth, hn, if_true] using hb
  obtain ⟨v, hv, hs⟩ := marked_sender G r A _ M hM hcard ht
  obtain ⟨x, hx, rfl⟩ := Finset.mem_map.mp hv
  obtain ⟨y, hy, hym⟩ := (Finset.mem_filter.mp hx).2
  refine ⟨e.symm x, hs, y, hym, ?_⟩
  rw [e.apply_symm_apply]
  exact (mem_positionOrbit15 _ _ _ _).mp hy

end K58
