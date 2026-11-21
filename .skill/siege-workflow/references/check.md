# Siege: check a proof

Use before anyone is told a result is proved. A check finds gaps; it does not repair them.
`ledger`, `D` and the gate are as in SKILL.md.

Match the checks to the claim: an exercise gets a reading (§2) and a recomputation (§3); another
model (§4) is for results others will rely on. A check ends at the first gap, or when every step
has been read.

Tools: a shell with Python 3, `search_web` and `web_fetch`, Ultramath for §4. A check whose tool
is unavailable is skipped and named in the Status, never recorded as passed.

## 1. What is checked

- Your own result: `<id>` is the entry that settles it. Write a clean copy to `D/checks/<id>-proof.md`.
- A proof brought to you: in a new `D`, create `D/checks/`, write the statement to `D/problem.md`
  and the statement and proof, exactly as given, to `D/checks/claim.md`. Then
  `ledger add D OPEN "<statement>" --goal --at problem.md` and
  `ledger add D PROVED "<statement>, as claimed" --on 1 --at checks/claim.md`. Every check goes
  on that entry, #2.

A clean copy holds the statement and the whole argument with its lemmas, and nothing else: a
reader who sees the exploration tends to agree.

## 2. Reading, in `checks/<id>-read.md`

Kind `self` if you wrote the proof (not independent, and the gate says so), `model` if you did
not. Read only the clean copy.

- The same statement: objects, quantifiers, hypotheses, parameter range.
- Cases: list every case the statement covers and the line that handles each. A case assumed
  away, or a step that uses its own conclusion, is a gap however natural it reads.
- Too strong? Run the argument where its conclusion fails, or would settle a famous open problem.
- Every cited result beyond textbook facts: its exact hypotheses, checked where it is used.
- A gap is a step you can name, with exactly why it does not follow; a vague doubt is a note.
  Stop at the first gap.

## 3. Recompute (kind `compute`), in `checks/<id>-compute.md`

With a new program in `checks/`, recompute every numerical or finite claim the argument uses, and
test every general lemma or inequality it states on small values. Keep the command, exit status
and output, and name what was covered. A recomputation that shows a step false is a gap, once the
program reproduces cases you can do by hand.

Lean (kind `lean`) only when the project already has a Lean statement of this result, or the
person asks: build it, `#print axioms` (no `sorryAx`), and compare the statements
(`lean-statement-audit`, if installed). Never start a formalization inside a check.

## 4. Another model (kind `model`), in `checks/<id>-model.md`

Only when the person says the result will be relied on (published, built on) or asks, in
Ultramath mode too; otherwise skip it and say so in the Status.

- Ultramath, 3 members, about 30 model calls and 30 minutes, on a model family other than the
  writer's unless the person fixed the model.
- The task: the clean copy, and "Find the first gap. One direction each: the logic step by step;
  the hypotheses of every cited result; counterexamples and edge cases. Submit the gap with its
  location, or 'no gap found' with what you checked."
- Accept a specific report; confirm a gap before recording it. A member who writes its own proof
  has not checked this one.

## 5. Record and report

`ledger add D CHECK "PASS: <what it covered>" --on <id> --kind <kind> --at <that check's file>`
(`checks/<id>-read.md`, `-compute.md`, `-lean.md` or `-model.md`), or `"GAP: <step and why>"`; a
check that shows a step false is a GAP. After a GAP, `RETRACT --on <id>`. For a brought proof of a
false statement, then `REFUTED "<the counterexample>" --on 1 --at <where>`, check the
counterexample (kind `compute`) on that new entry, and run the gate. Retract a GAP check only when
the gap is shown not to be one, and say why.

End with the verdict: the first gap, its step and why; or "no gap found", with the checks by kind
in the exact words of `ledger gate D`. No repair in the verdict: a repair is a new proof to check.
