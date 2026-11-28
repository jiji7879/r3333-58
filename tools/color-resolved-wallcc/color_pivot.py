"""Certified K58 physical-color pivot augmentation for an exact frozen parent.

The added escape/color clauses are proved against the reconstructed original
parent plus functional comparator-counter definitions.  A later UNSAT proof of
an augmented formula therefore has explicitly aux-extended-parent scope; it is
not silently described as a DRAT proof against the unextended original.
"""
from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic
import gzip
import hashlib
import itertools
import json
import os
import subprocess

from pysat.solvers import Minisat22

from problem import ROOT, digest, file_hash, json_bytes, require, row_formula
from cover_evidence import identity
from gluing import host, named_template

CACHE = ROOT / "color_cache"
VARIANTS = ("original", "counter", "escape", "color")
CACHE_SHA256 = {
    "full-wall.json.gz": "a0a6e29a4389dd7e36aabc3d2e75a31487280d1abe2144ee732841c522aaba8f",
    "local-proofs.json.gz": "939d960307cc44f31301980435b5fcab843e0be35d4ea75d71217241e80e74c4",
}


def encode(clauses):
    return b"".join((" ".join(map(str, clause)) + " 0\n").encode()
                    for clause in clauses)


def header(raw):
    first = raw.split(b"\n", 1)[0].split()
    require(len(first) == 4 and first[:2] == [b"p", b"cnf"], "invalid generated DIMACS header")
    return int(first[2]), int(first[3])


def augment(raw, clauses, variables):
    """The frozen encoder emits a canonical first line and a final newline."""
    old_n, old_m = header(raw)
    require(variables >= old_n, "auxiliary variables do not sit above the parent maximum")
    return (f"p cnf {variables} {old_m + len(clauses)}\n".encode()
            + raw.split(b"\n", 1)[1] + encode(clauses))


def miter(raw, targets):
    """A selected flag falsifies its target; the positive flag clause is refuted."""
    nv, _ = header(raw)
    flags = [nv + i + 1 for i in range(len(targets))]
    selector = [flags] + [[-flag, -literal]
                          for flag, clause in zip(flags, targets) for literal in clause]
    return augment(raw, selector, nv + len(flags)), flags


def counter(inputs, top):
    """Ascending insertion network; output j means at least j+1 true inputs."""
    outputs, definitions = [], []
    for item in inputs:
        carry = item
        ordered = []
        for previous in outputs:
            hi, lo = top + 1, top + 2
            top += 2
            definitions.extend(([-previous, hi], [-carry, hi], [previous, carry, -hi],
                                [previous, -lo], [carry, -lo], [-previous, -carry, lo]))
            ordered.append(hi)
            carry = lo
        outputs = ordered + [carry]
    return definitions, outputs, top


def insert(prover, steps, clause, variables):
    """Discharge a two-way case split when the desired clause is not already RUP."""
    possible, forced = prover.propagate(assumptions=[-literal for literal in clause])
    if possible:
        assigned = {abs(literal) for literal in forced} | {abs(literal) for literal in clause}
        candidates = [variable for variable in variables if variable not in assigned]
        require(candidates, f"satisfiable local counterexample to {clause}")
        literal = candidates[0]
        insert(prover, steps, clause + [literal], variables)
        insert(prover, steps, clause + [-literal], variables)
        require(not prover.propagate(assumptions=[-literal for literal in clause])[0],
                "failed to discharge the local case split")
    steps.append(clause)
    prover.add_clause(clause)


@lru_cache(maxsize=1)
def cache_data():
    contents = {}
    for name, expected in CACHE_SHA256.items():
        raw = (CACHE / name).read_bytes()
        require(digest(raw) == expected, f"audited cache hash mismatch: {name}")
        contents[name] = json.loads(gzip.decompress(raw))
    catalog = contents["full-wall.json.gz"]
    proofs = contents["local-proofs.json.gz"]
    require(len(catalog["cases"]) == len(proofs) == 240, "unexpected audited cache size")
    require(len(catalog["bindings"]) == 11585 and catalog["summary"]["no_pivot"] == 36,
            "unexpected audited binding roster")
    return catalog, proofs


@lru_cache(maxsize=128)
def binding(row_id):
    catalog, proofs = cache_data()
    matches = [entry for entry in catalog["bindings"] if entry[0] == row_id]
    require(len(matches) == 1, "row is absent from the audited pivot cache")
    entry = matches[0]
    require(entry[1] is not None, "this frozen row has no archived marked-spoke pivot; use --pivot-color off")
    _, index, sender, offset, pivot_literal = entry
    return entry, catalog["cases"][index], proofs[index]


@lru_cache(maxsize=1)
def benchmark_data():
    path = CACHE / "benchmarks/bench.json"
    require(path.is_file(), "missing audited benchmark receipt")
    return json.loads(path.read_bytes())


@lru_cache(maxsize=128)
def benchmark_batch(row_id):
    for path in sorted((CACHE / "benchmarks").glob("*.batch.json")):
        record = json.loads(path.read_bytes())
        if record["row"] == row_id:
            return record
    return None


def local_formula(case):
    """Reconstruct the audited local physical formula and color targets."""
    n, escape_color, marked = case["order"], case["arm_color"], case["marked_color"]
    palette = sorted(set(range(4)) - {marked})
    vertices = [v for v in range(n) if v not in case["support"]]
    matrix = named_template(n, case["kind"], escape_color)
    require(all(matrix[u][v] != marked for u, v in itertools.combinations(case["support"], 2)),
            "marked support has an invalid internal color")
    atom = lambda site, color: 4 * site + color + 1
    physical = []
    for i in range(len(vertices)):
        choices = [atom(i, color) for color in palette]
        physical.append(choices)
        physical.extend([[-u, -v] for u, v in itertools.combinations(choices, 2)])
    for i, j in itertools.combinations(range(len(vertices)), 2):
        color = matrix[vertices[i]][vertices[j]]
        if color in palette:
            physical.append([-atom(i, color), -atom(j, color)])
    top = 4 * len(vertices)
    definitions, outputs, last = counter([atom(i, escape_color) for i in range(len(vertices))], top)
    targets = []
    pivot_index = vertices.index(case["pivot"])
    for branch in case["branches"]:
        color, minimum = branch["color"], branch["minimum"]
        guard = atom(pivot_index, color)
        if minimum:
            require(minimum <= len(outputs), "branch minimum exceeds the free-spoke count")
            targets.append([-guard, outputs[minimum - 1]])
        for i, vertex in enumerate(vertices):
            if vertex != case["pivot"] and str(vertex) in branch["forced"]:
                require(minimum < len(outputs), "an above-minimum threshold is unavailable")
                targets.append([-guard, outputs[minimum], atom(i, branch["forced"][str(vertex)])])
    return vertices, palette, matrix, atom, physical, definitions, outputs, last, targets


def local_words(case, vertices, palette, matrix):
    """Enumerate every feasible local physical word, independently of its proof."""
    words = []
    word = []

    def visit(i):
        if i == len(vertices):
            words.append(tuple(word))
            return
        vertex = vertices[i]
        for color in palette:
            if any(color == word[j] == matrix[vertices[j]][vertex] for j in range(i)):
                continue
            word.append(color)
            visit(i + 1)
            word.pop()

    visit(0)
    require(words, "local configuration has no feasible physical word")
    return words


def checked_local_semantics(case, vertices, palette, matrix, atom, outputs, targets):
    """Check cached branch data and compute inclusion-minimal positive transversals."""
    words = local_words(case, vertices, palette, matrix)
    escape_color = case["arm_color"]
    pivot_index = vertices.index(case["pivot"])
    escape_masks = set()
    for branch in case["branches"]:
        colored = [word for word in words if word[pivot_index] == branch["color"]]
        require(colored, "cached pivot color has no realizing local word")
        minimum = min(sum(color == escape_color for color in word) for word in colored)
        allowed = [word for word in colored
                   if sum(color == escape_color for color in word) == minimum]
        forced = {}
        for i, vertex in enumerate(vertices):
            colors = {word[i] for word in allowed}
            if len(colors) == 1:
                forced[str(vertex)] = colors.pop()
        require((minimum, len(allowed), forced) ==
                (branch["minimum"], branch["words"], branch["forced"]),
                "cached branch data differs from exhaustive local enumeration")
        escape_masks.update(sum((word[i] == escape_color) << i for i in range(len(vertices)))
                            for word in words)
    full = (1 << len(vertices)) - 1
    bad = {mask for mask in range(full + 1)
           if not any(not mask & word_mask for word_mask in escape_masks)}
    minimal = sorted(mask for mask in bad
                     if all(mask ^ (1 << i) not in bad
                            for i in range(len(vertices)) if mask >> i & 1))
    baseline = [tuple(atom(i, escape_color) for i in range(len(vertices)) if mask >> i & 1)
                for mask in minimal]
    # Every cached target is explicitly constructed from the checked branch object.
    reconstructed = []
    for branch in case["branches"]:
        guard = atom(pivot_index, branch["color"])
        minimum = branch["minimum"]
        if minimum:
            reconstructed.append([-guard, outputs[minimum - 1]])
        for i, vertex in enumerate(vertices):
            if vertex != case["pivot"] and str(vertex) in branch["forced"]:
                reconstructed.append([-guard, outputs[minimum], atom(i, branch["forced"][str(vertex)])])
    require(reconstructed == targets, "reconstructed color targets differ from the cached proof targets")
    return [list(clause) for clause in baseline], len(words)


def physical_premises(raw):
    pairs = list(itertools.combinations(range(58), 2))
    pinned, denied = {}, set()
    for line in raw.splitlines()[1:]:
        fields = line.split()
        if len(fields) == 2 and 1 <= abs(int(fields[0])) <= 6612:
            literal = int(fields[0])
            a, b = pairs[(abs(literal) - 1) // 4]
            color = (abs(literal) - 1) % 4
            if literal > 0:
                pinned[a, b] = color
            else:
                denied.add((a, b, color))
    for (a, b), color in pinned.items():
        denied.update((a, b, other) for other in range(4) if color != other)
    for center in range(58):
        groups = defaultdict(list)
        for (a, b), color in pinned.items():
            if center == a:
                groups[color].append(b)
            if center == b:
                groups[color].append(a)
        for color, vertices in groups.items():
            for a, b in itertools.combinations(sorted(vertices), 2):
                denied.add((a, b, color))
    return pinned, denied


def strict_check(checker, query, proof, seconds):
    checker = Path(checker).resolve()
    require(checker.is_file() and os.access(checker, os.X_OK), f"missing checker {checker}")
    started = monotonic()
    with TemporaryDirectory(prefix="k58-color-miter-") as name:
        q, p = Path(name) / "query.cnf", Path(name) / "proof.drat"
        q.write_bytes(query)
        p.write_bytes(proof)
        try:
            run = subprocess.run([checker, q, p, "-I", "-f", "-W", "-U"],
                                 capture_output=True, timeout=seconds)
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"color miter checker exceeded {seconds} seconds")
    log = (run.stdout + run.stderr).decode(errors="replace")
    lines = log.splitlines()
    passed = ("s VERIFIED" in lines and run.returncode in (0, 1)
              and not any("WARNING" in line for line in lines))
    if run.returncode == 1 and "c trivial UNSAT" not in lines:
        passed = False
    require(passed, f"native color derivation failed: {log[-1600:]}")
    return {"status": "PASS_RUP_DERIVATION", "checker": str(checker),
            "checker_sha256": file_hash(checker),
            "arguments": ["-I", "-f", "-W", "-U"],
            "exit_code": run.returncode, "elapsed_s": round(monotonic() - started, 6),
            "log": log[-4000:]}


def variant_info(raw):
    nv, nc = header(raw)
    body = raw.split(b"\n", 1)[1]
    return {"sha256": digest(raw), "bytes": len(raw), "variables": nv, "clauses": nc,
            "header": raw.split(b"\n", 1)[0].decode(), "body_sha256": digest(body),
            "body_bytes": len(body)}


def build(row, tier="first", checker=None, check_seconds=120):
    """Build all four matched formulas from one exact parent and counter allocation."""
    require(tier == "first", "color-pivot augmentation is audited only for --tier first")
    require(identity(row) == row["id"], "frozen row identity mismatch")
    entry, case, cached_proof = binding(row["id"])
    _, template, sender, offset, pivot_literal = entry
    raw = row_formula(row, tier)
    parent_n, parent_m = header(raw)
    vertices, palette, matrix, atom, physical, definitions, outputs, last, color_local = local_formula(case)
    escape_local, local_word_count = checked_local_semantics(
        case, vertices, palette, matrix, atom, outputs, color_local)
    top = 4 * len(vertices)
    edge, _ = host(58)
    pinned, denied = physical_premises(raw)
    arm_color, marked = case["arm_color"], case["marked_color"]
    pivot_vertex = offset + case["pivot"]
    require(pinned[0, sender] == marked and pivot_literal == edge(sender, pivot_vertex, arm_color),
            "cached marked sender or pivot does not match the exact parent")
    group = [offset + v for v in range(case["order"])]
    require(all(pinned[0, vertex] == arm_color for vertex in group), "wrong parent arm color")
    require(all(pinned[u, v] == matrix[u - offset][v - offset]
                for u, v in itertools.combinations(group, 2)), "wrong parent template geometry")
    for vertex in group:
        domain = {color for color in range(4)
                  if (*sorted((sender, vertex)), color) not in denied}
        expected = set(palette) if vertex - offset in vertices else {marked}
        require(domain == expected, f"physical domain mismatch at vertex {vertex}")

    def transport(literal):
        variable = abs(literal)
        if variable > top:
            mapped = parent_n + variable - top
        else:
            site, color = divmod(variable - 1, 4)
            mapped = edge(sender, offset + vertices[site], color)
        return mapped if literal > 0 else -mapped

    mapped = lambda clauses: [[transport(literal) for literal in clause] for clause in clauses]
    mapped_definitions = mapped(definitions)
    # The audited exporter sorts positive clauses after transport to parent IDs.
    mapped_escape = sorted(mapped(escape_local))
    mapped_color = mapped(color_local)
    extended_n = parent_n + last - top
    require(extended_n > parent_n and min(abs(literal) for clause in mapped_definitions
              for literal in clause if abs(literal) > 6612) > parent_n,
            "fresh counter IDs do not sit above this parent's declared maximum")

    # First verify the exact cached color-only local query and proof identities.
    local_base = (f"p cnf {last} {len(physical) + len(definitions)}\n".encode()
                  + encode(physical + definitions))
    local_color_query, local_color_flags = miter(local_base, color_local)
    local_color_trace = encode(cached_proof["steps"] + [[-flag] for flag in local_color_flags] + [[]])
    require(digest(local_color_query) == cached_proof["local_query_sha256"]
            and digest(local_color_trace) == cached_proof["local_proof_sha256"],
            "cached local color proof/query hash mismatch")

    # Reuse that proof after a freshly generated proof of the positive escape bank.
    variables = [atom(i, color) for i in range(len(vertices)) for color in palette]
    escape_steps = []
    with Minisat22(bootstrap_with=physical + definitions) as prover:
        for clause in escape_local:
            insert(prover, escape_steps, list(clause), variables)
    combined_local = escape_local + color_local
    query_local, flags_local = miter(local_base, combined_local)
    del query_local  # Its mapped full-parent counterpart is the certified object.
    local_steps = escape_steps + cached_proof["steps"]
    trace_local = local_steps + [[-flag] for flag in flags_local] + [[]]
    extended = augment(raw, mapped_definitions, extended_n)
    query, actual_flags = miter(extended, mapped_escape + mapped_color)
    require(actual_flags == [transport(literal) for literal in flags_local],
            "full-parent miter flag transport mismatch")
    proof = encode(mapped(physical + trace_local))

    formulas = {
        "original": raw,
        "counter": extended,
        "escape": augment(extended, mapped_escape, extended_n),
        "color": augment(extended, mapped_escape + mapped_color, extended_n),
    }
    infos = {name: variant_info(data) for name, data in formulas.items()}
    for name in VARIANTS[1:]:
        infos[name]["clauses_added"] = infos[name]["clauses"] - parent_m
        infos[name]["auxiliary_variables"] = extended_n - parent_n
        infos[name]["auxiliary_interval"] = [parent_n + 1, extended_n]
    infos["original"]["clauses_added"] = 0
    infos["original"]["auxiliary_variables"] = 0

    batch = benchmark_batch(row["id"])
    benchmark_match = None
    if batch is not None:
        require(batch["parent"] == digest(raw), "audited benchmark parent hash differs")
        require(batch["definitions"] == mapped_definitions, "audited benchmark counter definitions differ")
        require(batch["B"] == mapped_escape, "audited benchmark positive escape clauses differ")
        require(batch["C_extra"] == mapped_color, "audited benchmark color clauses differ")
        expected = defaultdict(set)
        for run in benchmark_data()["runs"]:
            if run["row"] == row["id"]:
                expected[run["variant"]].add(run["query"])
        for name in VARIANTS:
            require(expected[name] == {infos[name]["sha256"]},
                    f"generated {name} formula differs from the audited benchmark hash")
        benchmark_match = {name: sorted(expected[name]) for name in VARIANTS}

    core = {
        "schema": 1, "row": row["id"], "tier": tier,
        "cache": dict(CACHE_SHA256), "template": template,
        "binding": {"sender": sender, "arm_offset": offset, "pivot_vertex": pivot_vertex,
                    "pivot_literal": pivot_literal, "arm_color": arm_color,
                    "marked_color": marked, "free_vertices": [offset + v for v in vertices],
                    "local_feasible_words": local_word_count},
        "original_parent_sha256": digest(raw),
        "counter": {"definitions": mapped_definitions, "def_sha256": digest(encode(mapped_definitions)),
                    "threshold_outputs": [transport(item) for item in outputs],
                    "escape_inputs": [transport(atom(i, arm_color)) for i in range(len(vertices))],
                    "first_fresh_variable": parent_n + 1, "last_fresh_variable": extended_n},
        "escape_clauses": mapped_escape, "color_clauses": mapped_color,
        "branches": case["branches"], "formulas": infos,
        "derivation_artifacts": {"query_sha256": digest(query), "query_bytes": len(query),
                                 "proof_sha256": digest(proof), "proof_bytes": len(proof),
                                 "scope": "original parent + functional counter definitions |- escape + color clauses"},
        "model_extension": "Each physical assignment has exactly one ascending OR/AND-counter extension; native RUP derives every added rule from that extension. Above-minimum branches and all physical pivot colors remain present.",
        "benchmark_exact_match": benchmark_match,
    }
    check = strict_check(checker, query, proof, check_seconds) if checker is not None else {
        "status": "NOT_RUN", "reason": "reconstruction only"}
    return {"core": core, "formulas": formulas, "query": query, "proof": proof, "check": check}


def core_digest(artifacts):
    return digest(json_bytes(artifacts["core"]))


def write_if_absent(path, data):
    if path.exists():
        require(path.read_bytes() == data, f"existing artifact differs: {path}")
    else:
        path.write_bytes(data)


def publish(out, artifacts, variants=()):
    """Retain deterministic provenance and compressed, independently replayable evidence."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    write_if_absent(out / "color-receipt.json", json_bytes(artifacts["core"]))
    check_path = out / "color-check.json"
    if check_path.exists():
        previous = json.loads(check_path.read_bytes())
        require(previous.get("status") == artifacts["check"]["status"] == "PASS_RUP_DERIVATION",
                "existing native color check differs or was not run")
    else:
        check_path.write_bytes(json_bytes(artifacts["check"]))
    for name, data in (("color-query.cnf", artifacts["query"]), ("color-proof.drat", artifacts["proof"])):
        path = out / (name + ".gz")
        compressed = gzip.compress(data, mtime=0)
        if path.exists():
            require(gzip.decompress(path.read_bytes()) == data, f"existing artifact differs: {path}")
        else:
            path.write_bytes(compressed)
    for name in variants:
        write_if_absent(out / f"{name}.cnf", artifacts["formulas"][name])
    return {"status": artifacts["check"]["status"], "row": artifacts["core"]["row"],
            "receipt_sha256": core_digest(artifacts),
            "original_parent_sha256": artifacts["core"]["original_parent_sha256"],
            "formulas": artifacts["core"]["formulas"]}


def verify_saved(out, checker, seconds=120):
    """Rebuild, hash-bind and natively replay a run's saved augmentation evidence."""
    out = Path(out)
    plan = json.loads((out / "plan.json").read_bytes())
    origin = plan["origin"]
    require(origin["kind"] in ("wall-color", "wall-color-square"), "run has no color-pivot extension")
    from problem import lookup
    row = lookup(origin["id"])
    artifacts = build(row, origin["tier"])
    require(core_digest(artifacts) == origin["color_receipt_sha256"], "color receipt binding mismatch")
    write_if_absent(out / "color-receipt.json", json_bytes(artifacts["core"]))
    query = gzip.decompress((out / "color-query.cnf.gz").read_bytes())
    proof = gzip.decompress((out / "color-proof.drat.gz").read_bytes())
    expected = artifacts["core"]["derivation_artifacts"]
    require(digest(query) == expected["query_sha256"] and digest(proof) == expected["proof_sha256"],
            "saved color query/proof differs from its bound hashes")
    require(query == artifacts["query"] and proof == artifacts["proof"],
            "saved color evidence differs from deterministic reconstruction")
    check = strict_check(checker, query, proof, seconds)
    check.update({"row": row["id"], "original_parent_sha256": digest(artifacts["formulas"]["original"]),
                  "selected_variant": origin["variant"],
                  "selected_parent_sha256": artifacts["core"]["formulas"][origin["variant"]]["sha256"]})
    return check
