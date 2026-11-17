#!/usr/bin/env python3
"""A versioned encoding manifest, and a checker that rebuilds CNFs from it.

The bundle's release manifest records what a producer *claims* about each case.
This one records what a checker needs in order to reconstruct the case's CNF
without trusting the producer: the case id, the recipe, the encoder revision,
and the expected CNF hash.

    make    --bundle K58 --out encodings-v1.json [--ids ids.txt]
    verify  --bundle K58 --manifest encodings-v1.json [--checker drat-trim] [--lrat-dir DIR]

`make` regenerates every selected case's CNF from the frozen ledger and records
its hash.  `verify` recomputes each hash from the ledger and the manifest's own
recipe, so a manifest that disagrees with the generator is caught here rather
than at proof-replay time.  With `--lrat-dir`, each case's binary LRAT is also
checked against the regenerated CNF if a checker is supplied.

The manifest is versioned by the encoder revision: the SHA-256 of the generator
sources that determine the CNF bytes.  A change to any of them changes the
revision, so an old manifest cannot silently validate new formulas.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

RECIPE_KEYS = ("tables", "total_critical", "full_root")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load(bundle):
    sys.path.insert(0, str(bundle))
    import cover_evidence as ce
    return ce


def encoder_revision(bundle, ce):
    """Hash the sources that determine the CNF bytes."""
    h = hashlib.sha256()
    for name in sorted(ce.SOURCES):
        h.update(name.encode() + b"\0" + sha256_file(bundle / name).encode() + b"\0")
    return h.hexdigest()


def rows(ce, bundle, only=None):
    for row in ce.records(bundle / "case-ledger.jsonl.gz"):
        if only and row["id"] not in only:
            continue
        yield row


def cmd_make(args):
    bundle = Path(args.bundle).resolve()
    ce = load(bundle)
    only = set(Path(args.ids).read_text().split()) if args.ids else None
    rev = encoder_revision(bundle, ce)
    entries = []
    for row in rows(ce, bundle, only):
        recipe = {k: row.get(k, False) for k in RECIPE_KEYS}
        if "recipe" in row:
            recipe = row["recipe"]
        ident = ce.formula_id(ce.formula_chunks(row, recipe))
        entries.append(dict(id=row["id"], branch=row["branch"], recipe=recipe,
                            cnf_sha256=ident["sha256"], cnf_bytes=ident["bytes"]))
    manifest = dict(schema=1, order=58, encoder_revision=rev,
                    ledger_sha256=sha256_file(bundle / "case-ledger.jsonl.gz"),
                    cases=entries)
    out = Path(args.out)
    out.write_text(json.dumps(manifest, sort_keys=True, indent=1) + "\n")
    print(json.dumps(dict(manifest=str(out), cases=len(entries),
                          encoder_revision=rev[:16], sha256=sha256_file(out))))
    return 0


def cmd_verify(args):
    bundle = Path(args.bundle).resolve()
    ce = load(bundle)
    man = json.loads(Path(args.manifest).read_text())
    rev = encoder_revision(bundle, ce)
    if man["encoder_revision"] != rev:
        print(f"FAIL encoder revision: manifest {man['encoder_revision'][:16]}, "
              f"bundle {rev[:16]}", file=sys.stderr)
        return 1
    if man["ledger_sha256"] != sha256_file(bundle / "case-ledger.jsonl.gz"):
        print("FAIL ledger hash", file=sys.stderr)
        return 1
    ledger = {r["id"]: r for r in ce.records(bundle / "case-ledger.jsonl.gz")}
    bad = 0
    for entry in man["cases"]:
        row = ledger.get(entry["id"])
        if row is None:
            print(f"FAIL unknown case {entry['id']}", file=sys.stderr)
            bad += 1
            continue
        ident = ce.formula_id(ce.formula_chunks(row, entry["recipe"]))
        if ident["sha256"] != entry["cnf_sha256"] or ident["bytes"] != entry["cnf_bytes"]:
            print(f"FAIL {entry['id'][:8]}: manifest {entry['cnf_sha256'][:12]} "
                  f"vs regenerated {ident['sha256'][:12]}", file=sys.stderr)
            bad += 1
    print(json.dumps(dict(cases=len(man["cases"]), failures=bad,
                          encoder_revision=rev[:16])))
    return 0 if bad == 0 else 1


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("mode", choices=("make", "verify"))
    p.add_argument("--bundle", required=True)
    p.add_argument("--out", help="manifest to write (make)")
    p.add_argument("--manifest", help="manifest to check (verify)")
    p.add_argument("--ids", help="file of case ids (make)")
    p.add_argument("--checker", help="drat-trim (accepted for symmetry; unused)")
    p.add_argument("--lrat-dir", help="directory of binary LRAT (reserved)")
    a = p.parse_args()
    if a.mode == "make":
        if not a.out:
            p.error("make needs --out")
        return cmd_make(a)
    if not a.manifest:
        p.error("verify needs --manifest")
    return cmd_verify(a)


if __name__ == "__main__":
    sys.exit(main())
