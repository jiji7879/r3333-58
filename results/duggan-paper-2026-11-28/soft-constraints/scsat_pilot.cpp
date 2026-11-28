// Core-guided unit-soft-constraint deletion for exact one-hot Ramsey CNFs.
// The guide determines assumptions ONLY; it is never added to the hard formula.
#include "cadical.hpp"
#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <numeric>
#include <stdexcept>
#include <string>
#include <tuple>
#include <vector>

using Clock = std::chrono::steady_clock;
struct Timeout : CaDiCaL::Terminator {
  Clock::time_point start;
  double seconds;
  Timeout(double s) : start(Clock::now()), seconds(s) {}
  bool terminate() override {
    return std::chrono::duration<double>(Clock::now() - start).count() >= seconds;
  }
};

struct Instance {
  int n, k, m;
  std::vector<std::tuple<int,int,int>> triples;
  std::vector<std::pair<int,int>> edges;
  std::vector<std::vector<int>> eid;
  Instance(int n_, int k_) : n(n_), k(k_), m(n_*(n_-1)/2),
      eid(n_, std::vector<int>(n_, -1)) {
    for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) {
      eid[i][j]=eid[j][i]=edges.size(); edges.push_back({i,j});
    }
    for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) for (int l=j+1;l<n;l++)
      triples.push_back({i,j,l});
  }
  int var(int e,int c) const { return e*k+c+1; }
  int edge(int i,int j) const { return eid.at(i).at(j); }
  void build(CaDiCaL::Solver &s) const {
    for (int e=0;e<m;e++) {
      for (int c=0;c<k;c++) s.add(var(e,c));
      s.add(0);
      for (int c=0;c<k;c++) for (int d=c+1;d<k;d++) {
        s.add(-var(e,c)); s.add(-var(e,d)); s.add(0);
      }
    }
    for (auto [i,j,l] : triples) for (int c=0;c<k;c++) {
      s.add(-var(edge(i,j),c)); s.add(-var(edge(i,l),c));
      s.add(-var(edge(j,l),c)); s.add(0);
    }
  }
  long long clauses() const {
    return (long long)m*(1+k*(k-1)/2)+(long long)triples.size()*k;
  }
};

static std::vector<std::vector<int>> read_col(const std::string &path, int want_n=-1, int want_k=-1) {
  std::ifstream f(path); if (!f) throw std::runtime_error("cannot open "+path);
  int n,k; f>>n>>k;
  if (n<1 || k<1 || (want_n>=0 && n!=want_n) || (want_k>=0 && k!=want_k))
    throw std::runtime_error("bad colouring header");
  std::vector<std::vector<int>> a(n,std::vector<int>(n));
  for (int i=0;i<n;i++) for (int j=0;j<n;j++) {
    if (!(f>>a[i][j]) || a[i][j]<0 || a[i][j]>=k) throw std::runtime_error("bad matrix entry");
  }
  std::string extra; if (f>>extra) throw std::runtime_error("trailing matrix data");
  for (int i=0;i<n;i++) {
    if (a[i][i]!=0) throw std::runtime_error("nonzero diagonal");
    for (int j=0;j<n;j++) if (a[i][j]!=a[j][i]) throw std::runtime_error("asymmetric matrix");
  }
  return a;
}

static int defects(const std::vector<std::vector<int>> &a) {
  int n=a.size(), ans=0;
  for (int i=0;i<n;i++) for (int j=i+1;j<n;j++) for (int l=j+1;l<n;l++)
    ans += a[i][j]==a[i][l] && a[i][j]==a[j][l];
  return ans;
}

static std::vector<std::vector<int>> model(CaDiCaL::Solver &s, const Instance &I) {
  std::vector<std::vector<int>> a(I.n,std::vector<int>(I.n));
  for (int e=0;e<I.m;e++) {
    auto [i,j]=I.edges[e]; int seen=0;
    for (int c=0;c<I.k;c++) if (s.val(I.var(e,c))>0) { a[i][j]=a[j][i]=c; seen++; }
    if (seen!=1) throw std::runtime_error("model does not have exactly one colour per edge");
  }
  if (defects(a)) throw std::runtime_error("model has a monochromatic triangle");
  return a;
}

static void write_col(const std::string &path, const std::vector<std::vector<int>> &a) {
  std::ofstream f(path); if (!f) throw std::runtime_error("cannot write "+path);
  f<<a.size()<<" 4\n";
  for (auto &r:a) { for (size_t j=0;j<r.size();j++) { if(j) f<<' '; f<<r[j]; } f<<'\n'; }
  f.close(); if (!f) throw std::runtime_error("failed colouring write");
}

static void selftest() {
  // Expected counts independently computed by brute force in validate_pilot.py.
  for (auto [n,k,expected] : {std::tuple<int,int,long long>{4,4,3156}, {5,2,12}}) {
    Instance I(n,k); CaDiCaL::Solver s; s.configure("plain"); I.build(s);
    long long count=0;
    while (true) {
      int r=s.solve();
      if (r==20) break;
      if (r!=10) throw std::runtime_error("selftest solver did not decide");
      std::vector<int> chosen;
      for (int e=0;e<I.m;e++) for (int c=0;c<I.k;c++)
        if (s.val(I.var(e,c))>0) chosen.push_back(I.var(e,c));
      for (int lit : chosen) s.add(-lit);
      s.add(0); count++;
    }
    std::cout<<"{\"test\":\"exact_enumeration\",\"n\":"<<n<<",\"k\":"<<k
             <<",\"models\":"<<count<<",\"expected\":"<<expected
             <<",\"pass\":"<<(count==expected?"true":"false")<<"}\n";
    if (count!=expected) throw std::runtime_error("enumeration mismatch");
  }
  Instance I(6,2); CaDiCaL::Solver s; s.configure("plain"); I.build(s);
  bool pass=s.solve()==20;
  std::cout<<"{\"test\":\"R_3_3_upper_base\",\"n\":6,\"k\":2,\"unsat\":"<<(pass?"true":"false")<<"}\n";
  if (!pass) throw std::runtime_error("K6 two-colour base unexpectedly SAT");
}

static std::string quote(const std::string &x) {
  std::string z="\"";
  for (char c:x) { if(c=='\"'||c=='\\') z+='\\'; z+=c; }
  return z+"\"";
}

static void search(const std::string &input, const std::string &logpath,
                   int conflicts, double timeout, int rounds, int percent,
                   const std::string &modelpath) {
  auto guide=read_col(input); int n=guide.size(), k=4;
  Instance I(n,k); CaDiCaL::Solver s; s.configure("sat"); I.build(s);
  std::ofstream log(logpath); if(!log) throw std::runtime_error("cannot write log");
  log<<"{\"event\":\"setup\",\"input\":"<<quote(input)
     <<",\"cadical\":"<<quote(CaDiCaL::Solver::signature())
     <<",\"n\":"<<n<<",\"k\":"<<k<<",\"variables\":"<<I.m*k
     <<",\"clauses\":"<<I.clauses()<<",\"guide_defects\":"<<defects(guide)
     <<",\"conflict_cap\":"<<conflicts<<",\"timeout_seconds\":"<<timeout
     <<",\"deletion_rule\":\"max(1,ceil(percent/100 * current failed-core size)); percent=0 removes one; ties by edge then colour\"}\n";
  std::vector<bool> active(I.m*k,true);
  std::vector<long long> score(I.m*k,0);
  int remaining=I.m;
  long long previous_conflicts=0, previous_decisions=0;
  for(int round=0;round<rounds;round++) {
    for(int e=0;e<I.m;e++) {
      int c=guide[I.edges[e].first][I.edges[e].second];
      int v=I.var(e,c); if(active[e*k+c]) s.assume(v);
    }
    long long before_c=s.get_statistic_value("conflicts");
    long long before_d=s.get_statistic_value("decisions");
    Timeout term(timeout); s.connect_terminator(&term);
    if(conflicts>=0) s.limit("conflicts",conflicts);
    auto t0=Clock::now(); int result=s.solve(); double elapsed=std::chrono::duration<double>(Clock::now()-t0).count();
    s.disconnect_terminator();
    long long total_c=s.get_statistic_value("conflicts"), total_d=s.get_statistic_value("decisions");
    previous_conflicts=total_c-before_c; previous_decisions=total_d-before_d;
    if(result==10) {
      auto a=model(s,I); if(!modelpath.empty()) write_col(modelpath,a);
      log<<"{\"event\":\"round\",\"round\":"<<round<<",\"status\":\"SAT\",\"active_edges\":"<<remaining
         <<",\"elapsed_seconds\":"<<elapsed<<",\"conflicts\":"<<previous_conflicts
         <<",\"decisions\":"<<previous_decisions<<",\"model_defects\":"<<defects(a)<<"}\n";
      log<<"{\"event\":\"final\",\"status\":\"SAT\",\"note\":\"independently re-check model file; no Ramsey claim from this driver\"}\n";
      log.flush(); std::cout<<"SAT round="<<round<<" active="<<remaining<<" defects="<<defects(a)<<"\n"; return;
    }
    if(result==0) {
      log<<"{\"event\":\"round\",\"round\":"<<round<<",\"status\":\"UNKNOWN\",\"active_edges\":"<<remaining
         <<",\"elapsed_seconds\":"<<elapsed<<",\"conflicts\":"<<previous_conflicts
         <<",\"decisions\":"<<previous_decisions<<"}\n";
      log<<"{\"event\":\"final\",\"status\":\"UNKNOWN\",\"note\":\"limit reached; neither SAT nor UNSAT and no row/bound inference\"}\n";
      log.flush(); std::cout<<"UNKNOWN round="<<round<<" active="<<remaining<<" conflicts="<<previous_conflicts<<"\n"; return;
    }
    if(result!=20) throw std::runtime_error("unexpected solver result");
    std::vector<int> core;
    for(int e=0;e<I.m;e++) {
      int c=guide[I.edges[e].first][I.edges[e].second], q=e*k+c;
      if(active[q] && s.failed(I.var(e,c))) { core.push_back(q); score[q]++; }
    }
    if(core.empty()) throw std::runtime_error("UNSAT with empty assumption core: stop; base UNSAT would need DRAT");
    std::stable_sort(core.begin(),core.end(),[&](int a,int b){
      if(score[a]!=score[b]) return score[a]>score[b];
      int ea=a/k,eb=b/k; if(ea!=eb) return ea<eb; return a<b;
    });
    int remove=std::max(1,(int)std::ceil(percent*core.size()/100.0));
    std::vector<int> removed;
    for(int i=0;i<remove;i++) { active[core[i]]=false; removed.push_back(core[i]); }
    remaining-=remove;
    // Unpinned count is the number of guide pins removed, not a proof about the optimum.
    log<<"{\"event\":\"round\",\"round\":"<<round<<",\"status\":\"UNSAT_ASSUMPTIONS\",\"active_before\":"<<(remaining+remove)
       <<",\"core_size\":"<<core.size()<<",\"removed\":"<<remove<<",\"active_after\":"<<remaining
       <<",\"unpinned_edges\":"<<(I.m-remaining)<<",\"elapsed_seconds\":"<<elapsed
       <<",\"conflicts\":"<<previous_conflicts<<",\"decisions\":"<<previous_decisions
       <<",\"removed_first_edge_colour\":["<<I.edges[removed[0]/k].first<<","<<I.edges[removed[0]/k].second<<","<<(removed[0]%k)<<"]"
       <<",\"core_edges_first10\":[";
    for(size_t z=0;z<std::min<size_t>(10,core.size());z++) {
      int e=core[z]/k; if(z) log<<","; log<<"["<<I.edges[e].first<<","<<I.edges[e].second<<","<<(core[z]%k)<<"]";
    }
    log<<"]}\n"; log.flush();
    std::cout<<"UNSAT_ASSUMPTIONS round="<<round<<" core="<<core.size()<<" removed="<<remove
             <<" active="<<remaining<<" conflicts="<<previous_conflicts<<"\n";
  }
  log<<"{\"event\":\"final\",\"status\":\"ROUND_CAP\",\"note\":\"only finite soft-deletion pilot; no completeness claim\"}\n";
  std::cout<<"ROUND_CAP active="<<remaining<<"\n";
}

int main(int argc,char **argv) {
  try {
    if(argc==2 && std::string(argv[1])=="selftest") { selftest(); return 0; }
    if(argc==9 && std::string(argv[1])=="search") {
      search(argv[2],argv[3],std::stoi(argv[4]),std::stod(argv[5]),std::stoi(argv[6]),std::stoi(argv[7]),argv[8]); return 0;
    }
    std::cerr<<"usage: "<<argv[0]<<" selftest\n  or "<<argv[0]
             <<" search GUIDE.col LOG.jsonl CONFLICT_CAP TIMEOUT_SECONDS ROUNDS PERCENT MODEL.col\n";
    return 2;
  } catch(const std::exception &e) { std::cerr<<"ERROR: "<<e.what()<<"\n"; return 1; }
}
