# Why the retry certificates are here and not in `evidence/`

Fourteen of the fifteen cut-off cases from batch 1 close at the retry budget
(70 s, 2.4M conflicts). Their certificates are in `retry-stronger-formula/`,
not in `evidence/`, because **they do not refute the same formula**.

The retry tier is run with `full_root=True`. In `dense.marked_threshold` that
sets `root_goal = critical_mass`: a cardinality constraint requiring *every*
vertex of *every* critical arm to send a ticket. The first-pass tier has
`root_goal = 0` and only the per-arm threshold.

The root hypothesis is `H(r) >= w(r)` with `w = M` the critical mass. What
that implies about senders inside the critical arms is

```
s_crit >= M - (57 - M) = 2M - 57
```

because at most `57 - M` senders can sit outside the critical arms. That is
exactly the `total_critical` bound the first-pass encoding uses
(`total = 2*critical_mass - sum(profile)`). It is **not** `s_crit = M`.

For `(15,15,15,12)`: the sound bound is 33 senders among the 45 critical
vertices; `full_root` demands all 45. A proof that no colouring reaches 45
does not exclude a colouring with 40, so it does not close the case.

The release verifier cannot see the difference. `cover_evidence.inspect_case`
regenerates the formula from `evidence["recipe"]`, which is read from the
certificate, and the ledger row carries no recipe to compare against. Built
over a root containing these fourteen certificates, the manifest reports
`CERTIFIED: 95` — see `manifest-with-retry.json`. Every one of the 95 proofs
replays; fourteen of them are proofs of the wrong formula.

This is either a missing lemma in the bundle (something that forces a root
with all critical vertices sending, which the `H >= w` averaging does not) or
a soundness gap in the retry tier. Until it is settled, retry closures should
be reported separately and never counted as cover closures, and
`--require-complete` should be treated as unable to catch this class of error.

The 81 first-pass certificates in `evidence/` are unaffected: their recipe is
`full_root = False`, which is the formula the ledger case denotes.
