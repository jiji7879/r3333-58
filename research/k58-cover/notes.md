# K58 cover: notes and measurements

1. Ledger: `ledger.md` in this folder. State of the campaign as of 21 November 2026.
2. Profile counts (from `tools/ledger_state.py`): 79,264 CERTIFIED, 20 SPLIT_CERTIFIED,
   1,743 LEGACY_HISTORICAL, 401 LEGACY_EXCLUSION, 31,751 OPEN, 113,179 total.
3. Weak-profile measurement: `runs/2026-11-21-two-critical-probe/README.md` (0/68 at
   the retry budget) and `review/WEAK_PROFILE_EXPERIMENT.md` (0/51 on the one-critical pair).
4. The 31,751 open rows: 20,166 in `(15,15,15,12)` (throughput), 11,585 in the seven
   weak profiles (no known method), 20 in `(16,15,15,11)` (split certificates, bookkeeping).
