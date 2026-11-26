#!/usr/bin/env python3
"""Rebind the supplied campaign manifest after the reviewed source patch.

This authenticates the resulting bytes, not their mathematical correctness.
Correctness is checked separately by the native/tree/matrix test harnesses.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ORIGINAL_MANIFEST_SHA256 = "87f4f890cea4ff0413778a1b665dd9f30825d616d9327ad3be19b5da83cfc029"
CHANGED_SOURCES = {"frontier.py", "arm_pairs.py", "coverage.py", "verify_campaign.py"}
NEW_SOURCE = "campaign_cache.py"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic(path, data):
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def parse_manifest(data):
    entries = []
    seen = set()
    for line in data.decode("utf-8").splitlines():
        if len(line) < 67 or line[64:66] != "  ":
            raise ValueError("unexpected SHA256SUMS line format")
        digest, name = line[:64], line[66:]
        if (len(name) == 0 or name.startswith("/") or ".." in Path(name).parts or
                len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest)):
            raise ValueError(f"invalid manifest entry: {name!r}")
        if name in seen:
            raise ValueError(f"duplicate manifest entry: {name}")
        seen.add(name)
        entries.append([digest, name])
    if len(entries) != 999:
        raise ValueError(f"expected the supplied 999-entry manifest, got {len(entries)}")
    if not CHANGED_SOURCES <= seen or NEW_SOURCE in seen:
        raise ValueError("unexpected campaign source manifest coverage")
    return entries


def verify_files(campaign, entries):
    for digest, name in entries:
        path = campaign / name
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"manifest target is not a regular file: {name}")
        if sha(path.read_bytes()) != digest:
            raise ValueError(f"manifest hash mismatch: {name}")


def finalise(campaign):
    campaign = campaign.resolve()
    path = campaign / "SHA256SUMS"
    before = path.read_bytes()
    before_hash = sha(before)
    if before_hash != ORIGINAL_MANIFEST_SHA256:
        raise ValueError(f"refusing unrecognized manifest: {before_hash}")
    entries = parse_manifest(before)
    # Refuse to certify an arbitrary unpatched state.  The semantic tests still
    # have to pass separately; these guards only pin the reviewed base/outputs.
    if (campaign / NEW_SOURCE).read_bytes() == b"":
        raise ValueError("empty campaign_cache.py")
    frontier_bytes = (campaign / "frontier.py").read_bytes()
    if (b"NativeCacheValidator" not in frontier_bytes or
            b"strict_check_drat" not in frontier_bytes):
        raise ValueError("campaign does not contain the reviewed native cache integration")
    # The optional tree integration changes frontier too.  Require at least all
    # five code targets rather than guessing validity from a manifest rewrite.
    for name in CHANGED_SOURCES | {NEW_SOURCE}:
        if not (campaign / name).is_file():
            raise ValueError(f"missing patched source: {name}")
    for entry in entries:
        if entry[1] in CHANGED_SOURCES:
            entry[0] = sha((campaign / entry[1]).read_bytes())
    entries.append([sha((campaign / NEW_SOURCE).read_bytes()), NEW_SOURCE])
    entries.sort(key=lambda item: item[1])
    data = "".join(f"{digest}  {name}\n" for digest, name in entries).encode()
    # Independent format/count checks for the new 1000-entry manifest.
    if len(entries) != 1000 or len({name for _, name in entries}) != 1000:
        raise ValueError("invalid final entry count")
    verify_files(campaign, entries)
    atomic(path, data)
    verify_files(campaign, entries)
    return {"schema": "k58-native-cache-manifest/v1",
            "campaign": str(campaign),
            "manifest_before_sha256": before_hash,
            "manifest_after_sha256": sha(data),
            "entries": len(entries), "verified_entries": len(entries),
            "source_sha256": {name: sha((campaign / name).read_bytes())
                              for name in sorted(CHANGED_SOURCES | {NEW_SOURCE})},
            "frontier_has_tree_integration": b"def checked_tree(" in frontier_bytes,
            "manifest_note": "Byte authentication only; semantic checks are separate."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    args = parser.parse_args()
    print(json.dumps(finalise(args.campaign), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
