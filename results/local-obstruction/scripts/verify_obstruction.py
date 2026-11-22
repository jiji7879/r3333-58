"""Standalone verifier for out/three_word_certificates.json.

Reads the .wit file named in each certificate and re-derives everything:
  * the three named vertices really lie in the arm whose root colour is k;
  * each word has length 15 and exactly five 0s;
  * for each of the three pairs the admissible-colour set
        L(x,y) = { f != k : M_f(x) cap M_f(y) = empty }
    equals exactly the singleton {c}, for the same c on all three pairs;
  * hence all three internal edges of the triangle are forced to c, which is a
    monochromatic triangle: the arm is not realisable.
Nothing else is assumed.  Exit status 0 iff every certificate checks out.
"""
import sys, json, os, itertools

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"
HERE = os.path.dirname(os.path.abspath(__file__))

def load(path):
    words, arms = {}, {}
    for ln in open(path):
        t = ln.split()
        if not t or t[0].startswith("#"):
            continue
        if t[0] == "word":
            words[int(t[1])] = tuple(map(int, t[2:]))
        elif t[0] == "arm":
            arms[int(t[1])] = list(map(int, t[2:]))
    return words, arms

def M(word, f):
    return frozenset(a for a, c in enumerate(word) if c == f)

def main():
    certs = json.load(open(os.path.join(HERE, "..", "out", "three_word_certificates.json")))
    ok = True
    for cert in certs:
        path = os.path.join(ROOT, cert["path"])
        words, arms = load(path)
        k = cert["arm_root_colour"]
        vs = cert["vertices"]
        c = cert["colour"]
        errs = []
        for v in vs:
            if v not in arms.get(k, []):
                errs.append("vertex %d is not in arm %d" % (v, k))
            if tuple(cert["words"][vs.index(v)]) != words[v]:
                errs.append("word %d in the certificate does not match the file" % v)
            wd = words[v]
            if len(wd) != 15:
                errs.append("word %d has length %d" % (v, len(wd)))
            if wd.count(0) != 5:
                errs.append("word %d has %d zeros" % (v, wd.count(0)))
        lists = []
        for a, b in itertools.combinations(vs, 2):
            L = sorted(f for f in range(4) if f != k and not (M(words[a], f) & M(words[b], f)))
            lists.append(L)
            if L != [c]:
                errs.append("L(%d,%d) = %s, expected [%d]" % (a, b, L, c))
        forced = all(L == [c] for L in lists)
        print("%-30s arm %d  triple %-12s  pair lists %s  colour %d  -> %s"
              % (cert["witness"], k, str(vs), lists, c,
                 "INFEASIBLE (monochromatic triangle forced)" if forced and not errs
                 else "FAIL " + "; ".join(errs)))
        ok &= forced and not errs
    print()
    print("%d certificates, %s" % (len(certs), "ALL VERIFIED" if ok else "FAILURES PRESENT"))
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
