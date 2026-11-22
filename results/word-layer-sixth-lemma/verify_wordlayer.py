"""Definition-level check of a 42-block word layer against every word-level family
of the branch: five zeros (block size 5), coverage 14 per position, per-arm
coverage <= 5 (mixture), and the sixth arm lemma's word form on all three arms."""
import sys, json, itertools
def maxclique(adj, vs):
    best=[0]
    def rec(cand,size):
        if not size+len(cand) <= best[0]:
            if not cand: best[0]=max(best[0],size); return
            for i,v in enumerate(cand):
                if size+len(cand)-i <= best[0]: return
                rec([u for u in cand[i+1:] if u in adj[v]], size+1)
    rec(sorted(vs),0); return best[0]
blocks = [set(b) for b in json.load(open(sys.argv[1]))]
assert len(blocks) == 42
bad = []
if any(len(b) != 5 for b in blocks): bad.append("block size != 5")
cov = [sum(1 for b in blocks if p in b) for p in range(15)]
if any(c != 14 for c in cov): bad.append(f"global coverage {cov}")
print("global coverage:", cov)
for arm in range(3):
    vs = list(range(arm*14, (arm+1)*14))
    per = [sum(1 for x in vs if p in blocks[x]) for p in range(15)]
    print(f"  arm {arm+1}: per-arm coverage {per} (max {max(per)}, bound 5; "
          f"{sorted(per, reverse=True).count(5)} 5s and {per.count(4)} 4s)")
    if max(per) > 5: bad.append(f"arm {arm+1} exceeds the mixture cap")
    adj = {x: set() for x in vs}
    for x, y in itertools.combinations(vs, 2):
        if blocks[x] & blocks[y]: adj[x].add(y); adj[y].add(x)
    c = maxclique(adj, vs)
    print(f"      intersection-graph clique number {c} (sixth arm lemma bound 5)")
    if c > 5: bad.append(f"arm {arm+1} violates the word form")
print("verdict:", "ALL WORD-LEVEL FAMILIES HOLD" if not bad else "VIOLATED: " + "; ".join(bad))
