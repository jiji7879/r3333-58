#!/usr/bin/env python3
"""Run the supplied quickstart reconstruction with strict, warning-free replay.

The package remains byte-identical. Its manifest is checked before its runner is
called; only check_native is replaced at runtime because the supplied helper
uses -w. No argument or evidence file is changed in the supplied package.
"""

if not __debug__:
    raise RuntimeError("Refinement verification requires Python assertions; do not use -O or PYTHONOPTIMIZE.")
import argparse
import contextlib
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import time


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--package", type=Path, required=True)
    ap.add_argument("--checker", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    package = args.package.resolve()
    checker = args.checker.resolve()
    checker.chmod(checker.stat().st_mode | stat.S_IXUSR)
    out = args.out.resolve()
    assert not out.exists()
    out.mkdir(parents=True)
    sys.path.insert(0, str(package))
    import review
    review.manifest()

    def strict(executable, query, proof, tmp, title):
        (tmp / "query.cnf").write_bytes(query)
        (tmp / "check.rup").write_bytes(proof)
        result = subprocess.run([str(executable), str(tmp / "query.cnf"), str(tmp / "check.rup"),
                                 "-i", "-U", "-t", "300"], stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=310)
        output = result.stdout.decode(errors="replace")
        with (out / "strict-checks.log").open("a") as stream:
            stream.write(f"===== {title} =====\n{output}\n")
        good = (result.returncode == 0 and result.stdout.count(b"s VERIFIED") == 1
                and b"WARNING" not in result.stdout.upper())
        if not good:
            raise ValueError(f"{title} failed strict replay: {output[-500:]!r}")

    review.check_native = strict
    emit = out / "direct-cover"
    sys.argv = [str(package / "review.py"), "--checker", str(checker), "--emit-cover", str(emit)]
    started = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()) as captured:
        review.main()
    (out / "review.log").write_text(captured.getvalue())
    print(captured.getvalue(), end="")
    result = subprocess.run([str(checker), str(emit / "cover.cnf"), str(emit / "cover.rup"),
                             "-i", "-U", "-t", "300"], stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=310)
    text = result.stdout.decode(errors="replace")
    assert result.returncode == 0 and result.stdout.count(b"s VERIFIED") == 1
    assert b"WARNING" not in result.stdout.upper()
    (out / "independent-cover-check.log").write_text(text)
    receipt = {"schema": "quickstart-strict-replay/v1", "package": str(package),
               "checker": str(checker), "external_checker_used": True,
               "warning_suppression_used": False, "seconds": time.perf_counter() - started,
               "package_manifest_checked": True,
               "direct_cover_rechecked_strictly": True,
               "output_from_supplied_runner": captured.getvalue()}
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print("PASS  Independent cover replay with -i -U and zero warnings.")


if __name__ == "__main__":
    main()
