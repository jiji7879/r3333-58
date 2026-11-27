#!/usr/bin/env python3
"""Run K58_case0's LRAT checks plus warning-free native RUP replay.

Only the optional native wrapper is replaced: the attachment's own wrapper uses
`-w`. The source CNF, proof bytes, event, and LRAT checker remain unchanged.
"""
import json
from pathlib import Path
import subprocess
import sys


def require(test, message):
    if not test:
        raise ValueError(message)


def main():
    if len(sys.argv) != 3:
        raise SystemExit("usage: verify_case0.py PACKAGE OUTPUT_LOG_DIR")
    package, logs = (Path(p).resolve() for p in sys.argv[1:])
    logs.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(package))
    import verify

    sequences = {}

    def strict(executable, query, proof, temp):
        cnf = temp / "query.cnf"
        cnf.write_bytes(query)
        command = [str(executable), str(cnf), str(proof), "-i", "-U", "-t", "300"]
        run = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=310)
        label = proof.name
        (logs / f"{label}.log").write_bytes(run.stdout)
        success_lines = sum(line.strip() == b"s VERIFIED" for line in run.stdout.splitlines())
        require(run.returncode == 0 and success_lines == 1 and b"WARNING" not in run.stdout.upper(),
                f"strict native replay rejected {label}: rc={run.returncode}")
        sequences[label] = {"query_sha256": verify.sha(query), "proof_sha256": verify.sha(proof.read_bytes()),
                            "returncode": run.returncode, "success_lines": success_lines,
                            "warning_free": True, "flags": ["-i", "-U", "-t", "300"]}

    verify.native_replay = strict
    # Compile and exercise the supplied C source as an optional native replay.
    sys.argv = [str(package / "verify.py"), "--native"]
    verify.main()
    (logs / "native-receipts.json").write_text(json.dumps(sequences, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"strict_native_proofs": len(sequences), "warning_suppression_used": False}))


if __name__ == "__main__":
    main()
