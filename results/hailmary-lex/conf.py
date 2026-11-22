import subprocess, re, os
K='/workspace/nucleus/work/projects/p-764e12eeb9f34762ad544edb924f4680/repo/.scratch/satcheck/bin/kissat'
for name in ('bare_7','lex_7'):
    r = subprocess.run([K,'--time=60',f'{name}.cnf',f'{name}.probe'], capture_output=True, text=True)
    out = r.stdout + r.stderr
    c = re.search(r'conflicts:\s+(\d+)', out); p = re.search(r'propagations:\s+(\d+)', out)
    print(name, 'exit', r.returncode, 'conflicts', c.group(1) if c else '?', 'props', p.group(1) if p else '?', flush=True)
