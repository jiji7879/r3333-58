---
name: lean-elaboration
metadata:
  display_name: "Lean Performance Tuning"
  category: "Lean"
  logo: "logos/lean.png"
  author: "Scott Armstrong"
  long_description: |-
    Diagnose and improve slow Lean 4 elaboration, tactic execution, and builds.
    Profile the reported file or timeout, distinguish import loading, typeclass
    inference, and proof costs, then test targeted optimizations with matched
    before-and-after measurements and downstream validation.

    Also supports requested repository benchmarks and trend reports. Preserve
    statement meaning, pinned dependencies, and build artifacts. A measurement-only
    request does not require edits; raising heartbeat limits is not a speedup.

    [GitHub source](https://github.com/scottnarmstrong/LeanAutoformalizationSkills)
description: "Profile and optimize slow Lean proofs, elaboration, and builds."
---

# Lean performance

Start with the reported slow target and the repository's pinned toolchain and
build instructions. Measure before editing. Do not run a repository-wide rebuild
just to diagnose one theorem.

## Choose the measurement scope

- **One slow file or timeout:** reproduce the symptom, ensure its dependencies
  are built, and obtain a warm own-file profile with the project-approved Lean
  command. Separate import loading, statement elaboration, typeclass inference,
  tactic execution, and output/compilation costs.
- **Repository benchmark or trend report:** read
  [Measurement procedure](references/measurement/guide.md). Record the commit,
  dirty state, targets, cache state, host, timing tool, and concurrency. A missing
  dependency cache is setup work, not a project elaboration regression.

## Improve only the measured bottleneck

Read the relevant section of [Optimization techniques](references/optimization.md)
after identifying the expensive phase. Try one change at a time and compare the
same target under matched conditions, repeating noisy runs. Keep the change only
when the improvement is reproducible and downstream validation still passes.
Historical timings and thresholds in the reference are examples, not acceptance
criteria for this repository. Profiler timings can also be affected by contention.

Preserve statement meaning, dependency pins, and upstream build artifacts. Do not
raise heartbeat limits as evidence of a speedup, weaken hypotheses, or edit a
frozen public interface for performance. A diagnostic proof-hole experiment is
only for an isolated, untracked copy when project policy permits; never leave it
in the delivered source or count it as a validated proof.

Report baseline and changed commands, scope, timings, variability, build results,
and remaining uncertainty. A measurement-only request does not require applying
fixes. Stop trying an optimization when measurements refute it.

## Upstream sources

This skill is adapted from [lean-elaboration](https://github.com/scottnarmstrong/LeanAutoformalizationSkills/tree/main/skills/lean-elaboration) and [lean-elaboration-test](https://github.com/scottnarmstrong/LeanAutoformalizationSkills/tree/main/skills/lean-elaboration-test) in Scott Armstrong's [LeanAutoformalizationSkills](https://github.com/scottnarmstrong/LeanAutoformalizationSkills).

Synchronized against upstream commit [`1837b95`](https://github.com/scottnarmstrong/LeanAutoformalizationSkills/commit/1837b95b3d5a9fd8d311367603902ad7fe261adf). The entrypoint and bundled guides retain the Open Math Model consolidation; see [NOTICE.md](NOTICE.md) for attribution and adaptations.
