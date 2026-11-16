# The two encodings in this batch

The 96 cases were attempted twice: the first pass at 12 s / 400k conflicts with
`full_root = False`, and the 15 cut-offs at 70 s / 2.4M conflicts with
`full_root = True`. Ninety-five certificates exist, with two different recipes,
and both are sound refutations of their case.

What the two recipes add on top of the host CNF and the fixed root units:

* **First pass** (`tables, total_critical, full_root = T, T, F`): a per-arm
  threshold `s_a >= t_a`, plus `s_crit >= 2M - 57` over the critical arms.
  Both are consequences of `H(r) >= w(r)`, used because they are cheap.
* **Retry** (`T, T, T`): the full cardinality `H(r) >= w(r)` over all 57
  neighbours. Instrumenting `dense.marked_threshold` on a `(15,15,15,12)` row
  gives `root_goal = 44` with 56 selectors and one vertex already forced,
  i.e. at least 45 of 57 senders — exactly `w(r) = M = 45`.

Since the retry formula is the case hypothesis itself (and the first-pass
formula is a consequence of it), a replay against either closes the case. The
certificate records which recipe it used (`verified.json.recipe`), and the
release verifier regenerates the CNF from that recipe, so the two cannot be
confused at replay time.

The one thing the ledger does not do is pin the recipe per case: it carries no
`recipe` field, so `--require-complete` cannot enforce that every certificate
uses a formula implied by its case. Here both recipes are implied. A future
shard should record the recipe in the ledger rather than trusting each
certificate to name one.
