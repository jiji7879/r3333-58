#!/usr/bin/env python3
"""Check consistency of pilot logs and emit the numerical summary used in ASSESSMENT.md."""
from pathlib import Path
import hashlib
import json
here = Path(__file__).resolve().parent
def load(name): return [json.loads(x) for x in (here/name).read_text().splitlines()]
def rounds(name): return [r for r in load(name) if r.get("event") == "round"]
def brute(n,k):
    import itertools
    es=list(itertools.combinations(range(n),2)); ts=list(itertools.combinations(range(n),3)); ans=0
    for values in itertools.product(range(k),repeat=len(es)):
        colour=dict(zip(es,values))
        if all(len({colour[tuple(sorted((i,j)))],colour[tuple(sorted((i,l)))],colour[tuple(sorted((j,l)))]}) > 1
               for i,j,l in ts): ans += 1
    return ans
for r in load("selftest.jsonl"):
    if r.get("test") == "exact_enumeration": assert r["models"] == r["expected"] == brute(r["n"],r["k"]) and r["pass"]
c = rounds("k51_core20_50k.jsonl")
assert [r["status"] for r in c[-2:]] == ["UNSAT_ASSUMPTIONS","UNKNOWN"]
u = c[:21]
assert len(c) == 22 and all(r["status"] == "UNSAT_ASSUMPTIONS" for r in u)
assert u[0]["core_size"] == 321 and u[0]["removed"] == 65
assert u[-1]["active_after"] == 485 and c[-1]["active_edges"] == 485
assert c[-1]["conflicts"] == 50003
short = rounds("k51_core20_40rounds.jsonl")
assert len(short) == 22
keys = ["round","status","core_size","removed","active_after","active_before","removed_first_edge_colour","conflicts","decisions"]
for x,y in zip(short[:21],u): assert all(x.get(q) == y.get(q) for q in keys)
one = rounds("k51_one_pin_80.jsonl")
assert len(one) == 80 and all(r["status"] == "UNSAT_ASSUMPTIONS" and r["removed"] == 1 and r["conflicts"] == 0 for r in one)
assert one[-1]["active_after"] == 1195 and len({tuple(r["removed_first_edge_colour"]) for r in one}) == 80
control = rounds("k50_control.jsonl")
assert [(r["status"],r.get("core_size"),r.get("removed")) for r in control] == [("UNSAT_ASSUMPTIONS",3,1),("SAT",None,None)]
assert control[-1]["model_defects"] == 0
replay = json.loads((here/"one_pin_round80_replay.json").read_text())
assert replay["strict_verified"] and replay["wrong_parent_rejected"] and replay["active_unit_pins"] == 1195
zebra_self = load("zebra_selftest.jsonl")
assert len(zebra_self) == 1 and zebra_self[0]["models"] == zebra_self[0]["brute_force"] == 48 and zebra_self[0]["pass"]
zebra = json.loads((here/"toeplitz_k51_result.json").read_text())
assert zebra["status"] == "UNKNOWN" and zebra["solver_exit"] == 0 and zebra["no_family_exclusion"] and zebra["no_model"]
assert zebra["variables"] == 5300 and zebra["clauses"] == 102775
summary = {
  "k50_control": {"initial_core":3,"pins_released":1,"sat_round":1,"independent_model_defects":0},
  "k51_core20": {"assumption_unsat_rounds":21,"first_core":321,"first_released":65,
                 "core_min":min(r["core_size"] for r in u),"core_max":max(r["core_size"] for r in u),
                 "released_before_unknown":790,"active_at_unknown":485,
                 "unknown_conflicts":c[-1]["conflicts"],"rounded_wall_seconds":1.66,
                 "status":"UNKNOWN_NOT_UNSAT","valid_k51_model_written":False},
  "k51_one_pin": {"assumption_unsat_reports":80,"active_after":1195,"released":80,
                  "all_reported_conflicts_zero":True,"only_round80_independently_DRAT_replayed":True},
  "k51_literal_zebra": {"definition":"x_(i,j),c iff z_(j-i),c (Toeplitz, not circulant)",
                        "variables":5300,"clauses":102775,"n4_models_sat_and_brute":48,
                        "status":"UNKNOWN_NOT_UNSAT","conflict_cap":50000,
                        "valid_k51_model_written":False,"family_exclusion_proven":False},
  "round80_replay": replay,
  "artifact_sha256": hashlib.sha256((here.parents[2]/"artifacts/k51_relax_m3_1defect_NOT_a_valid_colouring.col").read_bytes()).hexdigest()
}
(here/"pilot_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
print(json.dumps(summary,indent=2))
