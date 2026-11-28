import Mathlib

open scoped BigOperators
open Finset

/-- The per-root arithmetic used in the K58 full-vertex deficit bound.
The interval is exactly the colour-degree range at order 58. -/
theorem k58_root_margin (d : ℤ) (h9 : 9 ≤ d) (h16 : d ≤ 16) :
    60 ≤ 29 * d - d ^ 2 - 120 := by
  interval_cases d <;> norm_num

/-- Summing the margin over 58 vertices gives deficit at least 3480.
Here `ℓ v` denotes the exact catalogue value `e(3,16;57-d(v))`;
the constructive Clebsch bound supplies `ℓ v ≤ 120`. -/
theorem k58_total_deficit_lower {ι : Type*} [Fintype ι]
    (hcard : Fintype.card ι = 58) (d ℓ : ι → ℤ)
    (h9 : ∀ i, 9 ≤ d i) (h16 : ∀ i, d i ≤ 16) (hℓ : ∀ i, ℓ i ≤ 120) :
    3480 ≤ ∑ i, (29 * d i - d i ^ 2 - ℓ i) := by
  have hpoint : ∀ i ∈ (univ : Finset ι), 60 ≤ 29 * d i - d i ^ 2 - ℓ i := by
    intro i _
    have h := k58_root_margin (d i) (h9 i) (h16 i)
    have hi := hℓ i
    omega
  calc
    (3480 : ℤ) = ∑ _i ∈ (univ : Finset ι), 60 := by simp [hcard]
    _ ≤ ∑ i, (29 * d i - d i ^ 2 - ℓ i) := Finset.sum_le_sum hpoint

/-- A literal `(4,3)` instance contradicts the generic form of Duggan's
Lemma 2 as printed: K3 has n=3, e=3, three degree-2 vertices and empty H2. -/
theorem k3_naive_phi : (3 : ℤ) * 3 - 3 * (0 + 2 ^ 2) = -3 := by norm_num

#print axioms k58_root_margin
#print axioms k58_total_deficit_lower
#print axioms k3_naive_phi
