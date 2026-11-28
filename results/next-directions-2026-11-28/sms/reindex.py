#!/usr/bin/env python3
"""Record and verify the whole-formula bijection used for the SMS-shaped numbering.

Stock SMS requires the graph's edge variables to be the first C(n,2) variables in
row-wise upper-triangle order.  This script rewrites the *entire* exact
parent+cube by

    old physical variable 4r + colour + 1  ->  new r + 1                (colour 0)
                                            ->  new 1654 + 3r + colour  (colours 1..3)
    old auxiliary     6613 .. 19533        ->  unchanged

and then verifies that mapping every literal back recovers the original bytes
exactly.  No clause is added, removed or weakened; the clause file is pushed
through the same bijection.
"""
import hashlib
import json
from pathlib import Path

import sms_lib as L

HERE = Path(__file__).resolve().parent


def convert(text, mapper):
    out = []
    for line in text.splitlines():
        if not line or line.startswith("c"):
            out.append(line)
            continue
        parts = line.split()
        if parts[0] == "p":
            out.append(line)
            continue
        assert parts[-1] == "0", line
        literals = []
        for token in parts[:-1]:
            value = int(token)
            image = mapper(abs(value))
            literals.append(str(image if value > 0 else -image))
        out.append(" ".join(literals + ["0"]))
    return "\n".join(out) + "\n"


def main():
    assert L.check_bijection()
    original = (HERE / "parent_cube.cnf").read_text()
    reindexed = convert(original, L.reindex)
    (HERE / "parent_cube.reindexed.cnf").write_text(reindexed)
    if convert(reindexed, L.unindex) != original:
        raise SystemExit("ROUND TRIP FAILED: the bijection is not invertible on the formula")
    clauses = [tuple(int(x) for x in line.split()[:-1])
               for line in (HERE / "clauses.txt").read_text().splitlines() if line.strip()]
    images = []
    for clause in clauses:
        image = tuple(L.reindex(abs(x)) * (1 if x > 0 else -1) for x in clause)
        assert tuple(L.unindex(abs(x)) * (1 if x > 0 else -1) for x in image) == clause
        assert all(1 <= abs(x) <= L.NEDGE for x in image), image
        images.append(image)
    with open(HERE / "clauses.reindexed.txt", "w") as out:
        for image in images:
            out.write(" ".join(map(str, image)) + " 0\n")
    receipt = {
        "bijection": {
            "colour0": "old 4r+1 -> new r+1 for r = 0..1652",
            "other_colours": "old 4r+1+c -> new 1654+3r+c for c = 1..3",
            "aux": "6613..19533 unchanged",
            "checked_bijection_on_1..19533": True,
        },
        "parent_cube": {"sha256": hashlib.sha256(original.encode()).hexdigest(),
                        "bytes": len(original)},
        "parent_cube_reindexed": {
            "sha256": hashlib.sha256(reindexed.encode()).hexdigest(),
            "bytes": len(reindexed)},
        "round_trip_byte_identical": True,
        "clauses": len(images),
        "clause_images_in_first_1653_variables": True,
        "clauses_reindexed_sha256": hashlib.sha256(
            (HERE / "clauses.reindexed.txt").read_bytes()).hexdigest(),
    }
    (HERE / "reindex_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps(receipt, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
