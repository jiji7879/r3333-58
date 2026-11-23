"""Offline tests for zbmath.py with synthetic answers in the API's shapes (no network).
Run: python -m unittest discover -s skills/zbmath-query/scripts -p 'test_*.py'"""

import contextlib
import email.message
import http.client
import importlib.util
import io
import json
import os
import tempfile
import unittest
import urllib.error
from pathlib import Path

spec = importlib.util.spec_from_file_location("zbmath", Path(__file__).resolve().with_name("zbmath.py"))
zbmath = importlib.util.module_from_spec(spec)
spec.loader.exec_module(zbmath)

OK = {"execution": "successful request", "execution_bool": True, "internal_code": "ok", "status_code": 200}
NO_RESULTS = {"execution": "Entry not found!...", "execution_bool": False,
              "internal_code": "successful access. No results found.", "status_code": 404}
NO_ID = {"execution": "Entry not found!...", "execution_bool": False,
         "internal_code": "Entry not found! internal code: id does not exist!", "status_code": 200}


def doc(i, year="2001", authors=(("Doe, Jane", "doe.jane"),), editors=(), others=(), review=None, summary=None,
        msc=("11G05", "14H52"), ident=None, db="Zbl", license=(), refs=()):
    contributions = []
    if review is not None:
        contributions.append({"contribution_type": "review", "language": "English", "text": review,
                              "reviewer": {"name": "Rev Iewer", "sign": "R. Iewer (Nowhere)", "author_code": "iewer.rev"}})
    if summary is not None:
        contributions.append({"contribution_type": "summary", "language": "English", "text": summary,
                              "reviewer": {"name": None, "sign": None}})
    person = lambda n, c: {"name": n, "codes": [c], "aliases": [], "checked": "1"}
    return {"id": i, "identifier": ident if ident is not None else "%04d.%05d" % (1000 + i % 1000, i), "database": db,
            "year": year, "title": {"title": "Synthetic paper %d" % i, "subtitle": None, "addition": None, "original": None},
            "contributors": {"authors": [person(*a) for a in authors], "editors": [person(*e) for e in editors],
                             "author_references": [person(*o) for o in others]},
            "source": {"source": "J. Synth. %d, 1-10 (%s)." % (i, year)},
            "document_type": {"code": "j", "description": "journal article"},
            "language": {"languages": ["English"], "addition": [None]},
            "msc": [{"code": c, "scheme": "msc2020", "text": "Text of %s" % c} for c in msc],
            "keywords": ["synthetic", "test"], "links": [{"type": "doi", "identifier": "10.9999/syn.%d" % i,
                                                          "url": "https://doi.org/10.9999/syn.%d" % i}],
            "license": list(license), "references": list(refs), "editorial_contributions": contributions,
            "zbmath_url": "https://zbmath.org/%d" % i}


def page(rows, total):
    return rows, dict(OK, nr_total_results=total, nr_request_results=len(rows))


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        zbmath.main(list(argv))
    return out.getvalue()


class Fake:
    """Stands in for zbmath.call: answers by path, records every request."""

    def __init__(self, handler):
        self.handler, self.calls = handler, []

    def __call__(self, path, params=None):
        self.calls.append((path, dict(params or {})))
        return self.handler(path, params or {})


class Patched(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.saved = zbmath.call, zbmath.CACHE, zbmath.GAP
        zbmath.CACHE, zbmath.GAP = Path(self.tmp.name), 0

    def tearDown(self):
        zbmath.call, zbmath.CACHE, zbmath.GAP = self.saved
        self.tmp.cleanup()

    def fake(self, handler):
        zbmath.call = Fake(handler)
        return zbmath.call

    def msc_cache(self):
        names = {"%02d" % i: "Class %02d" % i for i in range(63)}
        names["11"] = "Number theory"
        (zbmath.CACHE / "msc-top.json").write_text(json.dumps(names))


class Queries(unittest.TestCase):
    def test_accepted(self):
        for q in ("au:Wiles ti:Fermat", 'ti:"Fermat\'s last: theorem"', "doi:10.1002/x:y", "arxiv:2208.09963",
                  "cc:(94A | 11T) py:2000-2015", "cc:*35 !any:elliptic", "en:arXiv:2208.09963", "py:1995 geometr*",
                  "py:(1995 | 1996) au:Wiles"):
            self.assertEqual(zbmath.check_query(q, zbmath.DOC_FIELDS, "search"), q)
        self.assertEqual(zbmath.check_query("ln:Wiles fn:Andrew", zbmath.AUTHOR_FIELDS, "authors"), "ln:Wiles fn:Andrew")

    def test_refused_before_any_request(self):
        for q in ("xx:foo", "ti:(Fermat", "ti:Fermat)", 'ti:"open phrase', "py:19x5", "py:2000-15", "   ",
                  "ln:Wiles", "ti:", "ti: au:Wiles", 'ti:" " au:Wiles', "py:2024-2020"):
            with self.assertRaises(zbmath.Fail):
                zbmath.check_query(q, zbmath.DOC_FIELDS, "search")


class Ids(unittest.TestCase):
    def test_document_ids(self):
        cases = {"0823.11029": ("id", "0823.11029"), "Zbl 0823.11029": ("id", "0823.11029"),
                 "zbl:0823.11029": ("id", "0823.11029"), "JFM 30.0424.01": ("id", "30.0424.01"),
                 "783777": ("id", "783777"), "DE 783777": ("id", "783777"),
                 "https://zbmath.org/?q=an:0823.11029": ("id", "0823.11029"),
                 "https://zbmath.org/?q=an%3A0823.11029": ("id", "0823.11029"),
                 "https://zbmath.org/783777": ("id", "783777"),
                 "arXiv:2412.08738": ("arxiv", "2412.08738"), "arxiv:2412.08738v2": ("arxiv", "2412.08738"),
                 "https://arxiv.org/abs/math/0211159": ("arxiv", "math/0211159"),
                 "10.2307/2118559": ("doi", "10.2307/2118559"), "doi:10.2307/2118559": ("doi", "10.2307/2118559"),
                 "https://doi.org/10.2307/2118559": ("doi", "10.2307/2118559")}
        for text, want in cases.items():
            self.assertEqual(zbmath.doc_ref(text), want, text)
        self.assertEqual(zbmath.doc_ref("2412.08738"), ("id", "2412.08738"))   # Zbl-shaped: arXiv ids need arXiv:
        for bad in ("hello", "0823.1102", "https://zbmath.org/?q=ai:wiles.andrew-j", ""):
            with self.assertRaises(zbmath.Fail):
                zbmath.doc_ref(bad)

    def test_author_codes(self):
        self.assertEqual(zbmath.author_code("Wiles.Andrew-J"), "wiles.andrew-j")
        self.assertEqual(zbmath.author_code("https://zbmath.org/authors/wiles.andrew-j"), "wiles.andrew-j")
        self.assertEqual(zbmath.author_code("https://zbmath.org/authors/?q=ai:wang.wei.103"), "wang.wei.103")
        self.assertEqual(zbmath.author_code("ai:heath-brown.roger"), "heath-brown.roger")
        for bad in ("Andrew Wiles", "", "wiles/andrew"):
            with self.assertRaises(zbmath.Fail):
                zbmath.author_code(bad)

    def test_msc_codes(self):
        cases = {"11": "11-XX", "11-XX": "11-XX", "11-xx": "11-XX", "11g": "11Gxx", "11Gxx": "11Gxx",
                 "11g05": "11G05", "11-02": "11-02", "1G05": None, "elliptic": None, "11G5": None}
        for text, want in cases.items():
            self.assertEqual(zbmath.msc_code(text), want, text)


class Answers(unittest.TestCase):
    """call() reads the API's status block: no match is HTTP 404 for a search, HTTP 200 for an id."""

    def setUp(self):
        self.saved = zbmath.fetch

    def tearDown(self):
        zbmath.fetch = self.saved

    def answer(self, code, body):
        zbmath.fetch = lambda path, params=None: (code, body if isinstance(body, str) else json.dumps(body))
        return zbmath.call("/document/_search", {"search_string": "x"})

    def test_no_match_and_unknown_id(self):
        self.assertEqual(self.answer(404, {"result": None, "status": NO_RESULTS})[0], None)
        self.assertEqual(self.answer(200, {"result": None, "status": NO_ID})[0], None)
        rows, st = self.answer(200, {"result": [{"id": 1}], "status": dict(OK, nr_total_results=7)})
        self.assertEqual((rows, st["nr_total_results"]), ([{"id": 1}], 7))

    def test_errors(self):
        window = {"result": None, "status": {"execution": "Bad Request...", "execution_bool": False,
                                             "internal_code": "Result window is too large, please choose ..."}}
        for code, body, words in ((400, window, "Result window is too large"),
                                  (422, {"detail": [{"loc": ["query", "page"], "msg": "value is not a valid integer"}]},
                                   "page: value is not a valid integer"),
                                  (200, "<html>maintenance</html>", "did not answer with JSON"),
                                  (200, {"result": []}, "unexpected answer"),
                                  (200, {"status": OK}, "without a result"),
                                  (200, {"result": None, "status": {"execution_bool": False, "internal_code": "boom"}},
                                   "could not answer")):
            with self.assertRaises(zbmath.Fail) as cm:
                self.answer(code, body)
            self.assertIn(words, str(cm.exception))

    def test_search_checks_the_shape(self):
        zbmath.fetch = lambda path, params=None: (200, json.dumps({"result": {"id": 1}, "status": OK}))
        with self.assertRaises(zbmath.Fail):
            zbmath.search("document", "x", 10, 1)


class Transport(unittest.TestCase):
    """fetch(): bounded retries, Retry-After, JSON bodies of 4xx answers passed on."""

    def setUp(self):
        self.saved = zbmath.urllib.request.urlopen, zbmath.time.sleep, zbmath.GAP
        self.slept = []
        zbmath.time.sleep = self.slept.append
        zbmath.GAP = 0

    def tearDown(self):
        zbmath.urllib.request.urlopen, zbmath.time.sleep, zbmath.GAP = self.saved

    def script(self, *answers):
        answers = list(answers)
        self.requests = []

        def urlopen(req, timeout=None):
            self.requests.append(req)
            a = answers.pop(0)
            if isinstance(a, Exception):
                raise a
            return a
        zbmath.urllib.request.urlopen = urlopen

    @staticmethod
    def http_error(code, body=b"", retry_after=None):
        headers = email.message.Message()
        if retry_after is not None:
            headers["Retry-After"] = retry_after
        return urllib.error.HTTPError("https://api.zbmath.org/v1/x", code, "status", headers, io.BytesIO(body))

    class Response(io.BytesIO):
        status = 200

    def test_retries_a_busy_server_then_succeeds(self):
        self.script(self.http_error(503, retry_after="7"), self.Response(b'{"ok": 1}'))
        self.assertEqual(zbmath.fetch("/x"), (200, '{"ok": 1}'))
        self.assertIn(7, self.slept)
        self.assertEqual(self.requests[0].get_header("User-agent"), zbmath.AGENT)

    def test_long_retry_after_stops_before_sending_again(self):
        self.script(self.http_error(429, retry_after="3600"))
        with self.assertRaises(zbmath.Fail) as cm:
            zbmath.fetch("/x")
        self.assertIn("HTTP 429", str(cm.exception))
        self.assertIn("retry after at least 3600 seconds", str(cm.exception))
        self.assertEqual(len(self.requests), 1)
        self.assertEqual(self.slept, [])

    def test_json_bodies_of_client_errors_are_returned(self):
        self.script(self.http_error(404, b'{"status": {}}'))
        self.assertEqual(zbmath.fetch("/x"), (404, '{"status": {}}'))
        self.script(self.http_error(403, b"forbidden"))
        with self.assertRaises(zbmath.Fail):
            zbmath.fetch("/x")
        self.assertEqual(len(self.requests), 1)   # not retried

    def test_network_failure(self):
        self.script(*[urllib.error.URLError("no route")] * 3)
        with self.assertRaises(zbmath.Fail) as cm:
            zbmath.fetch("/x")
        self.assertIn("cannot reach api.zbmath.org", str(cm.exception))

    def test_interrupted_error_response_is_retried(self):
        class Partial(io.BytesIO):
            def read(self, *args):
                raise http.client.IncompleteRead(b'{"st')

        error = urllib.error.HTTPError("https://api.zbmath.org/v1/x", 404, "", {}, Partial())
        self.script(error, self.http_error(404, b'{"status": {}}'))
        self.assertEqual(zbmath.fetch("/x"), (404, '{"status": {}}'))
        self.assertEqual(len(self.requests), 2)


class Search(Patched):
    def test_page_total_and_next(self):
        rows = [doc(1, review="A review."), doc(2, summary=zbmath.UNAVAILABLE), doc(3)]
        fake = self.fake(lambda path, p: page(rows, 41))
        out = run("search", "au:Doe", "--limit", "3", "--page", "2")
        self.assertEqual(fake.calls, [("/document/_search", {"search_string": "au:Doe", "page": 1, "results_per_page": 3})])
        self.assertIn("41 documents match au:Doe", out)
        self.assertIn("4. Zbl 1001.00001", out)
        self.assertIn("review by R. Iewer (Nowhere)", out)
        self.assertIn("summary not in the API (licence)", out)
        self.assertIn("no review or summary", out)
        self.assertIn("(results 4-6 of 41; next: --page 3)", out)

    def test_no_match_past_the_end_and_too_many(self):
        self.fake(lambda path, p: (None, NO_RESULTS))
        self.assertIn("No documents match zzqx", run("search", "zzqx"))
        self.assertIn("No results on page 5", run("search", "au:Doe", "--page", "5"))
        self.fake(lambda path, p: page([doc(1)], 413990))
        out = run("search", "geometry", "--limit", "1")
        self.assertIn("413,990 documents match", out)
        self.assertIn("Many results: narrow", out)

    def test_result_window(self):
        fake = self.fake(lambda path, p: page([doc(1)] * 10, 413990))
        self.assertIn("only the first 10,000", run("search", "geometry", "--page", "1000"))
        with self.assertRaises(zbmath.Fail):
            run("search", "geometry", "--page", "1001")
        self.assertEqual(len(fake.calls), 1)

    def test_bad_options(self):
        self.fake(lambda path, p: self.fail("no request expected"))
        for argv in (["--limit", "0"], ["--limit", "101"], ["--page", "0"], ["--limit", "x"], ["--limit"], ["--sort", "year"]):
            with self.assertRaises(zbmath.Fail):
                run("search", "au:Doe", *argv)


class Show(Patched):
    def test_document_with_long_review_and_licence(self):
        long_review = "word " * 999 + "last"
        r = doc(7, review=long_review, license=["https://creativecommons.org/licenses/by/4.0/"],
                editors=(("Ed, Itor", "ed.itor"),), others=(("Fore, Word", "fore.word"),))
        fake = self.fake(lambda path, p: (r, OK))
        out = run("show", "Zbl", "1007.00007")
        self.assertEqual(fake.calls[0][0], "/document/1007.00007")
        self.assertIn("Zbl 1007.00007  https://zbmath.org/7", out)
        self.assertIn("Doe, Jane [doe.jane]", out)
        self.assertIn("editors:    Ed, Itor [ed.itor]", out)
        self.assertIn("Fore, Word [fore.word] (other contributions", out)
        self.assertIn("11G05 (primary) Text of 11G05", out)
        self.assertIn("licence:    https://creativecommons.org/licenses/by/4.0/ (named in this record)", out)
        self.assertIn("[review by Rev Iewer (signed R. Iewer (Nowhere)), English]", out)
        self.assertIn("(4999 characters in all; --full prints everything)", out)
        self.assertNotIn("last", out)
        self.assertIn("word last", run("show", "1007.00007", "--full"))

    def test_withheld_text_and_reference_count(self):
        refs = [{"text": zbmath.UNAVAILABLE, "position": zbmath.UNAVAILABLE,
                 "zbmath": {"document_id": 5016583, "year": "2005"}},
                {"text": "A. Author, Some paper (1999).", "position": "2", "zbmath": {"document_id": None}}]
        r = doc(8, summary=zbmath.UNAVAILABLE, refs=refs)
        self.fake(lambda path, p: (r, OK))
        out = run("show", "1008.00008")
        self.assertIn("Not available through the API", out)
        self.assertNotIn(zbmath.UNAVAILABLE, out)
        self.assertIn("references: 2, 1 of them matched to zbMATH documents\n", out)

    def test_unknown_id_and_doi_lookups(self):
        self.fake(lambda path, p: (None, NO_ID))
        with self.assertRaises(zbmath.Fail) as cm:
            run("show", "999999999")
        self.assertIn("no document 999999999", str(cm.exception))
        self.fake(lambda path, p: (None, NO_RESULTS))
        with self.assertRaises(zbmath.Fail) as cm:
            run("show", "10.1002/(SICI)1097-0118(199709)26:1<9::AID-JGT2>3.0.CO;2-N")
        self.assertIn("verify the DOI on the result", str(cm.exception))
        fake = self.fake(lambda path, p: page([doc(1, db="arXiv", ident="arXiv:2412.08738"), doc(2)], 2))
        out = run("show", "arXiv:2412.08738")
        self.assertEqual(fake.calls[0][1]["search_string"], "arxiv:2412.08738")
        self.assertIn("2 documents carry arXiv id 2412.08738", out)
        self.assertIn("1. arXiv:2412.08738", out)

    def test_doi_lookup_uses_the_external_id_field(self):
        doi = "10.1002/(SICI)1097-0118(199709)26:1<9::AID-JGT2>3.0.CO;2-N"
        record = doc(1, ident="0878.05065")
        record["links"][0]["identifier"] = doi
        fake = self.fake(lambda path, p: page([record], 1))
        self.assertIn("Zbl 0878.05065", run("show", doi))
        self.assertEqual(fake.calls[0][1]["search_string"], 'en:"%s"' % doi)


class Author(Patched):
    PROFILE = {"code": "doe.jane", "name": "Doe, Jane Q.", "aliases": ["doe.j-q"],
               "spellings": [{"name": "Doe, J.", "count": 3}, {"name": "Doe, Jane", "count": 2}],
               "main_fields": [{"field": "11", "count": 4, "percent": "80"}, {"field": "99", "count": 1}],
               "awards": [{"title": "Some Prize", "year": 2020}],
               "external_ids": [{"type": "orcid", "external_id": "0000-0000-0000-0000"}],
               "zbmath_url": "https://zbmath.org/authors/doe.jane"}

    def handler(self, total, docs):
        def answer(path, p):
            if path.startswith("/author/"):
                return dict(self.PROFILE), OK
            if path == "/document/_search":
                start = p["page"] * p["results_per_page"]
                return page(docs[start:start + p["results_per_page"]], total)
            self.fail("unexpected request %s" % path)
        return answer

    def test_roles_years_and_recent_documents(self):
        self.msc_cache()
        docs = [doc(1, year="1990"), doc(2, year="2015", authors=(("Doe, J.", "doe.j-q"),)),
                doc(3, year="2010", authors=(("X, Y", "x.y"),), editors=(("Doe, J.", "doe.jane"),)),
                doc(4, year="2020", authors=(("X, Y", "x.y"),), others=(("Doe, J.", "doe.jane"),))]
        fake = self.fake(self.handler(4, docs))
        out = run("author", "Doe.J-Q")
        self.assertIn("(doe.j-q is another code of the profile doe.jane)", out)
        self.assertEqual(fake.calls[1][1]["search_string"], "ai:doe.jane")
        self.assertIn("4 linked to doe.jane: 2 as author (1990-2015), 1 as editor, 1 other contributions", out)
        self.assertIn("11 Number theory (4); 99 (1)", out)
        self.assertIn("most recent documents (4 of 4):", out)
        self.assertLess(out.index("2020  Zbl 1004.00004"), out.index("2015  Zbl 1002.00002"))
        self.assertLess(out.index("2015  Zbl 1002.00002"), out.index("1990  Zbl 1001.00001"))

    def test_many_documents_are_not_paged_through(self):
        self.msc_cache()
        docs = [doc(i) for i in range(100)]
        fake = self.fake(self.handler(1574, docs))
        out = run("author", "doe.jane")
        self.assertIn("1,574 linked to doe.jane (roles and recent documents need a complete set of at most 500", out)
        self.assertEqual(len([c for c in fake.calls if c[0] == "/document/_search"]), 1)

    def test_unknown_author(self):
        self.fake(lambda path, p: (None, NO_ID))
        with self.assertRaises(zbmath.Fail) as cm:
            run("author", "nobody.here")
        self.assertIn("zbmath.py authors NAME", str(cm.exception))


class Classification(Patched):
    def test_a_different_code_in_the_answer_is_refused(self):
        # zbMATH answers /classification/11 with an unrelated five-character code
        self.fake(lambda path, p: ({"code": "11R18", "level": 2, "short_title": "Cyclotomic extensions"}, OK))
        with self.assertRaises(zbmath.Fail) as cm:
            run("msc", "11")
        self.assertIn("no MSC 2020 code", str(cm.exception))

    def test_class_with_counts_and_subclasses(self):
        kids = [{"code": "11G05", "parent": "11Gxx", "short_title": "Elliptic"},
                {"code": "11Gxx", "parent": "11-XX", "short_title": "The class itself"},
                {"code": "11G99", "parent": "11Gxx", "short_title": "None of the above"}]

        def answer(path, p):
            if path == "/classification/11Gxx":
                return {"code": "11Gxx", "level": 1, "parent": "11-XX", "long_title": "Arithmetic geometry"}, OK
            if path == "/document/_search":
                return page([doc(1)], 17573 if p["search_string"] == "cc:11G" else 8431)
            if path == "/classification/_search":
                self.assertEqual(p["search_string"], "cc:11G*")
                return page(kids, 3)
            self.fail(path)
        self.fake(answer)
        out = run("msc", "11g")
        self.assertIn("second level; parent 11-XX", out)
        self.assertIn("17,573 with a code in 11Gxx, 8,431 with it as primary code", out)
        self.assertIn("2 subclasses:", out)
        self.assertLess(out.index("11G05"), out.index("11G99"))

    def test_words(self):
        fake = self.fake(lambda path, p: page([{"code": "14H52", "long_title": "Elliptic curves"}], 3))
        out = run("msc", "elliptic", "curves", "--limit", "1")
        self.assertEqual(fake.calls[0], ("/classification/_search",
                                         {"search_string": "elliptic curves", "page": 0, "results_per_page": 1}))
        self.assertIn("(1 of 3 MSC 2020 codes; --limit 100 for more)", out)


class Cache(Patched):
    def lv0(self, n=63):
        return page([{"code": "%02d-XX" % i, "short_title": "Fresh %02d" % i} for i in range(n)], n)

    def test_fresh_cache_needs_no_request(self):
        self.msc_cache()
        self.fake(lambda path, p: self.fail("no request expected"))
        self.assertEqual(zbmath.msc_top_names()["11"], "Number theory")

    def test_stale_cache_is_refreshed_and_kept_on_failure(self):
        self.msc_cache()
        path = zbmath.CACHE / "msc-top.json"
        os.utime(path, (0, 0))
        self.fake(lambda path, p: self.lv0())
        self.assertEqual(zbmath.msc_top_names()["11"], "Fresh 11")
        os.utime(path, (0, 0))
        self.fake(lambda path, p: self.lv0(20))   # a short list is not written over the good copy
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(zbmath.msc_top_names()["11"], "Fresh 11")
        self.assertIn("could not refresh the MSC names", err.getvalue())
        self.assertEqual(json.loads(path.read_text())["11"], "Fresh 11")
        self.assertEqual([p.name for p in zbmath.CACHE.iterdir()], ["msc-top.json"])   # no temporary file left

    def test_damaged_or_missing_cache(self):
        (zbmath.CACHE / "msc-top.json").write_text('{"11": "Number th')
        self.fake(lambda path, p: self.lv0())
        self.assertEqual(zbmath.msc_top_names()["05"], "Fresh 05")
        (zbmath.CACHE / "msc-top.json").unlink()

        def down(path, p):
            raise zbmath.Fail("cannot reach api.zbmath.org")
        self.fake(down)
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(zbmath.msc_top_names(), {})   # names are optional: codes are printed alone
        self.assertFalse((zbmath.CACHE / "msc-top.json").exists())


class Usage(unittest.TestCase):
    def test_help(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(zbmath.main(["--help"]), 0)
            self.assertEqual(zbmath.main([]), 2)
            self.assertEqual(zbmath.main(["frobnicate"]), 2)
        self.assertIn("zbmath.py search QUERY", out.getvalue())


if __name__ == "__main__":
    unittest.main()
