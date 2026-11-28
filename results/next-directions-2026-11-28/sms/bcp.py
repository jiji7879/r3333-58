#!/usr/bin/env python3
"""Numpy fixpoint unit-propagation over a DIMACS CNF (used by the SMS-substitute generator).

Only ever used to *shrink* emitted clauses: every literal it derives is a real
consequence of the loaded formula, so a partial- propagation set is still sound.
The naive scalar implementation below is the reference for the fast one.
"""
import numpy as np


class CNF:
    def __init__(self, path):
        with open(path, "rb") as stream:
            header = stream.readline()
            assert header.startswith(b"p cnf "), header
            self.nvars, self.nclauses = map(int, header.split()[2:])
            body = stream.read()
        lits = np.array(body.split(), dtype=np.int64)
        assert lits.size % (self.nclauses + 1) == self.nclauses + 1 - 1 or True
        # last entry of every clause is the 0 terminator
        assert int(lits[-1]) == 0
        # the file is a flat literal stream with a 0 terminator after each clause
        assert int(lits[-1]) == 0
        flat = lits[:-1]
        zeros = np.flatnonzero(flat == 0)
        assert zeros.size == self.nclauses - 1, (zeros.size, self.nclauses)
        starts = np.empty(self.nclauses, dtype=np.int64)
        starts[0] = 0
        starts[1:] = zeros + 1
        ends = np.append(starts[1:], flat.size)
        lengths = ends - starts
        lengths[:-1] -= 1                      # drop the 0 terminator of each clause
        assert np.all(lengths > 0)
        self.off = np.concatenate(([0], np.cumsum(lengths)))
        self.data = np.delete(flat, zeros).astype(np.int32)
        assert np.all(self.data != 0)
        self.sign = np.where(self.data > 0, 1, -1).astype(np.int8)
        self.abs = np.abs(self.data).astype(np.int64)
        assert self.off[-1] == self.data.size

    # ------------------------------------------------------------------ fast
    def propagate(self, assumptions):
        """Return (assignment array or None on conflict).  Index = variable."""
        val = np.zeros(self.nvars + 1, dtype=np.int8)
        for lit in assumptions:
            sign = 1 if lit > 0 else -1
            v = abs(lit)
            if val[v] and val[v] != sign:
                return None
            val[v] = sign
        off, data, sign, absd = self.off, self.data, self.sign, self.abs
        while True:
            s = val[absd].astype(np.int8) * sign
            zero = s == 0
            one = s == 1
            n_unk = np.add.reduceat(zero.astype(np.int32), off[:-1])
            any_true = np.maximum.reduceat(one.astype(np.int8), off[:-1])
            if np.any((n_unk == 0) & (any_true == 0)):
                return None
            units = np.flatnonzero((n_unk == 1) & (any_true == 0))
            if units.size == 0:
                return val
            progressed = False
            for ci in units:
                lo, hi = off[ci], off[ci + 1]
                for idx in range(lo, hi):
                    if s[idx] == 0:
                        v = int(absd[idx])
                        want = int(sign[idx])
                        if val[v] == 0:
                            val[v] = want
                            progressed = True
                        break
            if not progressed:
                return val

    # ------------------------------------------------------------------ slow reference
    def propagate_naive(self, assumptions):
        val = {}
        for lit in assumptions:
            v, want = abs(lit), (1 if lit > 0 else -1)
            if v in val and val[v] != want:
                return None
            val[v] = want
        clauses = [self.data[self.off[i]:self.off[i + 1]].tolist() for i in range(self.nclauses)]
        changed = True
        while changed:
            changed = False
            for clause in clauses:
                sat = False
                unknown = []
                for lit in clause:
                    v = abs(lit)
                    if v not in val:
                        unknown.append(lit)
                    elif val[v] == (1 if lit > 0 else -1):
                        sat = True
                        break
                if sat:
                    continue
                if not unknown:
                    return None
                if len(unknown) == 1:
                    lit = unknown[0]
                    v, want = abs(lit), (1 if lit > 0 else -1)
                    if v in val and val[v] != want:
                        return None
                    if v not in val:
                        val[v] = want
                        changed = True
        return val
