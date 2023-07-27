import os
import io
import unittest
import unittest.mock as mock
from dataclasses import dataclass

from src.jp_dict.ui import print_query
from src.jp_dict.ui.repl_ui import (
    HELP_MESSAGE,
    Repl,
    ReplError,
    run_once,
    run_repl,
)


@dataclass
class Entry:
    kana: str
    kanji: str
    meanings: list[tuple[str, str]]
    alt_forms: list[str]


RESULTS = [
    Entry(
        kana="first kana",
        kanji="first kanji",
        meanings=[("noun", "first meaning a"), ("noun", "first meaning b")],
        alt_forms=["first alt a", "first alt b"],
    ),
    Entry(
        kana="second kana",
        kanji="",
        meanings=[("noun", "second meaning a"), ("noun", "second meaning b")],
        alt_forms=["second alt a", "second alt b"],
    ),
    Entry(
        kana="third kana",
        kanji="third kanji",
        meanings=[("noun", "third meaning a"), ("noun", "third meaning b")],
        alt_forms=["third alt a", "third alt b"],
    ),
]


def query_func(_: str) -> list[Entry]:
    return RESULTS


def query_func_empty(_: str) -> list[Entry]:
    return []


EXPECTED_FIRST_PRINT = """
1)  first kanji
    first kana

    1. [noun]
    first meaning a

    2. [noun]
    first meaning b

    Other Forms: first alt a、first alt b
""".strip() + "\n"

EXPECTED_SECOND_PRINT = """
2)  second kana

    1. [noun]
    second meaning a

    2. [noun]
    second meaning b

    Other Forms: second alt a、second alt b
""".strip() + "\n"

EXPECTED_THIRD_PRINT = """
3)  third kanji
    third kana

    1. [noun]
    third meaning a

    2. [noun]
    third meaning b

    Other Forms: third alt a、third alt b
""".strip() + "\n"

EXPECTED_ALL_PRINT = "\n\n---\n" + "\n\n---\n".join([
    EXPECTED_FIRST_PRINT.strip(),
    EXPECTED_SECOND_PRINT.strip(),
    EXPECTED_THIRD_PRINT.strip(),
]) + "\n\n---\n\n"


class TestPrintUi(unittest.TestCase):

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_single_print(self, mock_out: io.StringIO) -> None:
        print_query(query_func=query_func, query="")
        mock_out.seek(0)
        self.assertEqual(EXPECTED_FIRST_PRINT, mock_out.read())

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_all_print(self, mock_out: io.StringIO) -> None:
        print_query(query_func=query_func, query="", print_all=True)
        mock_out.seek(0)
        self.assertEqual(EXPECTED_ALL_PRINT, mock_out.read())

    @mock.patch.dict(os.environ, {"PAGER": "page"})
    @mock.patch("subprocess.run")
    def test_all_page(self, mock_call: mock.MagicMock) -> None:
        print_query(query_func=query_func, query="", print_all=True, page=True)
        expected_text = EXPECTED_ALL_PRINT.removesuffix("\n")
        mock_call.assert_called_with(["page"], input=expected_text, text=True)

    @mock.patch.dict(os.environ, clear=True)
    def test_page_fail(self) -> None:
        err_msg = "Cannot find $PAGER, is this env var set?"
        with self.assertRaises(EnvironmentError, msg=err_msg):
            print_query(query_func=query_func, query="", page=True)

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_empty_query(self, mock_out: io.StringIO) -> None:
        print_query(query_func=query_func_empty, query="query")
        mock_out.seek(0)
        self.assertEqual("No results for query\n", mock_out.read())
        mock_out.seek(0)
        print_query(query_func=query_func_empty, query="query", print_all=True)
        mock_out.seek(0)
        self.assertEqual("No results for query\n", mock_out.read())
        mock_out.seek(0)
        print_query(
            query_func=query_func_empty,
            query="query",
            print_all=True,
            page=True
        )
        mock_out.seek(0)
        self.assertEqual("No results for query\n", mock_out.read())


class TestReplUi(unittest.TestCase):

    EXPECTED_QUERY = "expected query"

    @classmethod
    def setUpClass(cls) -> None:
        cls.repl = Repl(query_func=query_func)

    def setUp(self) -> None:
        self.repl.query = self.EXPECTED_QUERY
        self.repl.result_idx = 0
        self.repl.results = RESULTS

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_query(self, mock_out: io.StringIO) -> None:
        self.repl.query = "something else"
        self.repl.result_idx = 1
        self.repl.results = []
        with mock.patch("builtins.input", side_effect=[self.EXPECTED_QUERY]):
            run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(0, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)
        mock_out.seek(0)
        self.assertEqual(EXPECTED_FIRST_PRINT, mock_out.read())

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_next(self, mock_out: io.StringIO) -> None:
        with mock.patch("builtins.input", side_effect=["\\n"]):
            run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(1, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)
        mock_out.seek(0)
        self.assertEqual(EXPECTED_SECOND_PRINT, mock_out.read())

    def test_next_fail(self) -> None:
        self.repl.result_idx = 10
        with self.assertRaises(ReplError, msg="No next result"):
            with mock.patch("builtins.input", side_effect=["\\n"]):
                run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(2, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_prev(self, mock_out: io.StringIO) -> None:
        self.repl.result_idx = 1
        with mock.patch("builtins.input", side_effect=["\\p"]):
            run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(0, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)
        mock_out.seek(0)
        self.assertEqual(EXPECTED_FIRST_PRINT, mock_out.read())

    def test_prev_fail(self) -> None:
        with self.assertRaises(ReplError, msg="No previous result"):
            with mock.patch("builtins.input", side_effect=["\\p"]):
                run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(0, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)

    def test_backup_fail(self) -> None:
        with self.assertRaises(ReplError, msg="No backup function defined"):
            with mock.patch("builtins.input", side_effect=["\\b"]):
                run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(0, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)
        new_query = "new query"
        with self.assertRaises(ReplError, msg="No backup function defined"):
            with mock.patch("builtins.input", side_effect=[f"\\b {new_query}"]):
                run_once(self.repl)
        self.assertEqual(new_query, self.repl.query)
        self.assertEqual(0, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_help(self, mock_out: io.StringIO) -> None:
        with mock.patch("builtins.input", side_effect=["\\h"]):
            run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(0, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)
        mock_out.seek(0)
        self.assertEqual(HELP_MESSAGE + "\n", mock_out.read())
        mock_out.seek(0)
        with mock.patch("builtins.input", side_effect=["\\z"]):
            run_once(self.repl)
        self.assertEqual(self.EXPECTED_QUERY, self.repl.query)
        self.assertEqual(0, self.repl.result_idx)
        self.assertEqual(RESULTS, self.repl.results)
        mock_out.seek(0)
        self.assertEqual(HELP_MESSAGE + "\n", mock_out.read())

    @mock.patch("src.jp_dict.ui.repl_ui.page_text")
    def test_page(self, mock_call: mock.MagicMock) -> None:
        with mock.patch("builtins.input", side_effect=["\\a"]):
            run_once(self.repl)
        expected_text = EXPECTED_ALL_PRINT.removesuffix("\n")
        mock_call.assert_called_with(expected_text)

    def test_exit(self) -> None:
        with self.assertRaises(EOFError):
            with mock.patch("builtins.input", side_effect=["\\exit"]):
                run_once(self.repl)


class TestReplUiEmptyQuery(unittest.TestCase):

    EXPECTED_QUERY = "expected query"

    @classmethod
    def setUpClass(cls) -> None:
        cls.repl = Repl(query_func=query_func_empty)

    def setUp(self) -> None:
        self.repl.query = self.EXPECTED_QUERY
        self.repl.result_idx = 0
        self.repl.results = []

    def test_query(self) -> None:
        err_msg = f"No results for {self.EXPECTED_QUERY}\n"
        with mock.patch("builtins.input", side_effect=[self.EXPECTED_QUERY]):
            with self.assertRaises(ReplError, msg=err_msg):
                run_once(self.repl)


class TestRunRepl(unittest.TestCase):

    TARGET = "src.jp_dict.ui.repl_ui.run_once"

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_interrupt(self, mock_out: io.StringIO) -> None:
        with mock.patch(self.TARGET, side_effect=EOFError):
            run_repl(query_func=query_func)
        mock_out.seek(0)
        self.assertEqual("\n", mock_out.read())
        mock_out.seek(0)
        with mock.patch(self.TARGET, side_effect=KeyboardInterrupt):
            run_repl(query_func=query_func)
        mock_out.seek(0)
        self.assertEqual("\n", mock_out.read())

    @mock.patch("sys.stdout", new_callable=io.StringIO)
    def test_exception(self, mock_out: io.StringIO) -> None:
        msg = "exception message"
        with mock.patch(self.TARGET, side_effect=[Exception(msg), EOFError]):
            run_repl(query_func=query_func)
        mock_out.seek(0)
        self.assertEqual(f"{msg}\n\n", mock_out.read())


if __name__ == "__main__":
    unittest.main()
