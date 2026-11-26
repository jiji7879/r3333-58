"""Resume the ordinary wall from its signed rows and its exact binary frontier."""
import argparse
import csv
import fcntl
import gzip
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
from functools import cache
from itertools import zip_longest
from pathlib import Path
from tempfile import TemporaryDirectory
from time import monotonic

from roster import HERE, read_roster
from arm_pairs import between, check_drat, partition, records, RESULTS, sha
from bind import json_bytes, tsv, write_gzip
from spokes import lit, sites
from compile import append, bind as bind_parent, produce
from pentagons import compile_cas
from problem import check_model, family_and_pins, read_dimacs, row_formula

RUNS=HERE/'results/full-rows'
DEAD={'UNSAT_BASE','SAT_BASE'}


@cache
def context():
    rows={r['id']:r for r in read_roster()}
    bindings={r['id']:r for r in map(json.loads,gzip.decompress((HERE/'results/physical-bindings.jsonl.gz').read_bytes()).splitlines())}
    sr={r['row_id']:r for r in tsv(HERE/'results/row-strategies.tsv')}
    tables=json.loads(gzip.decompress((HERE/'results/spoke-tables.json.gz').read_bytes()))
    assert set(rows)==set(sr)==set(bindings)
    return rows,bindings,sr,tables


def atomic(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_name(path.name+f'.{os.getpid()}.tmp')
    temp.write_bytes(data); os.replace(temp,path)


@cache
def forbidden(n):
    rec=records(RESULTS)
    return sorted((w,z) for (w,z),rep in partition().items() if not between(w,z) or
                  rec.get((n,*rep),{}).get('status')=='UNSAT')


def pair_clauses(binding,third=False):
    # Instantiate the verified table once per pentagon, on the first two outside sites.
    # The all-pairs index is covered in the campaign ledger without inserting every clause into every CNF.
    for arm in binding['pentagons']:
        five=arm['pentagon']; palette=arm['palette']; n=arm['size']
        others=[v for v in range(arm['block_start'],arm['block_start']+n) if v not in five]
        x,y=others[:2]
        for w,z in forbidden(n):
            yield [-lit(u,v,palette[int(c)]) for u,s in ((x,w),(y,z)) for v,c in zip(five,s)]
        if third and n==14:
            from third_star import LEFT, RIGHT, DEST
            for result in sorted(DEST.glob('*.json')):
                rec=json.loads(result.read_bytes())
                if rec['status']=='UNSAT':
                    yield [-lit(u,v,palette[int(c)]) for u,s in zip(others[:3],(LEFT,RIGHT,rec['word']))
                           for v,c in zip(five,s)]


def candidates(binding,tables):
    spoke=binding['spoke']
    if spoke:
        tab=tables[spoke['key']]
        n,kind,b,a,free=tab['signature']
        pivots=sorted(sites(free),key=lambda j:(-tab['all_pivots'][str(j)][0],j))
        for j in pivots: yield lit(spoke['q'],spoke['start']+j,b)
    for arm in sorted(binding['pentagons'],key=lambda a:-a['size']):
        five=arm['pentagon']
        for x in range(arm['block_start'],arm['block_start']+arm['size']):
            if x in five: continue
            for v in five:
                yield lit(x,v,arm['palette'][0])


def read_tree(rid):
    loc=RUNS/rid/'tree.json'
    return json.loads(loc.read_bytes()) if loc.exists() else {'id':rid,'splits':{},'closed':{}}


def walk(tree):
    seen=set(); stack=[('r',[])]
    while stack:
        node,cube=stack.pop()
        v=tree['splits'].get(node)
        if v is None:
            yield node,cube
        else:
            assert type(v) is int and 0<v<=6612 and all(abs(x)!=v for x in cube)
            seen.add(node)
            stack.extend([(node+'1',cube+[v]),(node+'0',cube+[-v])])
    assert seen==set(tree['splits'])


class _CacheMiss(Exception):
    """The named receipt belongs to a different native query."""


def check_full_model(plain,cube,model):
    """Require a total, contradictory-free assignment satisfying the signed parent."""
    nv,clauses=read_dimacs(plain)
    if (not isinstance(model,list) or len(model)!=nv or
            any(type(x) is not int for x in model) or
            {abs(x) for x in model}!=set(range(1,nv+1))):
        raise ValueError('model is not a complete one-literal-per-variable assignment')
    check_model(clauses,cube,model,nv)


def receipt_artifact(receipt,old,key,suffix):
    """Load only the artifact generated beside this receipt, then bind its plaintext."""
    expected_name=receipt.stem+suffix
    if old.get(key)!=expected_name:
        raise ValueError(f'{key} is not the receipt-local artifact {expected_name!r}')
    data=gzip.decompress((receipt.parent/expected_name).read_bytes())
    if sha(data)!=old.get(key+'_sha256'):
        raise ValueError(f'{key} SHA-256 mismatch')
    return data


def check_native_drat(cnf,pf):
    """Replay binary DRAT without warning suppression changing parser control flow."""
    job=subprocess.run([str(HERE/'tools/drat-trim'),str(cnf),str(pf),'-i'],
                       stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    lines=[line.strip() for line in job.stdout.replace(b'\r',b'\n').splitlines()]
    if job.returncode or b's VERIFIED' not in lines:
        raise ValueError(job.stdout[-1000:])


def replay_receipt(receipt,expected,plain,query,cube):
    """A metadata match is only a cache key; terminal evidence must be replayed."""
    old=json.loads(receipt.read_bytes())
    if not isinstance(old,dict):
        raise ValueError('cached receipt is not a JSON object')
    if any(old.get(k)!=v for k,v in expected.items()):
        raise _CacheMiss(receipt.name)
    status=old.get('status')
    if status=='OPEN':
        return old
    if status not in ('UNSAT_BASE','AUGMENTED_UNSAT_PENDING_BASE','SAT_BASE'):
        raise ValueError(f'invalid cached native status {status!r}')
    if status=='SAT_BASE':
        modeldata=receipt_artifact(receipt,old,'model','.model.json.gz')
        check_full_model(plain,cube,json.loads(modeldata))
    else:
        proof=receipt_artifact(receipt,old,'proof','.drat.gz')
        with TemporaryDirectory(dir=receipt.parent) as tmp:
            q=Path(tmp)/'query.cnf';p=Path(tmp)/'proof.drat'
            # An augmented-query proof is evidence only for its nonterminal status.
            q.write_bytes(plain if status=='UNSAT_BASE' else query)
            p.write_bytes(proof);check_native_drat(q,p)
    return old


def invalid_cache(expected,errors):
    """Fail closed without destroying evidence or silently starting another search."""
    result=dict(expected,status='OPEN',cache_status='INVALID_CACHE')
    result['cache_error']='; '.join(errors)[:1000]
    return result


def run_native(base,cube,cuts,prefix,paircuts,rid,node,mode,cap,folder):
    name=f'{node}-{mode}-{cap}'
    receipt=folder/(name+'.json')
    expected={'id':rid,'node':node,'mode':mode,'cap':cap,'cube':cube,'parent_sha256':sha(base)}
    _,plain=append(base,[[v] for v in cube]) if cube else (None,base)
    _,query=append(plain,cuts+paircuts) if cuts or paircuts else (None,plain)
    expected.update(plain_sha256=sha(plain),query_sha256=sha(query),cuts=len(cuts),pair_cuts=len(paircuts))
    errors=[]
    if receipt.exists():
        try:
            return replay_receipt(receipt,expected,plain,query,cube)
        except _CacheMiss:
            pass
        except Exception as exc:
            errors.append(f'{receipt.name}: {type(exc).__name__}: {exc}')
        # The available shared rules can grow later. Keep older disjoint wave receipts.
        name+='-'+sha(query)[:12];receipt=folder/(name+'.json')
        if receipt.exists():
            try:
                return replay_receipt(receipt,expected,plain,query,cube)
            except Exception as exc:
                label=type(exc).__name__
                errors.append(f'{receipt.name}: {label}: {exc}')
        if errors:return invalid_cache(expected,errors)
    result=dict(expected)
    with TemporaryDirectory(dir=folder) as tmp:
        q=Path(tmp)/'query.cnf'; p=Path(tmp)/'proof.drat'; q.write_bytes(query)
        start=monotonic()
        job=subprocess.run([str(HERE/'tools/kissat'),'-s',f'--conflicts={cap}',str(q),str(p)],
                           stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        result['seconds']=round(monotonic()-start,3)
        conflicts=re.search(rb'^c conflicts:\s+(\d+)',job.stdout,re.M)
        result['conflicts']=int(conflicts[1]) if conflicts else 0
        if job.returncode==0 and b's UNKNOWN' in job.stdout:
            result['status']='OPEN'
        elif job.returncode==10:
            model=[int(v) for line in job.stdout.splitlines() if line.startswith(b'v ')
                   for v in line.split()[1:] if int(v)]
            check_full_model(plain,cube,model)
            modeldata=json_bytes(model); fn=name+'.model.json.gz'
            atomic(folder/fn,gzip.compress(modeldata,mtime=0))
            result.update(status='SAT_BASE',model=fn,model_sha256=sha(modeldata))
        elif job.returncode==20:
            check_native_drat(q,p)
            tail=p.read_bytes()
            q.write_bytes(plain); p.write_bytes(prefix+tail)
            try:
                check_native_drat(q,p)
            except ValueError:
                # Re-certify directly against the original parent with only the cube as input.
                check=subprocess.run([str(HERE/'tools/kissat'),'-s',f'--conflicts={4*cap}',str(q),str(Path(tmp)/'base.drat')],
                                     stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                if check.returncode==20:
                    p=Path(tmp)/'base.drat';check_native_drat(q,p)
                elif check.returncode==0 and b's UNKNOWN' in check.stdout:
                    result['status']='AUGMENTED_UNSAT_PENDING_BASE'; p.write_bytes(tail)
                else:
                    raise ValueError((check.returncode,check.stdout[-1000:]))
            proof=p.read_bytes(); fn=name+'.drat.gz'
            atomic(folder/fn,gzip.compress(proof,compresslevel=3,mtime=0))
            result.update(proof=fn,proof_sha256=sha(proof))
            result.setdefault('status','UNSAT_BASE')
        else:
            raise ValueError((job.returncode,job.stdout[-1200:]))
    atomic(receipt,json_bytes(result))
    return result


def run_row(task):
    rid,depth,cap,control,third=task
    rows,bindings,_,tables=context()
    row=rows[rid]; binding=bindings[rid]; tree=read_tree(rid)
    folder=RUNS/rid; folder.mkdir(parents=True,exist_ok=True)
    def save():atomic(folder/'tree.json',json_bytes(tree))
    base=row_formula(row,'first');bind_parent(row,base)
    assert tree.get('parent_sha256',sha(base))==sha(base)
    tree['parent_sha256']=sha(base)
    if control and not tree.get('root_verdict'):
        r=run_native(base,[],[],b'',[],rid,'r','stock',cap*(1<<depth),folder)
        if r['status'] in DEAD:
            tree['root_verdict']=r['status']; tree['closed']={'r':r['status']};tree['splits']={};save()
    if tree.get('root_verdict'):return rid
    _,pins=family_and_pins(row)
    pent,pp,_=compile_cas(row,set(pins))
    sp,ps=produce(row)
    extra=pent+sp; pair=list(pair_clauses(binding,third)); options=list(dict.fromkeys(candidates(binding,tables)))
    mode='guided3' if third else 'guided'
    queue=deque([('r',[])])
    while queue:
        node,cube=queue.popleft()
        if node in tree['closed']:continue
        if node in tree['splits']:
            var=tree['splits'][node]
        else:
            if not (node=='r' and control and depth>0):
                r=run_native(base,cube,extra,pp+ps,pair,rid,node,mode,cap,folder)
                if r['status'] in DEAD:
                    tree['closed'][node]=r['status']
                    if r['status']=='SAT_BASE':tree['root_verdict']='SAT_BASE'
                    save()
                    if tree.get('root_verdict'):break
                    continue
            if len(cube)>=depth:continue
            var=next((v for v in options if v not in set(map(abs,cube))),None)
            if var is None:continue
            tree['splits'][node]=var;save()
        queue.extend([(node+'0',cube+[-var]),(node+'1',cube+[var])])
    if all(tree['closed'].get(n)=='UNSAT_BASE' for n,_ in walk(tree)):tree['root_verdict']='UNSAT_BASE'
    save()
    return rid


def pilot():
    _,bindings,sr,_=context(); groups=defaultdict(list)
    for rid,r in sr.items():groups[r['profile']].append(rid)
    selected=[]
    favorites={'16,16,14,11':'4a71c66153af','16,16,13,12':'0404c3a22462'}
    for profile,group in sorted(groups.items()):
        if profile in favorites:
            rid=next(x for x in group if x.startswith(favorites[profile]))
        else:
            rid=min(group,key=lambda x:(bindings[x]['spoke'] is not None,
                     14 not in [a['size'] for a in bindings[x]['pentagons']],x))
        selected.append(rid)
    return selected


def index():
    _,_,sr,_=context(); import io
    out=io.StringIO(); writer=csv.writer(out,delimiter='\t',lineterminator='\n')
    writer.writerow(['row_id','profile','node','cube','status'])
    states=Counter(); receipts=Counter()
    for rid,r in sr.items():
        tree=read_tree(rid)
        states[tree.get('root_verdict','OPEN')]+=1
        for node,cube in walk(tree):
            status=tree['closed'].get(node,'INACTIVE_SAT_ROOT' if tree.get('root_verdict')=='SAT_BASE' else 'OPEN')
            writer.writerow([rid,r['profile'],node,' '.join(map(str,cube)),status])
            receipts[status]+=1
    write_gzip(HERE/'results/frontier.tsv.gz',out.getvalue().encode())
    print('Whole rows',dict(states),'binary frontier',dict(receipts),flush=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('action',choices=['index','pilot','advance','deepen','row'])
    p.add_argument('--id',default='')
    p.add_argument('--depth',type=int,default=1)
    p.add_argument('--cap',type=int,default=10000)
    p.add_argument('--jobs',type=int,default=2)
    p.add_argument('--limit',type=int,default=7)
    p.add_argument('--control',action='store_true')
    p.add_argument('--third-cuts',action='store_true')
    opt=p.parse_args()
    assert min(opt.cap,opt.jobs,opt.limit)>0 and opt.depth>=0
    RUNS.mkdir(parents=True,exist_ok=True)
    with (RUNS/'.campaign.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if opt.action=='index':index();return
        rows,_,sr,_=context()
        if opt.action=='pilot': ids=pilot()
        elif opt.action=='row':
            ids=[x for x in rows if opt.id and x.startswith(opt.id)]
            if len(ids)!=1:p.error('Specify a unique nonempty row ID prefix')
        else:
            byprofile=defaultdict(list)
            for rid,rec in sr.items():
                exists=(RUNS/rid/'tree.json').exists()
                if opt.action=='advance' and not exists:
                    byprofile[rec['profile']].append(rid)
                elif opt.action=='deepen' and exists:
                    tree=read_tree(rid)
                    mode='guided3' if opt.third_cuts else 'guided'
                    if not tree.get('root_verdict') and any(n not in tree['closed'] and
                            (len(cube)<opt.depth or not (RUNS/rid/f'{n}-{mode}-{opt.cap}.json').exists())
                            for n,cube in walk(tree)):
                        byprofile[rec['profile']].append(rid)
            ids=[i for line in zip_longest(*(byprofile[k] for k in sorted(byprofile))) for i in line if i][:opt.limit]
        with ProcessPoolExecutor(opt.jobs) as ex:
            for rid in ex.map(run_row,[(r,opt.depth,opt.cap,opt.control,opt.third_cuts) for r in ids]):
                print('saved',rid,flush=True)
        index()


if __name__=='__main__': main()
