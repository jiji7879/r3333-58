import K58.TransportReplay
namespace K58
noncomputable section
set_option maxHeartbeats 0
set_option maxRecDepth 100000
private def src : CaseKey := ⟨0, 0, 5, false, false, 2, ![0, 0, 0]⟩
private def dst : CaseKey := ⟨0, 0, 5, false, false, 1, ![0, 0, 0]⟩
private def vertexMap : Fin 58 → Fin 58 := ![0, 8, 9, 2, 15, 11, 6, 13, 4, 12, 5, 14, 3, 7, 10, 1, 16, 17, 19, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 45, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 32, 30, 31, 34, 33, 35, 36, 37, 38, 39, 40, 41, 42, 43]
private theorem vertexBij : Function.Bijective vertexMap := by decide +kernel
private def vertex := Equiv.ofBijective vertexMap vertexBij
private def paletteMap : Fin 4 → Fin 4 := ![0, 1, 3, 2]
private theorem paletteBij : Function.Bijective paletteMap := by decide +kernel
private def palette := Equiv.ofBijective paletteMap paletteBij
/-- Plan zero, arm zero, retained sender five. A palette transposition takes
the deleted U template with reference two into the frozen row at reference one. -/
theorem example_transport_into_frozen : CoveredKey (⟨0, 0, 5, false, false, 2, ![0,0,0]⟩ : CaseKey) :=
  covered_of_transportCheck (Frozen.Address.mem (a := ⟨0,1,0,0⟩) (k := dst) (by rfl))
    (e := vertex) (p := palette) (by decide +kernel)
end
end K58
