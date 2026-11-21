# Siege: solve a hard problem

`ledger`, `D` and the gate are as in SKILL.md.

Tools: a shell with Python 3, `search_web`, Ultramath. What is unavailable or declined is skipped
and named in `proof.md`'s Status.

## 1. Set up or resume

- If `D` exists: run `ledger status D`, read `D/notes.md`, and go on from what is open.
- Otherwise create `D/work/` and `D/checks/`, write the statement exactly as given to
  `D/problem.md`, and restate it in `D/notes.md`: objects, quantifiers, what counts as done. If it
  can be read two ways, ask the person.
- Unless the person forbids looking things up, search whether it is known; if it is, give the
  source and ask whether they want a proof anyway.
- Record the goal: `ledger add D OPEN "<the goal>" --goal --at problem.md`.
- Try the direct route first. If a complete argument comes, write it in `notes.md` and go to §5.

## 2. Work and record

- Write each settled step into `notes.md`, one numbered list (`notes.md#3` is step 3), before you
  reason further: a long reply can be cut off.
- Record with `ledger add`, never by hand:
  - `PROVED` or `REFUTED`, `--at` where the argument is, "by #N" for the entries it uses, `--on N`
    when it settles open entry N. Only the whole result goes `--on` the goal. The gate refuses a
    result that rests on an entry still `OPEN`: prove it, or do not cite it.
  - `--case` when it covers only some objects (some n, a finite range); a lemma about all of them
    is not a case. A finite search proves its range only, and the pattern it suggests is `OPEN`.
  - `OPEN` for a statement you need; `TRIED --on N` for an approach set aside, and why.
  - `RETRACT --on N` as soon as an entry is found false; then retract or re-derive what cites it.
- Read `ledger status D` before an approach; do not repeat a tried one without a new idea.
- Compute to test an idea, not in place of one: after two searches that suggest no mechanism,
  write down what an argument would need. A program that refutes something is a claim too: run it
  on cases you can do by hand before you trust it.
- Work in `D/work/`; anything over a minute runs as a background job.
- Lean only when the person asks or the problem gives a Lean statement (load `lean-workflow` with
  `skills_load` if it is installed).
  Never start formalizing a proof that is already written.

## 3. Checkpoint

When a line of attack ends (it settled what it was for, or you set it aside), run
`ledger checkpoint D`; only a new result that is not a case counts as progress. At `STALLED 2` or
more, stop opening cases: write the missing statement in `notes.md`, then change the mechanism or
the decomposition, or give it to Ultramath. The same gap twice: step back.

## 4. Ultramath

When checkpoints stall, or several independent approaches look plausible; not for a problem you
are about to finish, and not if the person said no.

- The task stands alone: the missing statement, tested on small cases first; what was tried and
  why it failed; what counts as solved; the person's rules (no lookups, limits). Present as proved
  only ledger entries in force, each re-tested on small cases.
- One swarm at a time; its limits follow the person and the Ultramath rules.
- A submitted solution: `PROVED --at ultramath:<swarm>/<member>`, checked with check.md (your
  reading is kind `model`: you did not write it) before the verdict; a gap means reject and
  retract. Bring its lemmas back as `OPEN` and its dead ends as `TRIED`.

## 5. Finish

1. Record the result `--on` the goal.
2. Check it with check.md.
3. Run `ledger gate D`. Tell no one it is proved before the gate allows it; describe the checks
   in its words.
4. Write `D/proof.md`, self-contained, opening with **Status**: the result, the gate's lines, checks
   skipped and why, what is open or conditional, and everything looked up. Short of the goal:
   the strongest results and the exact gap.

Say "no confident solution" rather than present a proof you do not believe, but not before a
checkpoint and, unless the person said no, one Ultramath round on the missing statement. To aim
higher once the goal is proved, record the stronger statement as `OPEN` without `--goal`: the gate
keeps reporting the proved goal.
