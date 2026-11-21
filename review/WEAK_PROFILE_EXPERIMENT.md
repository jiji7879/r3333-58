# The one-critical profiles do not close

Experiment on `(15,14,14,14)` and `(16,14,14,13)` — 469 cases, the profiles where
the ticket argument is weakest. Run on this machine with the pinned Kissat 4.0.4.

## Result: 0 of 51

| run | cases | budget | closed | mean CPU |
| --- | ---: | --- | ---: | ---: |
| Kissat, random sample | 42 | 60 s / 2.4M conflicts | **0** | 59.3 s |
| Kissat, random sample | 9 | 300 s / 12M conflicts | **0** | 299.9 s |
| CaDiCaL 2.1.2 | 1 | 120 s | **0** (UNKNOWN) | 120 s |

Every case consumed its entire budget: the 60 s run has median CPU 60.0 s, the
300 s run 299.9 s. There is no fast tail — this is a wall, not a bad sample.

## Why: these cases barely constrain anything

| profile | unit clauses | edges pinned |
| --- | ---: | ---: |
| `(15,14,14,14)` | 309 | 4.0% |
| `(16,14,14,13)` | 324 | 4.3% |
| `(15,15,14,13)` | 408 | 5.5% |
| `(15,15,15,12)` | 503 | 7.0% |
| `(16,15,15,11)` | 518 | 7.2% |

The percentages differ by less than a factor of two, so the count alone does not
explain 77% closure on the large profiles against 0% here. The structure does:
a three-critical case puts **three** 15-vertex blocks into rigid classified
templates, so 45 of 57 vertices sit in rigid configurations. A one-critical case
pins **one** such block and leaves 42 vertices free.

Refuting a `(15,14,14,14)` case therefore means proving that no triangle-free
4-colouring of `K_58` carries a single rigid 15-block with a sending vertex —
which is very nearly the original problem. The cover's ticket argument reduces
the large profiles to tractable searches and this profile to almost nothing.

## Second finding: hard cases emit enormous proofs

CaDiCaL produced a **644 MB DRAT proof in 120 s** on one of these cases before
returning UNKNOWN. Proof output runs at roughly 5 MB/s on a failing search, so
any of these cases that does close at a multi-minute budget will leave a
certificate of hundreds of MB or more, and checking it with drat-trim is then
the bottleneck.

This explains an incident in the live campaign: a `(15,15,15,12)` retry case
occupied drat-trim for **9 h 08 m** without finishing, against drat-trim's
default 40000-second limit. It was not a hang; it was a very large proof. The
checker now runs with `-t 300` and a failed check leaves the case OPEN
(`tools/patch_run_cover_timeout.py`).

## Consequence

The campaign's remaining 31,771 open cases split into two kinds:

* ~20,150 in `(15,15,15,12)`, which close at 77% and cost time, not thought;
* **12,054 that will not fall to brute force**: the 469 one-critical cases and
  the 11,585 in the other small profiles, all of which pin one or two blocks at
  most.

For those, the prediction is that more compute does not help — 5× the budget
here moved nothing. What the K60 proof did in this situation was to stop using
local ticket bounds and adopt a *structural* dichotomy (its C1/C2 entrance and
perfect-balance analysis). The analogous question here is what a root with only
one critical colour forces globally, and that is a research question rather than
a scheduling one.

## Reproduce

```sh
python3 tools/solve_weak.py --bundle K58 --out work --kissat bin/kissat \
    --workers 3 --seconds 60 --limit 42 --shuffle 7 --full-root
```
