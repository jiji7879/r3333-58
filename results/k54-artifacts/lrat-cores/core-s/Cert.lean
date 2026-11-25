import Mathlib

lrat_proof unsat_core_s
  (include_str "core.cnf")
  (include_str "core.lrat")

#print axioms unsat_core_s
