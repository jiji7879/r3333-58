"""Bind each search to either an exact frozen row or a supplied DIMACS formula."""
import gzip
import hashlib
import json
from collections import Counter
from functools import lru_cache
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "frozen"))
from cover_evidence import formula_chunks, identity
from gluing import Family, host, units

PHYSICAL = 4 * (58 * 57 // 2)
ROSTER_SHA = "d5641e1ba875bc4ec5fbe156d48585f610e877f5232de7181eb464d4ad4fa2bc"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    with path.open("rb") as stream:
        h = hashlib.sha256()
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
        return h.hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


@lru_cache(maxsize=1)
def roster():
    with gzip.open(ROOT / "data/wall.jsonl.gz", "rb") as stream:
        data = stream.read()
    require(digest(data) == ROSTER_SHA, "wall roster hash mismatch")
    return {r["id"]: r for r in map(json.loads, data.splitlines())}


def lookup(prefix):
    prefix = prefix.lower()
    require(prefix and all(ch in "0123456789abcdef" for ch in prefix), "invalid row ID")
    matches = [r for key, r in roster().items() if key.startswith(prefix)]
    require(len(matches) == 1, f"{len(matches)} wall rows match {prefix!r}; use a unique prefix")
    row = matches[0]
    require(identity(row) == row["id"], "frozen row identity mismatch")
    return row


def row_formula(row, tier):
    require(tier in ("first", "retry"), "unknown frozen recipe")
    return b"".join(formula_chunks(row, dict(tables=True, total_critical=True,
                                             full_root=tier == "retry")))


def family_and_pins(row):
    fields = dict(row["family"])
    for name in ("profile", "root_kinds"):
        fields[name] = tuple(fields[name])
    family = Family(**fields)
    return family, [x for x, in units(family, row["placement"])]


def encode_clauses(clauses):
    return b"".join((" ".join(map(str, c)) + (" " if c else "") + "0\n").encode()
                    for c in clauses)


def read_dimacs(data):
    """Handle comments, clauses spanning lines, empty clauses and unused variables."""
    header = None
    clauses, pending = [], []
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith(b"c"):
            continue
        if line.startswith(b"p"):
            parts = line.split()
            require(header is None and len(parts) == 4 and parts[:2] == [b"p", b"cnf"],
                    "invalid DIMACS header")
            header = tuple(map(int, parts[2:]))
            require(min(header) >= 0, "negative DIMACS counts")
            continue
        require(header is not None, "clause before DIMACS header")
        values = list(map(int, line.split()))
        if not pending and values and values[-1] == 0 and 0 not in values[:-1]:
            clauses.append(values[:-1])
        else:
            for value in values:
                if value:
                    pending.append(value)
                else:
                    clauses.append(pending)
                    pending = []
    require(header is not None and not pending and len(clauses) == header[1],
            "DIMACS clause count or termination mismatch")
    require(max((max(map(abs, c), default=0) for c in clauses), default=0) <= header[0],
            "DIMACS literal exceeds declared variable count")
    return header[0], clauses


def external_formula(path):
    data = gzip.decompress(path.read_bytes()) if path.suffix == ".gz" else path.read_bytes()
    nv, clauses = read_dimacs(data)
    canonical = f"p cnf {nv} {len(clauses)}\n".encode() + encode_clauses(clauses)
    return canonical, {"kind": "dimacs", "source_sha256": digest(data)}


def check_model(clauses, cube, model, nv):
    require(isinstance(model, list) and all(type(x) is int and 0 < abs(x) <= nv for x in model),
            "model has an invalid literal")
    assigned = set(model)
    require(not any(-x in assigned for x in assigned), "contradictory model")
    require(all(x in assigned for x in cube), "model violates cube")
    for i, clause in enumerate(clauses, 1):
        require(any(x in assigned for x in clause), f"model fails parent clause {i}")


def extend_dimacs(source, target, extras):
    """All stored parents have a canonical first-line header and a final newline."""
    import shutil
    with source.open("rb") as inp, target.open("wb") as out:
        p, cnf, nv, nc = inp.readline().split()
        require((p, cnf) == (b"p", b"cnf"), "invalid stored CNF header")
        out.write(f"p cnf {int(nv)} {int(nc) + len(extras)}\n".encode())
        shutil.copyfileobj(inp, out, 1 << 20)
        out.write(encode_clauses(extras))


def ranked_variables(clauses, limit):
    occurrence = Counter(abs(x) for c in clauses for x in c if abs(x) <= limit)
    return sorted(occurrence, key=lambda x: (-occurrence[x], x))
