"""Stage 1: regenerate the parent, emit the KMT parent, and check the exact map.

Writes only inside this member directory (+ .scratch/m7 for the CNFs).
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kmt_wall as W  # noqa: E402
import dense as production_dense  # noqa: E402
import problem as production_problem  # noqa: E402
from gluing import units  # noqa: E402


def parse(path):
    header = None
    clauses = []
    for line in path.read_text().splitlines():
        if not line or line[0] == "c":
            continue
        if line[0] == "p":
            assert header is None
            parts = line.split()
            header = (int(parts[2]), int(parts[3]))
            continue
        values = list(map(int, line.split()))
        assert values and values[-1] == 0
        clauses.append(values[:-1])
    assert header[1] == len(clauses)
    assert max(abs(x) for clause in clauses for x in clause) == header[0]
    return header, clauses


def inverse_map(stock_blocks, kmt_blocks):
    mapping = {value: value for value in range(1, W.PHYSICAL_MAX + 1)}
    for old, new in zip((b for b in stock_blocks if b["kind"] != "sender"),
                        (b for b in kmt_blocks if b["kind"] != "sender")):
        shift = new["aux_base"] - old["aux_base"]
        for value in range(new["aux_base"], new["aux_top"] + 1):
            mapping[value] = value - shift
    for old, new in zip((b for b in stock_blocks if b["kind"] == "sender"),
                        (b for b in kmt_blocks if b["kind"] == "sender")):
        mapping[new["guard"]] = old["guard"]
    return mapping


def block_spans(blocks, fixed_count):
    """(start, length) of every emitted block inside the suffix clause list."""
    spans, cursor = [], fixed_count
    for block in blocks:
        spans.append((block["kind"], block["ordinal"], cursor, len(block["clauses"])))
        cursor += len(block["clauses"])
    return spans, cursor


def main():
    item = W.row()
    family = W.family_of(item)
    stock_bytes, fixed, stock_extra, stock_blocks, stock_stats = W.parent_bytes(family, item, "stock")
    kmt_bytes, kmt_fixed, kmt_extra, kmt_blocks, kmt_stats = W.parent_bytes(family, item, "kmt")

    stock_fixed = fixed
    stock_fixed_ok = stock_fixed == kmt_fixed
    canonical = production_problem.row_formula(item, "first")
    canonical_ok = canonical == stock_bytes
    production = production_dense.marked_threshold(family, units(family, item["placement"]),
                                                   item["charge"], tables=True,
                                                   total_critical=True, full_root=False)
    faithful = production == stock_extra

    scratch = W.REPO / ".scratch/m7"
    scratch.mkdir(parents=True, exist_ok=True)
    (scratch / "stock.cnf").write_bytes(stock_bytes)
    (scratch / "kmt.cnf").write_bytes(kmt_bytes)
    (scratch / "stock-cube.cnf").write_bytes(W.with_cube(stock_bytes))
    (scratch / "kmt-cube.cnf").write_bytes(W.with_cube(kmt_bytes))
    for name in ("stock", "kmt", "stock-cube", "kmt-cube"):
        (scratch / f"{name}.sha256").write_text(W.sha((scratch / f"{name}.cnf").read_bytes()) + "\n")

    (sv, sc), stock_clauses = parse(scratch / "stock.cnf")
    (kv, kc), kmt_clauses = parse(scratch / "kmt.cnf")
    (scv, scc), stock_cube = parse(scratch / "stock-cube.cnf")
    (kcv, kcc), kmt_cube = parse(scratch / "kmt-cube.cnf")

    compare = W.comparisons(stock_blocks, kmt_blocks)
    alloc = W.allocation_map(stock_blocks, kmt_blocks)
    mapping = inverse_map(stock_blocks, kmt_blocks)

    # Positional clause comparison over the parsed files, block by block.
    fixed_count = len(kmt_fixed)
    assert stock_fixed == kmt_fixed and len(stock_fixed) == fixed_count
    host_count = len(kmt_clauses) - len(kmt_fixed) - len(kmt_extra)
    assert host_count == len(stock_clauses) - len(stock_fixed) - len(stock_extra) == 134995
    spans, cursor = block_spans(kmt_blocks, host_count + fixed_count)
    assert cursor == len(kmt_clauses), (cursor, len(kmt_clauses))
    assert stock_clauses[:host_count] == kmt_clauses[:host_count]
    assert (stock_clauses[host_count:host_count + fixed_count]
            == kmt_clauses[host_count:host_count + fixed_count] == stock_fixed)
    assert stock_clauses[host_count + fixed_count:] == stock_extra
    assert kmt_clauses[host_count + fixed_count:] == kmt_extra
    mismatches = []
    for kind, ordinal, start, length in spans:
        if kind == "sender":
            continue
        stock_block = stock_extra[stock_index(stock_blocks, kind, ordinal):][:length]
        kmt_block = kmt_clauses[start:start + length]
        mapped = []
        for clause in kmt_block:
            out = []
            for literal in clause:
                old = mapping.get(abs(literal))
                assert old is not None, literal
                out.append(old if literal > 0 else -old)
            mapped.append(out)
        if mapped != stock_block:
            mismatches.append(dict(kind=kind, ordinal=ordinal, length=length))

    surfaces = dict(
        schema=1,
        row=W.ROW_PREFIX,
        row_id="06861a3df60c08e409dd61965819af321f109e9b82bfd3bc5d05b2645362ec06",
        stock=dict(sha256=W.sha(stock_bytes), variables=sv, clauses=sc,
                   bytes=len(stock_bytes), matches_retained=W.sha(stock_bytes) == W.PARENT_SHA,
                   production_copy_faithful=faithful,
                   production_row_formula_match=canonical_ok),
        kmt=dict(sha256=W.sha(kmt_bytes), variables=kv, clauses=kc, bytes=len(kmt_bytes),
                 matches_prediction=(kv, kc) == (W.KMT_VARS, W.KMT_CLAUSES),
                 variables_delta=kv - sv, clauses_delta=kc - sc),
        cube=dict(literals=list(W.CUBE),
                  stock_cube=dict(sha256=W.sha((scratch / "stock-cube.cnf").read_bytes()),
                                  variables=scv, clauses=scc),
                  kmt_cube=dict(sha256=W.sha((scratch / "kmt-cube.cnf").read_bytes()),
                                variables=kcv, clauses=kcc),
                  physical=(max(map(abs, W.CUBE)) <= W.PHYSICAL_MAX),
                  appended_as_units=True),
        fixed_units_identical=stock_fixed_ok,
        fixed_units=len(stock_fixed),
        physical_literals=W.PHYSICAL_MAX,
        logical_comparison=compare,
        positional_clause_mismatches=mismatches,
        allocation=alloc,
        sender_inventory=[dict(ordinal=b["ordinal"], color=b["color"], vertex=b["vertex"],
                               guard=b["guard"], n=len(b["candidates"]), k=b["needed"],
                               aux=len(range(b["aux_base"], b["aux_top"] + 1)),
                               clauses=len(b["clauses"])) for b in kmt_blocks if b["kind"] == "sender"],
        stock_stats=stock_stats,
        kmt_stats=kmt_stats,
        support_events=sum(1 for b in kmt_blocks if b["kind"] == "support"),
        final_counters=[dict(label=b["label"], n=len(b["limits"]), k=b["bound"],
                             aux=len(range(b["aux_base"], b["aux_top"] + 1)),
                             clauses=len(b["clauses"])) for b in kmt_blocks if b["kind"] == "final"],
    )
    print(json.dumps(surfaces, indent=2, sort_keys=True))
    (HERE / "stage1.json").write_text(json.dumps(surfaces, indent=2, sort_keys=True) + "\n")
    assert (surfaces["stock"]["matches_retained"]
            and surfaces["stock"]["production_copy_faithful"]
            and surfaces["stock"]["production_row_formula_match"])
    assert surfaces["kmt"]["matches_prediction"] and compare["ok"] and not mismatches


def stock_index(blocks, kind, ordinal):
    cursor = 0
    for block in blocks:
        if block["kind"] == kind and block["ordinal"] == ordinal:
            return cursor
        cursor += len(block["clauses"])
    raise KeyError((kind, ordinal))


if __name__ == "__main__":
    main()
