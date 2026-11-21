#!/usr/bin/env python3
"""Claims ledger for one research problem: DIR/ledger.md, numbered and append-only.

    ledger.py add DIR STATUS TEXT [--at LOCATOR] [--on ID] [--kind KIND] [--goal] [--case]
    ledger.py status DIR
    ledger.py checkpoint DIR
    ledger.py gate DIR

STATUS is one of:
  OPEN                    a statement still to settle. --goal marks the goal (the newest counts).
  PROVED, REFUTED         a settled statement; needs --at, where the argument is. --on ID settles
                          the OPEN entry ID. --case: it covers only some of the objects (some n,
                          a finite range), which does not count as progress. Cite the entries an
                          argument uses as "#N" in TEXT: they must be statements in force, and
                          the gate refuses a goal whose citations reach an entry that is
                          retracted, refuted or still OPEN (an OPEN entry counts once a PROVED
                          entry settles it).
  TRIED --on ID           an approach to entry ID, set aside, and why.
  CHECK --on ID --kind K  a check of PROVED or REFUTED entry ID; TEXT starts with PASS or GAP and
                          says what it covered. K: self (the model that wrote it), compute (the
                          finite or numerical claims, recomputed), lean, model (a model that did
                          not write it), person. Only lean, model and person check the argument.
  RETRACT --on ID         takes statement or check ID out of force, with the reason.
A file locator must exist inside DIR or the current directory; "notes.md#3" must also have
a line "3." (or a heading "## 3."). "ultramath:<swarm>/<member>" and "person:<who>" are taken
as they are. The script keeps a hash of ledger.md in .ledger.sha256: status warns about, and add, checkpoint
and gate refuse, a ledger edited by hand. The gate allows the goal when its first line starts with
PROVED or REFUTED; NOT YET means it does not. Standard library only. Prints its result and exits
0, or "ERROR: ..." and exits 1.
"""

import hashlib
import re
import sys
from pathlib import Path

STATUSES = ("OPEN", "PROVED", "REFUTED", "TRIED", "CHECK", "RETRACT")
SETTLED = ("PROVED", "REFUTED")
KINDS = ("self", "compute", "lean", "model", "person")
WHOLE = ("lean", "model", "person")
LINE = re.compile(r"^(\d+)\. ([A-Z]+)(?: #(\d+))?((?: \[[a-z]+\])*): (.*?)(?: — (\S.*))?$")
MARK = re.compile(r"^- checkpoint after #(\d+): (progress|stalled \d+)$", re.M)


EDITED = ("ledger.md was edited by hand since the script last wrote it; the script will not add to it "
          "and the gate refuses it. Undo the edit (git) and record changes with ledger add; if you "
          "cannot, stop and tell the person.")


class Fail(Exception):
    pass


def read(d):
    path = d / "ledger.md"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    entries = []
    for raw in text.splitlines():
        m = LINE.match(raw.strip())
        if m and m.group(2) in STATUSES:
            n, status, on, tags, body, at = m.groups()
            entries.append({"n": int(n), "status": status, "on": int(on) if on else None,
                            "tags": set(re.findall(r"\[([a-z]+)\]", tags)), "text": body, "at": at})
    retracted = {e["on"] for e in entries if e["status"] == "RETRACT"}
    for e in entries:
        e["out"] = e["n"] in retracted
    for e in entries:
        e["closed_by"] = next((x["n"] for x in entries if x["status"] in SETTLED
                               and x["on"] == e["n"] and not x["out"]), None)
    return entries, MARK.findall(text)


def statements(entries):
    return [e for e in entries if e["status"] in ("OPEN",) + SETTLED and not e["out"]]


def by_number(entries, n):
    return next((e for e in entries if e["n"] == n), None)


def goal(entries):
    goals = [e for e in statements(entries) if "goal" in e["tags"]]
    if not goals:
        return None
    g = goals[-1]
    return by_number(entries, g["closed_by"]) if g["closed_by"] else g


def passes(entries, n):
    return [c for c in entries if c["status"] == "CHECK" and c["on"] == n and not c["out"]
            and c["text"].startswith("PASS")]


def kind(c):
    return next((k for k in KINDS if k in c["tags"]), "?")


def gaps(entries):
    live = {e["n"] for e in statements(entries)}
    return [c for c in entries if c["status"] == "CHECK" and not c["out"]
            and c["text"].startswith("GAP") and c["on"] in live]


def cites(e, n):
    return re.search(r"(?<![\w#])#%d(?!\d)" % n, e["text"]) is not None


def locator_ok(d, at):
    if re.match(r"^(ultramath|person):\S", at):
        return True
    path, _, anchor = at.partition("#")
    roots = (d.resolve(), Path.cwd().resolve())
    def inside(p):
        return any(p.resolve() == r or r in p.resolve().parents for r in roots)
    files = [p for p in (d / path, Path(path)) if path and p.exists() and inside(p)]
    if not files:
        raise Fail("locator %s does not exist inside %s or the current directory" % (at, d))
    if anchor.isdigit() and files[0].is_file():
        text = files[0].read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^\s*(?:#+\s*)?%s[.)]" % anchor, text, re.M):
            raise Fail("%s has no step %s (a line starting '%s.')" % (path, anchor, anchor))
    return True


def digest(d):
    return hashlib.sha256((d / "ledger.md").read_bytes()).hexdigest()


def write(d, line):
    if tampered(d):   # re-hashing now would hide the hand edit
        raise Fail(EDITED)
    with (d / "ledger.md").open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    (d / ".ledger.sha256").write_text(digest(d) + "\n", encoding="utf-8")


def tampered(d):
    """Whether ledger.md changed since this script last wrote it."""
    side = d / ".ledger.sha256"
    if not (d / "ledger.md").exists():
        return False
    return not side.exists() or side.read_text(encoding="utf-8").strip() != digest(d)


def add(d, args):
    if len(args) < 2:
        raise Fail("add needs STATUS and TEXT")
    status, text, rest = args[0].upper(), " ".join(args[1].split()), list(args[2:])
    if text.startswith("--"):
        raise Fail("TEXT comes right after STATUS, before the options")
    opts, tags = {}, []
    while rest:
        key = rest.pop(0)
        if key in ("--goal", "--case"):
            tags.append(key[2:])
        elif key in ("--at", "--on", "--kind") and rest:
            opts[key] = rest.pop(0)
        else:
            raise Fail("unknown or incomplete option %s" % key)
    if status not in STATUSES:
        raise Fail("STATUS must be one of " + ", ".join(STATUSES))
    if not text or " — " in text:
        raise Fail("TEXT must be non-empty and must not contain ' — ' (give the locator with --at)")
    if tags and status not in ("OPEN",) + SETTLED:
        raise Fail("--goal and --case belong on OPEN, PROVED or REFUTED")
    entries, _ = read(d)
    if status in ("OPEN",) + SETTLED:
        live = {e["n"] for e in statements(entries)}
        bad = [m for m in map(int, re.findall(r"(?<![\w#])#(\d+)", text)) if m not in live]
        if bad:
            raise Fail("TEXT cites %s, not a statement in force" % ", ".join("#%d" % m for m in bad))
    target = None
    if "--on" in opts:
        if status == "OPEN":
            raise Fail("--on does not belong on OPEN")
        if not opts["--on"].lstrip("#").isdigit():
            raise Fail("--on takes the number of an entry")
        target = int(opts["--on"].lstrip("#"))
        t = by_number(entries, target)
        if not t or t["out"]:
            raise Fail("entry %d is not in force" % target)
        if status in SETTLED and not (t["status"] == "OPEN" and not t["closed_by"]):
            raise Fail("entry %d is not an OPEN entry still to settle%s" % (target, (
                " (#%d settles it: retract #%d first)" % (t["closed_by"], t["closed_by"]))
                if t["closed_by"] else ""))
        if status in SETTLED and "goal" in t["tags"] and "case" in tags:
            raise Fail("a case does not settle the goal: record it without --on, as a case")
        if status == "CHECK" and t["status"] not in SETTLED:
            raise Fail("CHECK goes on a PROVED or REFUTED entry; entry %d is %s%s" % (
                target, t["status"], " (settled by #%d: check #%d)" % (t["closed_by"], t["closed_by"])
                if t["closed_by"] else ""))
        if status == "TRIED" and t["status"] not in ("OPEN",) + SETTLED:
            raise Fail("TRIED goes on a statement; entry %d is %s" % (target, t["status"]))
        if status == "RETRACT" and t["status"] not in ("OPEN", "CHECK") + SETTLED:
            raise Fail("RETRACT goes on a statement or a check; entry %d is %s" % (target, t["status"]))
    elif status in ("TRIED", "CHECK", "RETRACT"):
        raise Fail("%s needs --on ID, the number of the entry it is about" % status)
    if status == "CHECK":
        if opts.get("--kind") not in KINDS:
            raise Fail("CHECK needs --kind, one of " + ", ".join(KINDS))
        if not re.match(r"^(PASS|GAP)\b", text):
            raise Fail("CHECK text must start with PASS or GAP")
        tags.append(opts["--kind"])
    elif "--kind" in opts:
        raise Fail("--kind belongs on CHECK")
    at = opts.get("--at")
    if status in SETTLED + ("CHECK",) and not at:
        raise Fail("%s needs --at, where the argument or the check is" % status)
    if at:
        locator_ok(d, at)
    settled_by_target = [e["n"] for e in entries if target and e["closed_by"] == target]
    n = max([e["n"] for e in entries] + [0]) + 1
    line = "%d. %s%s%s: %s%s" % (n, status, " #%d" % target if target else "",
                                 "".join(" [%s]" % t for t in tags), text, " — " + at if at else "")
    write(d, line)
    out = "added " + line
    if status == "RETRACT":
        basis = [target] + settled_by_target   # an OPEN entry the retracted one settled is open again
        users = [e["n"] for e in statements(read(d)[0]) if any(cites(e, b) for b in basis)]
        if users:
            out += "\nstill in force and resting on %s: %s; retract or re-derive them" % (
                " or ".join("#%d" % b for b in basis), ", ".join("#%d" % u for u in users))
    return out


def show(e):
    return "#%d %s%s: %s" % (e["n"], e["status"], "".join(" [%s]" % t for t in sorted(e["tags"])), e["text"])


def with_checks(entries, e):
    kinds = sorted({kind(c) for c in passes(entries, e["n"])})
    return show(e) + ("  [checks: %s]" % ", ".join(kinds) if kinds else "")


def status(d):
    entries, _ = read(d)
    if not entries:
        return "empty ledger: add the goal first (OPEN ... --goal --at problem.md)"
    warning = ["WARNING: " + EDITED] if tampered(d) else []
    g = goal(entries)
    out = ["goal: " + (with_checks(entries, g) if g else "none in force")]
    goal_ids = {e["n"] for e in entries if "goal" in e["tags"]}
    out += ["    tried #%d: %s" % (t["n"], t["text"]) for t in entries
            if t["status"] == "TRIED" and t["on"] in goal_ids]
    for e in statements(entries):
        if e["status"] == "OPEN" and not e["closed_by"] and "goal" not in e["tags"]:
            out.append("open " + show(e))
            out += ["    tried #%d: %s" % (t["n"], t["text"]) for t in entries
                    if t["status"] == "TRIED" and t["on"] == e["n"]]
    out += [with_checks(entries, e) for e in statements(entries) if e["status"] in SETTLED and e is not g]
    out += ["GAP on #%d (#%d): retract #%d, then add the repaired claim" % (c["on"], c["n"], c["on"])
            for c in gaps(entries)]
    return "\n".join(warning + out)


def checkpoint(d):
    entries, marks = read(d)
    last = int(marks[-1][0]) if marks else 0
    top = max([e["n"] for e in entries] + [0])
    new = [e for e in statements(entries) if e["n"] > last
           and e["status"] in SETTLED and "case" not in e["tags"]]
    if new:
        write(d, "- checkpoint after #%d: progress" % top)
        return "PROGRESS: " + ", ".join("#%d" % e["n"] for e in new)
    stalled = 1
    for _, word in reversed(marks):
        if not word.startswith("stalled"):
            break
        stalled += 1
    write(d, "- checkpoint after #%d: stalled %d" % (top, stalled))
    if stalled < 2:
        return "STALLED 1: nothing new proved or refuted beyond special cases"
    return ("STALLED %d: do not open another special case. Change the mechanism or the decomposition "
            "of the missing statement and say what changed, or start Ultramath on it." % stalled)


def gate(d):
    entries, _ = read(d)
    if tampered(d):
        return "NOT YET: " + EDITED
    g = goal(entries)
    if not g:
        return "NOT YET: no goal in force"
    if g["status"] == "OPEN":
        return "NOT YET: the goal #%d is open" % g["n"]
    open_gaps = gaps(entries)
    if open_gaps:
        return "NOT YET: unresolved GAP on " + ", ".join("#%d" % c["on"] for c in open_gaps)
    seen, todo, unsettled, refuted = set(), [g], [], []
    while todo:
        cur = todo.pop()
        for m in map(int, re.findall(r"(?<![\w#])#(\d+)", cur["text"])):
            if m == cur["on"]:
                continue
            e = by_number(entries, m)
            if not e or m in seen:
                continue
            seen.add(m)
            if e["status"] == "OPEN" and not e["out"]:
                if not e["closed_by"]:
                    unsettled.append(m)
                    continue
                e = by_number(entries, e["closed_by"])   # follow the entry that settled it
                seen.add(e["n"])
                if e["status"] == "REFUTED":
                    refuted.append(m)
                    continue
            todo.append(e)
    gone = sorted(m for m in seen if by_number(entries, m)["out"])
    if gone:
        return "NOT YET: #%d rests on retracted %s" % (g["n"], ", ".join("#%d" % m for m in gone))
    if unsettled:
        return "NOT YET: #%d rests on %s, still OPEN" % (g["n"], ", ".join("#%d" % m for m in sorted(unsettled)))
    if refuted:
        return "NOT YET: #%d rests on %s, which was refuted" % (g["n"], ", ".join("#%d" % m for m in sorted(refuted)))
    done = passes(entries, g["n"])
    if not done:
        return "NOT YET: #%d has no check: check it (references/check.md)" % g["n"]
    whole = sorted({kind(c) for c in done if kind(c) in WHOLE})
    if whole:
        head = "%s #%d. The argument was checked by: %s." % (g["status"], g["n"], ", ".join(whole))
    elif any(kind(c) == "self" for c in done):
        head = "%s #%d. The argument was read only by the model that wrote it." % (g["status"], g["n"])
    else:
        head = "%s #%d. The argument was not read; only its computations were rechecked." % (g["status"], g["n"])
    return "\n".join([head] + ["  %s: %s" % (kind(c), c["text"]) for c in done])


def main(argv):
    if len(argv) > 1 and argv[1].upper() in STATUSES:
        raise Fail("%s is a status, not a command: ledger.py add DIR %s TEXT ..." % (argv[1], argv[1].upper()))
    if len(argv) < 3 or argv[1] not in ("add", "status", "checkpoint", "gate"):
        raise Fail("usage: ledger.py add|status|checkpoint|gate DIR ...")
    d = Path(argv[2])
    if not d.is_dir():
        raise Fail("%s is not a directory" % d)
    if argv[1] == "add":
        return add(d, argv[3:])
    if len(argv) > 3:
        raise Fail("%s takes only DIR" % argv[1])
    return {"status": status, "checkpoint": checkpoint, "gate": gate}[argv[1]](d)


if __name__ == "__main__":
    try:
        print(main(sys.argv))
    except Fail as err:
        print("ERROR: %s" % err)
        sys.exit(1)
