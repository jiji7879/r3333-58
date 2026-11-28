# Duggan paper method review evidence

See [the main assessment](../../review/DUGGAN_PAPER_ASSESSMENT.md).
The baseline is `dist/k58-massive-solver.zip` (SHA-256 `cc78f1d9f6f7901615b264c9ceaa3319bd152cd4caccc381a74ed742538bdb6a`).
**No bound, wall row or profile moved.**

All eight directions of `smwzxq4fl` were accepted after independent replay:

| result | report and compact evidence |
| --- | --- |
| exact gray-edge compression of critical links is impossible | [LINK_SATURATION.md](LINK_SATURATION.md), [witnesses](saturation/witnesses.tsv) |
| preferred-full-vertex catalogue method guarantees no full vertex at $K_{58}$ | [full-vertex](full-vertex/ASSESSMENT.md) |
| boundary-only conditional counter encoding | [guarded-counter](guarded-counter/assessment.md) and [actual audit](guarded-counter/audit.json) |
| vacuous historical lex comparator; corrected negative pilot | [symmetry report](symmetry/work/duggan-symmetry-assessment.md) and [evidence](symmetry/work/evidence.json) |
| unit/zebra soft-constraint implementation and negative $K_{51}$ pilots | [soft-constraints](soft-constraints/ASSESSMENT.md) |
| native counter/support-selector Lean extension lemmas | [encoder-extensions](encoder-extensions/REPORT.md) |
| full/pinned MCF negative assessment, star-degree lemma and closure witnesses | [maximality](maximality/assessment.md) |

Coordinator configurable-edge MCF normal form:
`../../tools/duggan/maximal_normal_form.py`; [small controls](maximal-selftest.json),
[build receipt](maximal-build.json), [matched solver statistics](maximal-comparison.jsonl).

The upstream MCTS assessment is in [mcts/ASSESSMENT.md](mcts/ASSESSMENT.md).
The direct 2024 cuber has an incompatible prior/action layout; current generic
MCTS generated an exact five-leaf OPEN wall frontier. On the completed control,
full rollout cost 306.456 s cubing versus 0.720 s greedy and 284,528 versus
226,881 conflicts. Eleven second-checker replays passed; my separate strict
replays are [here](mcts/replay-control.json). All original open-wall leaves and
both optional re-cubed descendants remained OPEN.

The full integrated `lean/build.sh` log is [here](lean-build-integrated.log).
The three accepted new Lean modules are also registered in `lean/K58/Check.lean`.

These directories contain research evidence and small controls, not a new
production CNF package or proof store. Reports that mention original member
paths preserve the provenance used for independent replay. Any OPEN result is
undecided; none of these pilots is a Ramsey nonexistence proof.
