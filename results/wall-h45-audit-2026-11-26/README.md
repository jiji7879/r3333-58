# Audit of the K58 contact-bound and H4/H5 packages

## Conclusion

**Useful.** The attachments provide a new, independently replayable local
refinement of the wall, with a useful whole-row cut for `0404`. They do **not**
close a frozen row or establish $R_4(3)\le58$.

The distinctive progress is the reverse contact bound:

| Profile | Reverse H >= 6 directions | Reverse H >= 7 directions |
| --- | ---: | ---: |
| `(16,15,14,12)` | 38 | 0 |
| `(16,15,13,13)` | 19 | 0 |
| `(16,16,13,12)` | 18 | 1 |
| `(16,16,14,11)` | 18 | 1 |
| **Total** | **93** | **2** |

The exceptional pairs are

- `0404c3a224626a202cbfa4355bb0b19513ec815d182050440c580208861f2296`, and
- `8f9f3644c15b423945ba11e778540f6cf6234d095e7493ed24dd537f1c8db31a`.

They are both branch 48, but in the two different profiles. The normalized
signed 42-vertex three-arm input is shared between them. Across the 93 rows,
the local subproblems have 41 vertices on 33 rows, 42 on 52 and 43 on 8.

Here **H is a site count**: a site is high when it has at least two further
marked-colour edges into the opposite target arm, beyond the distinguished
contact. It is **not** the root ticket quantity `H(r)` used by the earlier
frozen-row reductions. Do not insert the number 6 or 7 into those ticket/budget
formulas.

## Checks actually run

### Exact H4

I built the pinned environment with python-sat **1.9.dev22**, compiled the
supplied DRAT checker from source, and ran both H4 verifiers and the merge:

```sh
K58_wall_sweep/.venv/bin/python K58_wall_H4/boundary.py \
  K58_wall_sweep K58_wall_H4/results --verify --jobs 2
K58_wall_sweep/.venv/bin/python K58_wall_H4/boundary.py \
  K58_wall_sweep K58_wall_H4/followup --prior K58_wall_H4/results \
  --top 93 --per-mask 20000 --row-budget 170000 --verify --jobs 2
K58_wall_sweep/.venv/bin/python K58_wall_H4/merge_results.py \
  K58_wall_sweep K58_wall_H4 --verify
```

The self-check logs are `h4-verify.log`, `main-setup.log` and `h5-setup.log`.
Times were **33.27 s** for the first pass, **48.63 s** for the second, and
**0.93 s** for the merge.

- First pass: 3,319 refuted assignments.
- Second pass: 3,656 further assignments.
- Merge: **6,975/6,975 refuted**, **0 open**, on 93 directions.
- Separately read `H4-patterns.tsv.gz`: 6,975 rows, all `REFUTED`, with 75
  distinct assignments for each of the 93 IDs. The passage list and proof files
  are present for all 93 second-pass jobs.

The merge verifies the arguments of group proofs, not only receipts: it rebuilds
the low-site-compatible selector layer and the disjunction actually refuted,
and rejects overlapping candidates, dropped candidates, and unresolved patterns.
The classifier and full-subset coverage code checks 65,536 labelled subsets per
source template, positive/negative cover separation, maximal positive and
minimal negative sets.

### H5 local and H6 continuations

The complete compact command

```sh
bash verify.sh 2
```

finished successfully in **729.79 seconds** (`h5-verify.log`). It checked source
hashes, word catalogs and native local proofs, the eleven-low local floor,
exact-H5 transport, the two H6 controls, signed matching across the roster, the
three 170,000-conflict OPEN receipts, and the regenerated ledger and tables.

| Layer or transport | Independently tallied result |
| --- | ---: |
| Complete eleven-low patterns | 6,975 |
| Complete H5 labeled patterns | 51,615 |
| Complete H6 patterns on the two special rows | 4,830 |
| Eleven-low destination replays | 930 |
| H5 destination replays | 930 |
| H6 destination replays (10 per special row) | 20 |
| Distinct normalized three-arm inputs at H5 | 56 |
| H5 representative queries across the inputs | 3,528 |
| H5 representative queries per input | 63 |
| H6 representative queries on the shared 42-vertex input | 253 |
| New signed matches beyond the existing 93-row queue | 0 |

The verifier reconstructs selectors and signed pinned units for each destination,
checks that source-template automorphisms preserve the center and all required
pins, pulls back the physical high sites, and replays against the reconstructed
query. It does not assume that GLUing unlabelled isomorphism classes is safe.
The positive/negative local-word tables are also rechecked rather than allowing
a refutation of an accidentally empty problem to stand in for a template
classification.

The attached `direction-bounds.tsv.gz` and the file checked inside the H5 archive
are **byte-for-byte identical after decompression**. Independent CSV reading
confirmed all 93 directions at H>=6 and the two at H>=7, all
`h4_refuted = h4_candidates = 75`, `h4_open = 0`,
`h5_candidates = h5_refuted = 555` for those directions, and
`h6_candidates = h6_refuted = 2415` for the two exceptions. The per-profile
counts agree exactly with the report.

### Broader transfer and model audit

The full supplied main verifier completed successfully in **143.626 seconds**
(`main-verify.log`). It checked row/geometry bindings, all retained refutations
and saved local models, and the following stored totals:

- 11,585 wall rows and 22,737 eligible directions;
- 4,814 rows with some positive bound in the initial campaign;
- 1,152 rows with a bound beyond the two-template local floor;
- 66 independently verified donor proofs;
- **803** independently replayed destination transfers;
- 777 directions of five-vertex exterior transport reaching 556 rows;
- 189 native certified classifier queries over 42 catalogs/catalog-style inputs.

This was verification of the supplied bundle. It was not an independent repeat
of all 11,585 capped whole-row searches and does not promote any capped search
to UNSAT. The initial sweeps and the final 21 stronger whole-row trials all
remain OPEN. The compact H5/H6 proof is useful as structure, not as a solver
speed measurement.

### A fresh proof replay and mutation/control checks

I rebuilt one shared H6 query for all 253 representative masks and replayed its
6,502,872-byte binary DRAT with the project's existing checker:
`s VERIFIED`. Stale proof-hash binding rejects an altered proof.

Native replay, however, is **not a canonical byte-for-byte proof
authenticator**. The checker stops accepting after it has established the
necessary contradiction; it can ignore trailing content. My explicit mutations
had the following actual results:

| Mutation, with matching receipt hash supplied | Outcome |
| --- | --- |
| Valid original binary DRAT | ACCEPTED |
| Appended invalid text after the proof | ACCEPTED (trailing bytes ignored) |
| Rightmost two bytes removed | ACCEPTED (remaining valid proof prefix still closes) |
| Half-length truncation | REJECTED |

These are recorded in `proof-corruption.json`. They do **not** contradict the
valid proof. They mean a tamper test must distinguish semantic proof replay from
canonical byte authentication. The source package's hash list, query digest,
proof digest and proof completeness all matter. It would be wrong to advertise
that every changed proof byte is rejected.

## Export that is ready to inspect and use

`dist/k58-0404-forward11-reverse7.cnf.gz` was regenerated through the supplied
exporter with `--prior-0404`. It preserves the supplied historical checkpoint's
body byte-for-byte, adds the physical high-site/counting clauses, and recreates
the whole-row H7 query. The historic compressed input is checked by SHA-256,
and a deliberately altered checkpoint was rejected.

| Property | Historic checkpoint | New export |
| --- | ---: | ---: |
| Declared variables | 20,389 | 20,536 |
| Declared clauses | 223,603 | 225,915 |

Its raw, decompressed SHA-256 is

```
70881fa4b499354fbee6f1fdf047d733eba33cf2e9011b36c7719845fe29e62b
```

That exactly matches the supplied H7 whole-row query receipt. It is not a new
DRAT closure: that parent reached **170,003 conflicts** and remained **OPEN**.
The comparable supplied queries at reverse floors 5 and 6 also remained open
at their 170,000-conflict limits. `export-0404.log` and `export-0404.json` record
the rebuild, body preservation, clause parsing and exact receipt match.

The historical forward $H\ge11$ is used as an explicitly hash-pinned prior
checkpoint. I did not independently rerun its original proof here. The new
local certificate establishes the reverse H=6 layer empty, hence reverse
$H\ge7$, for the two rows. The non-historic exporter sets
`tables=True,total_critical=True,full_root=False`: there is no blanket perfect
balance assumption. The prior mode instead treats the supplied historical body
as a pinned artifact, not a newly re-derived semantic certificate.

## Frontend compatibility

I also passed the resulting **gzipped** parent through the current
`tools/selfcontained/wallcc/wallcc.py` frontend, at depth 0, with a
10,000-conflict budget. The plan and the verification run both report
`source_sha256 = parent_sha256 = 70881fa4…`. The parent-only leaf returned
**OPEN at 10,001 conflicts in 0.621 seconds**. This is a compatibility check,
not a matched speed comparison.

The verifier reported `{"counts":{"OPEN":1},"processed":1,"status":"OPEN"}` and
returned its documented nonzero status for an incomplete cover. The parent and
plan hashes were unchanged, and no DRAT export was attempted or claimed. See
`frontend-0404.log`, `frontend-0404-verify.log`, `frontend-plan.json` and
`frontend-receipt.json`.

For clients that prefer uncompressed input,
`dist/k58-0404-forward11-reverse7.cnf` has exactly the same decompressed
contents and SHA-256 as the `.cnf.gz` version. Its header is also
`p cnf 20536 225915`.

## What is most useful next

1. **Adopt the directional bound as an explicit, hypothesis-scoped input**, not
   as a hidden new global degree cap. For `0404`, the bound uses all omitted
   critical-arm neighbors and their signed units. Other branches of those two
   physical rows can inherit it, but an arbitrary new parent must regenerate the
   exact signed local input; removing frozen pins is not generally licensed.
2. **Preserve the source of proof**: local normalized spec, selector list,
   canonical physical high sites, source automorphism, query SHA-256 and proof
   SHA-256. A bare `.cnf` with auxiliary high flags is not enough provenance.
3. **Reuse the three-arm/symmetry reduction.** On the H5 queue it used 1,061,102
   local conflicts versus 11,449,625 for the full-row searches in the report.
   That is a search-effort comparison between two proof searches, not a guarantee
   that the appended H-floor on an arbitrary wall CNF accelerates a new solver.
4. If more work is authorized, the recorded frontier is
   - remaining reverse H=6: 91 rows, 219,765 masks in 23,023 row/orbit pairs;
   - remaining reverse H=7: two rows, 10,910 masks in 1,158 row/orbit pairs.

   Their shared 42-vertex H6 input has 253 distinct representatives. A full
   execution of that next frontier was **not** run in this audit.

An integration attempt should use the verified parent and a small bounded
comparison, retaining its identity and label OPEN if its budget is met. It
should not use the bounded compatibility test as evidence of wall closure or
claim an automatic speedup. Any Lean-level adoption also needs the explicit
embedding theorem from the local three-arm restriction back to the physical
row; the Python replay alone does not supply that central formal bridge.

## Missing or intentionally unperformed work

- The optional `verify-full.sh` full-row DRAT replay was **not run**: the
  `SHA256-FULL-*` parts and `first`/`second` full-search proof trees it expects
  are absent from the supplied H5 ZIP. The compact local replay, which is the
  mechanism needed for the new directional floor, is present and passed.
- No new full search over the remaining 91 six-high or two seven-high frontiers
  was launched.
- The original outside forward-$H\ge11$ proof was not re-derived from its
  external historical checkpoint.
- No case is newly excluded from the wall, and no previously open target row was
  closed. All 18 repaired rows of `(16,16,13,12)` are just directions receiving
  a stronger contact bound, not a profile-wide elimination.
- No further work on `(15,14,14,14)` is proposed here. The new-bound integration
  targets are within the four in-scope profiles shown above.
