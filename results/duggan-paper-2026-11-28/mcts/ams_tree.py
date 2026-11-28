#!/usr/bin/env python3
"""Run upstream AlphaMapleSAT on a K58 CNF with an explicit split-variable pool.

This is a heuristic adapter only: it changes which variables are *probed*, never
adds/deletes clauses or drops either sign of a split.  The caller must audit the
resulting full binary cover separately.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import time


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--upstream', type=Path, required=True)
    p.add_argument('--cnf', type=Path, required=True)
    p.add_argument('--pool-json', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--metadata', type=Path, required=True)
    p.add_argument('--depth', type=int, default=2)
    p.add_argument('--sims', type=int, default=10)
    p.add_argument('--rollout-extra', type=int, default=0,
                   help='extra MCTS depth beyond emitted depth; upstream default is 20')
    p.add_argument('--max-literals', type=int, default=6612)
    args = p.parse_args()
    if args.depth < 1 or args.sims < 1 or args.rollout_extra < 0:
        raise ValueError('depth and sims must be positive')
    upstream = args.upstream.resolve()
    source_dir = upstream / 'alphamaplesat' if (upstream / 'alphamaplesat').is_dir() else upstream
    sys.path.insert(0, str(source_dir))
    # wandb and coloredlogs are supplied as offline no-op stubs by PYTHONPATH.
    from main import args_f
    from ksgraph.KSGame import KSGame
    from ksgraph.EvalVarCalc import MarchPysatPropagate
    from Coach import Coach
    from utils import dotdict

    doc = json.loads(args.pool_json.read_text())
    if doc.get('schema') != 'ams-k58-split-pool/v1':
        raise ValueError('unrecognised pool schema')
    pool = doc['variables']
    if (not pool or len(set(pool)) != len(pool)
            or any(type(v) is not int or not 1 <= v <= args.max_literals for v in pool)):
        raise ValueError('invalid variable pool')
    if doc['max_literals'] != args.max_literals:
        raise ValueError('pool/action-space mismatch')

    # Upstream's construct_freevars otherwise returns every variable in 1..m
    # having a binary implication.  Preserve its API but apply the explicit,
    # recorded pool before LimitTop3 and PUCT, avoiding 2*m BCP calls per node.
    def restricted_freevars(self, binary_implications):
        if self.m != args.max_literals:
            raise RuntimeError('unexpected upstream action-space size')
        return list(pool)
    MarchPysatPropagate.construct_freevars = restricted_freevars
    # The 2024 revision predates construct_freevars and instead calls
    # Node.valid_cubing_lits directly. Restriction of this predicate is needed
    # for the same experiment there; the semantics is set-difference only.
    from ksgraph.EvalVarCalc import Node as EvalNode
    def restricted_valid(self, literals_all, *unused):
        negated_prior = [-lit for lit in self.prior_actions]
        negated_unsat = [-lit for lit in self.unsat_learnt_actions]
        signed_pool = set(pool).union(-v for v in pool)
        return list((signed_pool.intersection(literals_all))
                    - set(self.prior_actions) - set(negated_prior)
                    - set(self.unsat_learnt_actions) - set(negated_unsat))
    EvalNode.valid_cubing_lits = restricted_valid

    settings = dotdict(dict(args_f))
    settings.update({
        'debugging': False, 'verbose': False, 'wandb_logging': False,
        'MCTSmode': 0, 'LIMIT_TOP_3': True,
        'd': args.depth, 'n': -1, 'nMCTSEndOfG': -1,
        'STEP_UPPER_BOUND': args.depth, 'VARS_TO_ELIM': None,
        # Terminate MCTS evaluation at the same shallow horizon as the emitted
        # tree.  The paper permits non-terminal rewards; its default is 20.
        'STEP_UPPER_BOUND_MCTS': args.rollout_extra,
        'MAX_LITERALS': args.max_literals, 'm': args.max_literals,
        'order': 58,  # retained for Duggan's 2024 graph-specific KSGame API
        'numMCTSSims': args.sims, 'cpuct': 10.0, 'varpen': 0.0,
        'o': str(args.out.resolve()),
    })
    started = time.monotonic()
    game = KSGame(args=settings, filename=str(args.cnf.resolve()))
    coach = Coach(game, None, settings)
    coach.nolearnMCTS()
    elapsed = time.monotonic() - started
    if not args.out.is_file():
        raise RuntimeError('upstream cuber did not emit the requested cube file')
    metadata = {
        'schema': 'ams-k58-tree/v1',
        'upstream': str(upstream), 'cnf': str(args.cnf.resolve()),
        'pool': doc, 'depth': args.depth, 'sims': args.sims,
        'rollout_horizon': f'emitted depth + {args.rollout_extra} (STEP_UPPER_BOUND_MCTS)',
        'max_literals': args.max_literals, 'limit_top_3': True,
        'cpuct': 10.0, 'varpen': 0.0, 'elapsed_s': elapsed,
        'leaves': len(coach.leaf_counter * [0]),
        'adaptation': 'construct_freevars restricted to recorded variables; no clause or branch changes',
    }
    args.metadata.write_text(json.dumps(metadata, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'out': str(args.out), 'leaves': coach.leaf_counter,
                      'elapsed_s': elapsed}, sort_keys=True))


if __name__ == '__main__':
    main()
