# Admission audit of the bounded K58 evidence bank

Policy: [`POLICY.md`](POLICY.md). Machine: [`gate.py`](gate.py) (decision
function), [`adapters.py`](adapters.py) (receipt → record),
[`run_audit.py`](run_audit.py) (reproduction), [`tests/test_gate.py`](tests/test_gate.py)
(26 pinned cases). Nothing here runs a solver or edits the tree.

Reference HEAD: `e856d75`. Evidence read only from
`results/next-directions-2026-11-28/`.

```
python3 tests/test_gate.py   # 26/26
python3 run_audit.py         # 6/6 decisions reproduced, receipts/audit-summary.json
```

## 1. Verdicts

| candidate | record | trust | metric | cells | geomean | worst | decision |
|---|---|---|---|---|---|---|---|
| native LRAT vs DRAT + drat-trim, CPU | `lrat/receipt.json` | cross-checked | composite CPU | 4 | 1.1803 | 1.5270 | **REJECT** |
| same, CPU, one checker charged | `lrat/receipt.json` | single | composite CPU | 4 | 0.4974 | 0.7042 | **OPT_IN_EVIDENCE_BACKED** |
| same, retained artifact bytes | `lrat/receipt.json` | cross-checked | retained bytes | 2 | 0.6237 | 0.6824 | **OPT_IN_SINGLE_CASE** |
| sender-only KMT, 100k cap | `kmt/receipt.json` | — | composite CPU | 2 | 1.2504 | 1.3758 | **REJECT** |
| sender-only KMT, 1M cap | `kmt/receipt.json` | — | composite CPU | 2 | 1.2339 | 1.4579 | **REJECT** |
| one-colour lex/SMS | `sms/ab_summary.json` | — | composite CPU | 2 | 0.7949 | 0.8006 | **REJECT** |

Verdict JSON per row: `receipts/<name>.json`; the decision function is invoked
with `--mode audit` because pre-registration is not recorded in any published
receipt (rule `R3_prereg`, waived there and *not* waived in `admission` mode).

## 2. Native LRAT: what is adoptable is the format, not a speedup

Independently re-read from the receipt and the on-disk checker logs (no proof
re-run): every case's lrat-trim replay exits 20 **and** prints the literal
`s VERIFIED` line, drat-trim prints it on the DRAT side, and the second
(unverified) Python checker exits 20. Per-case search counters are identical
between the two arms, so this pipeline cannot be a CDCL speedup by construction;
only certificate cost can change.

Composite CPU, treatment / baseline (drat-trim route = 1):

| case | conflicts | one checker | + independent checker |
|---|---|---|---|
| H7 | 23 143 | 0.6701 | 0.9794 |
| H8 | 49 226 | 0.7042 | **1.0246** |
| N14 | root propagation only | 0.4865 | **1.5270** |
| R11 | 1 | 0.2667 | **1.2667** |

Geomean over the four cases: 0.4974 with one checker, **1.1803** with the second
checker the experiment itself used. Neither checker is formally verified, so the
policy's default trust level charges both and the CPU saving is **not
admissible**; three of four cases regress once the trust cost is paid. The
coordinator's phrase "gives back most of that saving, slightly more on H8" is,
in the policy's terms, a net regression overall (1.1803) with the smallest case
regression on H8 (1.0246).

Bytes are not uniform either:

| case | DRAT | untrimmed LRAT | retained/trimmed LRAT | retained DRAT reproduced? |
|---|---|---|---|---|
| H7 | 7 114 766 | 9 728 618 (1.37×) | 4 056 058 (**0.57×**) | yes |
| H8 | 9 529 642 | 14 594 230 (1.53×) | 6 503 105 (**0.68×**) | yes |
| N14 | 2 308 201 | 2 393 381 (1.04×) | 2 494 126 (1.08×) | **no** |
| R11 | 6 707 | 24 969 (3.72×) | 520 186 (77.6×) | **no** |

The *emitted* native LRAT is larger than DRAT in all four cases; the saving
appears only after trimming, and trimming is not even monotone (N14, R11 grow:
their deletion-id lists dominate). On N14/R11 the retained DRAT was not
reproduced by the fresh run (`fresh_drat_matches_retained=false`), so those two
byte comparisons are invalid and are excluded by rule `R10` — which is why the
byte claim is `OPT_IN_SINGLE_CASE` (H7, H8 only).

**Adoption boundary.** Eligible: an explicit opt-in proof-format choice, gated on
a caller-supplied, hash-pinned checker, with the verdict scope pasted in and the
trust level named. Not eligible: any claim that LRAT makes closure cheaper. Also
excluded by `R2`: the DRAT→LRAT *elaboration* route, whose trimmed variants all
needed `--relax` (`A_elab_trimmed_variant_needs_relax=true` on all four cases).

## 3. Sender-only KMT: a capability, not a speedup

Composite CPU (search + bootstrap + parse), treatment / stock:

| cap | seed 0 (AB) | seed 1 (BA) | geomean | peak RSS |
|---|---|---|---|---|
| 100k | 1.1365 | 1.3758 | 1.2504 | 87.6/86.5 MB vs 96.6/96.7 MB |
| 1M | 1.0444 | 1.4579 | 1.2339 | 99.3/108.8 MB vs 116.5/126.7 MB |

All eight runs `OPEN` at their caps. The RSS reduction is consistent (≈10 % at
100k, ≈13 % at 1M) and the encoded CNF is smaller (13 364 vars / 176 660 clauses
vs 19 533 / 184 335), but memory is not what is being bought here, and the
search cost regresses at both caps in both seeds. Additional deficits recorded:
the solver binary is not hash-pinned (only `CaDiCaL 1.9.5` + `pysat 1.9.dev22`),
there is no unsound/trajectory control, and order is confounded with seed (each
seed measured in one order only), so the design cannot separate seed from order.
Neither cap is an admission measurement at 1M anyway (≈60 s CPU per call).

**Adoption boundary.** Reject as a speedup. If the encoding is ever wanted for
its smaller formula or RSS, it must be admitted as an `encoding` override on its
own record with ≥2 seeds × 2 orders and a regime where the regression disappears.

## 4. One-colour lex/SMS: the control explains the effect

Composite CPU, treatment / baseline: 0.8006 (AB) and 0.7892 (BA), geomean
**0.7949** — a nominal 20 % gain that the cost rule alone would accept. The
experiment's own unsound control (same 765 clauses with one negated literal)
gives **0.7710**, i.e. an equally large apparent gain from a deliberately
unsound perturbation. The premise the clauses need — physical model-set
invariance — is unproved (`R7`), no input CNF or solver binary hash is recorded
(`R2`, `R4`), and there is one seed only (`R9`). The effect is therefore a
trajectory artefact, not a mechanism.

**Adoption boundary.** Reject. Do not re-fit this design around the corrupted
control; the control is the refutation.

## 5. Live validity traps, now enforced (board finding `d4/f1`)

`m8` reports three traps on the same retained parent+cube with the incumbent
PySAT CaDiCaL 1.9.5 binding. I did not re-run them (the retained parent+cube CNF
is not on disk in this workspace; a bounded search for a 3.3–3.7 MB CNF found
none, and regenerating it belongs to its owner). They are cited as evidence and
are now *rules*, so no future record can pass with the defect:

| trap (`d4/f1`) | what it invalidates | rule |
|---|---|---|
| `configure({'zzz_not_an_option':1})` leaves counters bit-identical: the binding accepts unknown option names silently | API acceptance is not implementation; an inert arm cannot explain a CPU change | `R9`: for `options`/`engine`/`search`, identical counters in every cell → `INCOMPLETE` |
| real knobs do move counters at cap 2 000 | short probes are usable as *effect* checks, not as cost evidence | `R8` counts only cost cells at the evaluation cap |
| seeds 0/1 identical at cap 2 000 but sharply different at 100 000 | a matched-seed panel validated at a short cap is effectively single-seed | `R9`: seeds must diverge in the baseline arm at the evaluation cap |

Consequence for the option-tuning direction (`d4`) and for any engine panel
(`d1`): the pre-registered fingerprint check must be taken at the evaluation cap,
and a "gain" from an arm whose counters did not move is noise by construction.

## 6. Claims with no record

Policy verdict for these is `INCOMPLETE` (nothing to evaluate), which is not
adoption. Listed so that nobody mistakes prose for evidence:

* `NATIVE.md`: search-only policy made 1.65× the conflicts in the same 120 s
  budget; native default "in the same range as the PySAT incumbent" on two
  parents — two-instance prose, no receipt. Under this policy the 1.65× number
  is also the reason conflicts cannot be a primary metric.
* Global / pinned / arm-3 MCF, full static lex, conditional-boundary Sinz, the
  full FKR census (>10 000 early cases), raw cross-parent learned-clause import,
  one-colour generated lex: already rejected on independent grounds. The policy
  adds a machine criterion (derivation pin, control, per-cell rule), it does not
  re-litigate those numbers.

## 7. What this implies for the live directions

| direction | must carry to pass `R` | expected outcome on present evidence |
|---|---|---|
| engine comparison (backend panel) | both binary hashes, `engine` class, ≥4 paired cells, no 1M-cap admission runs | open |
| one-shot preprocessing | derivation of the derived CNF from the host, `relax_used=false`, preprocessing CPU charged, root hypotheses untouched | open, but startup+replay must be inside the composite |
| proof-derived clause reuse | derivation from the *exact* parent, not subsumed by host units/bank, benchmark on that same parent | open; report-only if subsumed |
| native-LRAT opt-in patch | trust level declared, checker pin, `s VERIFIED`, `OPEN` handling | format only (§2) |
| physical/emitted bridge | a measured record, or the gate cannot admit it | out of scope of this policy |
| option tuning | `binding=budget_hash`, per-seed sign agreement, no cap-artefact | open |

## 8. Scope

This is a bounded audit of four published receipts at `e856d75` plus a policy and
its tests. It establishes no Ramsey bound, closes no profile, does not touch
`ChainReady`, and changes no default. `51 <= R_4(3) <= 62` stands; `<=58` and
`<=60` are not established here. Total solver CPU spent: **0 s** — every number
above is re-derived from committed receipts and their pinned checker logs.
