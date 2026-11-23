import K58.CaseRealization
import K58.MarkBreadth

namespace K58

/-- Named-colour orbits of the root position in the second, 15-vertex block. -/
def secondRoots15 (twisted : Bool) : List ℕ :=
  if twisted then [0,1,2,4,5,6,7,9,12] else [0,1,2]

theorem secondRoots15_exact (twisted : Bool) : secondRoots15 twisted =
    (markClasses15 (id : Fin 3 → Fin 3) twisted).map (fun v => v.1.val) := by
  cases twisted <;> decide

/-- Canonical profiles and kinds keep the first arm of each equal type. The
sender's root position uses the named-colour vertex orbits in the second block. -/
def rawFamilies : List CaseKey :=
  (List.finRange 41).flatMap fun i =>
    let P := indexedPlan i
    (List.finRange 4).flatMap fun a =>
      if (List.finRange 4).any (fun b => decide (b < a ∧
        plannedDegree P a = plannedDegree P b ∧ P.kinds.toList[a.val]? = P.kinds.toList[b.val]?)) then []
      else (ledgerMarks i a).flatMap fun q =>
        [false, true].flatMap fun sixteen => [false, true].flatMap fun twisted =>
          let roots := if sixteen then [0] else secondRoots15 twisted
          roots.map fun r => ⟨i, a, q, sixteen, twisted, r, fun _ => 0⟩

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem rawFamilies_length : rawFamilies.length = 1764 := by decide +kernel

/-- Dimensions of the three ordered support tables. -/
def placementShape (k : CaseKey) : Option (ℕ × ℕ × ℕ) := do
  if hr : k.rootPosition < k.secondSize then
    let r : Fin k.secondSize := ⟨_,hr⟩
    let (_,x) ← supportTable k r 0
    let (_,y) ← supportTable k r 1
    let (_,z) ← supportTable k r 2
    return (x.length,y.length,z.length)
  failure

/-- All triples before the marked second block's stabilizer and the remaining
global palette permutations act on the placements. -/
def rawPlacements (k : CaseKey) : List CaseKey := Id.run do
  let some (nx,ny,nz) := placementShape k | return []
  return (List.range nx).flatMap fun a => (List.range ny).flatMap fun b =>
    (List.range nz).map fun c => {k with placement := ![a,b,c]}

def rawKeys : List CaseKey := rawFamilies.flatMap rawPlacements

/-- Geometric coverage before the last finite quotient. -/
def RawCover : Prop := ∀ G : EdgeCol (Fin 58) 4, TriangleFree G →
  ∃ k ∈ rawKeys, RealizesKey G k

/-- A purely finite obligation for the explicit vertex and palette permutations
stored in the placement transport certificate. -/
def RawTransportCover : Prop :=
  ∀ k ∈ rawKeys, k ∈ frozenKeys ∨ ∀ A, expandKey k = some A →
    ∃ j ∈ frozenKeys, ∃ B, expandKey j = some B ∧
      ∃ e p, UnitTransport A B e p

theorem frozenCover_of_rawCover (raw : RawCover) (transports : RawTransportCover) : FrozenCover := by
  intro G hG
  obtain ⟨k, hk, A, hA, hGA⟩ := raw G hG
  rcases transports k hk with retained | moved
  · exact ⟨k, retained, A, hA, hGA⟩
  obtain ⟨j, hj, B, hB, e, p, ht⟩ := moved A hA
  exact ⟨j, hj, B, hB, realizes_of_unitTransport ht hGA⟩

end K58
