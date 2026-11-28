# Working notes

The source archive was extracted read-only for inspection to `.scratch/color-wall-v1/base`. `apply.py` maps local physical variables by `edge(sender, offset+local_site, color)` and maps local counter variables to fresh variables beginning one above the parent's declared maximum. Its `miter` flags make a violation of at least one target clause; successful derivation of all flags false certifies the conjunction of the target clauses, rather than the unmodified parent's UNSAT.

The catalog and exporter contain assertions against every fixed template edge and sender spoke domain. These still require an independent exhaustive/brute-force check: local template minima and forced assignments need not extend to an actual K58 coloring. A satisfying original assignment extends to the monotone comparator counter only when the count witnesses faithfully encode the count of the physical inputs.

`check_exports.py` claims original-parent transport on the six benchmark rows and one further row per eligible profile (ten total). All other eligible rows have data/geometry bindings and an on-demand workflow, not ten more completed full-parent replays. These transport limits and all failure/timeout results must be stated explicitly.

The new attachment is intentionally a separate research folder from `research/k58-proof-artifacts`, whose requested scope remains four packages.

## 2. Independently checked local counter and miter semantics

For comparator inputs $p,q$, the six defining clauses encode exactly $H=p\lor q$ and $L=p\land q$. The comparator replaces $[p,q]$ by $[H,L]$ where $H\ge L$ in Boolean order. Inserting a literal after an already sorted prefix preserves the sorted prefix. Consequently output $j$ is true exactly when at least $j+1$ inputs are true. Each auxiliary OR/AND value is uniquely determined by preceding values, so any assignment of physical inputs has exactly one extension satisfying the counter definitions.

`checks/counter_control.py` independently assigned these comparator values and all 510 physical assignments for counts $1,\ldots,8$ in the actual source counter and checked every defining clause and threshold. These are controlled instantiations; the inductive argument above supplies arbitrary finite input sizes. The test also recomputed source-local target counts on all 240 catalog records.

For targets $C_i=\ell_{i1}\lor\cdots\lor\ell_{ir}$, and fresh flags $f_i$, the source `miter` constructs
$$F\ \land\ \bigvee_i f_i\ \land\ \bigwedge_{i,j}(\neg f_i\lor\neg\ell_{ij}).$$
A true flag makes every literal of its target false, and at least one flag must be true. A flag may be false when its target holds. Hence the query has a model exactly when $F$ has a model falsifying at least one target; UNSAT means every target is entailed (including vacuously when $F$ itself is UNSAT). The tiny exhaustive model controls in `checks/counter-control.json` evaluated every flag assignment rather than assuming all flags true.

A separate native control took $F=\{1\}$ and an unsupported target $2$. Its first bogus addition failed native `drat-trim -I -f -W -U` with `s NOT VERIFIED` and no warning suppression. An actually implied target passed. These reject/accept outcomes test the checker behavior; they are not claims of local wall feasibility or original-parent UNSAT. Intermediate erroneous test scripts all failed their own assertions and were not counted as evidence.

## 3. Accepted full binding and transported-parent audit

The independent member direction reconstructed all 11,585 ordered row bindings and all 240 complete configuration objects with no package encoder imports: 11,549 non-null and 36 null pivots. Campaign minima, minimizing full-word/mask counts and forced-site maps matched, as did 1,347 unequal false-color minima and the other catalog totals. The coordinator reran this reconstruction. The 36 nulls are an archived-pivot selection limitation, not proof that no usable pivot exists.

A separate physical-unit/domain audit checked all 11,549 classified geometries (174,535 arm sites: 53,556 singleton support domains and 120,979 three-color free domains). The coordinator's path-adjusted rerun passed after the supplied script's relative-path issue was corrected in the copy, not in the artifact. All 51 extracted members match the 7,943,004-byte ZIP, SHA-256 `74a517db2c15f2b96c9834d4e4e135c86e62709cd0813b733c810936d411e020`.

All ten supplied transported parent queries replayed with native forward RUP, warnings fatal and `-U`, 159 conditional clauses in total. Every item in `transport.json` matches an independently generated parent/proof/export reconstruction. Six stored parents also match archived CNF bytes exactly. Four more require the bundled encoder's threshold suffix: their entire K58 body and physical units were independently rebuilt, but this audit does not claim an independent suffix-provenance proof. One actual on-demand export at 004097 was run by both the member and coordinator; the 3,353,247 export bytes hash to `ce69e196ae302f0cb00d3ee4c7d3114f401c21ba4633e1616438a20b43fb091d`. An arbitrary full variable-permutation transport also passed.

This validates conditional consequences, not the original parent's UNSAT, not extension of an arm-local attaining word, and not a full wall closure. No performance conclusion is supplied by this direction.

## 4. Accepted local mathematics and baseline semantics

The local direction independently enumerated 1,448,380 physical local words across all 240 configurations and reproduced all 720 branch minima/word counts/forced maps and every non-null campaign control. Each branch minimum is witnessed locally. Every physical word satisfies its color targets under the unique descending unary counter extension. All 8,190 assignments for counter sizes 1 through 12 pass, adding to the coordinator's independent 510-assignment check.

All 240 cached local queries/traces have independently matching hashes and pass native forward RUP with warnings fatal: 4,196 targets, 20,852 proof steps, 1,235,379 query bytes and 406,943 trace bytes. Omitted-target and false-pivot controls are rejected. The local direction also reconstructed all 4,510 minimal positive hitting clauses and found explicit physical counterwords for all 21,173 single-literal deletions. The exact matched six B banks total 94, while C targets total 97; all 191 batch clauses therefore have independent semantic justification, in addition to direction (c)'s full native batch replay.

For the ten transported parents, 135 minimum words were merely not refuted by unit propagation. This status is undetermined, not SAT, and no complete coloring search was made. Local minima are sharp only on their arms; a conditional consequence certificate is not a parent UNSAT proof.

## 5. Accepted batch and performance audit

Another independent direction rebuilt all six batch parents byte-for-byte and replayed all six complete miter batches natively, plus ten selected local and ten transported parent queries. Useless/malformed control traces were rejected. All 191 added batch clauses were explicitly present as derived targets, not imported as premises. Two actual exports match: batch 0 color is 3,328,774 bytes, SHA-256 `66cde0ddb0556a76a73244981976aff09d9928788a9dbf59f1a56779049efa50`; the coordinator independently reproduced this export as well as the previously recorded gap export.

All 48 full-row trials remain OPEN: 480013/480012/480006/480015 conflicts under original/counter/escape/color, and CPU 43.431247/40.873760/43.895359/40.746612 seconds. All 24 variant formula identities match their two seed receipts. These capped concurrent ratios are not speedup measurements. There are 510,002,619 partial-trace bytes recorded, but no retained traces or benchmark solver binary in this archive for independent replay.

The selected-child records have 114 B-side and zero C-side conflicts across 16 cases per treatment, with no retained child certificates. The four timing boundaries do not form a cold end-to-end ledger: batch `total_s` stops before persistent file writes and benchmark `materialize_s` stops before solver-input writing. Thus discovery, proof creation, recording and solving cannot be aggregated into a claimed win. The ledger will narrow the goal to this scoped audit, not claim the wall problem solved.
