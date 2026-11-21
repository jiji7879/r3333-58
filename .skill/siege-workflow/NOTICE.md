# Notice

This skill and its script were written for Open Math OS by Open Math Model (2026-11-18, revised
2026-11-20).

Licensed under the Apache License, Version 2.0 (see LICENSE).

Derived from the `siege` skill of Anthropic's math-proof plugin: its name and its core design
(claims ledger, progress test, gate, Status). This is an independent adaptation, not affiliated with
or endorsed by Anthropic. The skill restates these ideas in its own text and code; no text or code
was copied from the projects below.

## Sources

- **Anthropic, math-proof plugin** (Apache-2.0)
  - Source: https://github.com/anthropics/claude-plugins-official/tree/aa5654b7acb7d3096b5db44381bcfceaf4a71dfb/plugins/math-proof
  - Commit: `aa5654b7acb7d3096b5db44381bcfceaf4a71dfb`
  - From `siege`, the skill this one is derived from:
    - running a hard problem as stages that end in a checked, honestly labelled result;
    - a numbered, append-only claims ledger, with retractions;
    - a list of the approaches already tried;
    - a progress test that does not count special cases or narrowings, and that after a stall
      asks for a different mechanism or decomposition;
    - raising a proved goal while keeping it as the fallback;
    - a final `proof.md` whose Status section says what is and is not proved;
    - leaving the bookkeeping decisions to a script (`scripts/ledger.py`) rather than the model;
    - a gate that accepts a result only with checks that cite it by number and name files
      that exist;
    - independent checks of the exact text before a result is concluded;
    - checks that name where they came from (a file, or the Ultramath run and member).
  - From `solo`: writing each settled step to a notes file, so a reply cut off loses nothing.
- **Anthropic, math-olympiad plugin** (Apache-2.0)
  - Source: https://github.com/anthropics/claude-plugins-official/tree/9d468adfb857b1aeedb45f6279409820a0ffa573/plugins/math-olympiad
  - Commit: `9d468adfb857b1aeedb45f6279409820a0ffa573`
  - Solve: checking the intended reading of a problem before solving it; stepping back when the
    same gap appears twice; saying "no confident solution" rather than bluffing.
  - Check: verifying a clean copy, without the reasoning that produced it; asking whether the
    argument would prove a famous open problem; testing the general lemma behind a short proof on
    small cases.
- **MathRSI** (MIT)
  - Source: https://github.com/lisresearchgroup/math-rsi/tree/de556f3d5427343153d8d24bed4578ccfe66400c
  - Commit: `de556f3d5427343153d8d24bed4578ccfe66400c`
  - Solve: a workspace per problem that holds its statement, its research record and notes to
    resume from.
- **ProofCouncil** (MIT), and its paper [arXiv:2607.09474](https://arxiv.org/abs/2607.09474)
  - Source: https://github.com/eth-sri/proof-council/tree/1fcd5e51df23a3e458048da8c3b51da3a739ca50
  - Commit: `1fcd5e51df23a3e458048da8c3b51da3a739ca50`
  - Check: acceptance only by a fresh critic, readings by other models, and a computer-algebra
    check.
- **mathproof-skill** (MIT)
  - Source: https://github.com/Ztang-Yit-Xiaang/mathproof-skill/tree/05ec358bd2f83e16774a24ebda6e140eecda92df
  - Commit: `05ec358bd2f83e16774a24ebda6e140eecda92df`
  - Check: keeping an informal audit apart from a machine check; auditing the axioms and `sorry`
    of a Lean proof.
