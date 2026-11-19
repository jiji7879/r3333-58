
## 24. Final standing on the nine boards, and why size is not the variable

| board | columns | status | method | no-incumbent? |
| --- | ---: | --- | --- | --- |
| live-16 | 12216 | **feasible** | HiGHS incumbent under time limit, 280 s | - |
| local-20 | 8539 | **feasible** | HiGHS OPTIMAL, 521 s | - |
| local-22 | 10800 | **feasible** | HiGHS OPTIMAL, 990 s | - |
| local-24 | 12911 | **feasible** | HiGHS incumbent under time limit, 1001 s | - |
| live-13 | 12110 | **feasible** | HiGHS incumbent under time limit, 2501 s | - |
| fresh-07 | 8619 | OPEN | 5 methods, incl. CDCL 600-980 s, B&B 219 nodes | yes |
| live-02 | 10917 | OPEN | HiGHS, 1001 s and 2501 s | yes |
| local-09 | 18475 | OPEN | HiGHS, 2502 s | yes |
| local-17 | 14050 | OPEN | HiGHS, 2501 s | yes |

All five witnesses were re-verified here against C0-C4 with 0 violations, mass 52, population 26/26.

**Size does not explain the split.** The five feasible boards run from 8,539 to 12,911 columns; the
four open ones run from 8,619 to 18,475. fresh-07 (8,619) is the smallest of the nine and the
hardest - five independent methods found nothing - while local-24 (12,911) was solved. So whatever
separates them is structural in the pin pattern, not computational scale, and a bigger machine would
not change the picture for fresh-07.

**The only remaining question.** Whether any of the four open boards is integer-infeasible, which
would be a new board exclusion. Every one of them returns *no incumbent at all* - not a fractional
one, not an infeasible certificate, nothing - which is what a model with no integer point looks like,
and fresh-07 additionally ran 10^6 conflicts in its CNF encoding without a model. That is a signal
accumulated across five methods, and it is still not a proof. Closing any of them needs either a
long CDCL run with DRAT on a ~3-5M clause instance, or an infeasibility argument for the integer
model itself.

Even if all four fell, the ledger would move from 58/72 to 62/72 and seed 12 would not be one case
closer to closed, because the boards are a sample.
