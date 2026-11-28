"""Independent check: is the emitted 112-support catalogue exactly the set of
colour-marked-independent 4/5-subsets of the T16 named template?

Reads the production list from lean/K58/TargetSuffix.lean and the generator
list from tools/color-resolved-wallcc/frozen/support_tables.py, and re-derives
both from lean/K58/Templates.lean's dc/trade/swap01 definitions reproduced here.
No solver, no network.
"""
import ast, json, pathlib, sys
from itertools import combinations

REPO = pathlib.Path(__file__).resolve().parents[3]
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "tools/color-resolved-wallcc/frozen"))
from support_tables import allowed_supports  # noqa: E402

# --- lean/K58/Templates.lean, reproduced literally -------------------------
DC = {1: 0, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 1, 8: 0, 9: 2, 10: 0, 11: 1,
      12: 0, 13: 1, 14: 2}
TRADE = {21, 22, 28, 31, 37, 38, 44, 47, 88, 91, 104, 107, 140, 143, 188, 191}
SWAP01 = {0: 0, 1: 2, 2: 1}


def dc(d):
    return DC.get(d, 0)


def template_col(twisted, u, v):
    rule = dc(u ^ v)
    if twisted and 16 * min(u, v) + max(u, v) in TRADE:
        return SWAP01[rule]
    return rule


def template(n, twisted):
    return [[template_col(twisted, u, v) for v in range(n)] for u in range(n)]


def named(n, twisted, forbidden):
    palette = [c for c in range(4) if c != forbidden]
    return [[palette[c] for c in row] for row in template(n, twisted)]


# --- production list -------------------------------------------------------
def block(path, start, end):
    return path.read_text().split(start, 1)[1].split(end, 1)[0].strip()


target = ast.literal_eval(block(REPO / "lean/K58/TargetSuffix.lean",
                                "def targetSupports : List (List Nat) :=",
                                "\n\n/-- Exact linked allocation"))
gen = [sorted(s) for s in allowed_supports(16, "T", 0, 1)]
mine = named(16, True, 0)

# cross-check the reproduced template against the frozen generator's matrix
sys.path.insert(0, str(REPO / "tools/color-resolved-wallcc/frozen"))
from gluing import named_template  # noqa: E402
assert [list(r) for r in named_template(16, "T", 0)] == mine, "template mismatch"

FROZEN = {4: [], 5: []}
for k in (4, 5):
    for pts in combinations(range(16), k):
        if any(mine[u][v] == 1 for u, v in combinations(pts, 2)):
            continue
        deg = sorted(sum(mine[u][v] == 2 for v in pts if v != u) for u in pts)
        if k == 4 and deg == [1, 1, 2, 2]:
            FROZEN[4].append(list(pts))
        if k == 5 and deg == [2, 2, 2, 2, 2]:
            FROZEN[5].append(list(pts))

# weaker candidate characterisation: independence in colour 1 + size 4 or 5
INDEP = {4: [], 5: []}
for k in (4, 5):
    for pts in combinations(range(16), k):
        if all(mine[u][v] != 1 for u, v in combinations(pts, 2)):
            INDEP[k].append(list(pts))

res = {
    "template_T16_named_coords_matches_frozen_gluing": True,
    "target_source_len": len(target),
    "target_source_4": sum(len(s) == 4 for s in target),
    "target_source_5": sum(len(s) == 5 for s in target),
    "target_is_sorted_unique": all(s == sorted(set(s)) for s in target) and
        len({tuple(s) for s in target}) == len(target),
    "frozen_p4c5_equals_target_ordered": FROZEN[4] + FROZEN[5] == target,
    "frozen_p4c5_equals_target_as_sets":
        {tuple(s) for s in FROZEN[4] + FROZEN[5]} == {tuple(s) for s in target},
    "p4c5_counts": {"4": len(FROZEN[4]), "5": len(FROZEN[5])},
    "indep_only_counts": {"4": len(INDEP[4]), "5": len(INDEP[5])},
    "indep_only_equals_target":
        {tuple(s) for s in INDEP[4] + INDEP[5]} == {tuple(s) for s in target},
    "indep_equals_p4c5":
        {tuple(s) for s in INDEP[4] + INDEP[5]} == {tuple(s) for s in FROZEN[4] + FROZEN[5]},
}
# negative controls: wrong palette, wrong template, wrong path colour
controls = {}
for name, mat in (
    ("T16_marked0_path2", named(16, True, 1)),
    ("U16_marked1_path2", named(16, False, 1)),
    ("T16_marked1_path3", named(16, True, 1)),
    ("T15_marked1_path2", named(15, True, 1)),
):
    marked = int(name.split("marked")[1].split("_")[0])
    path = int(name.split("path")[1].split("_")[0])
    got = set()
    n = len(mat)
    for k in (4, 5):
        for pts in combinations(range(n), k):
            if any(mat[u][v] == marked for u, v in combinations(pts, 2)):
                continue
            deg = sorted(sum(mat[u][v] == path for v in pts if v != u) for u in pts)
            if (k == 4 and deg == [1, 1, 2, 2]) or (k == 5 and deg == [2, 2, 2, 2, 2]):
                got.add(tuple(pts))
    tgt = {tuple(s) for s in target}
    controls[name] = {"count": len(got), "equals_target": got == tgt,
                      "intersection_size": len(got & tgt)}
res["negative_controls"] = controls
res["single_bit_control_mask_0_2_4_6_vs_0_2_4_7_in_target"] = (
    [0, 2, 4, 6] in target, [0, 2, 4, 7] in target)
print(json.dumps(res, indent=2))
out = pathlib.Path(__file__).resolve().parent / "catalogue-semantics.json"
out.write_text(json.dumps(res, indent=2) + "\n")
