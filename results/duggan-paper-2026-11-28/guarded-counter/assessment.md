# Duggan cardinality counters: conditional-propagation transfer to K58

## Outcome

There is a specific, validated transfer from Duggan's Chapter 5 to this repository,
but it is an **encoding correction/strengthening**, not a new Ramsey result. For
an existing guarded constraint `g -> (sum x_i >= k)`, leave the Sinz recurrence
clauses unconditional and guard only its overflow/bound clauses. The repository
currently prepends `-g` to *every* counter clause in the tested `two5` encoder.
That choice disables internal counter propagation while `g` is unassigned.

The revised encoding has exactly the same projected Boolean models, variables,
and clause count, but strictly stronger unit propagation and fewer literals. It
was checked exhaustively on small instances and on all 168 actual counter gadgets
of historical full-root rank 1300. A single capped actual-row A/B remained OPEN
and did **not** show a time improvement. No wall row was closed, no Lemma L or
K51 consequence follows, and the original-parent DRAT-lifting gap remains.

## What the paper actually supports

I read `conor_duggan.pdf`, especially Chapter 5 (pp. 11--15) and Chapter 11
(pp. 32--34). Duggan uses Sinz sequential counters for small degree bounds and
totalizers for larger bounds, and emphasizes arc consistency and independent
DRAT checking. His degree constraints are logical consequences of the Ramsey
constraints but help propagation. He does **not** evaluate the repository's
conditional sender/arm guards or a four-colour K58 encoding. The transfer here
is therefore the propagation discipline for hard counters, adapted soundly to a
guard; it is not a theorem imported from R(3,8) or R(3,9).

The live repository already has much more than the generic suggestion "add
cardinality counters": `tools/cc/global_degree_caps.py` and the K60-style
sequential counter, totalizer degree-cap experiments, guarded arm/five/pair
counters, and the `two5` selector encoding. See
`research/k58-arm-cap-clauses/proof.md`, especially its mixed performance and
certificate-gap sections. This report does not repeat those as new ideas.

## Exact encoding and proof of projected equivalence

Let $P_k(x)$ mean $\sum_{i=1}^n x_i\ge k$. For $1<k<n$, PySAT's Sinz at-least
encoding is the standard at-most-$m$ counter on $y_i=\neg x_i$, where $m=n-k$.
Partition its clauses into:

* $E$: input/prefix recurrence clauses, using fresh cells $s$;
* $O$: overflow clauses enforcing the at-most bound.

The direct cases $k=1$ and $k=n$ have $E=\varnothing$. The current conditional
form and proposed form are respectively

$$
F_{\rm naive}=\bigwedge_{C\in E\cup O}(\neg g\lor C),\qquad
F_{\rm boundary}=E\land\bigwedge_{C\in O}(\neg g\lor C).
$$

For $k>n$, emit $\neg g$; for $k\le0$, emit nothing.

**Claim.** After existentially projecting all fresh cells,
$F_{\rm naive}$ and $F_{\rm boundary}$ both represent exactly
$g\Rightarrow P_k(x)$.

**Proof.** Every input assignment admits the canonical sequential-counter
extension satisfying $E$: evaluate each cell as the corresponding prefix
threshold. If $g$ is false, every guarded overflow clause is satisfied. If $g$
is true and $P_k(x)$ holds, at most $m$ of the $y_i$ are true, so the same
extension satisfies $O$. Conversely, with $g$ true the overflow clauses are the
ordinary hard counter and exclude every assignment with more than $m$ true
$y_i$. $\square$

The boundary construction never asks a fresh cell to satisfy an unconditional
output bound; only the recurrence is unconditional. Thus the proof is not an
assertion that fresh auxiliary variables can be assigned arbitrarily.

### Why propagation improves

With $g$ unassigned, every clause of $F_{\rm naive}$ still contains the
undecided literal $\neg g$. No recurrence clause can propagate a cell. In
$F_{\rm boundary}$, assigned inputs build the prefix counts normally. If already
more than $m$ inputs are false, the usual Sinz propagation reaches an overflow
clause whose other literals are false and derives $\neg g$. Setting $g$ true
reduces both versions to the same hard counter. The same argument applies to
`q -> at-least-five` selector counters; pair selector clauses can then propagate
further.

This changes propagation, not the physical constraint or the profile arithmetic.
The two encodings have the same number of variables and clauses. Boundary
guarding removes exactly $|E|$ occurrences of the guard literal.

## Validation performed

All commands below are run from the repository root with assertions enabled.
The complete sequence also runs as `bash .ultramath/smwzxq4fl/m3/reproduce.sh`
(about 19 seconds in the final run); it recreates both actual CNFs and all JSON
receipts, then checks both expected CNF hashes.

### 1. Generic exhaustive controls

```sh
PY=.scratch/k58/.venv/bin/python
M=.ultramath/smwzxq4fl/m3
$PY -B $M/guarded_counter.py
$PY -B $M/propagation_conformance.py
```

Results, recorded in `guarded-counter-results.json` and
`propagation-conformance.json`:

* 77 hard-counter comparisons: concatenating `E` and `O` agrees clause for
  clause with PySAT `CardEnc.atleast(..., EncType.seqcounter)` for $n=2..12$,
  every nontrivial bound, including variable allocation.
* 9,212 Minisat22 satisfiability checks: both conditional forms have precisely
  theSAT status of the direct projected relation, including $k=0$ and $k>n$.
  This is existential auxiliary-model equivalence, not merely clause comparison.
* All $3^{n+1}$ partial guard/input assignments for $n=2..6$, both forms:
  of 4,008 genuinely forced physical/guard literals, naive guarding missed
  1,034; boundary guarding missed 0. Neither produced an unsound conflict or
  missed an inconsistent partial assignment.
* 9,216 fully assigned bound violations for $n=2..10$: boundary derived
  $\neg g$ 9,216/9,216 times; naive did so 2,044 times.
* An independent Minisat22 `propagate` comparison agreed with the small BCP
  implementation on all 9,828 partial-assignment cases ($n=2..5$), zero
  mismatches.
* A negative control with the guard omitted rejected an assignment that must be
  allowed when $g$ is false. This guards against accidentally turning the
  conditional constraint into an unconditional one.

### 2. Actual rank-1300 `two5` encoder

I copied the published encoder into this member directory and added a
`--conditionalization {naive,boundary}` option. The default naive path must and
does reproduce the published artifact exactly.

```sh
PY=.scratch/k58/.venv/bin/python
M=.ultramath/smwzxq4fl/m3
$PY -B $M/two5_boundary_encoder.py 1300 --mode two5 \
  --conditionalization naive --out $M/actual/r1300-naive.cnf
$PY -B $M/two5_boundary_encoder.py 1300 --mode two5 \
  --conditionalization boundary --out $M/actual/r1300-boundary.cnf
$PY -B $M/audit_actual.py
```

Both use the exact original parent SHA-256
`56ad3dc529f1b855e65fa3f3f5363e8275930a7cb6ea5b04dc01a112535b0837`,
29,942 original variables and 211,564 original clauses. Each adds 4,923
variables and 8,533 clauses. The naive output is byte-identical to the retained
published CNF and has the expected SHA-256
`fe9de879d99b320c57c7d90582842a532a045da9c3d90c8df5880d96498eb9af`.
The boundary output has SHA-256
`8a054217a84fd3b995cc371fc795b2422ea6eb7f60d0336cad2ed567b499a277`.

`audit_actual.py` independently parses the emitted suffixes, compares against
the retained stock and published files, checks original-body preservation and
variable ranges, and obtains:

| check | result |
|---|---:|
| actual conditional counter gadgets | 168 |
| unchanged selector pair clauses | 168 |
| direct SAT/guard projection checks | 10,992 |
| sampled violating physical assignments | 736 |
| boundary derivations of selector negation | 736 |
| naive derivations of selector negation | 24 |
| added literal occurrences, naive | 30,097 |
| added literal occurrences, boundary | 22,184 |

The 24 naive successes are exactly the direct $k=1$ OR gadgets, which have no
recurrence. Thus the tested nontrivial sequential cases account for 712 misses.
The audit also constructs three six-input `q -> at-least-five` counters and the
three `two5` pair clauses. With all physical inputs false, boundary propagation
sets every $q$ false and then derives $\neg g$; naive propagation derives none
of these. This is the exact selector interaction used by the repository.

Removing the guard from recurrence clauses reduced the real suffix by 7,913
literal occurrences (26.29%), without deleting a recurrence or changing its
variable allocation.

### 3. Small actual A/B and its negative performance result

```sh
.scratch/k58/.venv/bin/python -B \
  .ultramath/smwzxq4fl/m3/bounded_ab.py
```

One CaDiCaL195/PySAT run per form, seed 0, 20,000-conflict budget, no proof
logging:

| form | status | conflicts | decisions | propagations | restarts | process CPU s |
|---|---|---:|---:|---:|---:|---:|
| naive | OPEN | 20,001 | 53,681 | 4,424,839 | 1,350 | 1.445 |
| boundary | OPEN | 20,001 | 51,735 | 5,382,933 | 1,237 | 1.466 |

Boundary had fewer decisions and restarts but 21.66% more propagations and
slightly higher CPU. This one capped seed supplies no full-run or speedup
evidence. The row is a historical **full-root completed** control, not one of
the 11,585 small-profile wall rows. OPEN is not SAT or UNSAT.

## Applicability by repository goal

1. **Small-wall row UNSAT:** plausible but unproved performance benefit. The
   boundary form is a drop-in semantics-preserving replacement for conditional
   sequential counters. It exposes counter propagation before guards/selectors
   are decided. The actual performance pilot was on a completed historical row
   and was not faster; no open wall formula was solved or claimed. A sensible
   next control is one hash-pinned ordinary wall parent with the existing guard
   bindings, comparing naive and boundary forms at the same small cap. Only a
   completed run with strict whole-proof DRAT replay can count as a closure.
2. **Lemma L / profile reduction:** no new consequence. The two extensions have
   identical physical projections, and the underlying five-cap/ticket facts were
   already present. This cannot distinguish any additional degree profile.
3. **K51 model finding:** no tested benefit. Unconditional K51 degree-cap
   counters are unchanged by this construction. It applies only where K51 uses
   a guarded cardinality constraint; no such K51 pilot was run and no colouring
   was found.
4. **Certificates:** the same existential-extension argument covers both forms,
   but a SAT equivalence test is not a DRAT prefix. A refutation of the boundary
   augmented CNF would still have augmented-parent scope until the accepted
   model-extension/selector argument is independently admitted. No new
   original-parent proof lift was implemented. In particular, do not relabel an
   augmented DRAT as a proof against the unextended physical parent.

For totalizers, the analogous discipline would be to leave the full tree
relations unconditional and guard only root output bounds. That was **not**
implemented or measured here; the validated transfer is specifically the Sinz
counter actually used by `two5`.

## Files and limitations

* `guarded_counter.py`: encoder split, direct-relation controls, and BCP.
* `propagation_conformance.py`: independent Minisat22 propagation comparison.
* `two5_boundary_encoder.py`: actual-encoder copy with both policies.
* `audit_actual.py`: actual-CNF/gadget and three-selector checks.
* `bounded_ab.py`: one small matched solver control.
* `actual/audit.json`, `actual/bounded-ab.json`: compact machine-readable results.

No production file, queue, ledger, or other member's workspace was changed. No
DRAT was generated because the actual A/B was capped and OPEN. No large sweep,
new row closure, new R(3,3,3,3) bound, or claim that R_4(3) has moved is made.
