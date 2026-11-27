#!/usr/bin/env python3
"""Strictly replay all 608 local RUP proofs, sequentially, never using -w."""
from collections import Counter
from tempfile import TemporaryDirectory
from pathlib import Path
import gzip
import hashlib
import json
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
BASE = HERE / "extracted" / "K58_wall_10k_batches"
sys.path.insert(0, str(BASE))
sys.path.insert(0, str(BASE / "engine"))
import cover_proofs
import preferred_proofs

CHECKER = BASE / "tools" / "drat-trim"


def replay_one(folder, kind, n, z, raw, receipt, proof):
    assert hashlib.sha256(raw).hexdigest() == receipt["query"] if kind == "preferred" else hashlib.sha256(raw).hexdigest() == receipt["query_sha256"]
    expected_proof = receipt["proof"] if kind == "preferred" else receipt["proof_sha256"]
    assert hashlib.sha256(proof).hexdigest() == expected_proof
    q = folder / "query.cnf"
    p = folder / "proof.rup"
    q.write_bytes(raw)
    p.write_bytes(proof)
    command = [str(CHECKER), str(q), str(p), "-i", "-U"]
    start = time.monotonic()
    run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    seconds = time.monotonic() - start
    output = run.stdout.decode(errors="replace")
    if run.returncode != 0 or "s VERIFIED" not in output.splitlines():
        raise RuntimeError({"kind": kind, "n": n, "z": z, "command": command,
                            "returncode": run.returncode, "output": output[-3000:]})
    return {"kind": kind, "n": n, "second": z, "proof_bytes": len(proof),
            "seconds": round(seconds, 6), "returncode": run.returncode,
            "flags": ["-i", "-U"], "verified_line": "s VERIFIED"}


def main():
    scratch = HERE / ".scratch"
    scratch.mkdir(exist_ok=True)
    results = []
    start = time.monotonic()
    with TemporaryDirectory(dir=scratch) as d:
        folder = Path(d)
        for n, z, allow, verify in cover_proofs.jobs(True):
            assert verify
            raw = cover_proofs.query(n, z, allow)
            stem = f"{n}-{z}"
            receipt = json.loads((cover_proofs.PROOFS / f"{stem}.json").read_text())
            proof = gzip.decompress((cover_proofs.PROOFS / f"{stem}.rup.gz").read_bytes())
            results.append(replay_one(folder, "sorted", n, z, raw, receipt, proof))
        for n in (11, 12, 13, 14):
            from common import WORDS
            for z in WORDS:
                raw = preferred_proofs.instance(n, z)
                stem = f"{n}-{z}"
                receipt = json.loads((preferred_proofs.DEST / f"{stem}.json").read_text())
                proof = gzip.decompress((preferred_proofs.DEST / f"{stem}.rup.gz").read_bytes())
                results.append(replay_one(folder, "preferred", n, z, raw, receipt, proof))
    counts = Counter(r["kind"] for r in results)
    assert counts == {"sorted": 304, "preferred": 304}
    summary = {
        "checker": str(CHECKER.relative_to(HERE)),
        "checker_sha256": hashlib.sha256(CHECKER.read_bytes()).hexdigest(),
        "command_flags_per_proof": ["-i", "-U"],
        "warnings_suppressed": False,
        "workers": 1,
        "queries_and_proof_sha256_regenerated_and_checked": len(results),
        "verified_counts": dict(counts),
        "total_proof_bytes": sum(r["proof_bytes"] for r in results),
        "wall_seconds": round(time.monotonic() - start, 3),
        "results": results,
    }
    (HERE / "strict_local_replay_results.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "results"}, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
