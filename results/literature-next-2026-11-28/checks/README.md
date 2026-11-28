# Checks

Only small Python/text checks and receipts are stored here; no compiled binaries,
archive or proof file is included. These are the accepted check scripts copied
from the reviewed members, including the unchanged counter-equivalence audit.
`check_catalogues.py` retains its explicit pinned-upstream path, as required for
byte-level comparison of the two generators.

The direct reproductions preserve the source provenance of each control, not
historical timing. Current large `DRAT`/LRAT files remain outside Git under
`.ultramath/`, which is deliberately ignored. No new solver build was done.

Useful runs from the repository root (where the baseline `.venv` exists):

```sh
.scratch/k58/.venv/bin/python results/literature-next-2026-11-28/checks/audit_candidates.py
.scratch/k58/.venv/bin/python results/literature-next-2026-11-28/checks/counter_specs.py
.scratch/k58/.venv/bin/python results/literature-next-2026-11-28/checks/symmetry_fit.py --full-cnf
.scratch/k58/.venv/bin/python results/literature-next-2026-11-28/checks/pair_support_check.py
python3 results/literature-next-2026-11-28/checks/fit_checks.py
python3 results/literature-next-2026-11-28/checks/check_catalogues.py
```

The two field and Schur scripts use only Python's standard library:
`cyclotomic_f49_control.py` enumerates its seed directly; `toeplitz_schur_control.py`
emits its direct constraint CNF, not an old wall formula. See the accepted detailed
memos for proof provenance and the historical external checks.

`schur-default.log` is the successful independent **default DRAT** replay against
the exact identified CNF. `schur-normalized-timeout.log` is a separate 60-second
unresolved warning-fatal run after valid deletion-only normalization. The latter
is not a certificate. The structural Toeplitz exclusion does not depend on it.
