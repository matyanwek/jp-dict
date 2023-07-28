import time
import unittest
from unittest import mock

from src.jp_dict.dict_query.search import search_dictionary
from src.jp_dict.dict_query.lazy_table import LazyTable

# compare first result ID to an iterable of IDs
# the idea is to ensure the first result is sensible


class TestEnSearch(unittest.TestCase):

    def test_single_word_query(self) -> None:
        results = search_dictionary("witch")
        self.assertIn(results[0].id, [1524150])  # 魔女
        results = search_dictionary("hello")
        self.assertIn(results[0].id, [1289400])  # 今日は

    def test_multi_word_query(self) -> None:
        results = search_dictionary("magical girl")
        self.assertIn(results[0].id, [2209700, 2061000])  # 魔法少女, 魔女っ子


class TestJpSearch(unittest.TestCase):

    def test_romaji_input_with_kanji(self) -> None:
        """entries that have both kanji and kana components"""
        results = search_dictionary("majo")
        self.assertIn(results[0].id, [1524150])  # 魔女
        results = search_dictionary("konban")
        self.assertIn(results[0].id, [1289470, 1289480])  # 今晩, 今晩は

    @unittest.skip("needs cases")
    def test_romaji_input_hiragana_only(self) -> None:
        """entries with only a hiragana component, no kanji"""
        pass

    @unittest.skip("will fail; can't currently convert hiragana to katakana")
    def test_romaji_input_katakana_only(self) -> None:
        """entries with only a katakana component, no kanji or hiragana"""
        results = search_dictionary("oorubakku")
        self.assertIn(results[0].id, [1033740])  # オールバック

    def test_kanji_input(self) -> None:
        results = search_dictionary("魔女")
        self.assertIn(results[0].id, [1524150])  # 魔女

    def test_hiragana_input(self) -> None:
        results = search_dictionary("まじょ")
        self.assertIn(results[0].id, [1524150])  # 魔女

    @unittest.skip("will fail; no way to convert hiragana to katakana")
    def test_katakana_input(self) -> None:
        results = search_dictionary("オールバック")
        self.assertIn(results[0].id, [1033740])  # オールバック


LAZY_TIMEOUT = 3


class TestLazyTable(unittest.TestCase):

    @mock.patch("src.jp_dict.dict_query.lazy_table.TIMEOUT", new=LAZY_TIMEOUT)
    def test_lazy_table(self) -> None:
        lazy_table = LazyTable(lambda: {})
        # contents unloaded
        self.assertFalse(hasattr(lazy_table, "_contents"))
        # load contents and return
        self.assertEqual(lazy_table.contents, {})
        # contents loaded
        self.assertTrue(hasattr(lazy_table, "_contents"))
        time.sleep(1)
        # reload contents before timeout
        lazy_table.contents
        time.sleep(2)
        # contents still loaded after first load timeout
        self.assertTrue(hasattr(lazy_table, "_contents"))
        time.sleep(LAZY_TIMEOUT - 2)
        # contents unloaded after last load timeout
        self.assertFalse(hasattr(lazy_table, "_contents"))


if __name__ == "__main__":
    unittest.main()
