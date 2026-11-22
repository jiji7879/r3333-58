# Does adding an implied constraint help the cover solver? No — it hurts, 3× over

Motivation: the cover's per-case CNF (`gluing.host(58)` + `units`) is bare — one
colour per edge, triangle-freeness, and the ~300 pin units: 6,612 variables,
135,319 clauses. Nothing else. So every consequence of triangle-freeness is
re-derived by the solver on every case, and the mean first-pass DRAT is 5.58 MB.
Question: do implied constraints such as the degree cap `d_c(v) <= 16`
(`R(3,3,3) = 17`) pay for themselves?

**Answer: no.** Same cases, same solver (kissat 4.0.4), same budgets, with and
without the degree cap as 232 sequential-counter cardinality constraints
(58 vertices x 4 colours, at most 16 of 57):

| run | cases | result | mean wall | mean DRAT |
| --- | ---: | --- | ---: | ---: |
| baseline | 6 | all UNSAT | 1.97 s | **7.66 MB** |
| + degree cap | 6 | all UNSAT | 5.83 s | **20.43 MB** |

The extra constraint costs 152,192 auxiliary variables and 310,184 clauses
(445,697 total against 135,513), and it nearly triples both the solve time and
the proof. The six cases are `16,15,15,11`, indices 0-5, at 400 k conflicts / 60 s;
every one closes in both arms, so this is a like-for-like comparison.

**On hard cases it is worse still.** Two OPEN cases from `16,14,14,13`, 60 s each:

| case | baseline conflicts | + degree cap conflicts |
| --- | ---: | ---: |
| 0 | 2,620,855 | 1,111,083 |
| 1 | 2,782,633 | 1,258,257 |

Both arms UNKNOWN, and the constrained arm reaches **less than half the
conflicts** in the same wall time: the auxiliary structure slows every conflict.

**Conclusion.** Leave the case CNFs bare. The bare host-plus-pins encoding is not
a shortcut that pays for itself later — it is the better encoding, on both axes
that matter here (time and stored proof). Implied constraints with an auxiliary
variable footprint are a liability for this campaign, whatever their logical
strength, because the proof has to work through them too.

*Caveat.* This tests one family (a degree cap encoded as cardinality). It says
nothing about cheap implied clauses with no auxiliary variables, which were not
tried here.

Rerun: `exp.py <profile> <indices> <conflicts> <secs>` and `hard.py`, both with
`.scratch/k58/.venv/bin/python`.
