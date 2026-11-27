#!/usr/bin/env python3
"""Preserve every binary DRAT addition and drop only deletion records."""
import hashlib,json,sys
from pathlib import Path

def decode(raw):
    pos=0;counts={'a':0,'d':0}
    while pos<len(raw):
        tag=raw[pos];end=raw.index(0,pos+1)
        if tag not in (97,100):raise ValueError(f'invalid tag {tag} at {pos}')
        counts[chr(tag)]+=1
        if tag==97:
            values=[];shift=value=0
            for byte in raw[pos+1:end]:
                value |= (byte&127)<<shift
                if byte&128:shift+=7
                else:
                    values.append(-(value//2) if value&1 else value//2)
                    value=shift=0
            if shift or value:raise ValueError('unterminated varint')
            yield tag,values
        pos=end+1
    decode.counts=counts

def encode(clause):
    data=bytearray(b'a')
    for lit in clause:
        value=2*abs(lit)+int(lit<0)
        while value>=128:data.append(128|(value&127));value>>=7
        data.append(value)
    data.append(0)
    return data

def main():
    source,dest=map(Path,sys.argv[1:3]);raw=source.read_bytes()
    with dest.open('wb') as out:
        for tag,clause in decode(raw):out.write(encode(clause))
    result=dict(source=str(source),destination=str(dest),original_bytes=len(raw),normalized_bytes=dest.stat().st_size,
     original_sha256=hashlib.sha256(raw).hexdigest(),normalized_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),
     additions=decode.counts['a'],deletions_removed=decode.counts['d'])
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':main()
