#!/usr/bin/env python3
"""Atomically install the fail-closed cache validator into a campaign copy.

The supplied ZIP remains untouched.  The original frontier source is identified
by SHA-256, so this refuses to overwrite an independently modified campaign.
Fresh and cached native proof checks both use strict binary DRAT replay.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

ORIGINAL_FRONTIER_SHA256 = "d6d49c41eea5d865c90e0aa41d97f1aca19f659beedcadd667075088e35c36cd"

IMPORT_OLD = "from problem import check_model, family_and_pins, read_dimacs, row_formula\n"
IMPORT_NEW = (IMPORT_OLD +
              "from campaign_cache import (NativeCacheValidator, strict_check_drat,\n"
              "                            validate_total_model)\n")

CACHE_OLD = '''    if receipt.exists():
        old=json.loads(receipt.read_bytes())
        # The available shared rules can grow later. Keep older disjoint wave receipts.
        if all(old.get(k)==v for k,v in expected.items()): return old
        name+='-'+sha(query)[:12]; receipt=folder/(name+'.json')
        if receipt.exists():
            old=json.loads(receipt.read_bytes())
            assert all(old.get(k)==v for k,v in expected.items())
            return old
'''
CACHE_NEW = '''    validator=NativeCacheValidator(sha,read_dimacs,check_model,
                                   lambda q,p: strict_check_drat(HERE/'tools/drat-trim',q,p))
    if receipt.exists():
        old=validator.load(receipt,expected,plain,query,cube)
        if old is not None: return old
        # The available shared rules can grow later. Keep older disjoint wave receipts.
        name+='-'+sha(query)[:12]; receipt=folder/(name+'.json')
        if receipt.exists():
            old=validator.load(receipt,expected,plain,query,cube,mismatch_is_invalid=True)
            assert old is not None
            return old
'''
MODEL_OLD = "            nv,cls=read_dimacs(plain); check_model(cls,cube,model,nv)\n"
MODEL_NEW = "            validate_total_model(plain,cube,model,read_dimacs,check_model)\n"
PROOF_OLD = "check_drat(q,p)"
PROOF_NEW = "strict_check_drat(HERE/'tools/drat-trim',q,p)"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def replace_once(source, old, new, label):
    if source.count(old) != 1:
        raise ValueError(f"expected exactly one {label} replacement site")
    return source.replace(old, new, 1)


def atomic(path, data):
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_bytes(data)
    os.replace(temporary, path)


def install(campaign, validator_source):
    campaign = campaign.resolve()
    frontier = campaign / "frontier.py"
    helper = campaign / "campaign_cache.py"
    target = validator_source.resolve()
    original_bytes = frontier.read_bytes()
    old_hash = sha(original_bytes)
    if old_hash != ORIGINAL_FRONTIER_SHA256:
        raise ValueError(f"refusing unrecognized frontier.py: {old_hash}")
    source = original_bytes.decode("utf-8")
    source = replace_once(source, IMPORT_OLD, IMPORT_NEW, "import")
    source = replace_once(source, CACHE_OLD, CACHE_NEW, "cache")
    source = replace_once(source, MODEL_OLD, MODEL_NEW, "fresh model")
    if source.count(PROOF_OLD) != 3:
        raise ValueError("expected exactly three fresh proof replay sites")
    source = source.replace(PROOF_OLD, PROOF_NEW)
    new_bytes = source.encode("utf-8")
    compile(new_bytes, str(frontier), "exec")
    helper_bytes = target.read_bytes()
    compile(helper_bytes, str(helper), "exec")
    atomic(helper, helper_bytes)
    atomic(frontier, new_bytes)
    return {"schema": "k58-native-cache-fix-install/v1",
            "campaign": str(campaign),
            "frontier_before_sha256": old_hash,
            "frontier_after_sha256": sha(new_bytes),
            "campaign_cache_sha256": sha(helper_bytes),
            "supplied_zip_modified": False,
            "manifest_modified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("campaign", type=Path)
    parser.add_argument("--validator-source", type=Path,
                        default=Path(__file__).with_name("campaign_cache.py"))
    args = parser.parse_args()
    print(json.dumps(install(args.campaign, args.validator_source),
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
