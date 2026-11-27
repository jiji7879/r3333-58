# Direction C: degree-certificate and transfer audit

## Conclusion

The archive contains a meaningful **owner-conditioned local constraint** pipeline, not a whole-row or global $K_{58}$ result. Its 59 pivot-free root certificates omit only a pivot-color assumption; they retain owner hypotheses. Its 334 other certificates additionally fix a branch color. The original-roster transfer consists of 51 newly stored UNSAT support-query payloads, restricted to hypotheses whose owner label exists there.

The relaxed SAT evidence is especially useful: all 59 queries remain SAT with just the two named words, and all 59 remain SAT after removing those words. These models show precisely why the local degree argument cannot be lifted merely by deleting owner information. They are **not** colorings of a physical row, much less of $K_{58}$.

I independently checked all 118 relaxed SAT models. I did not fully replay the 59/334 RUP banks, the 51 original-owner proofs, or the coverage census: the required `K58_three_seconds` kit and its exact generated CNFs/frozen inputs are not supplied here. No Ramsey-bound or row-closure claim follows.

Evidence identity: repository HEAD is `02787250241ebf752dbbdb05fcf7ac7c29b732f3`; the supplied ZIP has SHA-256 `d9d5a68214d1692237b6b3cc332f2116b3d90064f1f178b5b00497138d70cf3d`.

## 1. What the formulas actually ask

Source: `support_helpers.py` (`cycles`, `five_query`, `root_query`), `lift.py:13-26` (`query`), and the predecessor `arm_pairs.base` used by those scripts.

For an $n$-vertex abstract arm, `base(n)` gives every edge exactly one of colors $0,1,2$, prohibits monochromatic triangles, and fixes the initial five vertices to the standard two-colored pentagon. For a hypothesis $(a,Y)$, with $|Y|=2$ and $Y\subseteq\{0,\dots,4\}$, the support formula enumerates every five-set

$$S\supseteq Y,\qquad S\setminus Y\subseteq\{5,\dots,n-1\},$$

and every 5-cycle on $S$. A selector forces cycle edges to one member of $\{0,1,2\}\setminus\{a\}$ and the five complementary edges to the other. At least one selector must be true. Since a triangle-free two-colored $K_5$ is two complementary 5-cycles, the query asks:

> Is there a compatible pentagon on some such $S$ avoiding color $a$?

UNSAT of this support query is the bank's input to its earlier degree argument; SAT exhibits a five-set defeating that support argument. The final field of every one of the 334 records is literally `nominated arm cannot supply five`.

The different modes are not interchangeable:

| Evidence | Arm hypotheses | Pivot color | Recorded outcome and scope |
|---|---|---|---|
| 59 `rootcap-*` records | `parent(n,p,'revised')` | **deleted** by `root_query` | Claimed UNSAT support queries, used as pivot-free owner-local caps |
| 51 `original` events | `parent(n,p,'original')`, only if $p$ is an original label | no pivot unit | Claimed UNSAT support query with new proof payload |
| 59 `words` events | only `base(n)` plus the two named words | none | SAT model for the relaxed local support query |
| 59 `row` events | only `base(n)` | none | SAT model for the further relaxed local support query |
| 334 `degree16-*` records | `parent(n,p,'revised')` | fixed to recorded branch $c$ | Claimed UNSAT support queries, hence branch-specific only |

The crucial code detail is `root_query`: it calls `five_query(...,c=0,...)`, verifies that the next clause is exactly the pivot unit, and deletes that one clause. It does **not** delete the words or owner/rank constraints. “Pivot-free” is not “owner-free” and not “valid on an unsplit row.” Conversely, `five_query` leaves the pivot unit in place for the 334 branch certificates.

The archive does not itself present a self-contained derivation from UNSAT of this abstract support query to the numerical physical degree bound $\le15$. `replay.py --local` regenerates/checks the support CNFs, and `lift.py` maps $(a,Y)$ through `geometry(rid)` to physical vertices. Accepting the numerical degree semantics therefore also requires the preceding bank's combinatorial degree lemma and exact signed-unit mapping, not just a successful RUP line.

## 2. Independent check of the relaxed evidence

Files: `audit_support.py` and its output `support_audit.json`.

I reimplemented `base`, the optional word pins, five-set/cycle selectors, and clause construction without importing any archive Python. For each supplied assignment I checked:

1. every variable $1,\dots,\mathrm{top}$ is assigned exactly once, with no complementary pair;
2. every generated CNF clause is satisfied;
3. every arm triangle is non-monochromatic and the initial pentagon is correct;
4. for `words`, every edge to vertices 5 and 6 has the named word color;
5. a selected five-set and cycle can be decoded explicitly and all ten of its edges avoid $a$ with the required cycle/complement colors.

Result: **118/118 models passed** (59 `words`, 59 `row`) in about 0.44 seconds. There was no SAT search and no timeout/UNKNOWN result. `lift_evidence.jsonl.gz` has exactly 169 events: $59+59+51$. Its `False` means UNSAT of the support query; its `True` means SAT of the support query. Neither is a status for a physical row or global extension.

Concrete example from the checked data, `rootcap-0002`, `words` mode:

- hypothesis $(n,p,a,Y)=(12,(01210,22101),2,(0,4))$;
- an avoiding five-set is $S=(0,4,8,10,11)$;
- one selected cycle is $(0,4,11,10,8,0)$;
- its ten edges use only colors $0,1$, avoiding $a=2$, while retaining both named words.

This is a valid small abstract-arm witness. It does not assign the other physical $58-n$ vertices, exterior edges, signed row units, tickets, or global compatibility conditions.

The eight keys with no `original` event are `rootcap-0001`, `0005`, `0006`, `0007`, `0040`, `0041`, `0042`, and `0043`. They correspond to three owner-pair groups (one, three, and four hypotheses respectively). This agrees with the code's applicability skip when $p$ is absent from the original labels; they should not be described as eight original-owner proofs that timed out.

## 3. What the coverage numbers mean

Source: `lift.py:55-84` and `lift_summary.json`. For every current row and owner, `geometry(rid)` returns physical vertices matching an abstract $(a,Y)$. A `caps` set deduplicates multiple hypotheses hitting the same vertex for that owner. The reported counts are:

| Claimed coverage | Count | Exact denominator/meaning |
|---|---:|---|
| Revised pivot-free owner instances | 14,345 | $1.458160\%$ of 983,774 live revised representatives |
| Revised pivot-free vertex incidences | 27,429 | Deduplicated covered vertices per affected row/owner, not 27,429 distinct physical vertices globally |
| Original pivot-free owner instances | 13,933 | $1.264367\%$ of 1,101,974 original representatives |
| Original pivot-free vertex incidences | 26,029 | Same per-owner incidence meaning |
| Revised representatives with some branch-bank cap | 115,459 | $11.736334\%$ of 983,774; “some” does not mean every branch |
| Revised affected branches | 129,804 | $6.597247\%$ of 1,967,548 branch incidences |
| Branch-bank vertex incidences | 212,599 | Deduplicated per affected row/owner/branch |

Rows touched by pivot-free caps are reported as 2,183 revised and 2,301 original. Those are not full-row closures, and they are not a union count including the branch bank.

The 334 records are 334 distinct $(n,p,c,a,Y)$ hypotheses over 179 distinct $(n,p,c)$ owner/color pairs. Only 118 share an exact $(n,p,a,Y)$ with the 59 root hypotheses. They are a separate bank, not simply four or five copies of the 59. No corresponding original-roster transfer or pivot-free interpretation of this bank is computed in `lift.py`.

Do not add 27,429 and 212,599 and call the result unique coverage: the units and conditions differ, and banks can overlap. The metadata's saved `apps` arrays (202 root applications and 1,610 degree applications) are not used to compute the new totals. Instead, `lift.py` regenerates applicability over the current rosters. Consequently, those totals cannot be established from the old `apps` arrays alone; they need the missing current roster, owner labels, source rows, host literals, and geometry maps.

### Why no fixed-row bound follows

For each row/scheme, `lift.py` intersects the pivot-free `caps` sets over **every** owner. Empty coverage at even one owner makes the intersection empty. It reports `full_rows_one_common_vertex = 0` for both rosters. This exactly supports the narrow statement:

> In this bank, no row has one physical vertex whose relevant degree is bounded uniformly across all owners by the pivot-free certificates.

It does not say the bank is mathematically incapable of expansion. It says the current bank does not meet even this fixed-target coverage prerequisite. Branch-conditional caps are not included in that intersection and cannot silently fill it. Moreover, even a nonempty intersection would only be a prerequisite: one would still need the exact $(x,a)$, complete owner/branch coverage, signed-unit transfer proofs, and the subsequent whole-row contradiction. None is supplied by this census.

## 4. Standalone and strict-replay limitations

The ZIP does contain `replay.py`; it is not a standalone replay package. That driver requires the external `K58_three_seconds` directory, imports `run.check_inputs`, `exclusive`, and `prepare_local`, and builds a `PYTHONPATH` containing kit campaign/reference/engine/frozen directories. Other imports include `common`, `edge_domains`, `campaign_solver`, `new_names`, `cover50`, `arm_pairs`, `cover_proofs`, `sorted_arm`, `problem`, `timed50`, and `pysat`. Those inputs are absent here, as are the exact CNFs for the 59, 334, and 51 UNSAT payloads. NumPy being optional does not remove these dependencies.

I inspected all supplied Python scripts and did not run the replay pipeline. A `drat-trim` executable is available elsewhere in the repository, but running it without regenerating the exact owner CNF would be meaningless. Therefore I make no claim of RUP replay, full-roster regeneration, or independent verification of the claimed incidence totals. My independent replay is limited to the 118 relaxed models and metadata/payload integrity.

There is also a strictness issue to resolve before accepting a future replay. The visible predecessor `cover_proofs.rup` in `K58_adaptive_wall_solver.zip` runs `drat-trim ... -i -w ...` and accepts a substring `s VERIFIED`; this archive calls `rup(...,['-U'])`. The required external kit is missing, so its possibly different helper cannot be audited here. Under the requested acceptance policy, the checker must instead be invoked with `-i -U` and no `-w`, return exit code 0, print exactly one status line `s VERIFIED`, and emit zero warnings. Every query/proof must also be bound to its hypothesis and CNF hash; a cached status or a proof checked against an easier relaxed CNF is not a transfer certificate.

## 5. Acceptance criteria

An audit should distinguish these stages rather than collapse them into “verified degree progress”:

1. **Validated local root/branch certificate.** Identify $(scheme,n,p,c,a,Y)$. Regenerate the exact support CNF; verify the root proof really omits only the pivot unit or the branch proof really fixes $c$; strictly check UNSAT. Separately justify the no-pentagon-to-degree-15 lemma.
2. **Validated physical owner bound.** Give row ID, owner identity, palette index, physical vertex $x$, and signed-unit map from $(a,Y)$. Check the resulting bound is in the advertised color from root to $x$. Deduplicate repeated hypotheses without erasing their conditions.
3. **Validated original transfer.** Prove $p$ is an original label, regenerate the **original** parent/owner formula, strictly replay that exact 51-key query, and repeat the physical map against original-roster data. An old revised proof alone does not transfer.
4. **Validated replacement of a bad support argument.** An UNSAT proof must cover the complete intended hypothesis—not a stronger query with extra pins. Conversely, a SAT model such as the 118 checked here certifies only existence for the stated relaxation; it cannot replace a missing UNSAT proof or be promoted to global SAT.
5. **Validated row-global degree claim.** Exhibit a fixed physical $(x,a)$ and prove uniform coverage across every live owner and every necessary branch, then derive and check the whole-row consequence. Summing incidence counts or observing caps on many different vertices is insufficient.
6. **Remaining global constraints.** Triangle/degree compatibility inside a projection, exterior patterns, tickets, joins, and all other $K_{58}$ edges remain separate obligations. UNKNOWN/timeout remains UNKNOWN in every stage.

Within those limits, the archive does something useful: it exposes exactly which owner hypotheses make the old caps work, produces fresh candidates for 51 original-owner transfers, and quantifies how far the current banks are from a common fixed-vertex row argument. The hard bottleneck is uniform, physically aligned, unconditional coverage—not producing more disconnected local SAT/UNSAT badges.
