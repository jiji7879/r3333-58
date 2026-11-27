# Local computation record

All third-party files were read before execution. Input was extracted into a
new `.scratch/reusable-spoke-rules-v1/` tree after safe-path and duplicate
checks. No production ledger, queue or package bytes were edited.

## Archive

```sh
sha256sum attachments/let-s-try-and-rbdv/K58_reusable_spoke_rules.zip
```

Result:
`2a22f91d881ae39ac99bcd3a8d44e8fd55783f00b0255df44088f57970af6108`.
The ZIP has 151 files / approximately 40.28 MiB uncompressed, is CRC-valid,
and all 150 manifest hashes pass.

## Supplied replay under strict checking

The supplied `replay.py`, `transport.py`, `placements.py`, `check_exports.py`
and frozen `inputs/gluing.py` were inspected. Their standard checker calls
use warning suppression, so the run was wrapped in the same no-`-w` proxy used
for the preceding packages:

```sh
ROOT="$PWD"
P="$ROOT/.scratch/reusable-spoke-rules-v1/src/K58_reusable_spoke_rules"
D="$ROOT/.scratch/reusable-spoke-rules-v1/strict-verifier"
mkdir -p "$D/bin" "$D/tools" "$D/strict-logs" "$D/tmp"
cc -std=c99 -D_GNU_SOURCE -O2 "$P/tools/drat-trim.c" -o "$D/bin/drat-trim"
cp "$ROOT/.scratch/two-site-consequences-v1/tools/strict-drat-wrap.py" "$D/tools/strict-drat-wrap.py"
chmod +x "$D/tools/strict-drat-wrap.py"
export AUDIT_ROOT="$D" AUDIT_REAL_DRAT_TRIM="$D/bin/drat-trim" TMPDIR="$D/tmp"
export PYTHONDONTWRITEBYTECODE=1 K58_WORKERS=4
cd "$P"
python3 -B "$P/replay.py" "$D/tools/strict-drat-wrap.py" > "$D/verify.out"
```

Exit status 0. There were **91 accepted calls / 91 native proof checks**, in
**48.66517673432827 seconds** of checker time. The output labels match the
package claim: 9,288 catalogue entries on 6,617 representatives, six canonical
and eight physical proofs, 53 transfer proofs, 20 pivot-3 exclusions and
325 surviving pivot-3 arms. Pivot 0 has all 1,417 arms OPEN.

## Independent query/proof comparisons

The separate source [independent_replay_audit.py](independent_replay_audit.py)
does not import `replay.py`. It individually reconstructs parent identities,
physical query units, transferred proof streams, all arm-assignment partitions,
signature groups and canonical/example serialization. It imports only the
inspected pure binary proof mapper and metadata helper needed for the frozen
roster computations.

```sh
python3 -B research/k58-reusable-spoke-rules/checks/independent_replay_audit.py \
  .scratch/reusable-spoke-rules-v1/src/K58_reusable_spoke_rules \
  .scratch/reusable-spoke-rules-v1/strict-verifier \
  research/k58-reusable-spoke-rules/checks/2-compute.json \
  .scratch/two-site-consequences-v1/src/K58_two_site_consequences
```

Outcome: `result: PASS`. It checks:

- all 91 intended query/proof pairs as an exact multiset, not just call count;
- every reported proof-byte read equals its actual stream length;
- six canonical and eight physical obligations (covering all six classes);
- 53 transfer source/donor mappings, recipients, raw-prefix/suffix-derived
  parents and physical two-pin meanings, in 27 distinct wall rows;
- native final case-0 cubes, without trigger units or hidden alteration of the
  proof base, with sizes {13:1, 14:4, 15:3, 16:1, 82:11};
- both arm covers, all 1,417 + 345 = 1,762 length-91 assignments and the
  unique/monochromatic-triangle-free/pivot-consistent arms;
- exact hit/open frontiers 0/1417 and 20/325, plus equality with the older
  57/36 surviving four-edge word-group sets;
- 9,288 distinct representative/clause pairs on 6,617 representatives across
  6,489 rows and all 150 manifest hashes.

Receipt: [2-compute.json](2-compute.json), which contains all 91 native
query/proof/byte hashes and the 53 named transferred clause identities.

## Discriminating controls

```sh
python3 -B research/k58-reusable-spoke-rules/checks/negative_controls.py \
  .scratch/reusable-spoke-rules-v1/src/K58_reusable_spoke_rules \
  .scratch/reusable-spoke-rules-v1/strict-verifier/bin/drat-trim \
  research/k58-reusable-spoke-rules/checks/negative-controls.json
```

Results:

```text
satisfiable_pin_units_only rejected 1 verified_lines 0
genuine_proof_half_truncated rejected 1 verified_lines 0
```

The first query has only the two positive antecedent units and a model by
construction. The second uses the genuine complete query but half its proof.
Native rejection with nonzero status and no `s VERIFIED` demonstrates that we
did not merely accept any status substring or disregard malformed proofs.

## Not run or claimed

No independent-model swarm member was started after the person's explicit
stop request. No Lean formalisation was started, and native RUP checking is
not represented as a pure-kernel proof. No direct broad SAT/SLS search was
started, the control solver timings were not treated as a certified speedup,
and the global production wall was not changed.

The meta-placement derivation is checked for all 9,288 entries, with six
canonical and eight physical native proof examples. There is not an additional
9,288-full-parent-reproof claim. No whole representative, unconditional pivot
branch, other-owner generalisation, or Ramsey bound follows.
