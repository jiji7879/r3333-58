#!/usr/bin/env python3
"""Execute current MCTS.py on a toy game to test two-simulation root depth.

This is a control-flow check only; it is not a SAT, UNSAT, or colouring test.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

M = Path(__file__).resolve().parent.parent
SOURCE = M / '.scratch/AlphaMapleSAT/alphamaplesat'
sys.path.insert(0, str(M / '.scratch/ams_stubs'))
sys.path.insert(0, str(SOURCE))
from MCTS import MCTS


class Board:
    def __init__(self, depth=0, path=()):
        self.depth = depth
        self.path = path
        self.total_rew = float(depth + 1)
        # Indices 1,2 and their complements 3,4; index 0 is the dummy action.
        self.prob = np.array([0.0, 0.4, 0.3, 0.3, 0.0])

    def get_complement_action(self, action):
        return action + 2 if action <= 2 else action - 2


class ToyGame:
    def __init__(self, terminal_depth):
        self.terminal_depth = terminal_depth
        self.terminal_tests = []
        self.expanded_depths = []

    def getCanonicalForm(self, board):
        return board

    def getActionSize(self):
        return 5

    def stringRepresentation(self, board):
        # As in KSGame, distinguish states by their complete prior-action path.
        return str(board.path)

    def getGameEndedMCTS(self, board):
        self.terminal_tests.append(board.depth)
        return 1.0 if board.depth >= self.terminal_depth else None

    def getValidMoves(self, board):
        return np.array([0, 1, 1, 1, 0])

    def get_copy(self):
        return self

    def getNextState(self, board, action):
        self.expanded_depths.append(board.depth + 1)
        return Board(board.depth + 1, board.path + (action,))


def run(terminal_depth):
    # Each real adapter invocation is a fresh process with this same fixed seed.
    np.random.seed(42)
    game = ToyGame(terminal_depth)
    args = {'numMCTSSims': 2, 'debugging': False, 'MCTSmode': 0,
            'cpuct': 10.0, 'varpen': 0.0}
    from utils import dotdict
    mcts = MCTS(None, dotdict(args), [], None)
    probabilities = mcts.getActionProb(game, Board(), temp=0)
    selected = [i for i, value in enumerate(probabilities) if value]
    nonzero_root_actions = sorted(a for (s, a), n in mcts.Nsa.items()
                                  if s == '()' and n != 0)
    return {
        'terminal_depth': terminal_depth,
        'selected_actions': selected,
        'nonzero_root_actions': nonzero_root_actions,
        'terminal_test_depths': game.terminal_tests,
        'expanded_depths': game.expanded_depths,
        'max_depth_reached': max(game.terminal_tests),
        'root_visit_count': mcts.Ns.get('()', 0),
    }


results = [run(2), run(22)]
for result in results:
    assert result['max_depth_reached'] == 1, result
    assert result['terminal_test_depths'] == [0, 1, 1], result
    assert len(result['nonzero_root_actions']) == 2, result
    assert result['root_visit_count'] == 1, result
# The horizon setting cannot change the fresh-root decision after two simulations.
assert results[0]['selected_actions'] == results[1]['selected_actions']
output = {
    'schema': 'ams-mcts-two-simulation-root-control/v1',
    'source': str(SOURCE / 'MCTS.py'),
    'source_sha256': hashlib.sha256((SOURCE / 'MCTS.py').read_bytes()).hexdigest(),
    'meaning': 'actual MCTS.py control flow on a toy nonterminal game; no CNF verdict',
    'pass': True,
    'runs': results,
}
out = M / 'results/mcts-horizon-control.json'
out.write_text(json.dumps(output, indent=2, sort_keys=True) + '\n')
print(json.dumps(output, sort_keys=True))
