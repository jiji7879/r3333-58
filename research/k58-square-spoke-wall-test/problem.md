# The square/matching clause theorem and its ordinary-wall tests

Audit `K58_square_spoke_wall_test.zip` independently. Its rule asserts
$\neg g_{a,c}\lor\bigvee_{v\in S}\neg E_{a,v,c}$ under an encoder guard of
at least 14 colour-$c$ spokes outside $a$'s root arm, excluding the root. Four
sites exhibit square plus matching within another arm. The package distinguishes
its shared K15 theorem, a K14 boundary model, 14 first-tier ordinary wall
parents, and 13 full-root historical control parents.

Check the theorem and both boundary models, exact source-unit and guard
bindings, clause counts and propagation interpretations, and only report
native wall tests actually replayed. `full_root` flags, grouped-neighborhood
sizes, clause signs and the scopes of matched physical indices must not drift.
Ten OPEN original-cube calls have no full-parent refutation, and no Ramsey or
row-closure claim follows.
