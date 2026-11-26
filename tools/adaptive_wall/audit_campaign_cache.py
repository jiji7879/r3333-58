#!/usr/bin/env python3
"""Exercise a patched campaign's actual run_native cache path on tiny CNFs.

Three tiny fresh SAT/UNSAT solver calls validate compatibility.  Every cached
call is then checked not to invoke Kissat.  This script reads no K58 row and
launches no K58 search.
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path


def binary_clause(clause):
    out = bytearray(b"a")
    for literal in clause:
        value = 2 * abs(literal) + int(literal < 0)
        while value >= 128:
            out.append((value & 127) | 128)
            value >>= 7
        out.append(value)
    out.append(0)
    return bytes(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--work", type=Path, required=True,
                        help="new directory inside the project's scratch area")
    parser.add_argument("--out", type=Path, required=True, help="new JSON report")
    args = parser.parse_args()
    campaign = args.campaign.resolve()
    work = args.work.resolve()
    out = args.out.resolve()
    if work.exists() or out.exists():
        parser.error("--work and --out must be new")
    work.mkdir(parents=True)
    out.parent.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(campaign))
    import frontier
    from arm_pairs import sha
    from bind import json_bytes
    from campaign_cache import CACHE_INVALID
    from compile import append

    if Path(frontier.__file__).resolve().parent != campaign:
        raise ValueError("imported frontier from the wrong campaign")

    original_run = subprocess.run
    invocations = []

    def observed(command, **kwargs):
        name = Path(command[0]).name
        invocations.append({"executable": name, "arguments": [str(x) for x in command]})
        return original_run(command, **kwargs)

    subprocess.run = observed
    checks = []

    def record(name, condition, detail=None):
        if not condition:
            raise AssertionError(f"{name}: {detail}")
        checks.append({"name": name, "passed": True, "detail": detail})

    record("invalid_is_not_terminal", CACHE_INVALID not in frontier.DEAD)
    record("pending_is_not_terminal", "AUGMENTED_UNSAT_PENDING_BASE" not in frontier.DEAD)

    def identities(base, cube=()):
        _, plain = append(base, [[v] for v in cube]) if cube else (None, base)
        return plain, {"id": "synthetic", "node": "r", "mode": "stock", "cap": 100,
                       "cube": list(cube), "parent_sha256": sha(base),
                       "plain_sha256": sha(plain), "query_sha256": sha(plain),
                       "cuts": 0, "pair_cuts": 0}

    def cached_call(name, base, cube=()):
        folder = work / name
        folder.mkdir()
        plain, expected = identities(base, cube)
        return folder, plain, expected

    def native(base, folder):
        return frontier.run_native(base, [], [], b"", [], "synthetic", "r",
                                   "stock", 100, folder)

    def install(folder, expected, receipt):
        (folder / "r-stock-100.json").write_bytes(json_bytes(dict(expected, **receipt)))

    def artifact(folder, name, data):
        (folder / name).write_bytes(gzip.compress(data, mtime=0))

    def kissat_count():
        return sum(x["executable"] == "kissat" for x in invocations)

    def trim_count():
        return sum(x["executable"] == "drat-trim" for x in invocations)

    def invalid(name, base, receipt):
        folder, plain, expected = cached_call(name, base)
        install(folder, expected, receipt)
        before = kissat_count()
        got = native(base, folder)
        record(name, got["status"] == CACHE_INVALID and kissat_count() == before and
               "proof" not in got and "model" not in got, got)
        record(name + "_preserves_receipt", json.loads((folder / "r-stock-100.json").read_text())
               == dict(expected, **receipt))
        return got

    try:
        # Fresh tiny UNSAT, then genuine cache replay and a damaged artifact.
        unsat = b"p cnf 1 2\n1 0\n-1 0\n"
        folder = work / "fresh-unsat"
        folder.mkdir()
        got = native(unsat, folder)
        record("fresh_unsat", got["status"] == "UNSAT_BASE", got)
        receipt = json.loads((folder / "r-stock-100.json").read_text())
        before_k, before_t = kissat_count(), trim_count()
        before_invocations = len(invocations)
        cached = native(unsat, folder)
        record("valid_cached_unsat", cached == receipt and kissat_count() == before_k and
               trim_count() > before_t)
        record("cached_unsat_uses_strict_checker", all(
            "-w" not in x["arguments"] for x in invocations[before_invocations:]
            if x["executable"] == "drat-trim"))
        (folder / receipt["proof"]).unlink()
        receipt_bytes = (folder / "r-stock-100.json").read_bytes()
        before_k = kissat_count()
        cached = native(unsat, folder)
        record("missing_cached_proof", cached["status"] == CACHE_INVALID and
               kissat_count() == before_k, cached)
        record("invalid_receipt_not_rewritten", (folder / "r-stock-100.json").read_bytes()
               == receipt_bytes)

        # Fresh tiny SAT exercises the stricter total-model requirement before
        # cache reuse.  Remove one literal while updating the stored hash.
        sat = b"p cnf 2 2\n1 0\n2 0\n"
        folder = work / "fresh-sat"
        folder.mkdir()
        got = native(sat, folder)
        record("fresh_total_sat", got["status"] == "SAT_BASE", got)
        model_path = folder / got["model"]
        model = json.loads(gzip.decompress(model_path.read_bytes()))
        record("fresh_sat_has_every_variable", len(model) == 2 and
               {abs(x) for x in model} == {1, 2}, model)
        before_k = kissat_count()
        cached = native(sat, folder)
        record("valid_cached_sat", cached["status"] == "SAT_BASE" and kissat_count() == before_k)
        incomplete = model[:-1]
        data = json_bytes(incomplete)
        artifact(folder, got["model"], data)
        receipt = json.loads((folder / "r-stock-100.json").read_text())
        receipt["model_sha256"] = sha(data)
        (folder / "r-stock-100.json").write_bytes(json_bytes(receipt))
        before_k = kissat_count()
        cached = native(sat, folder)
        record("incomplete_cached_sat", cached["status"] == CACHE_INVALID and
               kissat_count() == before_k, cached)

        invalid("under_cap_open", sat,
                {"status": "OPEN", "seconds": 0.0, "conflicts": 3})
        invalid("missing_model", sat,
                {"status": "SAT_BASE", "seconds": 0.0, "conflicts": 0,
                 "model": "absent.model.gz", "model_sha256": "0" * 64})
        invalid("raw_unsat_not_promoted", unsat,
                {"status": "RAW_UNSAT", "seconds": 0.0, "conflicts": 1})

        # Produce a real tiny non-unit proof and use it only as pending
        # augmented evidence against the same exact query bytes.
        plain = b"p cnf 2 1\n1 2 0\n"
        cuts = [[-1, 2], [1, -2], [-1, -2]]
        _, query = append(plain, cuts)
        assert query == b"p cnf 2 4\n1 2 0\n-1 2 0\n1 -2 0\n-1 -2 0\n"
        proof_folder = work / "proof-source"
        proof_folder.mkdir()
        proof_result = native(query, proof_folder)
        record("fresh_nonunit_unsat", proof_result["status"] == "UNSAT_BASE", proof_result)
        proof = gzip.decompress((proof_folder / proof_result["proof"]).read_bytes())
        # This compact proof makes the malformed-prefix control deterministic:
        # strict -i rejects the X tag; the previously used -w mode accepts it.
        compact = binary_clause([2]) + binary_clause([])
        bad_tag = b"X" + compact[1:]
        folder, _, expected = cached_call("corrupt-binary-tag", query)
        artifact(folder, "bad-tag.drat.gz", bad_tag)
        install(folder, expected,
                {"status": "UNSAT_BASE", "seconds": 0.0, "conflicts": 1,
                 "proof": "bad-tag.drat.gz", "proof_sha256": sha(bad_tag)})
        before_k = kissat_count()
        got = native(query, folder)
        record("corrupt_binary_tag_rejected_strictly", got["status"] == CACHE_INVALID and
               kissat_count() == before_k, got)

        folder, plain_bytes, expected = cached_call("pending", plain)
        expected["query_sha256"] = sha(query)
        expected["cuts"] = len(cuts)
        artifact(folder, "pending.drat.gz", proof)
        install(folder, expected,
                {"status": "AUGMENTED_UNSAT_PENDING_BASE", "seconds": 0.0,
                 "conflicts": 1, "proof": "pending.drat.gz", "proof_sha256": sha(proof)})
        before_k, before_t = kissat_count(), trim_count()
        got = frontier.run_native(plain, [], cuts, b"", [],
                                  "synthetic", "r", "stock", 100, folder)
        record("pending_stays_pending", got["status"] == "AUGMENTED_UNSAT_PENDING_BASE" and
               kissat_count() == before_k and trim_count() > before_t, got)

        # Suffixed mismatches are invalid rather than asserted as another wave.
        folder, _, expected = cached_call("suffix", unsat)
        suffixed = "r-stock-100-" + sha(unsat)[:12] + ".json"
        (folder / suffixed).write_bytes(json_bytes(dict(expected, id="wrong")))
        (folder / "r-stock-100.json").write_bytes(json_bytes(dict(expected,
            status="OPEN", seconds=0.0, conflicts=100, query_sha256="0" * 64)))
        before_k = kissat_count()
        got = native(unsat, folder)
        record("query_suffix_identity", got["status"] == CACHE_INVALID and
               kissat_count() == before_k, got)
        record("all_native_drat_calls_strict", all(
            "-i" in x["arguments"] and "-w" not in x["arguments"] and
            "-W" not in x["arguments"] for x in invocations
            if x["executable"] == "drat-trim"))

        frontier_bytes = (campaign / "frontier.py").read_bytes()
        helper_bytes = (campaign / "campaign_cache.py").read_bytes()
        report = {
            "schema": "k58-native-cache-integration-audit/v1",
            "verdict": "PASS",
            "checks": checks,
            "check_count": len(checks),
            "fresh_tiny_kissat_calls": kissat_count(),
            "drat_trim_calls": trim_count(),
            "cached_calls_added_no_kissat": True,
            "k58_rows_or_formulas_used": False,
            "frontier_sha256": hashlib.sha256(frontier_bytes).hexdigest(),
            "campaign_cache_sha256": hashlib.sha256(helper_bytes).hexdigest(),
            "invocations": invocations,
        }
        out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        print(json.dumps({k: report[k] for k in
                          ("verdict", "check_count", "fresh_tiny_kissat_calls",
                           "drat_trim_calls", "frontier_sha256", "campaign_cache_sha256")},
                         indent=2, sort_keys=True))
    finally:
        subprocess.run = original_run


if __name__ == "__main__":
    main()
