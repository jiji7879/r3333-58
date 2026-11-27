# Audit four new K58 proof and local-clause archives

The person supplied `K58_general_spoke_test.zip`, `K58_rank1300_proof_mining.zip`, `K58_rank1300_comparison_proofs.zip`, and `K58_rank1300_projection_proofs.zip`. Assess the soundness of their local 2-SAT rules, mined direct clauses, square transfers, projection/refutation scopes and comparison certificates. Distinguish original unrestricted parent proofs from projection/augmented queries, local models and timing-only results.

Done means: independent DIMACS/hashes and parent scope; explanation of baseline proof/core identities; native RUP/LRAT checks on representative and appropriate full streams; local SAT/model validation; negative controls; and separate assessment of measured versus amortized solver benefit. A full original proof is not a local SAT model, a projection UNSAT is not a projection SAT certificate, and OPEN is never SAT or UNSAT. No unverified proof or timing result may be reported as established.

No production ledger or 1,300-row search is wanted. The four directions share a 45 CPU-minute-per-member native-checking budget and generate no publication archives in the repository. Text/scripts/small receipts belong in this folder; large proof streams stay in `.scratch` or the supplied attachments.
