"""Export exact SAT inputs and package and verify the evidence for the K58 cover."""
import argparse
from collections import Counter
import fcntl
import gzip
from hashlib import sha256
from importlib.metadata import version
from itertools import zip_longest
import json
from pathlib import Path
import shutil
import subprocess
from tempfile import NamedTemporaryFile, TemporaryDirectory
from time import monotonic

from audit_campaign import body, lines
from dense import marked_threshold
from gluing import Family, profiles, units
from joint_plan import cases
from matched_anchor import digest

SCHEMA = 1
CASE_COUNT = 113179
RECIPE = ("tables", "total_critical", "full_root")
SOURCES = (
    "anchor_cuts.py", "audit_campaign.py", "charge_plan.py", "cover_evidence.py", "dense.py",
    "gluing.py", "joint_plan.py", "matched_anchor.py", "palette_quotient.py",
    "run_cover.py", "support_tables.py",
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identity(row):
    data = {key: row[key] for key in ("family", "placement", "charge")}
    return sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def json_bytes(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def atomic_json(path, value):
    with NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temp = Path(stream.name)
        try:
            stream.write(json_bytes(value))
            stream.close()
            temp.replace(path)
        finally:
            temp.unlink(missing_ok=True)


def records(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8") as stream:
        for line in stream:
            yield json.loads(line)


def lookup(ledger, identifier):
    for row in records(ledger):
        if row["id"] == identifier:
            require(identity(row) == identifier, f"Invalid identity for {identifier}")
            return row
    raise ValueError(f"Case not present in ledger: {identifier}")


def audit_cover(ledger):
    expected = (case for profile in profiles(58) for case in cases(profile))
    seen = set()
    for entry, row in zip_longest(expected, records(ledger)):
        require(entry is not None and row is not None, "Cover length mismatch")
        family, placement, branch, charge = entry
        geometry = dict(family=vars(family), placement=placement, charge=charge)
        identifier = identity(geometry)
        require(row["id"] == identifier == identity(row) and row["branch"] == branch,
                f"Cover mismatch at {identifier}")
        require(identifier not in seen, f"Duplicate case {identifier}")
        seen.add(identifier)
        yield row
    require(len(seen) == CASE_COUNT, "Unexpected K58 cover size")


def recipe_from(row):
    recipe = {name: row[name] for name in RECIPE}
    require(all(type(value) is bool for value in recipe.values()), "Invalid encoding flags")
    return recipe


def formula_chunks(row, recipe):
    fields = dict(row["family"])
    for field in ("profile", "root_kinds"):
        fields[field] = tuple(fields[field])
    family = Family(**fields)
    fixed = units(family, row["placement"])
    require(set(recipe) == set(RECIPE), "Unexpected encoding flags")
    suffix = fixed + marked_threshold(family, fixed, row["charge"], **recipe_from(recipe))
    base, count, top = body()
    maximum = max(top, max((abs(lit) for clause in suffix for lit in clause), default=0))
    return f"p cnf {maximum} {count + len(suffix)}\n".encode(), base, lines(suffix)


def formula_id(chunks):
    hash_value = sha256()
    for chunk in chunks:
        hash_value.update(chunk)
    return {"sha256": hash_value.hexdigest(), "bytes": sum(map(len, chunks))}


def write_formula(path, chunks):
    with path.open("xb") as stream:
        for chunk in chunks:
            stream.write(chunk)


def tool_identity(executable, name):
    path = Path(shutil.which(executable) or executable).resolve()
    result = subprocess.run([str(path), "--version"], capture_output=True, text=True, check=True)
    return dict(name=name, path=str(path), version=(result.stdout or result.stderr).strip(),
                sha256=digest(path))


def case_dir(root, identifier):
    return root / identifier[:2] / identifier


def artifact(root, path):
    return dict(path=path.relative_to(root).as_posix(), bytes=path.stat().st_size,
                sha256=digest(path))


def validate_artifact(root, entry):
    path = (root / entry["path"]).resolve()
    require(path.is_relative_to(root.resolve()), f"Artifact escapes {root}: {path}")
    require(path.is_file() and path.stat().st_size == entry["bytes"], f"Missing or truncated {path}")
    require(digest(path) == entry["sha256"], f"Hash mismatch: {path}")
    return path


def gzip_copy(source, target):
    with source.open("rb") as src, NamedTemporaryFile(dir=target.parent, delete=False) as dst:
        temporary = Path(dst.name)
        try:
            with gzip.GzipFile(fileobj=dst, mode="wb", filename="", mtime=0, compresslevel=5) as stream:
                shutil.copyfileobj(src, stream)
            dst.close()
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)


def verify_compressed_proof(path, expected):
    payload = sha256()
    size = 0
    with gzip.open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            payload.update(block)
            size += len(block)
    require(expected == {"sha256": payload.hexdigest(), "bytes": size},
            f"Decompressed DRAT mismatch: {path}")


def certificate_metadata(row, folder, formula, proof, attempt, checker_hash, check_log,
                         artifacts=(), metrics=None):
    """Commit point is verified.json. Call only after replay of the exact input."""
    recipe = recipe_from(attempt)
    input_identity = artifact(formula.parent, formula)
    input_identity.pop("path")
    require(input_identity == formula_id(formula_chunks(row, recipe)),
            f"Incorrect CNF for {row['id']}")
    if artifacts:
        require(attempt["formula_sha256"] == input_identity["sha256"],
                f"Kissat input changed for {row['id']}")
    compressed = folder / "certificate.drat.gz"
    drat = {"sha256": digest(proof), "bytes": proof.stat().st_size}
    gzip_copy(proof, compressed)
    verify_compressed_proof(compressed, drat)
    return dict(
        schema=SCHEMA, id=row["id"], branch=row["branch"], recipe=recipe,
        input=input_identity, certificate=artifact(folder, compressed),
        drat=drat,
        checker_sha256=checker_hash, checker_log=artifact(folder, check_log),
        primary=[artifact(folder, path) for path in artifacts],
        provenance="kissat" if artifacts else "imported-drat",
        metrics=metrics or {},
    )


def replay_certificate(folder, evidence, chunks, checker):
    with TemporaryDirectory(prefix="k58-replay-") as tmp:
        formula, proof = Path(tmp, "formula.cnf"), Path(tmp, "proof.drat")
        write_formula(formula, chunks)
        compressed = validate_artifact(folder, evidence["certificate"])
        with gzip.open(compressed, "rb") as src, proof.open("xb") as dst:
            shutil.copyfileobj(src, dst)
        require(proof.stat().st_size == evidence["drat"]["bytes"] and
                digest(proof) == evidence["drat"]["sha256"], "Decompressed DRAT mismatch")
        return replay(checker, formula, proof)


def replay(checker, formula, proof):
    run = subprocess.run([checker, str(formula), str(proof)], text=True,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    require(run.returncode == 0 and "s VERIFIED" in run.stdout.splitlines(),
            f"DRAT replay failed for {formula}: {run.stdout[-1500:]}")
    return run.stdout


def inspect_primary(folder, evidence, row):
    entries = evidence["primary"]
    if evidence["provenance"] == "imported-drat":
        require(not entries, "Imported proof has unexpected solver receipts")
        return
    require(evidence["provenance"] == "kissat" and len(entries) == 3, "Invalid Kissat evidence")
    receipt, solver_log, trim_log = [validate_artifact(folder, entry) for entry in entries]
    attempt = json.loads(receipt.read_text())
    require(identity(attempt) == row["id"] and attempt["branch"] == row["branch"] and
            recipe_from(attempt) == evidence["recipe"] and attempt["exit_code"] == 20 and
            attempt["status"] == "UNSAT", f"Invalid Kissat receipt: {receipt}")
    solver = attempt["solver"]
    command = attempt["command"]
    options = ["--quiet", f"--time={attempt['seconds']}", f"--conflicts={attempt['budget']}"]
    require(solver["name"] == "Kissat" and len(solver["sha256"]) == 64 and solver["version"] and
            command[:4] == [solver["path"], *options] and len(command) == 6 and
            Path(command[-2]).name == receipt.with_suffix(".cnf").name and
            Path(command[-1]).name == receipt.with_suffix(".drat").name and
            attempt["formula_sha256"] == evidence["input"]["sha256"] and
            attempt["formula_bytes"] == evidence["input"]["bytes"], f"Invalid command: {receipt}")
    require("s UNSATISFIABLE" in solver_log.read_text().splitlines(), f"Kissat log: {solver_log}")
    require("s VERIFIED" in trim_log.read_text().splitlines(), f"Trim log: {trim_log}")


def inspect_secondary(folder, evidence):
    path = folder / "cadical.json"
    if not path.exists():
        return None
    row = json.loads(path.read_text())
    require(row["case_id"] == evidence["id"] and row["input"] == evidence["input"] and
            row["solver"]["name"] == "CaDiCaL" and len(row["solver"]["sha256"]) == 64 and
            row["solver"]["version"] and row["command"] == [row["solver"]["path"], "formula.cnf"],
            f"CaDiCaL receipt does not match {path}")
    log = validate_artifact(folder, row["log"])
    if row["exit_code"] == 20:
        require("s UNSATISFIABLE" in log.read_text().splitlines(), f"CaDiCaL log: {log}")
    return row


def inspect_case(root, row, checker=None):
    folder = case_dir(root, row["id"])
    marker = folder / "verified.json"
    if not marker.exists():
        return None
    evidence = json.loads(marker.read_text())
    require(evidence.get("schema") == SCHEMA, f"Use import-legacy for {marker}")
    require(evidence["id"] == row["id"] and evidence["branch"] == row["branch"],
            f"Certificate associated to the wrong case: {marker}")
    chunks = formula_chunks(row, evidence["recipe"])
    require(formula_id(chunks) == evidence["input"], f"Regenerated CNF mismatch: {marker}")
    check_log = validate_artifact(folder, evidence["checker_log"])
    require("s VERIFIED" in check_log.read_text().splitlines(), f"Checker log: {check_log}")
    inspect_primary(folder, evidence, row)
    if checker:
        replay_certificate(folder, evidence, chunks, checker)
    else:
        validate_artifact(folder, evidence["certificate"])
    secondary = inspect_secondary(folder, evidence)
    summary = dict(status="CERTIFIED", proof=evidence["drat"], input=evidence["input"],
                   recipe=evidence["recipe"], receipt=artifact(root, marker),
                   provenance=evidence["provenance"])
    if secondary:
        summary["cadical"] = artifact(root, folder / "cadical.json")
        summary["cadical_unsat"] = secondary["exit_code"] == 20
    return summary


def census(ledger, root, checker=None):
    marker_paths = set(root.glob("[0-9a-f][0-9a-f]/*/verified.json"))
    for row in audit_cover(ledger):
        marker_paths.discard(case_dir(root, row["id"]) / "verified.json")
        evidence = inspect_case(root, row, checker)
        if evidence is None:
            evidence = {"status": "OPEN" if row["status"] == "OPEN" else "LEGACY_EVIDENCE_NEEDED"}
        yield dict(id=row["id"], branch=row["branch"], prior_status=row["status"], **evidence)
    require(not marker_paths, f"Certificates outside the cover: {sorted(marker_paths)[:3]}")


def inputs(ledger):
    source = Path(__file__).resolve().parent
    return dict(schema=SCHEMA, order=58, ledger_sha256=digest(ledger),
                generators={name: digest(source / name) for name in SOURCES},
                dependencies={"python-sat": version("python-sat")})


def add_counts(counts, row):
    counts[row["status"]] += 1
    if row.get("cadical_unsat"):
        counts["CADICAL_UNSAT"] += 1


def make_manifest(args):
    args.output.mkdir(parents=True, exist_ok=False)
    counts = Counter()
    index = args.output / "cases.jsonl.gz"
    with index.open("xb") as handle, gzip.GzipFile(fileobj=handle, mode="wb", mtime=0,
                                                   filename="", compresslevel=5) as stream:
        for row in census(args.ledger, args.root):
            add_counts(counts, row)
            stream.write(json_bytes(row))
    manifest = args.output / "manifest.json"
    atomic_json(manifest, dict(**inputs(args.ledger), cases=artifact(args.output, index),
                               counts=dict(counts)))
    print(json.dumps(dict(manifest_sha256=digest(manifest), counts=counts), sort_keys=True))


def verify_manifest(args):
    if args.require_complete:
        require(args.checker, "--require-complete requires an independent --checker")
    manifest = args.manifest / "manifest.json"
    if args.manifest_sha256:
        require(digest(manifest) == args.manifest_sha256, "Release manifest SHA-256 mismatch")
    stored = json.loads(manifest.read_text())
    for key, value in inputs(args.ledger).items():
        require(stored[key] == value, f"Pinned release input mismatch: {key}")
    index = validate_artifact(args.manifest, stored["cases"])
    counts = Counter()
    for expected, actual in zip_longest(records(index), census(args.ledger, args.root, args.checker)):
        require(expected == actual, f"Coverage or evidence mismatch: {expected} / {actual}")
        add_counts(counts, actual)
    require(dict(counts) == stored["counts"], "Manifest count mismatch")
    print(json.dumps(dict(counts=counts, replayed=counts["CERTIFIED"] if args.checker else 0),
                     sort_keys=True))
    if args.require_complete:
        require(counts["CERTIFIED"] == CASE_COUNT, "The computational cover is incomplete")
    if args.require_cadical:
        require(counts["CADICAL_UNSAT"] == CASE_COUNT, "The independent CaDiCaL cover is incomplete")


def import_legacy(args):
    selected = set(args.case_id or ())
    all_rows = {row["id"]: row for row in records(args.ledger)}
    checker = str(Path(shutil.which(args.checker) or args.checker).resolve())
    checker_hash = digest(Path(checker))
    processed = Counter()
    for source in records(args.records):
        if source["status"] not in ("UNSAT", "CERTIFIED"):
            continue
        identifier = identity(source)
        if selected and identifier not in selected:
            continue
        row = all_rows.get(identifier)
        require(row and row["branch"] == source["branch"] and identity(row) == identifier,
                f"Imported receipt is outside the cover: {identifier}")
        folder = case_dir(args.root, identifier)
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / "lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            marker = folder / "verified.json"
            if marker.exists():
                inspect_case(args.root, row)
                processed["ALREADY_CERTIFIED"] += 1
                continue
            attempt = source
            if "attempt" in source:
                attempt = json.loads((args.legacy_root / source["attempt"]).read_text())
                require(identity(attempt) == identifier and attempt["branch"] == row["branch"],
                        f"Attempt does not match {identifier}")
            chunks = formula_chunks(row, recipe_from(attempt))
            require(formula_id(chunks)["sha256"] == source["formula_sha256"],
                    f"Historical CNF hash mismatch for {identifier}")
            proof = args.legacy_root / source["proof"]
            require(digest(proof) == source["proof_sha256"], f"Historical proof hash mismatch: {proof}")
            with TemporaryDirectory(prefix="k58-import-") as tmp:
                formula = Path(tmp, "formula.cnf")
                write_formula(formula, chunks)
                check_log = folder / "import-check.log"
                check_log.write_text(replay(checker, formula, proof))
                evidence = certificate_metadata(row, folder, formula, proof, attempt,
                                                checker_hash, check_log)
            atomic_json(marker, evidence)
            processed["IMPORTED"] += 1
    require(sum(processed.values()) > 0, "No legacy certificates matched")
    if selected:
        require(all((case_dir(args.root, i) / "verified.json").is_file() for i in selected),
                "Some requested legacy certificates were unavailable")
    print(json.dumps(processed, sort_keys=True))


def cross_check(args):
    solver = tool_identity(args.cadical, "CaDiCaL")
    requested = set(args.case_id or ())
    seen = set()
    counts = Counter()
    for row in records(args.ledger):
        if requested and row["id"] not in requested:
            continue
        folder = case_dir(args.root, row["id"])
        marker = folder / "verified.json"
        if not marker.exists():
            continue
        seen.add(row["id"])
        with (folder / "lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            inspect_case(args.root, row)
            evidence = json.loads(marker.read_text())
            if (old := inspect_secondary(folder, evidence)) and old["exit_code"] == 20:
                counts["ALREADY_UNSAT"] += 1
                continue
            chunks = formula_chunks(row, evidence["recipe"])
            command = [solver["path"], "formula.cnf"]
            with TemporaryDirectory(prefix="k58-cadical-") as tmp:
                write_formula(Path(tmp, "formula.cnf"), chunks)
                with NamedTemporaryFile(dir=folder, delete=False) as log:
                    temporary = Path(log.name)
                    started = monotonic()
                    try:
                        result = subprocess.run(command, cwd=tmp, stdout=log,
                                                stderr=subprocess.STDOUT, timeout=args.seconds)
                        code = result.returncode
                    except subprocess.TimeoutExpired:
                        code = None
                    finally:
                        log.close()
                log_path = folder / f"cadical-{digest(temporary)}.log"
                temporary.replace(log_path)
            receipt = dict(case_id=row["id"], input=evidence["input"], command=command,
                           seconds=args.seconds, elapsed=monotonic()-started, exit_code=code,
                           solver=solver, log=artifact(folder, log_path))
            atomic_json(folder / "cadical.json", receipt)
            inspect_secondary(folder, evidence)
            counts["UNSAT" if code == 20 else "NO_UNSAT"] += 1
            require(code in (None, 0, 20), f"Review CaDiCaL exit {code}: {log_path}")
    require(requested.issubset(seen), f"Requested certificates unavailable: {sorted(requested - seen)}")
    require(sum(counts.values()) > 0, "No certificates matched for cross-check")
    print(json.dumps(counts, sort_keys=True))


def export_input(args):
    row = lookup(args.ledger, args.case_id)
    path = case_dir(args.root, row["id"]) / "verified.json"
    recipe = {"tables": True, "total_critical": True, "full_root": args.full_root}
    if path.exists():
        evidence = json.loads(path.read_text())
        recipe = evidence["recipe"]
        require(not args.full_root or recipe["full_root"], "Selected certificate uses a different input")
    chunks = formula_chunks(row, recipe)
    if path.exists():
        require(formula_id(chunks) == evidence["input"], "Certified input hash mismatch")
    write_formula(args.output, chunks)
    print(json.dumps(formula_id(chunks), sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path, default=Path("case-ledger.jsonl.gz"))
    parser.add_argument("--root", type=Path, required=True, help="Publication runner output directory")
    commands = parser.add_subparsers(required=True)
    build = commands.add_parser("manifest")
    build.add_argument("output", type=Path)
    build.set_defaults(run=make_manifest)
    check = commands.add_parser("verify")
    check.add_argument("manifest", type=Path)
    check.add_argument("--manifest-sha256")
    check.add_argument("--checker")
    check.add_argument("--require-complete", action="store_true")
    check.add_argument("--require-cadical", action="store_true")
    check.set_defaults(run=verify_manifest)
    export = commands.add_parser("export-input")
    export.add_argument("case_id")
    export.add_argument("output", type=Path)
    export.add_argument("--full-root", action="store_true")
    export.set_defaults(run=export_input)
    legacy = commands.add_parser("import-legacy")
    legacy.add_argument("records", type=Path)
    legacy.add_argument("--legacy-root", required=True, type=Path)
    legacy.add_argument("--checker", required=True)
    legacy.add_argument("--case-id", action="append")
    legacy.set_defaults(run=import_legacy)
    independent = commands.add_parser("cross-check")
    independent.add_argument("--cadical", required=True)
    independent.add_argument("--seconds", type=float)
    independent.add_argument("--case-id", action="append")
    independent.set_defaults(run=cross_check)
    args = parser.parse_args()
    args.run(args)


if __name__ == "__main__":
    main()
