from typing import Any
from collections.abc import Callable

from .entry import Entry
from .condition_en_words import make_en_terms
from .romaji_to_kana import KanaError, convert_romaji_to_kana
from .tables import (
    load_entries,
    load_kana_table,
    load_kanji_table,
    load_rank_table,
    load_en_terms_table,
)


class LazyTable:

    def __init__(self, method: Callable[[], dict[int, Any]]) -> None:
        self._method = method

    @property
    def contents(self) -> dict[int, Any]:
        if not hasattr(self, "_contents"):
            self._contents = self._method()
        return self._contents


KANA_TABLE = LazyTable(load_kana_table)
KANJI_TABLE = LazyTable(load_kanji_table)
RANK_TABLE = LazyTable(load_rank_table)
EN_TERMS_TABLE = LazyTable(load_en_terms_table)


def search_jp(search_str: str, table: LazyTable) -> list[int]:
    """search algorithm used in both kana and kanji searches"""
    exact_matches = []
    start_matches = []
    contain_matches = []
    for id, values in table.contents.items():
        for value in values:
            if search_str == value:
                exact_matches.append(id)
            elif value.startswith(search_str):
                start_matches.append(id)
            elif search_str in value:
                contain_matches.append(id)
    exact_matches.sort(key=lambda id: RANK_TABLE.contents[id])
    start_matches.sort(key=lambda id: RANK_TABLE.contents[id])
    contain_matches.sort(key=lambda id: RANK_TABLE.contents[id])
    return exact_matches + start_matches + contain_matches


def search_kana(search_str: str) -> list[int]:
    return search_jp(search_str, KANA_TABLE)


def search_kanji(search_str: str) -> list[int]:
    ids = search_jp(search_str, KANJI_TABLE)
    if ids:
        return ids
    else:
        # if no kanji matches, try kana search:
        return search_kana(search_str)


def search_en(search_str: str) -> list[int]:
    search_terms = make_en_terms(search_str)
    entry_scores = {}
    for id, terms in EN_TERMS_TABLE.contents.items():
        # terms_count = sum(
        #     1
        #     for term in search_terms
        #     if term in terms
        # )
        terms_count = 0
        term_order_inverse = 1
        for i, term in enumerate(terms, 1):
            if term in search_terms:
                terms_count += 1
                term_order_inverse += i
        if terms_count:
            # sort order: by num of matching search terms, then by rank, then by
            # order of terms
            # exclude entries with no matching terms
            entry_scores[id] = (
                -terms_count,
                RANK_TABLE.contents[id],
                term_order_inverse
            )
            print(id, entry_scores[id])
    return sorted(entry_scores.keys(), key=lambda key: entry_scores[key])


def search_ascii(search_str: str) -> list[int]:
    """ascii search as either kana (romaji input) or EN (english input)"""
    try:
        kana = convert_romaji_to_kana(search_str)
    except KanaError:
        pass  # search_en outside of exception handling
    else:
        return search_kana(kana)
    return search_en(search_str)


def search_dictionary(search_str: str) -> list[Entry]:
    if search_str.isascii():
        ids = search_ascii(search_str)
    else:
        ids = search_kanji(search_str)
    return load_entries(ids)
