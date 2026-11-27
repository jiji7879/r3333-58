#!/usr/bin/env python3
"""Build the bounded K58 wall-983774 audit handover ZIP and its manifest."""
import collections
import hashlib
import json
import os
import sys
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path.cwd()
M = ROOT / ".ultramath/smwyfnpf0"
FILES = []
EXTENSIONS = {".py", ".md", ".json", ".jsonl", ".log", ".txt", ".tsv", ".gz", ".diff"}


def add(path):
    path = Path(path).resolve()
    if not path.exists():
        raise FileNotFoundError(path)
    if path.is_dir():
        for child in sorted(path.rglob("*")):
            if not child.is_dir() and "__pycache__" not in child.parts and "venv" not in child.parts:
                FILES.append(child.resolve())
    else:
        FILES.append(path)


add("results/wall-983774-2026-11-27")
add("tools/wall983774")
for spec in [
    "REPORT_A.md", "audit_packages.py", "audit_queue.py", "compare_prior_sources.py",
    "package-audit.json", "queue-audit.json", "source-comparison.json",
    "prior-source-differences.diff", "input-sha256.txt",
]:
    add(M / "m8" / spec)
for spec in ["report.md", "audit_b.py", "results", "logs"]:
    add(M / "m1" / spec)
for spec in [
    "report.md", "integration_audit.py", "summary.json", "static-summary.json",
    "results.jsonl", "evidence-sha256.txt", "physical-selection.json", "closed-selection.json",
    "cases", "logs",
]:
    add(M / "m2" / "audit" / spec)
for path in (M / "m3").iterdir():
    if path.is_file() and path.suffix in EXTENSIONS:
        FILES.append(path)
add(M / "m3" / "replay_results")
for spec in ["drat-trim", "relabel"]:
    add(M / "m3" / "tools" / spec)
for path in (M / "m4").iterdir():
    if path.is_file() and path.suffix in {".py", ".md", ".json", ".log", ".gz"}:
        FILES.append(path)
for spec in ["drat-trim-audit", "relabel-audit"]:
    add(M / "m4" / spec)
add(M / "m5" / "report.md")
for spec in [
    "audit_live0.py", "audit_cache_controls.py", "live0-formula-audit.json",
    "live0-strict-summary.json", "live0-physical.json", "cache-control-summary.json",
    "native-pin-audit.json", "submission-hashes.txt", "strict-live0",
    "negative-e2e-forged-cache", "cache-controls", "live0-run", "environment.txt",
    "negative-cli", "index-crosswalk.txt", "index-boundary.txt",
    "executed-input-hash-check.txt", "native-versions.txt", "cadical-version.txt",
]:
    add(M / "m5" / "audit" / spec)
for path in (M / "m6").iterdir():
    if not path.is_file():
        continue
    if path.name.startswith("src_") or path.name in {
        "REPORT.md", "audit_receipts.py", "audit_formula_bindings.py", "replay_positive_proofs.py",
        "audit-summary.json", "audit-run.log", "audit-discrepancies.txt", "cap128-call-map.tsv.gz",
        "formula-audit-summary.json", "formula-audit-run.log", "formula-query-samples.tsv",
        "formula-row-receipts.tsv", "positive-proof-replay.tsv", "positive-proof-replay-summary.json",
        "positive-proof-replay-run.log", "artifact-hashes.txt", "drat-trim-build.log",
    }:
        FILES.append(path)
add(M / "m6" / "positive-proof-logs")
add(M / "m6" / "bin" / "drat-trim")
for path in (M / "m7" / "work").iterdir():
    if path.is_file() and "__pycache__" not in path.parts:
        FILES.append(path)

# The generated package index includes the archive's own digest, so it must not
# be embedded in the archive whose contents it describes.
FILES = [p for p in FILES if p != ROOT / "results/wall-983774-2026-11-27/package-index.json"]
records = [path.relative_to(ROOT).as_posix() for path in FILES]
duplicates = [name for name, count in collections.Counter(records).items() if count > 1]
if duplicates:
    raise AssertionError(f"duplicate archive selection: {duplicates}")
digests = {}
uncompressed = 0
for path in sorted(FILES, key=lambda p: p.relative_to(ROOT).as_posix()):
    blob = path.read_bytes()
    digests[path.relative_to(ROOT).as_posix()] = hashlib.sha256(blob).hexdigest()
    uncompressed += len(blob)
manifest = "".join(f"{digests[name]}  {name}\n" for name in sorted(digests))
out = ROOT / "dist/k58-wall-983774-audit.zip"
replace_mode = "--replace" in sys.argv[1:]
if out.exists() and not replace_mode:
    raise FileExistsError("Archive already exists; use --replace only for an intentional rebuild")
temporary = out.with_suffix(".zip.tmp")
with ZipFile(temporary, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
    for path in sorted(FILES, key=lambda p: p.relative_to(ROOT).as_posix()):
        archive.write(path, path.relative_to(ROOT).as_posix())
    archive.writestr("SHA256SUMS", manifest)
with ZipFile(temporary) as archive:
    if archive.testzip() is not None:
        raise RuntimeError("ZIP integrity check failed")
os.replace(temporary, out)
digest = hashlib.sha256(out.read_bytes()).hexdigest()
existing = (ROOT / "dist/SHA256SUMS").read_text()
lines = [line for line in existing.splitlines()
         if not line.endswith("  dist/k58-wall-983774-audit.zip")]
lines.append(f"{digest}  dist/k58-wall-983774-audit.zip")
(ROOT / "dist/SHA256SUMS").write_text("\n".join(lines) + "\n")
index = {
    "archive": "dist/k58-wall-983774-audit.zip", "files": len(FILES) + 1,
    "sha256": digest, "bytes": out.stat().st_size, "uncompressed_bytes": uncompressed,
    "member_report_count": len(FILES), "source_bundles_required_for_regeneration": True,
}
(ROOT / "results/wall-983774-2026-11-27/package-index.json").write_text(
    json.dumps(index, indent=2, sort_keys=True) + "\n")
print(json.dumps(index, indent=2))
