import K58.LedgerData
import K58.CaseExpansion

namespace K58

def Frozen.Family.toKey (f : Frozen.Family) (p : Fin 41) (rank : ℕ) : CaseKey :=
  ⟨p, f.arm, f.mark, f.sixteen, f.twisted, f.root,
    ![rank / f.lastRadix / f.middleRadix, rank / f.lastRadix % f.middleRadix,
      rank % f.lastRadix]⟩

def Frozen.Family.keys (f : Frozen.Family) (p : Fin 41) : List CaseKey :=
  f.runs.flatMap fun (start, len) =>
    (List.range len).map fun j => f.toKey p (start + j)

/-- All keys retained in the published ledger, ordered by plan, family and placement. -/
def frozenKeys : List CaseKey :=
  Frozen.planFamilies.flatMap fun (p, fs) => fs.flatMap fun f => f.keys p

set_option maxRecDepth 100000 in
set_option maxHeartbeats 0 in
theorem frozenKeys_length : frozenKeys.length = 113179 := by
  simp only [frozenKeys, List.length_flatMap, Frozen.Family.keys, List.length_map,
    List.length_range]
  decide +kernel

/-- Global coverage obligation for the actual frozen rows. -/
def FrozenCover : Prop := ∀ G : EdgeCol (Fin 58) 4, TriangleFree G →
  ∃ k ∈ frozenKeys, RealizesKey G k

end K58
