import K58.Templates

/-!
Every alternative colour for an edge of a critical template already occurs on
both other edges of a triangle through its endpoints.  Consequently changing
only that edge to the alternative colour creates a monochromatic triangle.
This file proves the representative statement by kernel computation; it does
not prove `K58.Classified`, the completeness of the two-template catalogue.
-/
namespace K58

def AlternativeClosed {n : ℕ} (G : EdgeCol (Fin n) 3) : Prop :=
  ∀ u v d, u ≠ v → G.col u v ≠ d → ∃ w,
    w ≠ u ∧ w ≠ v ∧ G.col u w = d ∧ G.col v w = d

instance decidableAlternativeClosed {n : ℕ} (G : EdgeCol (Fin n) 3) :
    Decidable (AlternativeClosed G) := by
  unfold AlternativeClosed
  infer_instance

theorem template_alternativeClosed_15 (t : Bool) :
    AlternativeClosed (template 15 t) := by
  revert t
  decide

theorem template_alternativeClosed_16 (t : Bool) :
    AlternativeClosed (template 16 t) := by
  revert t
  decide

#print axioms K58.template_alternativeClosed_15
#print axioms K58.template_alternativeClosed_16

end K58
