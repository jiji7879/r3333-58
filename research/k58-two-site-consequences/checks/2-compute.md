# Compute check for ledger entry 2

The working directory was the project root. No SAT/SLS search was launched;
all CDCL statuses discussed are bounded records supplied by the package, not
new search conclusions.

## Input and checker

The ZIP identity and manifest were recomputed from the attached input:

- input `attachments/let-s-try-and-rbdv/K58_two_site_consequences.zip`;
- SHA-256
  `7cb24544a5f8d3afe78e0fb9cc2f7cc3318a87a15a8bbf34af1893b48059e48d`;
- extraction `.scratch/two-site-consequences-v1/src/K58_two_site_consequences`;
- `sha256sum -c SHA256SUMS`: 444/444 entries completed with no mismatches
  (full output `.scratch/two-site-consequences-v1/manifest-verify.log`);
- drat-trim source SHA-256
  `d834b649f437e091597f5347f259b9f681087f89ca0844d0cee250a1a1a0c2ee`.

```sh
cc -std=c99 -D_GNU_SOURCE -O2 tools/drat-trim.c -o drat-trim
```

The Makefile was not used. Each separate run compiled a local binary; checker
binary hashes can differ across builds even when source hash and verdicts match.

## Strict full-package verifier

The complete command sequence of the last fresh run is:

```sh
ROOT="$PWD"
P="$ROOT/.scratch/two-site-consequences-v1/src/K58_two_site_consequences"
D="$ROOT/.scratch/two-site-consequences-v1/supplied-strict-final"
mkdir -p "$D/bin" "$D/tools" "$D/strict-logs" "$D/tmp"
cc -std=c99 -D_GNU_SOURCE -O2 "$P/tools/drat-trim.c" -o "$D/bin/drat-trim"
cp "$ROOT/.scratch/two-site-consequences-v1/tools/strict-drat-wrap.py" "$D/tools/strict-drat-wrap.py"
chmod +x "$D/tools/strict-drat-wrap.py"
export AUDIT_ROOT="$D"
export AUDIT_REAL_DRAT_TRIM="$D/bin/drat-trim"
export TMPDIR="$D/tmp"
cd "$P"
python3 -B "$P/verify.py" "$D/tools/strict-drat-wrap.py" > "$D/verify.out"
```

Exit status was 0, and this was a completed run, not interleaved partial output:

```text
47 owners {'LIVE': 11, 'LOCAL': 33, 'DEAD': 3}
ordinary-row replays 66
K58 pair search [(0, {'OPEN': 25}), (3, {'OPEN': 30})]
Full signature search [(0, {'OPEN': 7, 'CLOSED': 1}), (3, {'OPEN': 17, 'CLOSED': 11})]
Witness pairs and conditional recolouring proofs verified.
```

All **196/196** checker calls were accepted by the strict proxy, with exit 0
and exactly one `s VERIFIED` after removal of `-w`. Checker time was
**40.61196473101154 s**. The raw stdout-independent summary, with all 196
query/proof hashes, is [2-supplied-verify.json](2-supplied-verify.json).
The proxy source is retained as [strict-replay-proxy.py](strict-replay-proxy.py).
It never accepts a `s VERIFIED` that carries a warning.

## Repaired twelve-case replay

Source `.ultramath/smwze4dpo/m2/replay12.py` was read, then executed in a fresh
isolated output directory. It was not rerun in its member's working directory.

```sh
ROOT="$PWD"
S="$ROOT/.scratch/two-site-consequences-v1/src/K58_two_site_consequences"
D="$ROOT/.scratch/two-site-consequences-v1/strict-m2-review"
mkdir -p "$D"
cc -std=c99 -D_GNU_SOURCE -O2 "$S/tools/drat-trim.c" -o "$D/drat-trim"
cd "$D"
python3 -B "$ROOT/.ultramath/smwze4dpo/m2/replay12.py" "$S" "$D/drat-trim" > replay12.out
python3 -B "$ROOT/.ultramath/smwze4dpo/m2/crossbranch.py" "$S" "$D/drat-trim" > crossbranch.out
```

Both exited 0. Results:

- **286 checks, zero failures**;
- complete projection for each pivot: **24,686 clauses = 19,485 edge-only +
  5,201 owner/auxiliary clauses**, using 831 auxiliaries;
- all 36 local signature witnesses satisfy the full projection, not just the
  19,485-clause physical subset; maximum measured colour-degree is 15;
- all 12 `search` and 12 pivot-free `unsplit` replays pass without warnings,
  with full proof bytes read and no RAT lemmas in core;
- the two exact signature block covers pass, of proof sizes 38,378 and 61,530
  decompressed bytes;
- all eight two-example/four-pivot-colour cross-branch replays pass;
- SAT-query, cross-case and 60-percent-truncation controls reject;
- corrupted proof plus junk gives an exact verified line with a warning and is
  rejected by the strict gate; the `-w` style accepts it.

The fresh receipt disagrees with the member's receipt only in the local
checker path and binary hash. Cross-branch receipts are byte-identical.
Case query/proof hashes are saved in [2-closure-receipts.json](2-closure-receipts.json).

## Independent finite recomputation (new source)

The separate checker [recompute.py](recompute.py) rebuilds actual signed graph
clauses, owner parents/guard units, local projections and word tables; it
performs no SAT search. Its last completed invocation was:

```sh
python3 -B research/k58-two-site-consequences/checks/recompute.py \
  .scratch/two-site-consequences-v1/src/K58_two_site_consequences \
  .scratch/two-site-consequences-v1/strict-m2-review/drat-trim \
  research/k58-two-site-consequences/checks/2-compute.json \
  .scratch/two-site-consequences-v1/strict-m2-review/receipts/replay12.json \
  > research/k58-two-site-consequences/checks/recompute.out
```

Exit status 0; receipt [2-compute.json](2-compute.json). Coverage:

- **3,701 assertions pass, 42 strict DRAT calls pass**;
- all 444 manifest entries;
- actual 1653/9918/123424 K58 constraint families, and all 47 parent identity
  and guard-unit relationships;
- 315 signature/control local witnesses over all eight tables;
- 157 owner/lattice local witnesses;
- branch 0/3 has 31/34 clauses beyond the signed parent, not just pivot units;
- 24,686 complete projection clauses for either pivot signature;
- the 57/36 untriggered and 8/28 triggered word sets, and 29/0 intersections;
- 17 owner/antecedent-impossibility proofs and 14 minimal subset proofs;
- eight local table block-cover proofs;
- the exact two branch residuals and unsplit 24-word frontier (three more
  proof replays).

The independent subset derivation gives six live two-site minima
`3,5,7,19,23,32`, five live three-pin minima `0,11,12,24,25`, and three
impossible antecedents `14,31,36`. Its output names **OPEN**, not SAT, for the
remaining 7+17 words.

## Corrected semantic rerun

The updated m4 source was executed with `K58_PKG` set to the read-only package
and `K58_OUT` set to a new `.scratch/two-site-consequences-v1/semantic-review-v2`.
The same drat-trim compiler command above was used. `s1_reconstruct.py`,
`s2_projection.py`, `s3_replay.py`, `s4_sub.py`, `s5_structure.py` and
`s7_containment.py` completed successfully. In particular:

- every owner parent and the two principal bases have exactly all
  1653/9918/123424 signed constraint clauses;
- V30 has 435/2610/16240 and all 157 witnesses have zero errors;
- all 17 owner and 17 subset replays pass, no warnings;
- `uncovered=[]`, `core_mismatch=[]`, all 47 owner cubes are units of their
  **own signed parent**, not `row-0`;
- row-0's 19,454-clause projection is contained in every owner projection;
- word mapping controls reject reversal, rotation, all-zero and colour swap.

Timing-only fields aside, the semantic receipts agree with the member's. The
member's auxiliary s6/s8 detail receipts are not needed for that agreement:
the decisive signed axiom checks and projection relationships are covered by
s1/s2/s5/s7 and independently by `recompute.py`.

The first m4 scripts had positive rather than negative AMO/triangle clauses
and inspected owner cubes against the wrong base. Their bad diagnostics were
rejected, not concealed. The newer output corrects those specific defects.
The original package is unaffected by these audit-script bugs.

## Source regeneration

[regenerate_owners.py](regenerate_owners.py) uses the restored audited campaign,
without writing in it or invoking its solver:

```sh
.scratch/k58/.venv/bin/python -B \
  research/k58-two-site-consequences/checks/regenerate_owners.py \
  .scratch/review-attachments-v1/audited-K58 \
  .scratch/two-site-consequences-v1/src/K58_two_site_consequences \
  research/k58-two-site-consequences/checks/owner-regeneration.json
```

The standard `python3` on PATH lacks `pysat` in this session; that first
invocation failed with `ModuleNotFoundError` before export. The command above
uses the existing pinned `pysat 1.9.dev22` environment and exits 0:
**47 regenerated, 47 distinct parents, all parent formula hashes and all owner
cubes match, zero solver calls**. JSON arrays of word pairs are converted
back to Python tuples before calling the source's queue guard.
Receipt: [owner-regeneration.json](owner-regeneration.json).

## Model-independent artifacts, limitations

No kernel-level Lean check exists for these software-generated proofs because
this task supplies the original CNF/DRAT artifacts rather than a Lean
statement. No Lean formalisation was started inside this check. No full-parent
SAT model was found, none of the 24 OPEN words was searched further, and no
production files were mutated. The complete legacy event-proof byte store was
not supplied and those missing proofs were not counted as replayed evidence.
