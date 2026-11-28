#!/usr/bin/env python3
"""Delete only binary DRAT deletion commands; preserve every addition byte exactly."""
import hashlib
import json
import sys
from pathlib import Path

src, dst, receipt = map(Path, sys.argv[1:4])
raw_hash = hashlib.sha256()
out_hash = hashlib.sha256()
counts = {op: {"commands": 0, "literals": 0, "bytes": 0} for op in ("a", "d")}
empty_additions = 0
with src.open("rb") as fi, dst.open("wb") as fo:
    while True:
        first = fi.read(1)
        if not first:
            break
        raw_hash.update(first)
        op = first.decode("ascii", errors="strict")
        if op not in counts:
            raise ValueError(f"bad opcode {first!r} at command {sum(x['commands'] for x in counts.values())}")
        command = bytearray(first)
        literals = 0
        while True:
            # Standard binary DRAT signed zigzag varint; zero terminates a command.
            value = 0
            terminated = False
            for shift in range(0, 35, 7):
                b = fi.read(1)
                if not b:
                    raise EOFError("truncated varint/command")
                raw_hash.update(b)
                command += b
                value |= (b[0] & 127) << shift
                if b[0] < 128:
                    terminated = True
                    break
            if not terminated:
                raise ValueError("overlong varint")
            if value == 0:
                break
            literals += 1
        counts[op]["commands"] += 1
        counts[op]["literals"] += literals
        counts[op]["bytes"] += len(command)
        if op == "a":
            fo.write(command)
            out_hash.update(command)
            if literals == 0:
                empty_additions += 1
metadata = {
    "input": str(src), "output": str(dst),
    "input_bytes": src.stat().st_size, "output_bytes": dst.stat().st_size,
    "input_sha256": raw_hash.hexdigest(), "output_sha256": out_hash.hexdigest(),
    "commands": counts, "empty_additions": empty_additions,
    "bytes_accounted": counts["a"]["bytes"] + counts["d"]["bytes"],
    "complete_parse": True,
    "transformation": "drop d commands; copy a commands byte-for-byte"
}
assert metadata["bytes_accounted"] == metadata["input_bytes"]
assert metadata["output_bytes"] == counts["a"]["bytes"]
assert metadata["empty_additions"] == 1, metadata
receipt.write_text(json.dumps(metadata, indent=2) + "\n")
print(json.dumps(metadata, indent=2))
