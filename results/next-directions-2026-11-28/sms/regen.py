#!/usr/bin/env python3
"""Regenerate the exact retained ordinary K58 parent and its cube, record hashes.

Read-only with respect to the repository: writes only into this directory.
"""
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FROZEN = ROOT / "tools/color-resolved-wallcc/frozen"
sys.path.insert(0, str(FROZEN))
from gluing import Family, units                     # noqa: E402
from dense import marked_threshold                   # noqa: E402
from cover_evidence import formula_chunks, RECIPE    # noqa: E402

ROW_ID = "06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06"
CUBE = [-1413, 1014]
EXPECT_PARENT = "90d06e3254f64986032a66f619ba6e7ae273d89850a7d245b7992e0b860f56ae"
EXPECT_CUBE = "8791f627a2e567785018d46b1a6fa15ced009fc0490b3bab4f218108182460a8"


def load_row():
    with gzip.open(ROOT / "tools/color-resolved-wallcc/data/wall.jsonl.gz", "rt") as stream:
        for line in stream:
            row = json.loads(line)
            if row["id"] == ROW_ID:
                return row
    raise AssertionError("retained row absent")


def main():
    row = load_row()
    recipe = {"tables": True, "total_critical": True, "full_root": False}
    chunks = formula_chunks(row, recipe)
    data = b"".join(chunks)
    parent_hash = hashlib.sha256(data).hexdigest()
    header, _, rest = data.partition(b"\n")
    assert header.startswith(b"p cnf "), header
    nvars, nclauses = map(int, header.split()[2:])
    with open(HERE / "parent.cnf", "wb") as out:
        out.write(data)
    cube_bytes = data.replace(header + b"\n", b"p cnf %d %d\n" % (nvars, nclauses + 2), 1) \
        + b"-1413 0\n1014 0\n"
    with open(HERE / "parent_cube.cnf", "wb") as out:
        out.write(cube_bytes)
    cube_hash = hashlib.sha256(cube_bytes).hexdigest()
    fields = dict(row["family"])
    for field in ("profile", "root_kinds"):
        fields[field] = tuple(fields[field])
    family = Family(**fields)
    fixed = units(family, row["placement"])
    receipt = {
        "row": ROW_ID,
        "profile": family.profile,
        "charge": row["charge"],
        "recipe": recipe,
        "declared_recipe": list(RECIPE),
        "header": header.decode(),
        "vars": nvars,
        "clauses": nclauses,
        "parent_sha256": parent_hash,
        "parent_sha256_expected": EXPECT_PARENT,
        "parent_match": parent_hash == EXPECT_PARENT,
        "parent_cube_sha256": cube_hash,
        "parent_cube_sha256_expected": EXPECT_CUBE,
        "parent_cube_match": cube_hash == EXPECT_CUBE,
        "parent_bytes": len(data),
        "cube": CUBE,
        "fixed_units": len(fixed),
        "positive_units": sum(1 for c in fixed if c[0] > 0),
        "negative_units": sum(1 for c in fixed if c[0] < 0),
        "suffix_clauses_excluding_units": nclauses - sum(1 for _ in rest.split(b"\n") if _.strip()),
    }
    (HERE / "regen.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: receipt[k] for k in
                      ("header", "parent_sha256", "parent_match",
                       "parent_cube_sha256", "parent_cube_match", "parent_bytes")},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
