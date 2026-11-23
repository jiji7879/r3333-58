# The generated replay tree: `K58.Replay.frozenCover`

`K58.Replay.frozenCover : K58.FrozenCover` is the unconditional form of the cover
object: the 113,179 frozen case keys are realized by the raw cover and the
transports.  It is *not* a statement that any case is refuted — ruling out the
frozen cases is a separate project.

## What is in this directory

| file | what it is |
| --- | --- |
| `generate_replay.py` | emits the 1,588 `ReplayGen/` modules from the handoff ZIP and the transport certificate; it checks the input rows (omitted, extra and duplicate rows are errors) |
| `placement-transports.jsonl.gz` | the transport certificate (500 KB): every complete placement family attached to a frozen key |
| `run_replay.py` | compiles the generated dependency graph, caching only successful modules (source, dependency and output hashes); `--plan N` restricts to one plan |
| `check_build.py` | checks `Check.lean`'s declaration list against a build log and rejects `sorry`, `admit`, `native_decide` and `sorryAx` anywhere in `K58/*.lean` |
| `build-catalogue.sh` | fetches the pinned upstream (`milostatarevic/r3333-upper-bound` at `6c3f2fd0386335321801fa4079397d4a4c1962f3`, the source of the T/U classification) and applies `catalogue-4.33.1.patch` so it builds against Lean 4.33.1 |

## How it is built

```sh
# once, in lean/: the upstream catalogue (network, ~150 MB, needs a Lean 4.33.1 Mathlib)
bash replay/build-catalogue.sh

# the K58 library (order.txt is the topological order of the import edges)
bash build.sh

# the generated tree; ReplayGen/ is a build artefact and is gitignored
python3 replay/generate_replay.py . \
    /path/to/R3333_K58_LLM_handoff.zip \
    replay/placement-transports.jsonl.gz ReplayGen
python3 replay/run_replay.py . . --jobs 2      # or: bash build.sh --replay
```

`run_replay.py` prints the axiom dependencies of `K58.Replay.rawTransportCover`
and `K58.Replay.frozenCover`; a zero exit from the full replay is what establishes
both.  The generation step needs `python-sat`; the archived replay sources can be
checked without it.

## Provenance

The bundle is `attachments/let-s-try-and-wcbj/R3333_K58_Lean_gluing_and_transport.zip`.
It was verified here on 2026-11-22 at its own base commit `e62d8ab` (all 1,588
modules recompiled with every `.stamp` deleted, exit 0).  The landing onto this
tree is recorded in `review/LANDING_GLUE.md`, including what changed and what was
re-measured rather than inherited.
