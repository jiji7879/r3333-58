#!/usr/bin/env python3
"""Regenerate the six outside-27 projection keys and their physical directions.

This is a literal transcription of local_spec in the supplied wall_map_sweep.py,
kept separate so the benchmark report need not rely on row-prefix prose.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any
from zipfile import ZipFile

CATALOGUE = "K58_wall_copy_maps/template-results/wall_copy_inputs.jsonl.gz"
RECEIPT_PREFIX = "K58_wall_copy_maps/data/wall-copy/outside-27/"


def edge_data(n: int):
    pairs = list(combinations(range(n), 2))
    return pairs, {pair: 1 + 4 * i for i, pair in enumerate(pairs)}


def projection_key(row: dict[str, Any], count: int = 27) -> str:
    U, T = row["u"], row["t"]
    both = U + T
    outside = set(range(58)) - set(both)
    pairs, atoms = edge_data(58)
    coordinates = {v: i for i, v in enumerate(both)}
    hue = {c: i for i, c in enumerate(row["palette"])}
    signs = defaultdict(list)
    for lit in row["pins"]:
        z = abs(lit) - 1
        a, b = pairs[z // 4]
        for x, v in ((a, b), (b, a)):
            if x in outside and v in coordinates:
                color = hue[z % 4]
                signs[x].append((coordinates[v], color if lit > 0 else -color - 1))
    select = sorted(outside, key=lambda x: (-len(signs[x]), sorted(signs[x]), x))[:count]
    vertices = both + select
    ix = {v: i for i, v in enumerate(vertices)}
    n = len(vertices)
    _, var = edge_data(n)
    units = []
    for lit in row["pins"]:
        z = abs(lit) - 1
        a, b = pairs[z // 4]
        if a in ix and b in ix:
            x = var[tuple(sorted((ix[a], ix[b])))] + hue[z % 4]
            units.append(x if lit > 0 else -x)
    spec = dict(n=n, contact=row["q"], pins=sorted(set(units)))
    encoded = json.dumps(spec, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def catalogue_bindings(zf: ZipFile) -> dict[str, list[dict[str, str]]]:
    keys = {
        json.loads(zf.read(n))["key"]
        for n in zf.namelist()
        if n.startswith(RECEIPT_PREFIX) and n.endswith("/receipt.json")
    }
    found = defaultdict(list)
    with gzip.open(zf.open(CATALOGUE), "rt") as stream:
        for line in stream:
            row = json.loads(line)
            key = projection_key(row)
            if key in keys:
                found[key].append({"row_id": row["row_id"], "direction": row["direction"]})
    if set(found) != keys:
        raise ValueError(f"unbound projection keys: {sorted(keys - set(found))}")
    return dict(found)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip", type=Path)
    args = parser.parse_args()
    with ZipFile(args.zip) as zf:
        print(json.dumps(catalogue_bindings(zf), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
