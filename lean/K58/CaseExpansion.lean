import K58.Cases
import K58.NamedSixteen

namespace K58

private def named16U := named16 false
private def named16T := named16 true

def supportEmbeddings {n m : ℕ} (source : EdgeCol (Fin n) 3) (a : Fin 4)
    (target : EdgeCol (Fin m) 3) (b : Fin 4) (group : List (Fin m → Fin m)) :
    List (Fin n) → List (Fin n × Fin m) → List (List ℕ)
  | [], chosen =>
    let word := chosen.reverse.map Prod.snd
    if group.all (fun g => decide (word ≤ word.map g)) then [word.map Fin.val] else []
  | x :: rest, chosen =>
    (List.finRange m).flatMap fun y =>
      if chosen.all (fun (u,v) => decide
        (v ≠ y ∧ a.succAbove (source.col u x) = b.succAbove (target.col v y))) then
        supportEmbeddings source a target b group rest ((x,y) :: chosen)
      else []

/-- Local vertices of the second template attached to host arm b, in the order
used to index that support's embeddings. -/
def supportAt (k : CaseKey) (r : Fin k.secondSize) (b : Fin 4) :=
  (List.finRange k.secondSize).filter fun i => decide
    (i ≠ r ∧ k.arm.succAbove ((template k.secondSize k.secondTwisted).col r i) = b)

def targetWords {n : ℕ} (C : EdgeCol (Fin n) 3) (a b : Fin 4) (m : ℕ) (kind : Char)
    (s : List (Fin n)) : Option (List (List ℕ)) := do
  if kind = '-' then return [List.range s.length]
  guard (kind = 'U' ∨ kind = 'T')
  let t := kind == 'T'
  if m = 15 then return supportEmbeddings C a (template 15 t) b (named15 t) s []
  if m = 16 then
    return supportEmbeddings C a (template 16 t) b (if t then named16T else named16U) s []
  failure

def supportChoices (k : CaseKey) (b : Fin 4) (s : List (Fin k.secondSize)) :
    Option (List (List ℕ)) := do
  let kind ← k.plan.kinds.toList[b.val]?
  targetWords (template k.secondSize k.secondTwisted) k.arm b (plannedDegree k.plan b) kind s

theorem named16_target_group (t : Bool) :
    (if t then named16T else named16U) = PositionSearch.automorphisms (template 16 t) := by
  cases t <;> exact named16_exact _

/-- Source order and canonical target words for a single support. Both the raw
placement generator and the numeric case decoder use this function. -/
def supportTable (k : CaseKey) (r : Fin k.secondSize) (c : Fin 3) :
    Option (List (Fin k.secondSize) × List (List ℕ)) := do
  let b := k.arm.succAbove c
  let s := supportAt k r b
  return (s, ← supportChoices k b s)

theorem supportTable_of_words (k : CaseKey) (r : Fin k.secondSize) (c : Fin 3)
    (kind : Char) (words : List (List ℕ))
    (hk : k.plan.kinds.toList[(k.arm.succAbove c).val]? = some kind)
    (hw : targetWords (template k.secondSize k.secondTwisted) k.arm (k.arm.succAbove c)
      (plannedDegree k.plan (k.arm.succAbove c)) kind (supportAt k r (k.arm.succAbove c)) = some words) :
    supportTable k r c = some (supportAt k r (k.arm.succAbove c),words) := by
  simp [supportTable, supportChoices, hk, hw]

/-- Expand the three ledger placement indices into the second block. Out-of-range
indices, incomplete supports and repeated host vertices fail the expansion. -/
def expandKey (k : CaseKey) : Option ExpandedCase := do
  if hr : k.rootPosition < k.secondSize then
    let r : Fin k.secondSize := ⟨_, hr⟩
    let parts ← (List.finRange 3).mapM fun c => do
      let b := k.arm.succAbove c
      let (s, choices) ← supportTable k r c
      let positions ← choices[k.placement c]?
      return s.zip (positions.map (blockLabel k.plan b))
    let pairs := (r, 0) :: parts.flatten
    let label := fun i => (pairs.lookup i).getD 58
    if hv : ∀ i, label i < 58 then
      let f : Fin k.secondSize → Fin 58 := fun i => ⟨_, hv i⟩
      if hi : Function.Injective f then
        if hz : f r = 0 then
          if hq : k.markPosition < plannedDegree k.plan k.arm then
            return ⟨k, f, hi, hr, hz, hq⟩
    failure
  else failure

/-- The meaning of a raw ledger key, including its three numeric placements. -/
def RealizesKey (G : EdgeCol (Fin 58) 4) (k : CaseKey) : Prop :=
  ∃ C, expandKey k = some C ∧ RealizesCase G C

end K58
