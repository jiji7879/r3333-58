"""Independent from-scratch strict-RUP check of the shipped K15 theorem proof.

This does not call drat-trim and does not call any SAT solver.  It builds the
package's own K15 query (block.formula(True)) in memory, parses the shipped
binary DRAT trace itself, and checks every added clause by unit propagation
against the base formula plus all earlier additions, with *all deletion
records ignored* (the strictly stronger addition-only / RUP check).

Exit status 0 iff every addition after the base formula is RUP and the empty
clause is derived.
"""
import gzip
import hashlib
import itertools
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PKG = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / 'pkg'
sys.path.insert(0, str(PKG / 'next'))


def parse_binary_drat(raw):
    """Decode CaDiCaL binary DRAT: 'a'/'d' prefix bytes, 7-bit varint literals."""
    out = []
    i, n = 0, len(raw)
    kind = 'a'
    lits = []

    def varint(i):
        v, shift = 0, 0
        while True:
            b = raw[i]
            i += 1
            v |= (b & 0x7F) << shift
            if not b & 0x80:
                return v, i
            shift += 7

    while i < n:
        if raw[i] in (0x61, 0x64):
            if lits:
                out.append((kind, lits))
                lits = []
            kind = chr(raw[i])
            i += 1
            continue
        v, i = varint(i)
        if v == 0:
            out.append((kind, lits))
            lits = []
            kind = 'a'
            continue
        lits.append(-(v >> 1) if v & 1 else (v >> 1))
    if lits:
        out.append((kind, lits))
    return out


class Propagator:
    """UP over an addition-only clause database with per-check stamps."""

    def __init__(self, clauses, nv):
        self.clauses = [list(c) for c in clauses]
        self.nv = nv
        self.occ = [[] for _ in range(2 * nv + 2)]       # literal -> clause ids
        self.stamp = [0] * 4096
        self.false_count = [0] * 4096
        self.version = 0
        self.units = []
        for cid, cl in enumerate(self.clauses):
            for l in cl:
                self.occ[self.idx(l)].append(cid)
            if len(cl) == 1:
                self.units.append(cl[0])

    @staticmethod
    def idx(l):
        return 2 * l if l > 0 else -2 * l + 1

    def add(self, cl):
        cid = len(self.clauses)
        self.clauses.append(list(cl))
        while len(self.stamp) <= cid:
            self.stamp.append(0)
            self.false_count.append(0)
        for l in cl:
            self.occ[self.idx(l)].append(cid)
        if len(cl) == 1:
            self.units.append(cl[0])
        return cid

    def rup(self, cl):
        """True iff cl has a unit-propagation refutation of its negation."""
        self.version += 1
        stamp = self.stamp
        count = self.false_count
        version = self.version
        # assignment value[var] = +1 true / -1 false, 0 unassigned, via trail
        value = {}
        trail = []
        queue = []
        for l in cl:
            val = -1 if l > 0 else 1   # -l is assumed true, so l is false
            v = abs(l)
            if value.get(v) == -val:
                return True            # tautological clause, trivially RUP
            if value.get(v, 0) == 0:
                value[v] = val
                trail.append(v)
                queue.append(-l)       # the literal that became true
        for u in self.units:
            v = abs(u)
            want = 1 if u > 0 else -1
            have = value.get(v, 0)
            if have == 0:
                value[v] = want
                trail.append(v)
                queue.append(u)
            elif have != want:
                return True
        head = 0
        while head < len(queue):
            l = queue[head]
            head += 1
            for cid in self.occ[self.idx(-l)]:
                c = self.clauses[cid]
                if stamp[cid] != version:
                    stamp[cid] = version
                    count[cid] = 1
                else:
                    count[cid] += 1
                if count[cid] == len(c):
                    return True
                if count[cid] == len(c) - 1:
                    # c has exactly one literal that is not already false
                    rest = None
                    for x in c:
                        want_x = 1 if x > 0 else -1        # value of abs(x) that makes x true
                        if value.get(abs(x), 0) == -want_x:
                            continue                        # x is false, skip it
                        rest = x
                        break
                    if rest is None:
                        return True
                    v = abs(rest)
                    want = 1 if rest > 0 else -1
                    have = value.get(v, 0)
                    if have == 0:
                        value[v] = want
                        trail.append(v)
                        queue.append(rest)
                    elif have != want:
                        return True
        # empty clause in the database?
        for cid, c in enumerate(self.clauses):
            if not c:
                return True
        return False


def main():
    import block
    f = block.formula(True)
    nv = f.nv
    text = 'p cnf %d %d\n' % (nv, len(f.clauses)) + ''.join(
        ' '.join(map(str, c)) + ' 0\n' for c in f.clauses)
    print('query sha256', hashlib.sha256(text.encode()).hexdigest(),
          '| nv', nv, '| clauses', len(f.clauses))
    fp = block.formula(False)
    textp = 'p cnf %d %d\n' % (fp.nv, len(fp.clauses)) + ''.join(
        ' '.join(map(str, c)) + ' 0\n' for c in fp.clauses)
    print('path  sha256', hashlib.sha256(textp.encode()).hexdigest(),
          '| nv', fp.nv, '| clauses', len(fp.clauses))

    raw = gzip.decompress((PKG / 'next/matching.drat.gz').read_bytes())
    recs = parse_binary_drat(raw)
    adds = [l for k, l in recs if k == 'a']
    dels = [l for k, l in recs if k == 'd']
    print('records', len(recs), '| additions', len(adds), '| deletions', len(dels),
          '| deletions ignored (addition-only mode)')

    prop = Propagator(f.clauses, nv)
    base = len(f.clauses)
    bad = []
    empty_seen = False
    for step, cl in enumerate(adds, 1):
        if not cl:
            empty_seen = True
        if not prop.rup(cl):
            bad.append((step, cl))
            if len(bad) > 5:
                break
        if cl:
            prop.add(cl)
    print('non-RUP additions:', len(bad), bad[:5])
    print('empty clause present among additions:', empty_seen)
    ok = not bad and empty_seen
    print('RESULT', 'STRICT RUP VERIFIED' if ok else 'NOT VERIFIED BY RUP ALONE')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
