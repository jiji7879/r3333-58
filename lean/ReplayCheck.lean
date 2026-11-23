/-
The audit of the generated replay tree.  Separate from `K58/Check.lean` because it
needs `ReplayGen/`, which is a build artefact (see `replay/README.md`); `build.sh`
compiles it only in the `--replay` path, after `run_replay.py` has succeeded.

`K58.Replay.frozenCover : K58.FrozenCover` is the unconditional cover object; it
says the 113,179 frozen keys are realized by the raw cover and the transports.  It
does not say that any case is refuted.
-/
import ReplayGen.Complete
#print axioms K58.Replay.rawTransportCover
#print axioms K58.Replay.frozenCover
