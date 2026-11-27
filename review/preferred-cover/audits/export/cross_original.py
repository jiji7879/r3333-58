"""Cross-check bundle parents against the tracked original wallcc encoder."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BUNDLE = HERE / "bundle/K58_wall_10k_batches"
TRACKED = REPO / "tools/selfcontained/wallcc"
sys.path.insert(0, str(BUNDLE))
from common import sha, tsv, wall, OUT
from problem import row_formula

rows, _, arms = wall()
ids = {next(rid for rid in sorted(rows) if arms[rid]["size"] == n) for n in (11, 12, 13, 14)}
ids.add(tsv(OUT / "preferred-sample.tsv.gz")[0]["row_id"])
ids.add(tsv(OUT / "cold-raw.tsv.gz")[0]["id"])
checks = []
code = """import json,sys
from common import sha
from problem import lookup,row_formula
r=lookup(sys.argv[1]); b=row_formula(r,'first')
print(json.dumps({'id':r['id'],'sha256':sha(b)}))
"""
# tracked wallcc has no common.py; use hashlib in the child instead.
code = code.replace("from common import sha", "from hashlib import sha256 as _sha256").replace("sha(b)", "_sha256(b).hexdigest()")
for rid in sorted(ids):
    expected = sha(row_formula(rows[rid], "first"))
    run = subprocess.run([str(BUNDLE / ".venv/bin/python"), "-c", code, rid],
                         cwd=TRACKED, check=True, capture_output=True, text=True)
    actual = json.loads(run.stdout)
    assert actual == {"id": rid, "sha256": expected}, (rid, expected, actual)
    checks.append(actual)
    print(rid, expected, flush=True)
source_matches = {}
for path in sorted((BUNDLE / "engine/frozen").glob("*.py")):
    counterpart = TRACKED / "frozen" / path.name
    assert counterpart.read_bytes() == path.read_bytes(), path.name
    source_matches[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
wall_matches = ((BUNDLE / "inputs/wall.jsonl.gz").read_bytes() ==
                (TRACKED / "data/wall.jsonl.gz").read_bytes())
assert wall_matches
out = {"tracked_commit": "8e5a10eb58de4c4b50b128eadc9a36c4b105ee4f",
       "parents_cross_regenerated": checks,
       "frozen_python_sources_byte_identical": source_matches,
       "wall_jsonl_gz_byte_identical": wall_matches,
       "bundle_problem_diff": "only fallback inputs path and checked_case helper; row_formula unchanged"}
(HERE / "original_source_audit.json").write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps({"parents": len(checks), "frozen_sources": len(source_matches), "wall_matches": wall_matches}))
