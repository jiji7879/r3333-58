# Two axiom-free laws, and two facts that stay outside the kernel

`K58Laws.lean` from swarm `smwv2qfbi/m6`. The judge compiled it and ran `#print axioms` on each
result rather than accepting the summary.

| theorem | axioms (checked here) | status |
| --- | --- | --- |
| `K58.no_shared_colour` | **none** | axiom-free |
| `K58.class_indep` | **none** | axiom-free |
| `K58.T_mono`, `K58.U_no_zero` | `[propext]` | inside the campaign's set |
| `K58.T_no_indep6_*`, `K58.U_no_indep6_*` | `[…, native_decide.ax]` | **outside** the set |
| `K58.word_bound_{T,U}_{1,2,3}` | `[…, native_decide.ax]` | **outside** the set |

## What this settles

- **The word law is now proved, not assumed**: if `x` and `y` share a neighbour `a` of colour `k`
  then `colour(x,y) ≠ k` — with no axioms at all.
- **A sender's colour-class on `A` is colour-`k` independent**, again axiom-free.
- Both classified 15-templates are monochromatic-triangle-free with colours 1..3, on `propext` only.

## What it does not settle

The two results that the word counts rest on — `alpha_k(T) = alpha_k(U) = 5` and the 44-vertex
**word bound** (every ordinary-arm vertex has at most five colour-`k` neighbours in `A`) — carry a
`native_decide` axiom. The campaign does not accept those as kernel-checked.

The judge tried to upgrade one: `by decide` fails with *maximum recursion depth has been reached*, and
`set_option maxRecDepth 4000000` gets past that only to exhaust heartbeats. **Enumeration does not
reach the kernel in practical time**; a structural proof of `alpha = 5` and of the word bound is what
would be needed. Do not re-attempt by enumeration.

This is still an improvement on the previous state, where the `254,628` and `254,088` word counts
rested on an assertion. They now rest on a computation that has been machine-checked under a trusted
compiler — weaker than a kernel proof, stronger than an assertion.
