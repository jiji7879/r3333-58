---
name: siege-workflow
description: "Derived from Anthropic's siege skill: solve hard math problems and check proofs."
metadata:
  display_name: "Siege: Solve and Check"
  category: "Math research"
  logo: "logos/siege.png"
  long_description: |-
    Work through hard mathematical problems or review existing proofs with an
    explicit record of what is proved and how it was checked. Each problem stays in
    its own workspace with an append-only claims ledger, stall checkpoints, and a
    final write-up that separates established results, open gaps, and skipped checks.

    Checks are recorded by kind (self-reading, recomputation, another model's
    reading, or Lean when a Lean statement is already present), and a result is
    reported as proved only after its cited dependencies and checks pass the ledger
    gate. Requires Python 3 in the project shell, with optional web search and
    Ultramath; follows user restrictions such as no lookups or no Ultramath, and
    does not guarantee mathematical correctness.

    Independent adaptation for Open Math OS from the `siege` skill in Anthropic's
    [math-proof](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/math-proof)
    plugin (Apache-2.0), also drawing on Anthropic's
    [math-olympiad](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/math-olympiad)
    (Apache-2.0), [MathRSI](https://github.com/lisresearchgroup/math-rsi) (MIT),
    [ProofCouncil](https://github.com/eth-sri/proof-council) (MIT), and
    [mathproof-skill](https://github.com/Ztang-Yit-Xiaang/mathproof-skill) (MIT).
    This adaptation is not affiliated with or endorsed by Anthropic, and is
    published under Apache-2.0 in compliance with these licenses, with full source
    revisions and notices bundled in the skill.
---

# Siege

Use when the person wants a hard problem worked to a checked result (a proof, a classification,
a counterexample), or a proof checked before it is called proved.

- `ledger` stands for `python3 .skill/siege-workflow/scripts/ledger.py`, run from the project
  root; the top of that file lists every option.
- `D` is the problem's folder, `research/<name>` (lowercase, hyphens), in the project root. The
  `--at` paths of `ledger add` are relative to `D`.
- The gate is `ledger gate D`. It allows the result when its first line starts with `PROVED` or
  `REFUTED`; `NOT YET` means it does not.
- Each stage below is a document of this skill, not a separate skill: read it when its stage
  comes.

1. **Solve** with [references/solve.md](references/solve.md), until the goal is PROVED or REFUTED
   in the ledger, or the strongest results and the exact gap are recorded.
2. **Check** the entry that settles the goal with [references/check.md](references/check.md). Tell
   no one it is proved before the gate allows it.
3. **Report** with solve.md §5: write `D/proof.md`, opening with its Status, and give the person
   the result in the gate's words with the path to `proof.md`.

A proof brought to be checked starts at check.md §1. If `ledger` refuses a ledger edited by hand,
stop and tell the person; do not work around it.

Match the effort to the problem, in Ultramath mode too. An exercise you can finish yourself needs
no Ultramath, and its check is a reading and a recomputation; Lean and another model's reading
are for results others will rely on. Once the proof is written and checked, stop.

The person's instructions come first (no Ultramath, no web search, a time limit). Follow them,
and say in the Status what was skipped because of them.

Tools: a shell with Python 3 for the ledger, `search_web` and `web_fetch`, Ultramath. A stage
whose tool is unavailable is skipped and named in the Status, never reported as done.
