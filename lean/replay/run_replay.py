"""Compile the generated proof dependency graph, resuming verified modules atomically."""
import argparse
import concurrent.futures
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

class MemoryLimit(RuntimeError):
    pass

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lean_dir',type=Path)
    parser.add_argument('generated',type=Path)
    parser.add_argument('--jobs',type=int,default=1)
    parser.add_argument('--plan',type=int,action='append',help='check these complete plans in the packed full input')
    args=parser.parse_args()
    root=args.generated.resolve()
    lean=args.lean_dir.resolve()
    if args.jobs<1:
        parser.error('--jobs must be positive')
    env=os.environ.copy()
    env['LEAN_PATH']=os.pathsep.join((str(root),str(lean),str(lean/'.catalogue/lib'),env['LEAN_PATH']))
    manifest=json.loads((root/'manifest.json').read_text())
    deps={}
    def source(name):
        return root/(name.replace('.','/')+'.lean')
    def visit(name):
        if name not in deps:
            deps[name]=re.findall(r'^import (ReplayGen\.\w+)$',source(name).read_text(),re.M)
            for dep in deps[name]:
                visit(dep)
    summary=manifest['summaries']
    metrics=manifest['metrics']
    if args.plan:
        if not set(args.plan)<=set(manifest['plans']) or 'family_plans' not in manifest:
            raise ValueError('plan selection requires a packed manifest containing the requested plans')
        summary=[f'ReplayGen.P{p}' for p in sorted(set(args.plan))]
        metrics={i:v for i,v in metrics.items() if manifest['family_plans'][i] in args.plan}
    for name in summary:
        visit(name)
    priority={}
    if 'family_plans' in manifest:
        by_plan=sorted(manifest['plans'],key=lambda p:sum(m['raw'] for i,m in manifest['metrics'].items() if manifest['family_plans'][i]==p))
        def prefer(name,rank):
            if name not in deps or name in priority:
                return
            priority[name]=rank
            for d in deps[name]:
                prefer(d,rank)
        for rank,p in enumerate(by_plan):
            prefer('ReplayGen.P'+str(p),rank)
    base=hashlib.sha256(subprocess.check_output(['lean','--version'],env=env))
    for path in sorted((lean/'K58').glob('*.olean')):
        base.update(path.name.encode())
        base.update(hashlib.sha256(path.read_bytes()).digest())
    base=base.digest()
    def check_axioms(src,log):
        expected=re.findall(r'^#print axioms ([\w.]+)$',src.read_text(),re.M)
        if not expected:
            return True
        if not log.exists():
            return False
        content=log.read_text()
        for decl in expected:
            result=re.search(r"'"+re.escape(decl)+r"' (?:depends on axioms:\s*\[([^\]]*)\]|does not depend on any axioms)",content)
            if result is None:
                return False
            axioms={x.strip() for x in (result[1] or '').split(',') if x.strip()}
            if axioms-{'propext','Classical.choice','Quot.sound'}:
                return False
        return True
    def action(name):
        with source(name).with_suffix('.lock').open('a') as guard:
            fcntl.flock(guard.fileno(),fcntl.LOCK_EX)
            return compile_one(name)
    def compile_one(name):
        src=source(name)
        dest=src.with_suffix('.olean')
        stamp=src.with_suffix('.stamp')
        log=src.with_suffix('.log')
        seed=hashlib.sha256(base)
        seed.update(src.read_bytes())
        for dep in deps[name]:
            seed.update(source(dep).with_suffix('.stamp').read_bytes())
        tag=seed.hexdigest()
        if stamp.exists() and dest.exists():
            old=stamp.read_text().split()
            if old==[tag,hashlib.sha256(dest.read_bytes()).hexdigest()] and check_axioms(src,log):
                return 'cached'
        tmp=dest.with_suffix('.tmp.olean')
        started=time.monotonic()
        with log.open('w') as stream:
            run=subprocess.run(['lean','-j1','-o',str(tmp),str(src)],cwd=root,env=env,stdout=stream,stderr=subprocess.STDOUT)
        if run.returncode or not tmp.exists():
            tmp.unlink(missing_ok=True)
            exc=MemoryLimit if run.returncode==-9 else RuntimeError
            raise exc(f'{name} failed (exit {run.returncode})\n{log.read_text()[-3000:]}')
        if not check_axioms(src,log):
            raise RuntimeError(f'missing or unexpected axiom record for {name}')
        tmp.replace(dest)
        tmp_stamp=stamp.with_suffix('.tmp.stamp')
        tmp_stamp.write_text(tag+' '+hashlib.sha256(dest.read_bytes()).hexdigest()+'\n')
        tmp_stamp.replace(stamp)
        return f'{time.monotonic()-started:.2f}s'
    done=set()
    running={}
    waiting=set(deps)
    slots=args.jobs
    drain=False
    exclusive=set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        while waiting or running:
            ready=sorted((name for name in waiting if set(deps[name])<=done),key=lambda name:(priority.get(name,999),name))
            if drain:
                if running:
                    ready=[]
                else:
                    ready=[name for name in ready if name in exclusive][:1]
                    if not ready:
                        drain=False
                        continue
            for name in ready[:max(0,slots-len(running))]:
                waiting.remove(name)
                running[pool.submit(action,name)]=name
            if not running:
                raise ValueError('cyclic import graph')
            complete,_=concurrent.futures.wait(running,return_when=concurrent.futures.FIRST_COMPLETED)
            for future in complete:
                name=running.pop(future)
                try:
                    outcome=future.result()
                except MemoryLimit:
                    if name in exclusive:
                        raise
                    print(f'{name} exceeded available memory. Retrying alone after active checks finish.',flush=True)
                    exclusive.add(name)
                    waiting.add(name)
                    slots=max(1,slots-1)
                    drain=True
                else:
                    print(name,outcome,flush=True)
                    exclusive.discard(name)
                    done.add(name)
    raw=sum(x['raw'] for x in metrics.values())
    moved=sum(x['moved'] for x in metrics.values())
    print(f'Checked {len(metrics)} complete families, {raw} raw placements, {moved} omitted transports.')
if __name__=='__main__':
    main()
