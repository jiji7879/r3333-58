# Problem

The 1,300 hard, historically solved `full_root=true` K58 rows are all UNSAT, but stock CaDiCaL needs large searches. Find general clauses or compact constraints that are implied by each original row formula and that measurably improve matched CaDiCaL solving, building beyond the existing paired-arm, signed, square and six-site families.

A completed result requires a precise soundness proof with correct guard and auxiliary-variable scope; a deterministic generator tied to the original CNF identity; meaningful positive and negative controls; at least representative fresh original-parent DRAT verification without warning suppression; and matched fresh solver evidence on the original parents, distinguishing conflict counts, process CPU, wall time, proof overhead, and encoding-generation time. OPEN is neither SAT nor UNSAT. A local propagation improvement alone is not enough to call the solver improved. The scope is solver research, not a new Ramsey bound or a production-cover update.

The supplied `K58_square_spoke_wall_test(2).zip` is byte-identical to the previously audited square package. `K58_CaDiCaL_Glucose_reduction.zip` additionally asks for a local assessment of a Glucose-style learned-clause reducer on the same completed hard-row baseline.
