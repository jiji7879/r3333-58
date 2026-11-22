"""Referee check on the record's word-level numbers.

Recomputes, from the template files alone:
  * the number of admissible words (maps A -> {0,1,2,3} with exactly five 0s and
    every ordinary part M_f independent in template colour f-1);
  * alpha of each template colour class and the number of maximum independent sets;
  * the number of extremal words (some ordinary part empty).

Record claims checked: 254,628 admissible T^- words and 254,088 U^- words
(PROFILE §2/§16); "each colour graph of the T^- template has alpha = 5 with exactly
eleven maximum independent 5-sets, so ... there are only 18 extremal words"
(WALL §24).
"""
import sys, os, itertools, json, glob

ROOT = "/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo"

def load(path):
    toks = open(path).read().split()
    n, k = int(toks[0]), int(toks[1])
    vals = list(map(int, toks[2:2 + n * n]))
    return n, k, [vals[i * n:(i + 1) * n] for i in range(n)]

def indep_sets_of_size(n, adj, size):
    out = []
    def rec(start, cur):
        if len(cur) == size:
            out.append(tuple(cur)); return
        for v in range(start, n):
            if all(not (adj[v] >> u) & 1 for u in cur):
                rec(v + 1, cur + [v])
    rec(0, [])
    return out

PAT = sys.argv[1] if len(sys.argv) > 1 else "k1[56]_*.col"
for p in sorted(glob.glob(os.path.join(ROOT, "artifacts", PAT))):
    n, k, M = load(p)
    if n != 15 or k != 3:
        continue
    adj = [0] * n
    for i in range(n):
        for j in range(n):
            if i != j and M[i][j] == M[j][i]:
                adj[i] |= 1 << j
    stats = []
    for c in range(3):
        a = adj  # colour c of the template
        # reindex: template colour c -> adjacency
        ad = [0] * n
        for i in range(n):
            for j in range(n):
                if i != j and M[i][j] == c:
                    ad[i] |= 1 << j
        best = 0
        for s in range(1, n + 1):
            if indep_sets_of_size(n, ad, s):
                best = s
        mis = indep_sets_of_size(n, ad, best)
        stats.append((best, len(mis)))
    # admissible words
    total = 0
    extremal = 0
    for zero in itertools.combinations(range(n), 5):
        Z = set(zero)
        rest = [i for i in range(n) if i not in Z]
        # each remaining position gets 1,2,3; part f must be independent in colour f-1
        # enumerate all 3^10 = 59049 assignments
        for assign in itertools.product((1, 2, 3), repeat=len(rest)):
            parts = {1: [], 2: [], 3: []}
            for pos, v in zip(rest, assign):
                parts[v].append(pos)
            ok = True
            for f in (1, 2, 3):
                for x, y in itertools.combinations(parts[f], 2):
                    if M[x][y] == f - 1:
                        ok = False
                        break
                if not ok:
                    break
            if ok:
                total += 1
                if any(not parts[f] for f in (1, 2, 3)):
                    extremal += 1
    print("%-40s alpha/num-max-indep per colour %s ; admissible words %d ; extremal %d"
          % (os.path.basename(p), stats, total, extremal), flush=True)
