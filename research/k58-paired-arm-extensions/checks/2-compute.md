# Commands and computation evidence

## Input and integrity

```sh
sha256sum attachments/let-s-try-and-rbdv/K58_paired_arm_rule_extensions.zip
```

Result:
`01b80535b4bee450b8d5cd0b888502816d4e6071f27037be02798fd5877628e8`.
All 121 ZIP members passed CRC validation. The `hard-study/geometry.json`
bytes are identical to those in the preceding paired-arm package. Fresh
`hard-study/audit.json` regeneration again gives
`{'full_root': 1300}` hash matches, 48 template-colour combinations and
32,768 exhaustively checked binary K6 colourings. That is input identity, not
replay of the recorded 191 GB historical proof set, which remains unavailable.

`Paired_arm_rules.md`, `join.py`, `wider.py`, `signed.py`, `check_supports.py`,
`replay.py`, `widereplay.py`, `widecheck.py`, `screen.py`, `same.py`, relevant
`probe.py`, `dense.py` and encoder helpers were read before execution. Solver
performance reporters (`bench.py`, `widebench.py`) were inspected, but their
fixed-seed searches were not retimed.

The pinned existing `.scratch/k58/.venv/bin/python` supplies python-sat
`1.9.dev22`, as required by `hard-study/setup.sh`. No install was needed and
`setup.sh` itself was not run.

## Regenerating entire datasets and propagation panels

A separate working copy `.scratch/hard1300-paired-arm-ext-v1/reproduction`
was created because output paths in the supplied scripts overwrite JSON reports.
No source archive artifacts were modified.

```sh
ROOT="$PWD"
P="$ROOT/.scratch/hard1300-paired-arm-ext-v1/src"
D="$ROOT/.scratch/hard1300-paired-arm-ext-v1/reproduction"
mkdir -p "$D"
cp -a "$P/." "$D/"
PY="$ROOT/.scratch/k58/.venv/bin/python"
cd "$D"
"$PY" -B hard-more/wider.py > regeneration-wider.out
"$PY" -B hard-more/signed.py > regeneration-signed.out
"$PY" -B hard-more/join.py > regeneration-join.out
"$PY" -B hard-study/check.py > hard-study/audit-run.out
"$PY" -B hard-more/screen.py > regeneration-screen.out
"$PY" -B hard-more/check_supports.py > hard-more/check-supports.out
"$PY" -B hard-more/widecheck.py > regeneration-widecheck.out
```

`wider.json.gz`, `signed.json.gz`, `rules.json.gz` and `same.json.gz` all
reproduce **identical decompressed JSON** to the supplied artifacts. The
computed totals are 176,136 four-literal clauses, 26,224 mixed signed and
10,136 double-negative signed. Every one of the 1,300 wider lists is nonempty.
The standalone `join` log reports `plain=0`, `joint=0`, `new=0`; the `same`
lookup returns 1,300 empty lists.

`screen.json` matches exactly and records zero residual cases in each listed
signed screen. Independently invoking `widecheck.py` reproduces all thirteen
panel objects:

```text
rows 13
four_literal_candidates 1747
survivors_after_ternary 1747
survivors_after_direct 939
panel objects equal_supplied: True
```

These counts do not mean those candidates complete as SAT or UNSAT. They are
false-cube propagation survivors: exactly the cases that still require search.

All thirteen independent support cases and their `[6,1]`-style finite numbers
are retained in `check-supports.out`. The representative rank-340 case has
`[2,1]` instead of `[6,1]`, so its different multiplicity was not silently
replaced with a generic witness.

## Native replay and why the first gate failed

```sh
cc -std=c99 -D_GNU_SOURCE -O2 "$P/hard-study/tools/drat-trim.c" \
  -o "$D/bin/drat-trim"
```

The supplied replay tools were initially given the strict proxy from the first
audit (remove `-w`, exact legitimate status, no warning). On the earliest raw
positive proof the checker itself writes warning lines such as
`backward mode ignores deletion of (pseudo) unit clause [0]`, while returning
0 and emitting `s VERIFIED`. This caused the strict call to abort rather than
silently reward the stock `-w` loop. The partial batch deliberately recorded
two example failure receipts instead of claiming all 16 passed unchanged.

The complete strict repair then ran:

```sh
"$ROOT/.scratch/k58/.venv/bin/python" -B \
  research/k58-paired-arm-extensions/checks/repair_replay.py \
  .scratch/hard1300-paired-arm-ext-v1/src \
  .scratch/hard1300-paired-arm-ext-v1/strict-replay/bin/drat-trim \
  .scratch/hard1300-paired-arm-ext-v1/clean-replay \
  research/k58-paired-arm-extensions/checks/strict-clean-replay.json
```

This accepted all **16** example obligations. Each one uses a fresh query
`parent + negated(clause)` that hashes to the retained metadata's `query`, and
preserves **both** original and normalised proof hashes. The checker flags are
`-i -U -W -t 600`: RUP-only and warning-fatal, never `-w`. It fully consumes
every generated-normalised stream and reports `0 RAT lemmas in core`.

Total original proof bytes = **431,370**; total normalised bytes = **263,222**.
Only deletion records are removed, so the original addition clause set is not
weakened. The inputs and original files are never rewritten.

The README shell `python3` could not import `pysat` on this VM, so the original
pinned environment was used consistently. It was not confused with an
unverified generic system interpreter. A small initial path-selection failure
in the regeneration job was fixed by using `hard-study/check.py` rather than
`check.py`; the reported results come only from the completed corrected calls.
No result from aborted partial output was accepted as a completed sweep.

## Performance and escalation boundary

`benchmark.json` and `wide-benchmark.json` were read in full. Every supplied
native `result` is `null` for all six rows and both reported policies at 60,000
conflicts. These files were not regenerated, because a repeat performance
experiment is not needed to establish the clause identities or validity. Their
CPU figures and the long-run limits are supplied metadata, not a certified
speed-up nor a measurement by this reviewer.

No further Ultramath members, production sweeps, new SAT budgets, standalone
Lean theorems or repository archives were created. The generated endpoint is a
scoped mathematical/certificate audit plus small reproducibility files, not a
replacement for the original proof package or a claim of an easier uniform
wall closure.
