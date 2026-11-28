#!/usr/bin/env python3
"""Two-checker replay of the retained RUP derivation, with scoped status."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    results = []
    for name, checker in (("own", ROOT / "bin/drat-trim-own"),
                          ("massive", ROOT / "bin/drat-trim-massive")):
        cmd = [str(checker.resolve()), str((ROOT / "inputs/parent.cnf").resolve()),
               str((ROOT / "inputs/cas.drat").resolve()), "-i", "-f", "-U", "-t", "120"]
        run = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             timeout=135)
        log = run.stdout.replace(b"\r", b"\n")
        path = ROOT / "checks" / f"derivation-replay-{name}.log"
        path.write_bytes(log)
        text = log.decode(errors="replace")
        lines = text.splitlines()
        expected_warning = "c WARNING: no empty clause detected, this is not a refutation"
        warnings = [x for x in lines if "WARNING" in x or "ERROR" in x]
        passed = (run.returncode == 1 and lines.count("s DERIVATION") == 1
                  and "s VERIFIED" not in lines and "s NOT VERIFIED" not in lines
                  and "c VERIFIED derivation: all lemmas preserve satisfiability" in lines
                  and "c finished parsing, read 183180 bytes from proof file" in lines
                  and "c 0 RAT lemmas in core; 0 redundant literals in core lemmas" in lines
                  and warnings == [expected_warning])
        results.append({"name": name, "checker_sha256": sha(checker),
                        "returncode": run.returncode, "passed": passed,
                        "derivation_lines": lines.count("s DERIVATION"),
                        "verified_refutation_lines": lines.count("s VERIFIED"),
                        "warnings": warnings,
                        "parent_sha256": sha(ROOT / "inputs/parent.cnf"),
                        "cas_sha256": sha(ROOT / "inputs/cas.drat"),
                        "proof_bytes": (ROOT / "inputs/cas.drat").stat().st_size,
                        "log": str(path.relative_to(ROOT)), "command": cmd})
        print(name, "PASS" if passed else "FAIL", "rc", run.returncode)
    report = {"schema": "k58-two-checker-rup-derivation/v1", "passed": all(x["passed"] for x in results),
              "scope": "DERIVATION only; no empty clause and no UNSAT claim", "results": results}
    (ROOT / "checks/derivation-replay.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    assert report["passed"]


if __name__ == "__main__":
    main()
