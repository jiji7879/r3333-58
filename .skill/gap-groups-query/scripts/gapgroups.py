#!/usr/bin/env python3
"""Look up and identify finite groups in GAP's group libraries: the Small Groups library (every
group of order at most 2000 except 1024, and many larger orders), the transitive groups
(degree up to 47 in a default installation, with separate downloads for 32 and 48) and the
primitive groups (degree below 4096 by default, with separate data for 4096 to 8191).
GAP runs locally through the libgap of Sage or passagemath, so python3 must be able to import
sage. Nothing is sent over the network.

    gapgroups.py count ORDER                       how many groups of order ORDER exist
    gapgroups.py small ORDER ID                    SmallGroup(ORDER, ID): structure and invariants
    gapgroups.py list ORDER [FILTER ...] [--all]   the groups of order ORDER matching every FILTER
    gapgroups.py identify GENERATOR ...            a permutation group from its generators in
                                                   cycle notation, such as "(1,2,3)(4,5)" "(1,4)"
    gapgroups.py identify --group EXPR             a named group, such as "PSL(2,7)", "SymmetricGroup(5)"
    gapgroups.py transitive DEGREE [NR] [FILTER ...] [--all]
                                                   the transitive groups of a degree, or group nTk
    gapgroups.py primitive DEGREE [NR] [FILTER ...] [--all]
                                                   the primitive groups of a degree, or one of them
    gapgroups.py version                           GAP, the libraries, their coverage and authors

Lists show the first 50 groups unless --all. A FILTER is a property, optionally =no
(abelian, abelian=no; also cyclic, nilpotent, solvable, supersolvable, simple, perfect, and
primitive for transitive groups) or a number (center=4, exponent=8, classes=10,
derived_length=2, nilpotency_class=3, and order=168 for transitive and primitive groups).
"""
import re
import sys

PACKAGES = ("smallgrp", "transgrp", "primgrp")
SHOWN = 50
MAX_SCAN = 60000          # groups examined by a filtered list or listed with --all
MAX_POINT = 100000
LMFDB_GROUP = "https://www.lmfdb.org/Groups/Abstract/%d.%d"
LMFDB_GALOIS = "https://www.lmfdb.org/GaloisGroup/%dT%d"
LMFDB_OTHER_LABELS = {512, 1024, 1152, 1536, 1920}   # LMFDB labels need not be SmallGroup ids here
MISSING = ("GAP is not available: python3 cannot import Sage's or passagemath's libgap. In Open "
           "Math OS, use the project VM's Python with Sage if available. With the user's approval, "
           "install passagemath in a virtual environment: pip install "
           "passagemath-gap passagemath-gap-pkg-smallgrp-data passagemath-gap-pkg-transgrp-data "
           "passagemath-gap-pkg-primgrp-data")
BOOL = {"abelian": "IsAbelian", "cyclic": "IsCyclic", "nilpotent": "IsNilpotentGroup",
        "solvable": "IsSolvableGroup", "supersolvable": "IsSupersolvableGroup",
        "simple": "IsSimpleGroup", "perfect": "IsPerfectGroup"}
INT = {"center": "Size(Centre(G))", "exponent": "Exponent(G)", "classes": "NrConjugacyClasses(G)",
       "derived_length": "DerivedLength(G)", "nilpotency_class": "NilpotencyClassOfGroup(G)",
       "order": "Size(G)"}
INT_GUARD = {"derived_length": "IsSolvableGroup(G)", "nilpotency_class": "IsNilpotentGroup(G)"}
ALIASES = {"centre": "center", "soluble": "solvable", "supersoluble": "supersolvable",
           "size": "order", "derivedlength": "derived_length", "class": "nilpotency_class"}
NAMED = {"SymmetricGroup": 1, "AlternatingGroup": 1, "CyclicGroup": 1, "DihedralGroup": 1,
         "QuaternionGroup": 1, "ElementaryAbelianGroup": 1, "MathieuGroup": 1,
         "SL": 2, "GL": 2, "PSL": 2, "PGL": 2, "SU": 2, "PSU": 2, "GU": 2, "Sp": 2, "PSp": 2,
         "SmallGroup": 2, "TransitiveGroup": 2, "PrimitiveGroup": 2}
YES, NO = {"yes", "y", "true", "1"}, {"no", "n", "false", "0"}
ONAN_SCOTT = {"1": "affine", "2": "almost simple", "3a": "diagonal, socle of two minimal normal subgroups",
              "3b": "diagonal, minimal normal socle", "4a": "product action, component of type 3a",
              "4b": "product action, component of type 3b", "4c": "product action, component of type 2",
              "5": "twisted wreath product"}

_gap = None


class Fail(Exception):
    pass


def libgap():
    global _gap
    if _gap is None:
        try:
            try:
                import sage.all__sagemath_gap  # noqa: F401  (passagemath)
            except ImportError:
                import sage.all  # noqa: F401  (Sage)
            from sage.libs.gap.libgap import libgap as lg
        except ImportError:
            raise Fail(MISSING)
        for pkg in PACKAGES:
            if str(lg.LoadPackage(pkg)) != "true":
                raise Fail("the GAP package %s is not installed; it provides part of the libraries" % pkg)
        _gap = lg
    return _gap


def ev(code):
    lg = libgap()
    try:
        return lg.eval(code)
    except Exception as e:   # GAP errors arrive as sage.libs.gap.util.GAPError
        lines = [l.strip() for l in str(e).splitlines() if l.strip()]
        raise Fail("GAP: " + (lines[0] if lines else type(e).__name__))


def val(code):
    return str(ev(code)).strip()


def yes(code):
    s = val(code)
    if s not in ("true", "false"):
        raise Fail("GAP returned %r where true or false was expected" % s)
    return s == "true"


def num(code):
    s = val(code)
    if not re.fullmatch(r"-?\d+", s):
        raise Fail("GAP returned %r where an integer was expected" % s)
    return int(s)


def positive(text, what):
    if not re.fullmatch(r"\d{1,30}", text or "") or int(text) < 1:
        raise Fail("%s must be a positive integer, not %r" % (what, text))
    return int(text)


def parse_filters(args, perm):
    """FILTER words -> list of (label, GAP predicate on G)."""
    out = []
    for a in args:
        key, _, value = a.partition("=")
        key = key.strip().lower().replace("-", "_")
        key = ALIASES.get(key, key)
        value = value.strip().lower()
        if key == "primitive" and perm:
            gap_bool = "IsPrimitive(G, MovedPoints(G))"
        elif key in BOOL:
            gap_bool = "%s(G)" % BOOL[key]
        elif key in INT and (key != "order" or perm):
            if not re.fullmatch(r"\d{1,30}", value):
                raise Fail("%s needs a number: %s=4" % (key, key))
            pred = "%s = %d" % (INT[key], int(value))
            if key in INT_GUARD:
                pred = "%s and %s" % (INT_GUARD[key], pred)
            out.append((a, pred))
            continue
        else:
            known = sorted(set(BOOL) | set(INT) | ({"primitive"} if perm else set()))
            if not perm:
                known.remove("order")
            raise Fail("unknown filter %r; known: %s" % (a, ", ".join(known)))
        if value in ("",) or value in YES:
            out.append((a, gap_bool))
        elif value in NO:
            out.append((a, "not " + gap_bool))
        else:
            raise Fail("%s takes no value or =yes / =no, not %r" % (key, value))
    return out


def predicate(filters):
    return "G -> " + " and ".join("(%s)" % p for _, p in filters)


def ranges(nums):
    out, start, prev = [], None, None
    for n in nums + [None]:
        if start is None:
            start = prev = n
        elif n is not None and n == prev + 1:
            prev = n
        else:
            out.append(str(start) if start == prev else "%d-%d" % (start, prev))
            start = prev = n
    return ", ".join(out)


def lmfdb_group(order, i):
    if order <= 2000 and order not in LMFDB_OTHER_LABELS:
        return "LMFDB label %d.%d: %s (if LMFDB holds this group)" % (order, i, LMFDB_GROUP % (order, i))
    return None


def describe(var, title):
    """Lines describing the group stored in the GAP variable VAR."""
    size = num("Size(%s)" % var)
    lines = ["%s; GAP StructureDescription %s" % (title, val("StructureDescription(%s)" % var))]
    abelian, nilp, solv = yes("IsAbelian(%s)" % var), yes("IsNilpotentGroup(%s)" % var), yes("IsSolvableGroup(%s)" % var)
    props = ["order %d" % size]
    props.append(("cyclic" if yes("IsCyclic(%s)" % var) else "abelian") if abelian else "nonabelian")
    props.append("nilpotent of class %d" % num("NilpotencyClassOfGroup(%s)" % var) if nilp else "not nilpotent")
    props.append("solvable of derived length %d" % num("DerivedLength(%s)" % var) if solv else "not solvable")
    if solv and not nilp:
        props.append("supersolvable" if yes("IsSupersolvableGroup(%s)" % var) else "not supersolvable")
    if not solv:
        props.append("simple" if yes("IsSimpleGroup(%s)" % var) else "not simple")
        props.append("perfect" if yes("IsPerfectGroup(%s)" % var) else "not perfect")
    lines.append("; ".join(props))
    inv = re.findall(r"\d+", val("AbelianInvariants(%s)" % var))
    lines.append("centre of order %d; derived subgroup of order %d; abelianization %s; exponent %d; %d conjugacy classes"
                 % (num("Size(Centre(%s))" % var), num("Size(DerivedSubgroup(%s))" % var),
                    "invariants [%s]" % ", ".join(inv) if inv else "trivial", num("Exponent(%s)" % var),
                    num("NrConjugacyClasses(%s)" % var)))
    return size, lines


def small_id(var, size):
    if yes("IdGroupsAvailable(%d)" % size):
        ident = val("IdGroup(%s)" % var)
        m = re.fullmatch(r"\[\s*(\d+),\s*(\d+)\s*\]", ident)
        if not m:
            raise Fail("unexpected IdGroup result %r" % ident)
        i = int(m.group(2))
        out = ["SmallGroup id [ %d, %d ]" % (size, i)]
        link = lmfdb_group(size, i)
        return out + ([link] if link else [])
    if yes("SmallGroupsAvailable(%d)" % size):
        return ["the library has the groups of order %d but cannot identify them (no IdGroup for this order)" % size]
    return ["order %d is outside the Small Groups library" % size]


def perm_lines(var, transitive_known=None):
    """Transitive and primitive identification of a permutation group in VAR."""
    pts = num("NrMovedPoints(%s)" % var)
    if pts == 0:
        return []
    if not yes("IsTransitive(%s, MovedPoints(%s))" % (var, var)):
        return ["intransitive on its %d moved points; orbit lengths %s"
                % (pts, val("List(Orbits(%s, MovedPoints(%s)), Length)" % (var, var)))]
    out = []
    if transitive_known:
        k = transitive_known
    elif pts > 1 and yes("TransitiveGroupsAvailable(%d)" % pts):
        k = num("TransitiveIdentification(%s)" % var)
    else:
        k = None
        out.append("transitive on %d points; the transitive groups of degree %d are not available here "
                   "(gapgroups.py version lists the degrees)" % (pts, pts))
    if k:
        out.append("transitive group %dT%d = TransitiveGroup(%d, %d), GAP name %s; LMFDB %s"
                   % (pts, k, pts, k, val("Name(TransitiveGroup(%d, %d))" % (pts, k)), LMFDB_GALOIS % (pts, k)))
    if yes("IsPrimitive(%s, MovedPoints(%s))" % (var, var)):
        if yes("PrimitiveGroupsAvailable(%d)" % pts):
            p = num("PrimitiveIdentification(%s)" % var)
            t = val("ONanScottType(PrimitiveGroup(%d, %d))" % (pts, p))
            out.append("primitive: PrimitiveGroup(%d, %d), GAP name %s, O'Nan-Scott type %s (%s)"
                       % (pts, p, val("Name(PrimitiveGroup(%d, %d))" % (pts, p)), t, ONAN_SCOTT.get(t, "see the GAP manual")))
        else:
            out.append("primitive; the primitive groups of degree %d are not in the library" % pts)
    else:
        out.append("imprimitive")
    return out


def show_list(rows, total, what, note=""):
    """ROWS are the lines shown, TOTAL the number of matches."""
    print("%d %s%s" % (total, what, note if total else ""))
    for r in rows:
        print(r)
    if total > MAX_SCAN:
        print("... %d more; this library entry exceeds the --all limit of %d" % (total - len(rows), MAX_SCAN))
    elif total > len(rows):
        print("... %d more; add --all to see them" % (total - len(rows)))


def cmd_count(args):
    if len(args) != 1:
        raise Fail("count takes one ORDER")
    n = positive(args[0], "ORDER")
    try:
        total = num("NumberSmallGroups(%d)" % n)
    except Fail as e:
        if "not available" not in str(e):
            raise
        raise Fail("the Small Groups library does not cover order %d" % n)
    notes = []
    if not yes("SmallGroupsAvailable(%d)" % n):
        notes.append("the library knows the number but does not contain the groups")
    elif yes("IdGroupsAvailable(%d)" % n):
        notes.append("SmallGroup(%d, 1) to SmallGroup(%d, %d); IdGroup identifies them" % (n, n, total))
    else:
        notes.append("SmallGroup(%d, 1) to SmallGroup(%d, %d); IdGroup is not available for this order" % (n, n, total))
    print("order %d: %d groups up to isomorphism; %s" % (n, total, "; ".join(notes)))


def cmd_small(args):
    if len(args) != 2:
        raise Fail("small takes ORDER and ID, for example small 24 12")
    n, i = positive(args[0], "ORDER"), positive(args[1], "ID")
    if not yes("SmallGroupsAvailable(%d)" % n):
        raise Fail("the Small Groups library does not contain the groups of order %d" % n)
    total = num("NumberSmallGroups(%d)" % n)
    if i > total:
        raise Fail("there are %d groups of order %d; ID must be at most %d" % (total, n, total))
    ev("_gg := SmallGroup(%d, %d)" % (n, i))
    _, lines = describe("_gg", "SmallGroup(%d, %d)" % (n, i))
    link = lmfdb_group(n, i)
    for line in lines + ([link] if link else []):
        print(line)


def cmd_list(args, show_all):
    if not args:
        raise Fail("list takes ORDER and optional FILTERs")
    n = positive(args[0], "ORDER")
    filters = parse_filters(args[1:], perm=False)
    if not yes("SmallGroupsAvailable(%d)" % n):
        raise Fail("the Small Groups library does not contain the groups of order %d" % n)
    total = num("NumberSmallGroups(%d)" % n)
    if total > MAX_SCAN and (filters or show_all):
        raise Fail("order %d has %d groups, too many to examine or list in full (limit %d)" % (n, total, MAX_SCAN))
    if filters:
        if total > 5000:
            print("examining %d groups; this can take a minute or more" % total, file=sys.stderr)
        ids = [int(x) for x in re.findall(r"\d+", val("List(IdsOfAllSmallGroups(%d, %s, true), x -> x[2])"
                                                        % (n, predicate(filters))))]
    else:
        ids = range(1, total + 1)
    shown = ids if show_all else ids[:SHOWN]
    rows = ["%d.%d  %s" % (n, i, val("StructureDescription(SmallGroup(%d, %d))" % (n, i))) for i in shown]
    what = "of the %d groups of order %d match %s" % (total, n, " ".join(f for f, _ in filters)) if filters \
        else "groups of order %d" % n
    show_list(rows, len(ids), what, "; listed as ORDER.ID with GAP's StructureDescription")


def parse_generators(args):
    if any(re.search(r"\d\s+\d", arg) for arg in args):
        raise Fail("separate points within a cycle with commas")
    gens = [re.sub(r"\s+", "", arg) for arg in args]
    if len(gens) == 1:
        text = gens[0]
        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1]
        gens = re.split(r"(?<=\)),(?=\()", text)
    if not gens or not all(gens):
        raise Fail("give at least one generator in cycle notation, such as \"(1,2,3)(4,5)\"")
    normalized = []
    for g in gens:
        if not re.fullmatch(r"\(\)|(\(\d{1,6}(,\d{1,6})+\))+", g):
            raise Fail("not a permutation in cycle notation: %r (write \"(1,2,3)(4,5)\")" % g)
        seen = set()
        cycles = []
        for cycle in re.findall(r"\(([\d,]+)\)", g):
            pts = [int(p) for p in cycle.split(",")]
            if min(pts) < 1 or max(pts) > MAX_POINT:
                raise Fail("points must be between 1 and %d" % MAX_POINT)
            if seen & set(pts) or len(set(pts)) != len(pts):
                raise Fail("the cycles of %s are not disjoint: write each generator as a product of "
                           "disjoint cycles, and separate generators by spaces" % g)
            seen |= set(pts)
            cycles.append("(%s)" % ",".join(map(str, pts)))
        normalized.append("".join(cycles) or "()")
    return "Group([%s])" % ", ".join(normalized)


def parse_named(expr):
    m = re.fullmatch(r"\s*([A-Za-z]+)\s*\(\s*(\d{1,12}(?:\s*,\s*\d{1,12})*)\s*\)\s*", expr or "")
    if not m or m.group(1) not in NAMED:
        raise Fail("--group takes one of %s with integer arguments, such as PSL(2,7) or SymmetricGroup(5)"
                   % ", ".join(sorted(NAMED)))
    name, nums = m.group(1), [int(x) for x in m.group(2).split(",")]
    if len(nums) != NAMED[name]:
        raise Fail("%s takes %d integer argument%s" % (name, NAMED[name], "s" if NAMED[name] > 1 else ""))
    return "%s(%s)" % (name, ", ".join(map(str, nums)))


def cmd_identify(args):
    if args[:1] == ["--group"]:
        if len(args) != 2:
            raise Fail("--group takes one expression, such as \"PSL(2,7)\"")
        expr, title = parse_named(args[1]), args[1].strip()
    else:
        expr = parse_generators(args)
        title = "the group generated by %s" % " ".join(args)
    ev("_gg := %s" % expr)
    size, lines = describe("_gg", title)
    lines += small_id("_gg", size)
    if yes("IsPermGroup(_gg)"):
        lines += perm_lines("_gg")
    for line in lines:
        print(line)


def cmd_perm_library(kind, args, show_all):
    if not args:
        raise Fail("%s takes DEGREE, then NR or FILTERs" % kind)
    d = positive(args[0], "DEGREE")
    lib = "TransitiveGroup" if kind == "transitive" else "PrimitiveGroup"
    avail = "%sGroupsAvailable(%d)" % ("Transitive" if kind == "transitive" else "Primitive", d)
    if d < 2 or not yes(avail):
        raise Fail("the %s groups of degree %d are not available in this installation (see version)" % (kind, d))
    total = num("Nr%sGroups(%d)" % (lib[:-5], d))
    if len(args) == 2 and re.fullmatch(r"\d+", args[1]):
        k = positive(args[1], "NR")
        if k > total:
            raise Fail("there are %d %s groups of degree %d" % (total, kind, d))
        ev("_gg := %s(%d, %d)" % (lib, d, k))
        title = "%s(%d, %d)%s, GAP name %s" % (lib, d, k, " = %dT%d" % (d, k) if kind == "transitive" else "",
                                                val("Name(_gg)"))
        size, lines = describe("_gg", title)
        lines += small_id("_gg", size)
        lines += perm_lines("_gg", transitive_known=k if kind == "transitive" else None)
        lines.append("generators %s" % val("GeneratorsOfGroup(_gg)"))
        for line in lines:
            print(line)
        return
    filters = parse_filters(args[1:], perm=True)
    if total > MAX_SCAN and (filters or show_all):
        raise Fail("degree %d has %d %s groups, too many to examine or list in full (limit %d)"
                   % (d, total, kind, MAX_SCAN))
    if filters:
        if total > 5000:
            print("examining %d groups; this can take a minute or more" % total, file=sys.stderr)
        ks = [int(x) for x in re.findall(r"\d+", val("Filtered([1..%d], k -> (%s)(%s(%d, k)))"
                                                       % (total, predicate(filters), lib, d)))]
    else:
        ks = range(1, total + 1)
    shown = ks if show_all else ks[:SHOWN]
    label = (lambda k: "%dT%d" % (d, k)) if kind == "transitive" else (lambda k: "%s(%d, %d)" % (lib, d, k))
    rows = ["%s  %s  order %s" % (label(k), val("Name(%s(%d, %d))" % (lib, d, k)), val("Size(%s(%d, %d))" % (lib, d, k)))
            for k in shown]
    what = "of the %d %s groups of degree %d match %s" % (total, kind, d, " ".join(f for f, _ in filters)) if filters \
        else "%s groups of degree %d" % (kind, d)
    show_list(rows, len(ks), what)


def cmd_version():
    print("GAP %s" % val("GAPInfo.Version"))
    for pkg in PACKAGES:
        info = "PackageInfo(\"%s\")[1]" % pkg
        authors = val("JoinStringsWithSeparator(List(Filtered(%s.Persons, p -> p.IsAuthor), "
                      "p -> Concatenation(p.FirstNames, \" \", p.LastName)), \", \")" % info)
        print("%s %s (%s): %s" % (pkg, val("GAPInfo.PackagesLoaded.%s[2]" % pkg), val("%s.Subtitle" % info), authors))
    small_missing = [n for n in range(1, 2001) if not yes("SmallGroupsAvailable(%d)" % n)]
    id_missing = [n for n in range(1, 2001) if not yes("IdGroupsAvailable(%d)" % n)]
    trans = [d for d in range(2, 61) if yes("TransitiveGroupsAvailable(%d)" % d)]
    prim = num("First([4095, 4094 .. 2], d -> PrimitiveGroupsAvailable(d))")
    print("small groups: every order up to 2000%s; IdGroup up to 2000%s"
          % (" except " + ranges(small_missing) if small_missing else "",
             " except " + ranges(id_missing) if id_missing else ""))
    print("transitive groups: degrees %s" % (ranges(trans) or "none"))
    print("primitive groups: degrees up to %d in the standard data; check higher degrees directly if using extra data" % prim)


def main(argv):
    show_all = "--all" in argv
    argv = [a for a in argv if a != "--all"]
    cmds = {"count": cmd_count, "small": cmd_small, "identify": cmd_identify}
    if not argv or argv[0] not in ("count", "small", "list", "identify", "transitive", "primitive", "version"):
        print(__doc__)
        return 0 if argv[:1] in (["-h"], ["--help"], ["help"]) else 2
    cmd, rest = argv[0], argv[1:]
    libgap()                 # report a missing GAP as such, before any command interprets errors
    if cmd in cmds:
        if cmd == "identify" and not rest:
            raise Fail("identify takes generators in cycle notation or --group EXPR")
        cmds[cmd](rest)
    elif cmd == "list":
        cmd_list(rest, show_all)
    elif cmd in ("transitive", "primitive"):
        cmd_perm_library(cmd, rest, show_all)
    else:
        cmd_version()
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Fail as e:
        print("gapgroups.py: %s" % e, file=sys.stderr)
        sys.exit(1)
