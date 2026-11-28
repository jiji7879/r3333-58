# AMS wall follow-up

Exact parent `90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae`, working `39d669585242b4fe6447908f0812906e62077ae0a5403837e6470516e623cf38`, RUP/CAS prefix `dd5d54003af3959c52ac3fde604ababda980d1a90277248332eb1fbd55aaf4c3`.

1. Semantic readiness check completed before solver work: current native Lean binding is used correctly, full build and native counter/gadget checks pass, no full-parent semantic assembly exists. The older sign-renamed atLeast theorem is not reused as native. `full_root=False` is a relaxation: UNSAT of the exact relaxation transfers only after proving extension obligations, SAT never establishes a physical row.

2. The conditional boundary encoder preserves projected models: recurrence clauses stay unconditional, only overflow clauses receive the negative guard. Exact parent inventory: 31 guarded sender counters, 21,203 recurrence and 418 overflow clauses. Boundary would remove 21,203 guard occurrences without changing clauses or auxiliaries. Favourable performance is not established yet.

3. Pure-kernel configurable maximalisation is now proved and registered in `lean/K58/ConfigurableMaximal.lean`. Safe one-edge recolouring, colour-c/path monotonicity, sequential normalisation and OutsideDependent suffix preservation establish `normalForm_equisatisfiable`. Exact witness-binding and long-disjunction lemmas match the three emitted clauses and final disjunction. Only standard axioms occur.

4. Exact semantic map independently reconstructed the parent and all gadget streams: 438 frozen units, 31 guards, 15 support families/1,680 selectors, 112 direct colour-2 supports (96 P4 and 16 C5), 12,921 contiguous disjoint auxiliaries. It also verified 504 MCF physical variables absent from the actual 49,340-clause suffix, 126 configurable edges and 20 fixed exclusions. Five real obligations remain: frozen-unit realization, criticality-to-guards, floor witness selection, exact support membership, and Lean list/byte assembly.

5. Current MCTS, selective-cubing, matched boundary performance and full-parent assembly experiments continue. No solver claim beyond CNF performance is permitted, and no OPEN is a verdict.
