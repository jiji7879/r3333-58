"""Text DRAT: remove only d records, preserving every addition byte exactly."""
from hashlib import sha256
from pathlib import Path
import json,sys
src,dst,receipt=map(Path,sys.argv[1:4])
counts={op:{'lines':0,'literals':0,'bytes':0} for op in ('a','d')}
in_hash=sha256();out_hash=sha256();raw_bytes=0;empty_additions=0
with src.open('rb') as fi,dst.open('wb') as fo:
    for line in fi:
        in_hash.update(line);raw_bytes+=len(line)
        stripped=line.lstrip()
        if not stripped:continue  # retained empty whitespace line
        if stripped.startswith(b'c'):
            fo.write(line);out_hash.update(line)
            continue
        if stripped.startswith(b'd ') or stripped==b'd\n':
            op='d';tokens=stripped[2:].split()
        else:
            op='a';tokens=stripped.split()
            if tokens and tokens[0]==b'a':tokens=tokens[1:]
        values=[int(x) for x in tokens]
        assert values[-1]==0 and all(x!=0 for x in values[:-1]),(op,tokens[:8])
        counts[op]['lines']+=1;counts[op]['literals']+=len(values)-1;counts[op]['bytes']+=len(line)
        if op=='a':
            fo.write(line);out_hash.update(line)
            if len(values)==1:empty_additions+=1
    assert not fi.read(1)
meta={'input':str(src),'output':str(dst),'input_bytes':raw_bytes,'output_bytes':dst.stat().st_size,
      'input_sha256':in_hash.hexdigest(),'output_sha256':out_hash.hexdigest(),
      'commands':counts,'empty_additions':empty_additions,
      'bytes_accounted':counts['a']['bytes']+counts['d']['bytes']+raw_bytes-sum(x['bytes'] for x in counts.values()),
      'complete_parse':True,'transformation':'text: drop d records; copy a records byte-for-byte; preserve comment and whitespace lines'}
assert raw_bytes==meta['input_bytes'] and meta['bytes_accounted']==raw_bytes
assert counts['a']['bytes']<=dst.stat().st_size,(meta,dst.stat().st_size)
assert empty_additions==1,meta
receipt.write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps(meta,indent=2))
