import os
import subprocess
from collections.abc import Iterable

from .protocols import Entry, QueryFunc


def dump_entry(entry: Entry) -> str:
    sections = []
    sections.append(
        f"{entry.kanji}\n{entry.kana}"
        if entry.kanji
        else entry.kana
    )
    sections.extend(
        f"\t{i}. [{tag}]\n{meaning}"
        for i, (tag, meaning) in enumerate(entry.meanings, 1)
    )
    if entry.alt_forms:
        sections.append(f"Other Forms: {'、'.join(entry.alt_forms)}")
    return "\n\n".join(sections)


def dump_all_entries(entries: Iterable[Entry]) -> str:
    sep = "\n\n---\n"
    entry_strs = sep.join(
        dump_entry(entry)
        for entry in entries
    )
    return sep + entry_strs + sep


def page_text(text: str) -> None:
    pager = os.getenv("PAGER")
    if pager:
        subprocess.run([pager], input=text, text=True)
    else:
        raise EnvironmentError("Cannot find $PAGER, is this env var set?")


def print_query(
    query_func: QueryFunc,
    query: str,
    dump_all: bool=False,
    page: bool=False,
) -> None:
    results = query_func(query)
    text = (
        dump_all_entries(results)
        if dump_all
        else dump_entry(results[0])
    )
    if page:
        page_text(text)
    else:
        print(text)
