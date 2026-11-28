# Independent reading of the submitted claim (kind: model)

I read m1's `proof.md`, the two transfer scripts and both receipts, and the written claim in `2-proof.md`. The statement's quantifiers match its proof:

* All three vertices are distinct and the pivot colour ranges over the four physical colours.
* $Q$ is obtained by resolving the palette for $E(v,w,c)$ with the no-monochromatic-triangle clause at exactly that literal. The resulting signs and distinguished vertices are `-E(u,w,c) OR -E(u,v,c) OR OR_{d != c}E(v,w,d)`. m4's corrected d3/f11 statement agrees; its earlier f7 swapped a vertex subscript and is superseded.
* $R$ requirespositive case-unit premises as well as the host palette and triangle. The proof does not deduce those pins from an unsupported general guard.
* Auxuliary-extended parents retain the physical clauses. The transfer proof does not erase them from a native case refutation; the original-only physical scope is explicitly separate and includes only host plus case units.
* A source or destination raw parent refutation and a false-cube clause implication are different obligations. Each final certificate uses the correct one.

The previous accepted clause banks concern larger square/spoke, pivot, and guard constructions. There is no logical leap from a theorem's physical literal form to those banks or to a new degree constraint. A separate low-complexity schema that is implied by palette/triangle does not acquire their strength.

The native parent identities and case delimitation were checked against the full receipts. Neither historical certification status nor a solver UNSAT exit alone does the proof work: fresh DRAT outputs were read by `drat-trim`, while small clause implications were separately checked as RUP. All three case and two schema claims are therefore supported by the clean proof. No gap found in the statement as scoped.
