#include <algorithm>
#include <array>
#include <bit>
#include <cstdint>
#include <iostream>
#include <vector>
#include <string>
using namespace std;
using Word=array<unsigned,4>;
int mat[14][14];
unsigned adj[14][4];
vector<Word> words;
vector<vector<int>> options;
vector<int> selected;
int between[12][12];
int maxIndependent=16;
unsigned allowedSupport;
bool independenceOK(int depth){
    int base=14-popcount(allowedSupport);
    int needed=maxIndependent+1-base;
    // The retained H vertices have ordinary spokes to all these outsiders.
    // For each independent subset of the outsiders, take all compatible omitted H vertices.
    for(unsigned S=1u<<depth;S<(1u<<(depth+1));++S){
        if(popcount(S)+int(popcount(allowedSupport))<needed)continue;
        unsigned available=allowedSupport;
        bool independent=true;
        for(int i=0;i<=depth && independent;++i)if(S>>i&1){
            available &= ~words[selected[i]][3];
            for(int j=0;j<i;++j)if((S>>j&1) && between[j][i]==3){independent=false;break;}
        }
        if(independent && popcount(S)+popcount(available)>=needed)return false;
    }
    return true;
}
void enumerateWords(int i,unsigned allowed,Word &w){
    if(i==14){words.push_back(w);return;}
    for(int c=0;c<4;++c){
        if(c==3 && !(allowed & (1u<<i)))continue;
        if(w[c]&adj[i][c])continue;
        w[c]^=1u<<i;enumerateWords(i+1,allowed,w);w[c]^=1u<<i;
    }
}
bool grow(int target,const vector<int>& pool);
bool colorToPrevious(int i,int depth,int id,int target,const vector<int>& pool){
    if(i==depth){
        selected.push_back(id);
        bool ok=(maxIndependent==16 || independenceOK(depth)) && grow(target,pool);
        selected.pop_back();
        return ok;
    }
    int choices=options[selected[i]][id];
    for(int j=0;j<i;++j)if(between[j][i]==between[j][depth])choices &= ~(1<<between[j][i]);
    for(int c=0;c<4;++c)if(choices & (1<<c)){
        between[i][depth]=c;
        if(colorToPrevious(i+1,depth,id,target,pool))return true;
    }
    return false;
}
bool grow(int target,const vector<int>& pool){
    int depth=selected.size();
    if(depth==target)return true;
    for(size_t j=0;j<pool.size();++j){
        int id=pool[j];vector<int> tail;
        for(size_t h=j;h<pool.size();++h)if(options[id][pool[h]])tail.push_back(pool[h]);
        if(depth+1<target && tail.empty())continue;
        if(colorToPrevious(0,depth,id,target,tail))return true;
    }
    return false;
}
int main(int argc,char**argv){
    if(argc==2)maxIndependent=stoi(argv[1]);
    int row,P,bound;
    while(cin>>row>>P>>bound){
        if(P<0){
            for(auto &r:adj)fill(begin(r),end(r),0u);
            for(int i=0;i<14;++i)for(int j=0;j<14;++j){
                cin>>mat[i][j];if(i!=j)adj[i][mat[i][j]]|=1u<<j;
            }
            continue;
        }
        allowedSupport=P;Word w{};words.clear();enumerateWords(0,P,w);
        int n=words.size();options.assign(n,vector<int>(n,15));
        vector<int> pool;
        for(int i=0;i<n;++i){
            pool.push_back(i);
            for(int j=0;j<=i;++j){
                int mask=15;for(int c=0;c<4;++c)if(words[i][c]&words[j][c])mask^=1<<c;
                options[i][j]=options[j][i]=mask;
            }
        }
        int lo=0,hi=bound+1;
        while(hi>lo+1){int k=(lo+hi)/2;if(grow(k,pool))lo=k;else hi=k;}
        cout<<row<<' '<<P<<' '<<n<<' '<<lo<<"\n";
    }
}
