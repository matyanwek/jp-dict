import functools

from .entry import Entry
from .lazy_table import LazyTable
from .condition_en_words import make_en_terms
from .romaji_to_kana import KanaError, convert_romaji_to_kana
from .tables import (
    load_entries,
    load_kana_table,
    load_kanji_table,
    load_rank_table,
    load_en_terms_table,
)


KANA_TABLE = LazyTable(load_kana_table)
KANJI_TABLE = LazyTable(load_kanji_table)
RANK_TABLE = LazyTable(load_rank_table)
EN_TERMS_TABLE = LazyTable(load_en_terms_table)


def search_jp(term: str, table: LazyTable) -> dict[int, int]:
    """search algorithm used in both kana and kanji searches"""
    exact_matches = []
    start_matches = []
    contain_matches = []
    for entry_id, values in table.contents.items():
        for value in values:
            if term == value:
                exact_matches.append(entry_id)
            elif value.startswith(term):
                start_matches.append(entry_id)
            elif term in value:
                contain_matches.append(entry_id)
    exact_matches.sort(key=lambda id: RANK_TABLE.contents[id])
    start_matches.sort(key=lambda id: RANK_TABLE.contents[id])
    contain_matches.sort(key=lambda id: RANK_TABLE.contents[id])
    all_matches = exact_matches + start_matches + contain_matches
    return {
        match_id: i
        for i, match_id in enumerate(all_matches)
    }


def search_kana(term: str) -> dict[int, int]:
    return search_jp(term, KANA_TABLE)


def search_kanji(term: str) -> dict[int, int]:
    ids = search_jp(term, KANJI_TABLE)
    if ids:
        return ids
    else:
        # if no kanji matches, try kana search:
        return search_kana(term)


# def search_en(search_str: str) -> dict[int, int]:
#     search_terms = make_en_terms(search_str)
#     entry_scores = {}
#     for entry_id, terms in EN_TERMS_TABLE.contents.items():
#         terms_count = 0
#         term_order_inverse = 1
#         for i, term in enumerate(terms, 1):
#             if term in search_terms:
#                 terms_count += 1
#                 term_order_inverse += i
#         if terms_count:
#             # sort order: by num of matching search terms, then by rank, then
#             # by order of terms
#             # exclude entries with no matching terms
#             entry_scores[entry_id] = (
#                 -terms_count,
#                 RANK_TABLE.contents[entry_id],
#                 term_order_inverse
#             )
#     matches = sorted(entry_scores.keys(), key=lambda key: entry_scores[key])
#     return {
#         match_id: i
#         for i, match_id in enumerate(matches)
#     }


def search_en(term: str) -> dict[int, int]:
    entry_ids = {}
    for entry_id, entry_terms in EN_TERMS_TABLE.contents.items():
        try:
            idx = entry_terms.index(term)
        except ValueError:
            continue
        score = (RANK_TABLE.contents[entry_id], idx / len(entry_terms))
        entry_ids[entry_id] = score
    matches = sorted(entry_ids.keys(), key=lambda key: entry_ids[key])
    return {
        match_id: i
        for i, match_id in enumerate(matches)
    }


def search_ascii(term: str) -> dict[int, int]:
    """ascii search as either kana (romaji input) or EN (english input)"""
    try:
        kana = convert_romaji_to_kana(term)
    except KanaError:
        pass  # search_en outside of exception handling
    else:
        return search_kana(kana)
    return search_en(term)


def search_single_term(term: str) -> dict[int, int]:
    if term.isascii():
        entry_ids = search_ascii(term)
    else:
        entry_ids = search_kanji(term)
    return entry_ids


def search_dictionary(search_str: str) -> list[Entry]:
    """search from multiple terms individually, order results by num of terms
    matched"""
    terms = search_str.split()
    if not terms:
        return []
    elif len(terms) == 1:
        # dict keys are in insertion order; no need to order entry_ids
        entry_ids = search_single_term(search_str).keys()
        return load_entries(entry_ids)
    match_dicts = [
        search_single_term(term)
        for term in terms
        if term
    ]
    entry_ids = {
        entry_id
        for match_dict in match_dicts
        for entry_id in match_dict.keys()
    }
    matches = {}
    for entry_id in entry_ids:
        match_ranks = [
            rank
            for match_dict in match_dicts
            if (rank := match_dict.get(entry_id)) is not None
        ]
        terms_count = len(terms) - len(match_ranks)
        best_rank = max(match_ranks)
        # sort order: by num of search terms matched, then by best rank
        matches[entry_id] = (terms_count, best_rank)
    match_ids = sorted(matches.keys(), key=lambda key: matches[key])
    return load_entries(match_ids)
