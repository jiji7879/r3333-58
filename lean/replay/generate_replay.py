"""Emit ordinary Lean proofs for complete placement families or a complete plan.

The output is split into importable modules. Omitted, extra and duplicate input
rows are errors. Generated arithmetic, target membership and unit equalities
are premises that the Lean kernel must discharge.
"""
import argparse
import ast
import collections
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import re
import tempfile

from transport_domain import load_domain

def literal(xs):
    return ','.join(str(x).lower() for x in xs)

def key(header, v=None):
    return '⟨' + literal(header) + ', ' + ('fun _ => 0' if v is None else '![' + literal(v) + ']') + '⟩'

def addresses(headers, retained):
    result = {}
    rows = collections.defaultdict(list)
    for f, v in retained:
        rows[headers[f]].append(v)
    next_index = collections.Counter()
    for h, vs in sorted(rows.items()):
        p = h[0]
        family_index = next_index[p]
        next_index[p] += 1
        b = max(v[1] for v in vs) + 1
        c = max(v[2] for v in vs) + 1
        ranks = sorted(((x*b+y)*c+z,(x,y,z)) for x,y,z in vs)
        for run, (_, xs) in enumerate(itertools.groupby(enumerate(ranks), lambda t: t[1][0] - t[0])):
            for offset, (_, (_, v)) in enumerate(xs):
                result[h,v] = (p,family_index,run,offset)
    return result

def balanced(names, combine):
    if len(names)==1:
        return names[0]
    mid = len(names)//2
    return f'({combine} (len := {mid}) (more := {len(names)-mid}) {balanced(names[:mid],combine)} {balanced(names[mid:],combine)})'

def module(imports, body):
    return '\n'.join(f'import {i}' for i in imports) + '''

namespace K58.Replay
noncomputable section
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 0
set_option maxRecDepth 200000

''' + '\n'.join(body) + '\nend\nend K58.Replay\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('lean_dir', type=Path)
    parser.add_argument('handoff_zip', type=Path)
    parser.add_argument('certificate', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--plan', type=int, action='append')
    parser.add_argument('--arm', type=int)
    parser.add_argument('--mark', type=int)
    args=parser.parse_args()
    out=args.output.resolve()
    out.mkdir(parents=True,exist_ok=True)
    cases=out/'ReplayGen'
    cases.mkdir(exist_ok=True)
    source=(args.lean_dir/'K58'/'Plans.lean').read_text()
    plans=[(tuple(ast.literal_eval(m[1])),tuple(m[2])) for m in re.finditer(r'prof := (\[.*?\]), kinds := "(.*?)"',source)]
    if len(plans)!=41:
        raise ValueError('wrong number of plans')
    with tempfile.TemporaryDirectory() as tmp:
        families,retained=load_domain(args.handoff_zip.resolve(),Path(tmp))
        import gluing
        hs=[(plans.index((f.profile,f.root_kinds)),f.arm,f.mark_position,f.marked_size==16,f.marked_kind=='T',f.root_position) for f in families]
        data=[gluing.data(f) for f in families]
        shapes=[tuple(map(len,d[1])) for d in data]
    addr=addresses(dict(zip(families,hs)),retained)
    selected=sorted((i for i,h in enumerate(hs) if (args.plan is None or h[0] in args.plan) and (args.arm is None or h[1]==args.arm) and (args.mark is None or h[2]==args.mark)), key=hs.__getitem__)
    if not selected:
        raise ValueError('empty family selection')
    chosen=set(selected)
    moves={}
    with gzip.open(args.certificate,'rt') as inp:
        for line in inp:
            i,v,j,w,p,e=json.loads(line)
            if i not in chosen:
                continue
            k=i,tuple(v)
            if k in moves or (hs[i],k[1]) in addr:
                raise ValueError('duplicate or retained source')
            if (hs[j],tuple(w)) not in addr:
                raise ValueError('unretained target')
            moves[k]=(j,tuple(w),tuple(p),tuple(e))
    def label(i, v):
        supports,choices,_=data[i]
        h=hs[i]
        m=families[i].marked_size
        slots=[None]*m
        slots[h[-1]]=0
        for (arm,positions),ws,j in zip(supports,choices,v):
            offset=1+sum(families[i].profile[:arm])
            for pos,value in zip(positions,ws[j]):
                slots[pos]=offset+value
        if None in slots or len(set(slots))!=m:
            raise ValueError('invalid marked block')
        return tuple(slots)
    def pack(values,width):
        return hex(sum(v<<(width*i) for i,v in enumerate(values)))
    def left_inverse(values,size):
        iv=[0]*size
        for k,x in enumerate(values):
            iv[x]=k
        return iv
    def pname(perm):
        return 'p'+hashlib.sha256(bytes(perm)).hexdigest()[:16]
    def ident(value):
        return hashlib.sha256(str(value).encode()).hexdigest()[:16]
    def fmt(xs):
        return '['+literal(xs)+']'
    def emit(name,imports,body):
        path=cases/(name+'.lean')
        content=module(sorted(set(imports)),body)
        if not path.exists() or path.read_text()!=content:
            path.write_text(content)
        return 'ReplayGen.'+name
    def chunks(xs,n):
        for i in range(0,len(xs),n):
            yield xs[i:i+n]
    from functools import lru_cache
    label=lru_cache(None)(label)
    active=set(selected) | {j for j,_,_,_ in moves.values()}
    shape_info={}
    for i in active:
        f=families[i]
        supports,choices,_=data[i]
        entries=[]
        for (b,source),words in zip(supports,choices):
            sig=(f.marked_size,f.marked_kind=='T',f.arm,b,f.profile[b],f.root_kinds[b],tuple(source))
            entries.append(sig)
            words=tuple(map(tuple,words))
            if sig in shape_info and words!=shape_info[sig]:
                raise ValueError('support table changed under normalization')
            shape_info[sig]=words
        data[i]=(supports,choices,entries)
    smods={}
    for sig,words in sorted(shape_info.items()):
        n,t,a,b,m,kind,src=sig
        tag='s'+ident(sig)
        template=f'(template {n} {str(t).lower()})'
        body=[f'def {tag}W : List (List ℕ) := ['+', '.join(fmt(w) for w in words)+']']
        want=f'targetWords {template} {a} {b} {m} \'{kind}\' {fmt(src)} = some {tag}W'
        if kind=='-':
            body.append(f'theorem {tag}OK : {want} := by rfl')
        else:
            tw=str(kind=='T').lower()
            ch=[f'{tag}C{y}' for y in range(m)]
            for y,cname in enumerate(ch):
                ws=[w for w in words if w[0]==y]
                body.append(f'private def {cname} : List (List ℕ) := ['+', '.join(fmt(w) for w in ws)+']')
                body.append(f'private theorem {cname}OK : supportEmbeddings {template} {a} (template {m} {tw}) {b} (named{m} {tw}) {fmt(src[1:])} [({src[0]},{y})] = {cname} := by decide +kernel')
            body.extend([f'private def {tag}B : Fin {m} → List (List ℕ) := !['+','.join(ch)+']',
                         f'theorem {tag}OK : {want} := by',
                         f'  apply Eq.trans (words{m}_first {template} {a} {b} {tw} {src[0]} {fmt(src[1:])} {tag}B ?_)',
                         '  · rfl','  · intro y','    fin_cases y'])
            body.extend(f'    · exact {c}OK' for c in ch)
        smods[sig]=emit('S'+ident(sig),['K58.StructuralTransport'],body)
    fmods={}
    for i in sorted(active):
        f=f'family{i}'
        entries=data[i][2]
        body=[f'def {f} : CaseKey := {key(hs[i])}',f'def table{i} : PlacementTables {f} where',
              '  rootBound := by decide',
              '  table := !['+', '.join(f'(({fmt(sig[-1])} : List (Fin {sig[0]})),s{ident(sig)}W)' for sig in entries)+']',
              '  exactTable := by','    intro c','    fin_cases c']
        for c,sig in enumerate(entries):
            root=f'⟨{f}.rootPosition,by decide⟩'
            b=f'({f}.arm.succAbove {c})'
            tag='s'+ident(sig)
            body.extend([f'    · have hs : supportAt {f} {root} {b} = ({fmt(sig[-1])} : List (Fin {sig[0]})) := by decide +kernel',
                         f"      have hw : targetWords (template _ {f}.secondTwisted) {f}.arm {b} (plannedDegree {f}.plan {b}) '{sig[5]}' (supportAt {f} {root} {b}) = some {tag}W := by",
                         '        rw [hs]',f'        exact {tag}OK',
                         f"      exact (supportTable_of_words {f} {root} {c} '{sig[5]}' {tag}W (by rfl) hw).trans (by rw [hs]; rfl)"])
        body.extend([f'theorem markBound{i} : {f}.markPosition < plannedDegree {f}.plan {f}.arm := by decide',
                     f'noncomputable def marking{i} (w inverse : ℕ)',
                     f'    (hi : ∀ x : Fin {f}.secondSize, packedValue inverse 4 (packedLabels w x).val = x.val)',
                     f'    (hz : packedLabels w (⟨{f}.rootPosition,table{i}.rootBound⟩ : Fin {f}.secondSize) = 0) : Marking {f} :=',
                     f'  packedMarking {f} w inverse table{i}.rootBound markBound{i} hi hz'])
        fmods[i]=emit('T'+str(i),[smods[x] for x in entries],body)
    aligned={}
    perms=set()
    rootchecks=set()
    edgechecks=set()
    for (i,v),(j,w,p,e) in moves.items():
        L=label(i,v)
        N=label(j,w)
        index={u:x for x,u in enumerate(N)}
        z=tuple(index[e[u]] for u in L)
        if len(set(z))!=len(z) or len(z)!=len(N):
            raise ValueError('nonbijective second-block alignment')
        left=hs[i]
        right=hs[j]
        root=(left[0],right[0],e,p)
        edge=(len(z),left[4],left[1],right[4],right[1],p,z)
        perms.update((p,e,z))
        rootchecks.add(root)
        edgechecks.add(edge)
        aligned[i,v]=(root,edge,z)
    pmods={}
    for block in chunks(sorted(perms),32):
        body=[]
        for perm in block:
            width=(len(perm)-1).bit_length()
            inv=left_inverse(perm,len(perm))
            body.append(f'def {pname(perm)} := packedPerm {len(perm)} {width} {pack(perm,width)} {pack(inv,width)} (by decide +kernel)')
        mod=emit('Maps'+ident(block),['K58.StructuralTransport'],body)
        pmods.update(dict.fromkeys(block,mod))
    roots={}
    for block in chunks(sorted(rootchecks),12):
        body=[]
        imports=set()
        for item in block:
            a,b,e,p=item
            imports.update((pmods[e],pmods[p]))
            body.extend([f'theorem root{ident(item)} : (rootUnitList (indexedPlan {a})).toFinset.image (fun u => u.relabel {pname(e)} {pname(p)}) =',
                         f'    (rootUnitList (indexedPlan {b})).toFinset := root_transport_of_bits (by decide +kernel)'])
        mod=emit('Roots'+ident(block),imports,body)
        roots.update(dict.fromkeys(block,mod))
    edges={}
    for block in chunks(sorted(edgechecks),32):
        body=[]
        imports=set()
        for item in block:
            n,t,a,s,b,p,z=item
            imports.update((pmods[p],pmods[z]))
            body.append(f'theorem edges{ident(item)} : ∀ i j : Fin {n}, i ≠ j → {pname(p)} (({a} : Fin 4).succAbove ((template {n} {str(t).lower()}).col i j)) = ({b} : Fin 4).succAbove ((template {n} {str(s).lower()}).col ({pname(z)} i) ({pname(z)} j)) := by decide +kernel')
        mod=emit('Edges'+ident(block),imports,body)
        edges.update(dict.fromkeys(block,mod))
    def marking(i,v):
        L=label(i,v)
        return f'(marking{i} {pack(L,6)} {pack(left_inverse(L,58),4)} (by decide +kernel) (by decide +kernel))'
    modules={}
    metrics={}
    used=set()
    for i in selected:
        nx,ny,nz=shapes[i]
        h=hs[i]
        f=f'family{i}'
        cells=list(itertools.product(range(nx),range(ny),range(nz)))
        pieces=[]
        for start in range(0,len(cells),64):
            batch=cells[start:start+64]
            imports={fmods[i]}
            local_align={}
            row_names=[]
            body=[]
            mnames={}
            def local_mark(j,w):
                kw=(j,w)
                if kw not in mnames:
                    nm=f'm{len(mnames)}'
                    body.append(f'private def {nm} := {marking(j,w)}')
                    mnames[kw]=nm
                return mnames[kw]
            for off,v in enumerate(batch):
                rank=start+off
                if (h,v) in addr:
                    wit=f'Or.inl (Frozen.Address.mem (a := ⟨{literal(addr[h,v])}⟩) (by rfl))'
                else:
                    used.add((i,v))
                    j,w,p,e=moves[i,v]
                    r,ed,z=aligned[i,v]
                    imports.update((fmods[j],roots[r],edges[ed]))
                    align=(j,p,e,z)
                    if align not in local_align:
                        nm=f'a{len(local_align)}'
                        local_align[align]=nm
                        body.append(f'private def {nm} : Alignment {f} family{j} := ⟨{pname(e)}, {pname(p)}, {pname(z)}, root{ident(r)}, by decide +kernel, by decide +kernel, by decide +kernel, edges{ident(ed)}⟩')
                    wit=(f'covered_aligned (v := !{fmt(v)}) (w := !{fmt(w)}) table{i} table{j} '
                         f'{local_mark(i,v)} {local_mark(j,w)} {local_align[align]} '
                         f'(Frozen.Address.mem (a := ⟨{literal(addr[hs[j],w])}⟩) (by rfl)) '
                         '(by decide +kernel) (by decide +kernel) (by decide +kernel)')
                nm=f'row{rank}'
                body.append(f'private theorem {nm} : GridCover {f} {ny} {nz} {rank} 1 :=\n  grid_single ({wit})')
                row_names.append(nm)
            name=f'piece{i}x{start}'
            body.append(f'theorem {name} : GridCover {f} {ny} {nz} {start} {len(batch)} :=\n  {balanced(row_names,"grid_append")}')
            mod=emit(f'B{i}x{start}',imports,body)
            pieces.append((mod,name,start,len(batch)))
        def merge(xs):
            if len(xs)==1:
                return xs[0][1],xs[0][3]
            mid=len(xs)//2
            a,na=merge(xs[:mid])
            b,nb=merge(xs[mid:])
            return f'(grid_append (len := {na}) (more := {nb}) {a} {b})',na+nb
        cover=merge(pieces)[0] if pieces else '(by intro x hx; omega)'
        body=[f'theorem covered{i} : ∀ k ∈ rawPlacements {f}, CoveredKey k :=',
              f'  cover_family_of_grid (nx := {nx}) (ny := {ny}) (nz := {nz}) table{i}.shape {cover}']
        modules[i]=emit(f'F{i}',[fmods[i],*(part[0] for part in pieces)],body)
        metrics[i]={'raw':len(cells),'moved':sum((i,v) in used for v in cells)}
    if used!=moves.keys():
        raise ValueError('out-of-range transport rows')
    # In sorted header order the family constants reduce to the original generator.
    joins=[]
    for p in sorted({hs[i][0] for i in selected}):
        idx=[i for i in selected if hs[i][0]==p]
        label=f'P{p}'+('' if args.arm is None else 'A'+str(args.arm))+('' if args.mark is None else 'M'+str(args.mark))
        filt=f'f.planIndex.val == {p}'
        if args.arm is not None:
            filt+=f' && f.arm.val == {args.arm}'
        if args.mark is not None:
            filt+=f' && f.markPosition == {args.mark}'
        fs='['+','.join(f'family{i}' for i in idx)+']'
        proof='family_nil'
        # The primitive list constructor does not require decidable equality on keys.
        for i in idx[::-1]:
            proof=f'(family_cons covered{i} {proof})'
        body=[f'theorem scope{label} : ∀ f ∈ rawFamilies.filter (fun f => {filt}), ∀ k ∈ rawPlacements f, CoveredKey k := by',
              f'  have shape : rawFamilies.filter (fun f => {filt}) = {fs} := by rfl',
              '  rw [shape]',f'  exact {proof}',f'#print axioms K58.Replay.scope{label}']
        joins.append(emit(label,[modules[i] for i in idx],body))
    if len(selected)==len(families) and args.arm is None and args.mark is None:
        body=['theorem rawTransportCover : RawTransportCover := by','  apply rawTransportCover_of_plans',
              '  intro p','  fin_cases p']
        for p in range(41):
            body.append(f'  · exact scopeP{p}')
        body.extend(['theorem frozenCover : FrozenCover := frozenCover_of_rawCover K58.rawCover rawTransportCover',
                     '#print axioms K58.Replay.rawTransportCover','#print axioms K58.Replay.frozenCover'])
        joins=[emit('Complete',['K58.FamilyGluing',*joins],body)]
    manifest={'permutations':sorted(set(pmods.values())),'families':list(modules.values()),'summaries':joins,
              'plans':sorted({hs[i][0] for i in selected}),'metrics':metrics}
    (out/'manifest.json').write_text(json.dumps(manifest,separators=(',',':'))+'\n')
    print(f'{len(selected)} families, {sum(x["raw"] for x in metrics.values())} placements, {len(moves)} transports')
if __name__=='__main__':
    main()
