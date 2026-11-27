#!/usr/bin/env python3
"""Independent, read-only audit of the supplied 40,000 K58 trials and receipts.
No solver or K58 search is invoked; imports are only Python stdlib.
"""
import bisect
import collections
import csv
import gzip
import hashlib
import json
import math
import random
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = ROOT / "extracted/K58_wall_10k_batches"
R = BASE / "results"
I = BASE / "inputs"
OUT = ROOT / "work"
OUT.mkdir(exist_ok=True)


def shabytes(data):
    return hashlib.sha256(data).hexdigest()


def read_tsv(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def read_json(path):
    with open(path, "rb") as f:
        return json.load(f)


def counter(rows, key):
    return dict(sorted(collections.Counter(key(r) for r in rows).items(), key=lambda x: str(x[0])))


def quant(values):
    values = sorted(values)
    if not values:
        return None
    def q(p):
        if len(values) == 1:
            return values[0]
        x = p * (len(values)-1)
        lo = int(x)
        hi = min(lo+1, len(values)-1)
        return values[lo] + (values[hi]-values[lo])*(x-lo)
    return {"n":len(values), "sum":sum(values), "min":values[0],
            "p05":q(.05), "p25":q(.25), "median":q(.5),
            "p75":q(.75), "p95":q(.95), "max":values[-1],
            "mean":sum(values)/len(values)}


def wilson(k, n, z=1.959963984540054):
    p = k/n
    den = 1+z*z/n
    mid = (p+z*z/(2*n))/den
    half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [p, mid-half, mid+half]


def main():
    result = {"checks":{}, "details":{}}
    ck = result["checks"]
    det = result["details"]

    # External TSV must be exactly the uncompressed bundled trials table.
    ext = (ROOT/"inputs/K58_40000_pattern_trials.tsv").read_bytes()
    bundled = gzip.decompress((R/"trials.tsv.gz").read_bytes())
    ck["external_tsv_equals_bundled_trials_bytes"] = (ext == bundled)
    ck["external_tsv_sha256"] = shabytes(ext)
    trials = list(csv.DictReader(ext.decode().splitlines(), delimiter="\t"))
    for wave in "ABCD":
        assert sum(r["wave"] == wave for r in trials) == 10000
    assert len(trials) == 40000
    expected_fields = ["wave","rank","global_index","row_id","profile","arm","w","z",
        "raw_pair","ordering_stage","possible_two_smallest","preferred_label","probe_raw",
        "conflicts_raw","probe_sorted","conflicts_sorted","probe_preferred","conflicts_preferred",
        "marked_template_plus_arm","third_arm_probe"]
    assert list(trials[0]) == expected_fields
    ck["trial_rows"] = len(trials)
    ck["distinct_global_indices"] = len({r["global_index"] for r in trials})
    ck["distinct_physical_identities"] = len({(r["row_id"],r["w"],r["z"]) for r in trials})
    ck["distinct_rows"] = len({r["row_id"] for r in trials})
    ck["per_wave_ranks_exact_0_through_9999"] = all(
        sorted(int(r["rank"]) for r in trials if r["wave"] == w) == list(range(10000)) for w in "ABCD")
    det["wave_counts"] = counter(trials, lambda r:r["wave"])
    det["stage_counts_by_wave"] = {w:counter((r for r in trials if r["wave"]==w),lambda r:r["ordering_stage"]) for w in "ABCD"}
    det["arm_counts_by_wave"] = {w:counter((r for r in trials if r["wave"]==w),lambda r:r["arm"]) for w in "ABCD"}
    det["profile_counts_by_wave"] = {w:counter((r for r in trials if r["wave"]==w),lambda r:r["profile"]) for w in "ABCD"}
    det["rows_per_wave"] = {w:len({r["row_id"] for r in trials if r["wave"]==w}) for w in "ABCD"}
    det["distinct_rows_by_wave_pair"] = {
        a+b:len({r["row_id"] for r in trials if r["wave"]==a}&{r["row_id"] for r in trials if r["wave"]==b})
        for a,b in [("A","B"),("A","C"),("A","D"),("B","C"),("B","D"),("C","D")]}
    assert ck["distinct_global_indices"] == ck["distinct_physical_identities"] == 40000
    assert ck["distinct_rows"] == 11134

    # Independent reconstruction of the raw roster and sampling maps.
    pairrows = read_tsv(I/"pair-class-index.tsv.gz")
    pairs = {n:[(r["word_1"],r["word_2"]) for r in pairrows if r[f"arm_{n}"]=="SAT"]
             for n in (11,12,13,14)}
    assert {n:len(p) for n,p in pairs.items()} == {11:5361,12:5361,13:5361,14:5190}
    wall = [json.loads(x) for x in gzip.decompress((I/"wall.jsonl.gz").read_bytes()).splitlines()]
    idxrows = read_tsv(I/"campaign.tsv")
    idx = {r["row_id"]:r for r in idxrows}
    bindings = [json.loads(x) for x in gzip.decompress((I/"physical-bindings.jsonl.gz").read_bytes()).splitlines()]
    campaign_arm = {r["id"]:r["pentagons"][int(idx[r["id"]]["arm_index"])]["size"] for r in bindings}
    rowkeys = sorted(r["id"] for r in wall)
    assert len(rowkeys) == len(idx) == len(campaign_arm) == 11585
    offsets = {}
    ends = []
    total = 0
    for rid in rowkeys:
        offsets[rid] = total
        total += len(pairs[campaign_arm[rid]])
        ends.append(total)
    assert total == 60817332
    pairord = {n:{p:i for i,p in enumerate(ps)} for n,ps in pairs.items()}
    for r in trials:
        rid,n,w,z = r["row_id"],int(r["arm"]),r["w"],r["z"]
        assert rid in offsets and campaign_arm[rid] == n and r["profile"] == idx[rid]["profile"]
        assert (w,z) in pairord[n]
        assert int(r["global_index"]) == offsets[rid]+pairord[n][w,z]
        assert len(w)==len(z)==5 and set(w+z)<=set("012")
        assert r["raw_pair"] == "HAS_ARM_WITNESS"
    ck["all_40000_global_indices_reconstructed"] = True
    ck["all_rows_profiles_arms_and_words_match_roster"] = True

    # Recreate A/B without using bundle sampling code or output files.
    rng = random.Random(581433326)
    draws = rng.sample(range(total),20000)
    ab = [r for r in trials if r["wave"] in "AB"]
    ab.sort(key=lambda r:(r["wave"],int(r["rank"])))
    for i,(g,r) in enumerate(zip(draws,ab)):
        j = bisect.bisect_right(ends,g)
        rid = rowkeys[j]
        n = campaign_arm[rid]
        p = pairs[n][g-(ends[j-1] if j else 0)]
        assert (r["global_index"],r["row_id"],r["arm"],r["w"],r["z"]) == (str(g),rid,str(n),*p)
        assert r["wave"] == ("A" if i<10000 else "B") and int(r["rank"]) == i%10000
    ck["AB_exact_seed_and_uniform_without_replacement_draw_reproduced"] = True

    capacity_rows = read_tsv(R/"capacity.tsv.gz")
    cap = {(int(r["n"]),r["w"],r["z"]):r["stage"] for r in capacity_rows}
    survivors = {n:[p for p in pairs[n] if cap[n,*p]=="SURVIVES"] for n in pairs}
    assert {n:len(x) for n,x in survivors.items()} == {11:1308,12:1249,13:743,14:651}
    send = []
    stotal = 0
    for rid in rowkeys:
        stotal += len(survivors[campaign_arm[rid]])
        send.append(stotal)
    assert stotal == 8254067
    seen = {(r["row_id"],r["w"],r["z"]) for r in trials if r["wave"] in "AB"}
    rng = random.Random(581433327)
    c_expect=[]
    got=set()
    while len(c_expect)<10000:
        pos=rng.randrange(stotal)
        j=bisect.bisect_right(send,pos)
        rid=rowkeys[j];n=campaign_arm[rid]
        w,z=survivors[n][pos-(send[j-1] if j else 0)]
        if pos in got or (rid,w,z) in seen: continue
        got.add(pos)
        c_expect.append((rid,n,w,z))
    c_actual=sorted((r for r in trials if r["wave"]=="C"),key=lambda r:int(r["rank"]))
    assert [(r["row_id"],int(r["arm"]),r["w"],r["z"]) for r in c_actual] == c_expect
    ck["C_exact_conditional_survivor_frame_draw_reproduced"] = True

    catalogs={n:read_json(R/"preferred"/f"{n}.json") for n in pairs}
    preferred={n:[tuple(p) for p in catalogs[n]["pairs"]] for n in pairs}
    assert {n:len(x) for n,x in preferred.items()} == {11:1214,12:941,13:530,14:156}
    pend=[];ptotal=0
    for rid in rowkeys:
        ptotal += len(preferred[campaign_arm[rid]])
        pend.append(ptotal)
    assert ptotal == 3604436
    prior={int(r["global_index"]) for r in trials if r["wave"] in "ABC"}
    rng=random.Random(581433328);got=set();d_expect=[]
    while len(d_expect)<10000:
        pos=rng.randrange(ptotal);j=bisect.bisect_right(pend,pos)
        rid=rowkeys[j];n=campaign_arm[rid];w,z=preferred[n][pos-(pend[j-1] if j else 0)]
        g=offsets[rid]+pairord[n][w,z]
        if g in prior or pos in got: continue
        got.add(pos);d_expect.append((rid,n,w,z,g))
    d_actual=sorted((r for r in trials if r["wave"]=="D"),key=lambda r:int(r["rank"]))
    assert [(r["row_id"],int(r["arm"]),r["w"],r["z"],int(r["global_index"])) for r in d_actual] == d_expect
    ck["D_exact_conditional_preferred_frame_draw_reproduced"] = True

    # Row queue independently confirms root status, exact arm totals, contiguous indices,
    # and the number of D probes charged to each row.
    queue=read_tsv(R/"row-queue.tsv.gz")
    assert len(queue)==11585 and len({r["row_id"] for r in queue})==11585
    assert all(r["root_status"]=="OPEN" for r in queue)
    expected_pos=0
    sorted_by_n=collections.Counter(int(r["n"]) for r in read_tsv(R/"sorted-outcomes.tsv.gz") if r["status"]=="SAT")
    d_by_row=collections.Counter(r["row_id"] for r in trials if r["wave"]=="D")
    for q in queue:
        rid=q["row_id"];n=int(q["arm"])
        assert campaign_arm[rid]==n and rid in offsets
        assert (int(q["unrestricted_live_pairs"]),int(q["admitted_by_column_rule"]),
                int(q["possible_two_smallest"]),int(q["preferred_pairs"])) == (
                len(pairs[n]),len(survivors[n]),
                sorted_by_n[n],
                len(preferred[n]))
        assert int(q["index_begin"])==expected_pos
        expected_pos+=len(preferred[n])
        assert int(q["index_end_exclusive"])==expected_pos
        assert int(q["preferred_jobs_probed"])==d_by_row[rid]
    assert expected_pos==ptotal and sum(d_by_row.values())==10000
    ck["row_queue_all_11585_OPEN_counts_indices_and_D_charges_recomputed"] = True
    det["row_queue"]={"rows":11585,"root_OPEN":11585,"contiguous_preferred_indices":expected_pos,
                      "D_probed_jobs":10000,"rows_with_D_probes":len(d_by_row)}

    # Independently recompute ordering stages from complete local tables/catalogs.
    sortedrows=read_tsv(R/"sorted-outcomes.tsv.gz")
    exact={(int(r["n"]),r["w"],r["z"]) for r in sortedrows if r["status"]=="SAT"}
    assert len(exact)==3330 and len(sortedrows)==3951
    for r in trials:
        n,w,z=int(r["arm"]),r["w"],r["z"]
        rule=cap[n,w,z]
        stage=rule if rule!="SURVIVES" else ("SORTED_ARM" if (n,w,z) not in exact else
                    ("REASSIGN" if (w,z) not in preferred[n] else "PREFERRED"))
        assert stage==r["ordering_stage"]
        assert r["possible_two_smallest"]==str(int((n,w,z) in exact))
        assert r["preferred_label"]==str(int((w,z) in preferred[n]))
        if r["wave"]=="C": assert rule=="SURVIVES"
        if r["wave"]=="D": assert (w,z) in preferred[n]
    ck["all_40000_stages_and_local_table_flags_recomputed"] = True
    det["raw_and_preferred_weighted_totals"]={"raw":total,"after_degree":stotal,"sorted":sum(
        sum(campaign_arm[rid]==n for rid in rowkeys)*sum(n2==n for n2,w,z in exact) for n in pairs),
        "preferred":ptotal}
    det["preferred_conditional_C"]={
        "preferred_among_after_degree":wilson(4391,10000),
        "preferred_among_exact_sorted":wilson(4391,6641),
        "reassign_among_exact_sorted":wilson(2250,6641)}

    # Join every external probe cell back to every detailed receipt, then all block receipts.
    runs={}
    for name in ("cheap-raw","cheap-C-control","cheap-sorted","cheap-preferred"):
        top=read_tsv(R/(name+".tsv.gz")); meta=read_json(R/(name+".json"))
        for r in top:
            for k in ("rank","block","cap","conflicts"):
                r[k]=int(r[k])
        allblocks=[]; block_seconds={}; block_sizes=[]
        for p in sorted((R/(name+"-blocks")).glob("*.json.gz")):
            d=json.loads(gzip.decompress(p.read_bytes()))
            rs=d["records"];allblocks.extend(rs);block_sizes.append(len(rs))
            assert len({r["block"] for r in rs})==1
            assert len({r["group"] for r in rs})==1
            block_seconds[str(rs[0]["block"])]=d["seconds"]
            # String form of JSON scalars equals TSV fields, including empty absent fields.
            for r in rs:
                assert all(str(v)==str(r[k]) for k,v in r.items())
        key=lambda r:(r["wave"],int(r["rank"]))
        assert sorted(allblocks,key=key)==sorted(top,key=key)
        assert len({key(r) for r in top})==len(top)==meta["records"]
        assert len({key(r) for r in allblocks})==len(allblocks)
        assert block_seconds==meta["seconds_by_block"]
        assert len(block_sizes)==meta["blocks"]
        assert all(0<n<=meta["block_size"] for n in block_sizes)
        assert sum(r["conflicts"] for r in top)==meta["conflicts"]
        assert dict(collections.Counter(r["status"] for r in top))==meta["verdicts"]
        assert all(int(r["cap"])==meta["cap"] for r in top)
        runs[name]={"top":top,"meta":meta,"blocks":allblocks}
        det[name]={"records":len(top),"verdicts":dict(collections.Counter(r["status"] for r in top)),
                   "conflicts":quant([r["conflicts"] for r in top]),
                   "blocks":len(block_sizes),"block_size":quant(block_sizes),
                   "distinct_groups":len({r["group"] for r in top}),
                   "block_seconds_sum":sum(block_sizes and block_seconds.values()),
                   "reported_run_seconds":meta["run_seconds"],"workers":meta["workers"]}
    ck["all_751_block_gz_receipts_reconstruct_top_level_probe_tables"] = True
    ck["all_probe_counts_conflicts_verdicts_and_block_times_match_metadata"] = True

    lookup={name:{(r["wave"],int(r["rank"])):r for r in d["top"]} for name,d in runs.items()}
    for r in trials:
        for label,name in [("raw","cheap-raw" if r["wave"] in "AB" else "cheap-C-control" if r["wave"]=="C" else None),
                           ("sorted","cheap-sorted" if r["wave"]=="C" else None),
                           ("preferred","cheap-preferred" if r["wave"]=="D" else None)]:
            val=r["probe_"+label];cf=r["conflicts_"+label]
            if name is None:
                assert val==cf==""
            else:
                q=lookup[name][r["wave"],int(r["rank"])]
                assert (q["row_id"],q["w"],q["z"])==(r["row_id"],r["w"],r["z"])
                assert val==q["status"] and int(cf)==q["conflicts"]
    ck["all_probe_cells_join_exactly_to_identities_conflicts_and_statuses"] = True
    det["C_run_comparability"]={
        "raw_workers":runs["cheap-C-control"]["meta"]["workers"],"sorted_workers":runs["cheap-sorted"]["meta"]["workers"],
        "raw_groups":det["cheap-C-control"]["distinct_groups"],"sorted_groups":det["cheap-sorted"]["distinct_groups"],
        "raw_blocks":det["cheap-C-control"]["blocks"],"sorted_blocks":det["cheap-sorted"]["blocks"],
        "raw_reported_run_seconds":det["cheap-C-control"]["reported_run_seconds"],
        "sorted_reported_run_seconds":det["cheap-sorted"]["reported_run_seconds"],
        "sorted_divided_by_raw_reported_run_seconds":det["cheap-sorted"]["reported_run_seconds"]/det["cheap-C-control"]["reported_run_seconds"],
        "raw_block_seconds_sum":det["cheap-C-control"]["block_seconds_sum"],
        "sorted_block_seconds_sum":det["cheap-sorted"]["block_seconds_sum"],
        "sorted_divided_by_raw_block_seconds":det["cheap-sorted"]["block_seconds_sum"]/det["cheap-C-control"]["block_seconds_sum"],
        "note":"Same cells/cap/physical assumptions, but added sorting formulas, grouping, learning reuse and worker count differ; not a causal runtime comparison."}

    rawC=lookup["cheap-C-control"]; sortedC=lookup["cheap-sorted"]
    assert set(rawC)==set(sortedC)
    assert all(rawC[k]["assumptions_sha256"]==sortedC[k]["assumptions_sha256"] for k in rawC)
    ck["C_raw_sorted_identities_rank_cap_and_physical_assumption_hashes_match"] = True
    det["C_raw_sorted_formula_group_hashes"]={
        "equal":sum(rawC[k]["group"]==sortedC[k]["group"] for k in rawC),
        "different":sum(rawC[k]["group"]!=sortedC[k]["group"] for k in rawC)}
    det["C_sorted_by_stage_and_status"]={stage:
        dict(sorted(collections.Counter(sortedC[r["wave"],int(r["rank"])]["status"]
              for r in trials if r["wave"]=="C" and r["ordering_stage"]==stage).items()))
        for stage in ("SORTED_ARM","REASSIGN","PREFERRED")}
    assert sum(r["status"]=="UNSAT_SORTED_ARM" for r in runs["cheap-sorted"]["top"]) == 2418
    for r in trials:
        if r["wave"]!="C":continue
        ss=sortedC["C",int(r["rank"])]["status"]
        if ss=="UNSAT_SORTED_ARM":assert r["ordering_stage"]=="SORTED_ARM"
    det["C_sorted_exclusions_split"]={"complete_table_exclusions":3359,
        "solver_reported_UNSAT_SORTED_ARM":2418,"table_exclusions_still_OPEN_at_cap":941,
        "table_realizable_REASSIGN_or_PREFERRED_any_sorted_UNSAT":0,
        "raw_UNSAT":0}
    for stage in ("SORTED_ARM","REASSIGN","PREFERRED"):
        ids=[int(r["rank"]) for r in trials if r["wave"]=="C" and r["ordering_stage"]==stage]
        det["C_conflicts_"+stage]={
            "raw":quant([rawC["C",i]["conflicts"] for i in ids]),
            "sorted":quant([sortedC["C",i]["conflicts"] for i in ids])}
    both_open=[i for i in range(10000) if sortedC["C",i]["status"]=="OPEN"]
    det["C_matched_conflicts_on_sorted_OPEN_cells"]={
        "n":len(both_open),"raw":quant([rawC["C",i]["conflicts"] for i in both_open]),
        "sorted":quant([sortedC["C",i]["conflicts"] for i in both_open]),
        "sorted_minus_raw":quant([sortedC["C",i]["conflicts"]-rawC["C",i]["conflicts"] for i in both_open])}
    exact_c_ranks=[int(r["rank"]) for r in trials if r["wave"]=="C" and r["ordering_stage"]!="SORTED_ARM"]
    local_bad_c_ranks=[int(r["rank"]) for r in trials if r["wave"]=="C" and r["ordering_stage"]=="SORTED_ARM"]
    assert len(exact_c_ranks)==6641 and len(local_bad_c_ranks)==3359
    raw_exact=sum(rawC["C",i]["conflicts"] for i in exact_c_ranks)
    sorted_exact=sum(sortedC["C",i]["conflicts"] for i in exact_c_ranks)
    assert all(sortedC["C",i]["status"]=="OPEN" for i in exact_c_ranks)
    det["C_locally_realizable_matched_comparison"]={"cells":6641,"raw_UNSAT":0,"sorted_UNSAT":0,
        "raw_conflicts":raw_exact,"sorted_conflicts":sorted_exact,
        "sorted_minus_raw_conflicts":sorted_exact-raw_exact,
        "sorted_relative_conflict_change":(sorted_exact-raw_exact)/raw_exact,
        "note":"These are REASSIGN plus PREFERRED: realizable under the exact two-smallest local-arm table."}
    det["C_table_exclusions_avoidable_work"]={"cells":3359,
        "sorted_conflicts_actually_spent":sum(sortedC["C",i]["conflicts"] for i in local_bad_c_ranks),
        "sorted_UNSAT_conflicts":sum(sortedC["C",i]["conflicts"] for i in local_bad_c_ranks if sortedC["C",i]["status"]!="OPEN"),
        "sorted_OPEN_conflicts":sum(sortedC["C",i]["conflicts"] for i in local_bad_c_ranks if sortedC["C",i]["status"]=="OPEN"),
        "implementation_note":"cheap.py checks the complete local table only inside certify(), after solve_limited returns False; it does not prefilter before solve_limited."}
    det["C_stage_by_arm"]={a:dict(collections.Counter(r["ordering_stage"] for r in trials
        if r["wave"]=="C" and r["arm"]==a)) for a in ("11","12","13","14")}
    det["C_sorted_UNSAT_conflicts"]=quant([r["conflicts"] for r in runs["cheap-sorted"]["top"] if r["status"]=="UNSAT_SORTED_ARM"])
    c_by_rank={int(r["rank"]):r for r in trials if r["wave"]=="C"}
    det["C_sorted_UNSAT_by_arm"] = dict(collections.Counter(
        c_by_rank[r["rank"]]["arm"] for r in runs["cheap-sorted"]["top"] if r["status"]=="UNSAT_SORTED_ARM"))

    # Per-wave conflict distribution, arm/profile signal, and cap semantics.
    for wave,name in [("A","cheap-raw"),("B","cheap-raw"),("C","cheap-C-control"),("C_sorted","cheap-sorted"),("D","cheap-preferred")]:
        source_wave="C" if wave=="C_sorted" else wave
        ts={int(r["rank"]):r for r in trials if r["wave"]==source_wave}
        rr=[r for r in runs[name]["top"] if r["wave"]==source_wave]
        if wave in "AB": rr=[r for r in rr if r["wave"]==wave]
        det[wave+"_conflicts_by_arm"]={a:quant([q["conflicts"] for q in rr if ts[int(q["rank"])]["arm"]==a]) for a in ("11","12","13","14")}
        det[wave+"_OPEN_conflicts_extremes"]={"below_cap":sum(q["conflicts"]<128 for q in rr if q["status"]=="OPEN"),
             "equal_cap":sum(q["conflicts"]==128 for q in rr if q["status"]=="OPEN"),
             "above_cap":sum(q["conflicts"]>128 for q in rr if q["status"]=="OPEN")}
    d_by_rank={int(r["rank"]):r for r in trials if r["wave"]=="D"}
    det["D_verdict_by_arm"]={a:dict(collections.Counter(q["status"] for q in runs["cheap-preferred"]["top"]
        if d_by_rank[q["rank"]]["arm"]==a)) for a in ("11","12","13","14")}
    det["D_verdict_by_profile"]={p:dict(collections.Counter(q["status"] for q in runs["cheap-preferred"]["top"]
        if d_by_rank[q["rank"]]["profile"]==p)) for p in sorted({r["profile"] for r in trials})}

    # The longer-budget cold controls are a separate sample subset/engine/cap.
    cold=read_tsv(R/"cold-raw.tsv.gz")
    assert len(cold)==512 and all(r["status"]=="OPEN" and int(r["conflicts"])>=512 and r["cap"]=="512" for r in cold)
    assert {(r["wave"],int(r["rank"])) for r in cold}=={(w,i) for w in "AB" for i in range(256)}
    det["cold_raw_512_controls"]={"records":512,"OPEN":512,"conflicts":quant([int(r["conflicts"]) for r in cold]),
                                  "exactly_cap":sum(int(r["conflicts"])==512 for r in cold),
                                  "above_cap":sum(int(r["conflicts"])>512 for r in cold),
                                  "seconds":quant([float(r["seconds"]) for r in cold]),
                                  "sum_seconds":sum(float(r["seconds"]) for r in cold)}
    ck["cold_controls_all_OPEN_not_closure"] = True

    # Proj. receipt roster checks explain projection re-use and never upgrade OPEN to UNSAT.
    glue=read_tsv(R/"raw-glue.tsv.gz")
    det["projection_receipts"]={"rows":len(glue),"status_counts":dict(collections.Counter(r["status"] for r in glue)),
        "conflicts":quant([int(r["conflicts"]) for r in glue])}
    maps=json.loads(gzip.decompress((R/"maps.json.gz").read_bytes()))
    gluemap={(r["key"],r["w"],r["z"]):r for r in glue}
    gcount=0
    for r in trials:
        if r["wave"] not in "AB": assert r["marked_template_plus_arm"]=="";continue
        g=gluemap[maps[r["row_id"]]["key"],r["w"],r["z"]]
        assert g["status"]==r["marked_template_plus_arm"]=="SAT";gcount+=1
    assert gcount==20000
    third=read_tsv(R/"three-arm-outcomes.tsv.gz")
    mp3=json.loads(gzip.decompress((R/"three-arm-maps.json.gz").read_bytes()))
    t3={(r["key"],r["w"],r["z"]):r for r in third}
    thirdstats=collections.Counter()
    for r in trials:
        if r["wave"]!="A" or r["row_id"] not in mp3: assert r["third_arm_probe"]=="";continue
        status=t3[mp3[r["row_id"]]["key"],r["w"],r["z"]]["status"]
        assert status==r["third_arm_probe"];thirdstats[status]+=1
    det["third_arm_projection"]={"stored_receipts":len(third),"stored_distinct_lookup_keys":len(t3),
        "mapped_A_trials":sum(thirdstats.values()),"mapped_statuses":dict(thirdstats),
        "map_row_ids":len(mp3)}
    ck["projection_SAT_is_only_partial_graph_witness_not_full_row_closure"] = True

    # Summary arithmetic and headline ratios.
    s=read_json(R/"summary.json")
    assert s["distinct_sample_cells"]==40000 and s["distinct_sample_rows"]==11134
    assert s["original_cells"]==total and s["forward_queue"]==ptotal and s["original_rows"]==11585
    det["compression_arithmetic"]={
        "preferred_divided_by_raw":ptotal/total,
        "scheduled_job_reduction_percent":100*(1-ptotal/total),
        "preferred_divided_by_after_degree":ptotal/stotal,
        "preferred_divided_by_sorted":ptotal/det["raw_and_preferred_weighted_totals"]["sorted"],
        "note":"Representative-count compression only; all ordinary rows remain OPEN."}
    det["all_raw_probe_verdicts"]={name:dict(collections.Counter(r["status"] for r in runs[name]["top"]))
                                   for name in ("cheap-raw","cheap-C-control")}
    det["preconditions"]={"ordinary_wall_rows_OPEN":11585,"verified_whole_row_closures_in_these_probe_receipts":0,
        "A_B_C_raw_OPEN":30000,"D_preferred_OPEN":10000,"C_sorted_UNSAT_SORTED_ARM":2418,
        "C_complete_local_table_exclusions":3359}
    det["arm_weighted_frames"]={
        frame:{str(n):sum(campaign_arm[rid]==n for rid in rowkeys)*count(n) for n in pairs}
        for frame,count in [("raw",lambda n:len(pairs[n])),("after_degree",lambda n:len(survivors[n])),
            ("sorted",lambda n:sum(n2==n for n2,w,z in exact)),("preferred",lambda n:len(preferred[n]))]}
    det["C_local_exclusion_solver_coverage"]={"UNSAT_among_table_exclusions":wilson(2418,3359),
        "cap_OPEN_among_table_exclusions":wilson(941,3359)}

    path=OUT/"audit_results.json"
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"checks":ck,"headline":det["preconditions"],"compression":det["compression_arithmetic"],
        "C_split":det["C_sorted_exclusions_split"],"C_stage_status":det["C_sorted_by_stage_and_status"],
        "run_summaries":{k:det[k] for k in runs},"D_conflicts":det["D_conflicts_extremes"] if "D_conflicts_extremes" in det else det["D_OPEN_conflicts_extremes"]},indent=2,sort_keys=True))
    print("WROTE",path)

if __name__=="__main__":main()
