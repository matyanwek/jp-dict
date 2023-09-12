import json
import gzip
import shutil
from typing import Any
from importlib import resources
from xml.etree import ElementTree
from urllib.request import urlopen
from collections.abc import Iterable
from importlib.abc import Traversable

from .entry import Entry
from .condition_en_words import make_en_terms
from . import data

DICT_DL_URL = "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"

# data files
DATA = resources.files(data)
KANA_TABLE_JSON = DATA / "kana.json"
KANJI_TABLE_JSON = DATA / "kanji.json"
RANK_TABLE_JSON = DATA / "ranks.json"
EN_TERMS_TABLE_JSON = DATA / "en_terms.json"
ENTRIES_DIR = DATA / "entries"


def get_tag_text(elt: ElementTree.Element, tag: str) -> list[str]:
    return [
        child.text
        for child in elt.findall(tag)
        if child is not None
        and child.text is not None
    ]


def get_rank(elt: ElementTree.Element) -> int:
    """use JMdict priority tags; max is 48; no priority tag set to 50"""
    rank_tags = get_tag_text(elt, "./k_ele/ke_pri")
    if not rank_tags:
        rank_tags = get_tag_text(elt, "./r_ele/re_pri")
    ranks = [50]
    for tag in rank_tags:
        if tag.startswith("nf"):
            ranks.append(int(tag.removeprefix("nf")))
        elif tag.startswith("gai"):
            rank = int(tag.removeprefix("gai"))
            ranks.append((rank * 24) - (rank * 4))
        elif tag.startswith("news"):
            rank = int(tag.removeprefix("news"))
            ranks.append((rank * 24) - (rank * 8))
        elif tag.startswith("ichi"):
            rank = int(tag.removeprefix("ichi"))
            ranks.append((rank * 24) - (rank * 8))
        elif tag.startswith("spec"):
            rank = int(tag.removeprefix("spec"))
            ranks.append((rank * 24) - (rank * 8))
    return min(ranks)


def get_kanjis(elt: ElementTree.Element) -> list[str]:
    return get_tag_text(elt, "./k_ele/keb")


def get_kanas(elt: ElementTree.Element) -> list[str]:
    return get_tag_text(elt, "./r_ele/reb")


def get_meanings(elt: ElementTree.Element) -> list[tuple[str, str]]:
    meanings = []
    for sense in elt.findall("sense"):
        pos = ", ".join(get_tag_text(sense, "pos"))  # part of speech
        gloss = "; ".join(get_tag_text(sense, "gloss"))  # glossary
        meanings.append((pos, gloss))
    return meanings


def make_entry(elt: ElementTree.Element) -> Entry:
    id_tag = elt.find("ent_seq")
    assert id_tag is not None and id_tag.text
    id = int(id_tag.text)
    rank = get_rank(elt)
    kanjis = get_kanjis(elt)
    kanas = get_kanas(elt)
    meanings = get_meanings(elt)
    return Entry(id, rank, kanjis, kanas, meanings)


# def get_en_term_freqs(entry: Entry) -> dict[str, int]:
#     en_terms = [
#         term
#         for _, meaning in entry.meanings
#         for term in make_en_terms(meaning)
#     ]
#     freqs: dict[str, int] = {}
#     for term in en_terms:
#         try:
#             freqs[term] += 1
#         except KeyError:
#             freqs[term] = 1
#     return freqs


def write_traversable(obj: Any, trav: Traversable) -> None:
    with resources.as_file(trav) as path:
        if not path.parent.exists():
            path.parent.mkdir(parents=True)
        path.write_text(json.dumps(obj, indent=4, ensure_ascii=False) + "\n")


def write_entry(entry: Entry) -> None:
    entry_file = ENTRIES_DIR / f"{entry.id}.json"
    write_traversable(entry.__dict__, entry_file)


def index_dictionary(dict_xml: bytes) -> None:
    root = ElementTree.fromstring(dict_xml)
    kana_table = {}
    kanji_table = {}
    rank_table = {}
    en_terms_table = {}
    for elt in root.findall("entry"):
        entry = make_entry(elt)
        write_entry(entry)
        kana_table[entry.id] = entry.kanas
        kanji_table[entry.id] = entry.kanjis
        rank_table[entry.id] = entry.rank
        # en_terms_table[entry.id] = get_en_term_freqs(entry)
        en_terms_table[entry.id] = [
            term
            for _, meaning in entry.meanings
            for term in make_en_terms(meaning)
        ]
    write_traversable(kana_table, KANA_TABLE_JSON)
    write_traversable(kanji_table, KANJI_TABLE_JSON)
    write_traversable(rank_table, RANK_TABLE_JSON)
    write_traversable(en_terms_table, EN_TERMS_TABLE_JSON)


def update_dictionary() -> None:
    gzip_bytes = urlopen(DICT_DL_URL).read()
    index_dictionary(gzip.decompress(gzip_bytes))


def del_traversable(trav: Traversable) -> None:
    with resources.as_file(trav) as path:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)


def clean_dictionary() -> None:
    del_traversable(KANA_TABLE_JSON)
    del_traversable(KANJI_TABLE_JSON)
    del_traversable(RANK_TABLE_JSON)
    del_traversable(EN_TERMS_TABLE_JSON)
    del_traversable(ENTRIES_DIR)


def entry_object_hook(json_obj: dict[Any, Any]) -> Entry | dict[Any, Any]:
    try:
        return Entry(**json_obj)
    except TypeError:
        return json_obj


def load_entry(entry_id: int) -> Entry:
    entry_file = ENTRIES_DIR / f"{entry_id}.json"
    return json.loads(entry_file.read_text(), object_hook=entry_object_hook)


def load_entries(entry_ids: Iterable[int]) -> list[Entry]:
    return [
        load_entry(id)
        for id in entry_ids
    ]


def load_kana_table() -> dict[int, list[str]]:
    return json.loads(KANA_TABLE_JSON.read_text())


def load_kanji_table() -> dict[int, list[str]]:
    return json.loads(KANJI_TABLE_JSON.read_text())


def load_rank_table() -> dict[int, int]:
    return json.loads(RANK_TABLE_JSON.read_text())


def load_en_terms_table() -> dict[int, dict[str, float]]:
    return json.loads(EN_TERMS_TABLE_JSON.read_text())
