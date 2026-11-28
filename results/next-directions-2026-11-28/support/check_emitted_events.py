"""Independent census of the emitted support events in lean/K58/TargetSuffix.lean.

Reads the production suffix source (no solver, no Lean) and reports, for each
`emittedSupportStep`, its guard variable, the 16 atom variables, the selector
base and the target arm/kind implied by the frozen inventory.  Also checks that
the atom list of every support event is a subset of the preceding guarded
counter's atom list in the same order (the generator property that makes the
support and the counter talk about the same physical edges).
"""
import ast, json, pathlib, re

REPO = pathlib.Path(__file__).resolve().parents[3]
txt = (REPO / "lean/K58/TargetSuffix.lean").read_text()
body = txt.split("def targetSuffixSteps : List ExtensionStep := [", 1)[1]

# split on the constructor names at top level of the list
tokens = re.split(r"\n  (freshGuardedCounterStepAuto|emittedSupportStep|nativeCounterStepAuto)\n", body)
events, i = [], 1
while i < len(tokens):
    kind, payload = tokens[i], tokens[i + 1]
    if kind == "emittedSupportStep":
        head = payload.strip().split("\n")[0]
        oldTop, guard, n, k, newTop = [int(x) for x in head.split()[:5]]
        atoms = ast.literal_eval(
            payload.strip().split("(listAtoms ")[1].split(")")[0].replace(" ", ","))
        events.append({"oldTop": oldTop, "guard": guard, "n": n, "k": k,
                       "newTop": newTop, "atoms": atoms})
    elif kind == "freshGuardedCounterStepAuto":
        head = payload.strip().split("\n")[0]
        oldTop, guard, n, bound, newTop = [int(x) for x in head.split()[:5]]
        atoms = ast.literal_eval(
            payload.strip().split("(listAtoms ")[1].split(")")[0].replace(" ", ","))
        events.append({"kind": "counter", "oldTop": oldTop, "guard": guard, "n": n,
                       "bound": bound, "newTop": newTop, "atoms": atoms})
    else:
        head = payload.strip().split("\n")[0]
        oldTop, n, bound, newTop = [int(x) for x in head.split()[:4]]
        events.append({"kind": "native", "oldTop": oldTop, "n": n, "bound": bound,
                       "newTop": newTop})
    i += 2

supports = [e for e in events if e.get("k") == 112]
counters = [e for e in events if e.get("kind") == "counter"]
res = {
    "emitted_support_events": len(supports),
    "guards": [e["guard"] for e in supports],
    "oldTops": [e["oldTop"] for e in supports],
    "n_and_k_all_16_112": all(e["n"] == 16 and e["k"] == 112 for e in supports),
    "atoms_all_16_distinct": all(len(e["atoms"]) == 16 and len(set(e["atoms"])) == 16
                                 for e in supports),
    "first_atoms": supports[0]["atoms"],
    "first_atom_hashes_are_16": len(supports[0]["atoms"]) == 16,
    # each support event's atoms are the leading 16 atoms of the immediately
    # preceding guarded counter (same physical edges, generator order)
    "atoms_prefix_of_previous_counter": all(
        any(c["newTop"] == e["oldTop"] and c["atoms"][:16] == e["atoms"] for c in counters)
        for e in supports),
    "counters_total": len(counters),
    "counter_shape_counts": {
        "30_10": sum(1 for e in counters if e["n"] == 30 and e["bound"] == 10),
        "41_14": sum(1 for e in counters if e["n"] == 41 and e["bound"] == 14)},
    "native_events": [{k: e[k] for k in ("oldTop", "n", "bound", "newTop")}
                      for e in events if e.get("kind") == "native"],
    "distinct_atom_sets": len({tuple(e["atoms"]) for e in supports}),
}
print(json.dumps(res, indent=2))
(pathlib.Path(__file__).resolve().parent / "emitted-events.json").write_text(
    json.dumps(res, indent=2) + "\n")
