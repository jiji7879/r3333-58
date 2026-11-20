// Classify which ten-vertex restrictions occur in a three-colored K15.
#include <algorithm>
#include <array>
#include <bit>
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <vector>
using namespace std;
using Blocks=vector<vector<int>>;
int graph[15][15];
array<int,3> perm;
string canon(Blocks parts) {
    for (;;) {
        Blocks out;
        for (const auto& group:parts) {
            if(group.size()==1) {out.push_back(group);continue;}
            map<array<unsigned char,30>,vector<int>> buckets;
            for(int i:group) {
                array<unsigned char,30> h{};
                for(size_t k=0;k<parts.size();++k)
                    for(int j:parts[k]) if(i!=j) ++h[3*k+perm[graph[i][j]]];
                buckets[h].push_back(i);
            }
            for(const auto& [k,g]:buckets) out.push_back(g);
        }
        if(out.size()==parts.size())break;
        parts=move(out);
    }
    for(size_t k=0;k<parts.size();++k) if(parts[k].size()>1) {
        string best;
        for(int v:parts[k]) {
            auto c=parts;
            c[k].erase(find(c[k].begin(),c[k].end(),v));
            c.insert(c.begin()+k,vector<int>{v});
            auto q=canon(move(c));
            if(best.empty() || q<best) best=move(q);
        }
        return best;
    }
    string code;
    for(size_t i=0;i<parts.size();++i) for(size_t j=i+1;j<parts.size();++j)
        code.push_back('0'+perm[graph[parts[i][0]][parts[j][0]]]);
    return code;
}
int main() {
    int n,idx;set<string> targets;
    while(cin>>n>>idx) {
        for(int i=0;i<n;++i)for(int j=0;j<n;++j)cin>>graph[i][j];
        for(int mask=0;mask<(1<<n);++mask) if(popcount((unsigned)mask)==10) {
            vector<int> subset;
            for(int i=0;i<n;++i)if((mask>>i)&1)subset.push_back(i);
            perm={0,1,2};
            if(n==15) {
                do {targets.insert(canon({subset}));}while(next_permutation(perm.begin(),perm.end()));
            } else if(targets.contains(canon({subset}))) {
                cout<<idx<<' '<<(((1<<n)-1)^mask)<<'\n';
            }
        }
    }
}
