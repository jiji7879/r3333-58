# Member supplements, kept for provenance

Lean files produced by Ultramath members that are **not** in `lean/build.sh`.
They build against `lean/` (and `lean/K58/Arm.lean` for the model lemmas) but
their declarations overlap the integrated development, so importing them next to
it would collide. Keep them as sources; lift a declaration into `lean/K58/` if
it is needed downstream.

## `m4/` — swarm `smwr0lr3q`, direction d4/d10

| file | content | status |
| --- | --- | --- |
| `Interface.lean` | `interface_sum`, `interface` (a second kernel-checked proof of the interface identity), `indep_le_sixteen`, `deg_le_sixteen`, `armFar_*` (arm-set saturation `0/2/5`) | builds at 4.33.1, axiom-clean |
| `Colours.lean` | `nbr_disjoint_of_col`, `colour_occurs_inside`, **`exists_disjoint_arm_parts`** — every colour occurs on an edge inside the 42 outside the arm, so some pair has disjoint `M_f` parts | builds, axiom-clean |
| `Sixteen.lean` | **`forced_six`, `forced_six_two`** — a fully critical 16-arm forces one and then two outside vertices with `>= 6` colour-0 edges into it; the source of the `14p <= 5(57-p) iff p <= 15` boundary fact | builds, axiom-clean |

The saturation bounds and the interface identity are already in `lean/K58/Arm.lean`
under different names; `exists_disjoint_arm_parts` and `forced_six` are not
anywhere else and are the two worth lifting if the 16-armed wall profiles are
worked.
