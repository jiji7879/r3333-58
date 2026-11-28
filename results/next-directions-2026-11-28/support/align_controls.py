"""Align the Lean-side finite predicates with the emitted catalogue, and pick
explicit negative controls.  Reproduces lean/K58/Templates.lean's T16 palette."""
import ast, json, pathlib
from itertools import combinations

REPO = pathlib.Path(__file__).resolve().parents[3]
DC = {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 1, 8: 0, 9: 2, 10: 0, 11: 1,
      12: 0, 13: 1, 14: 2}
TRADE = {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}
SWAP = {0: 0, 1: 2, 2: 1}
def col(u, v, twisted=True):
    r = DC.get(u ^ v, 0)
    return SWAP[r] if twisted and 16 * min(u, v) + max(u, v) in TRADE else r
T = lambda u, v: col(u, v, True)
U = lambda u, v: col(u, v, False)

def block(path, start, end):
    return path.read_text().split(start, 1)[1].split(end, 1)[0].strip()
target = ast.literal_eval(block(REPO / "lean/K58/TargetSuffix.lean",
                                "def targetSupports : List (List Nat) :=",
                                "\n\n/-- Exact linked allocation"))
TS = {tuple(s) for s in target}

def indep0(S, C=T):
    return all(C(u, v) != 0 for u, v in combinations(sorted(S), 2))

# ordered P4 tuples with the six K60-style relations
tuples = []
for a in range(16):
    for b in range(16):
        if T(a, b) != 1: continue
        for d in range(16):
            if T(b, d) != 1 or T(a, d) != 2: continue
            for e in range(16):
                if T(d, e) != 1 or T(a, e) != 2 or T(b, e) != 2: continue
                tuples.append((a, b, d, e))
p4sets = {tuple(sorted(set(t))) for t in tuples}
u_tuples = []
for a in range(16):
    for b in range(16):
        if U(a, b) != 1: continue
        for d in range(16):
            if U(b, d) != 1 or U(a, d) != 2: continue
            for e in range(16):
                if U(d, e) != 1 or U(a, e) != 2 or U(b, e) != 2: continue
                u_tuples.append((a, b, d, e))
u4 = {tuple(sorted(set(t))) for t in u_tuples}

five = [s for s in target if len(s) == 5]
four = [s for s in target if len(s) == 4]
res = {
  "p4_order_tuple_count": len(tuples),
  "p4_ordered_tuple_sets_equal_target_four": p4sets == {tuple(s) for s in four},
  "p4_sets_count": len(p4sets),
  "u16_p4_sets_are_a_control": {"count": len(u4), "all_in_target": u4 <= {tuple(s) for s in four},
                                 "equals_target_four": u4 == {tuple(s) for s in four}},
  "five_sets_are_exactly_the_indep5": {tuple(s) for s in five} ==
      {tuple(sorted(p)) for p in combinations(range(16), 5) if indep0(p)},
}
# candidate negative controls
indep_not_p4 = sorted({tuple(sorted(p)) for p in combinations(range(16), 4)
                       if indep0(p)} - {tuple(s) for s in four})
p4_with_marked_edge = sorted({tuple(sorted(p)) for p in combinations(range(16), 4)
                              if not indep0(p)
                              and sorted(sum(T(u, v) == 1 for v in p if v != u) for u in p) == [1,1,2,2]})
# P4 in local colour 2 with local-1 diagonals  (the "either colour" shortcut)
alt = sorted({tuple(sorted(p)) for p in combinations(range(16), 4)
              if all(T(u, v) != 1 for u, v in combinations(p, 2))
              and sorted(sum(T(u, v) == 2 for v in p if v != u) for u in p) == [1,1,2,2]})
def degrees(s, c=1):
    return sorted(sum(T(u, v) == c for v in s if v != u) for u in s)
res["controls"] = {
  "indep_not_p4_count": len(indep_not_p4), "indep_not_p4_first": list(indep_not_p4[:3]),
  "indep_not_p4_first_degrees": [degrees(s) for s in indep_not_p4[:3]],
  "p4_with_marked_edge_count": len(p4_with_marked_edge),
  "p4_with_marked_edge_first": list(p4_with_marked_edge[:3]),
  "color2_p4_with_col1_diag_count": len(alt), "color2_p4_first": list(alt[:3]),
  "all_controls_outside_target": all(tuple(s) not in TS for s in
      list(indep_not_p4[:3]) + list(p4_with_marked_edge[:3]) + list(alt[:3])),
}
# a catalogue entry (for a "positive" sample) and a one-bit-away non-member
sample = tuple(four[0])
print(json.dumps(res, indent=2))
(pathlib.Path(__file__).resolve().parent / "align-controls.json").write_text(json.dumps(res, indent=2) + "\n")
