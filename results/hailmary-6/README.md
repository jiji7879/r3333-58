# Hail mary (their item 3): one variable per independent set — definitionally
# equivalent, and measurably identical

Their hypothesis: the pinned arm has only eleven independent 5-sets per colour,
so each outside vertex's colour-`f` part can be one variable over the independent
sets instead of 15 edge cells, and "propagation is much stronger".

**The census first** (`indep.py`), and it is better than the hypothesis states:
each of the template's three colour graphs has independent sets in sizes
`{0:1, 1:15, 2:70, 3:130, 4:90, 5:11}` — **317 sets per colour**, eleven maximum
ones. So a slot's ordinary part is one of 317 objects, and its zero part is
unconstrained (any 5-subset of the 15, since colour 0 never occurs inside the
template), which is why the word census is 254,628 over 3,003 zero-parts.

**The encoding.** For each slot and ordinary colour, one selector per independent
set, defined by `sel <-> AND of its cells` — 42 slots x 3 colours x 317 sets,
plus the definitional clauses. On the 42-slot instance:

| encoding | variables | clauses | status @120 s | conflicts @120 s |
| --- | ---: | ---: | --- | ---: |
| cell (as built) | 45,381 | 179,318 | UNKNOWN | 4,743,303 |
| one variable per independent set | 85,197 | 340,094 | UNKNOWN | **4,735,559** |

Two per cent fewer conflicts on an 89 % larger clause set: **no change in the
search**. Both arms UNKNOWN.

**Why this had to happen.** The selector is a *definitional* extension: `sel` is
true exactly when its cells are, so the formula has the same models as before, and
any "stronger propagation" would have to come from clause structure alone. It does
not here — kissat's conflict count is the same to within 0.2 %, which is what one
expects when the added clauses are implications between literals that propagation
already reaches.

For item 3 to add real strength the encoding would have to *restrict* the parts to
independent sets — and that restriction is already in the instance as the
part-independence family. There is no third option: a re-parameterisation cannot
add logical content, and the measured cost of attempting it is 89 % more clauses
for nothing.

**Verdict.** Item 3 is closed: the idea is correct as a description of the
structure (317 sets, eleven maxima) and empty as an encoding change, because its
content is already encoded.
