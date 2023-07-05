from typing import Protocol
from collections.abc import Iterable


class Entry(Protocol):

    @property
    def kanji(self) -> str:
        ...

    @property
    def kana(self) -> str:
        ...

    @property
    def meanings(self) -> Iterable[tuple[str, str]]:
        ...

    @property
    def alt_forms(self) -> Iterable[str]:
        ...


def dump_entry(entry: Entry, num: int) -> str:
    sections = []
    kanji_line = (
        f"{entry.kanji}\n    {entry.kana}"
        if entry.kanji
        else entry.kana
    )
    sections.append(f"{f'{num})':<4}{kanji_line}")
    sections.extend(
        f"    {i}. [{tag}]\n    {meaning}"
        for i, (tag, meaning) in enumerate(entry.meanings, 1)
    )
    if entry.alt_forms:
        sections.append(f"    Other Forms: {'、'.join(entry.alt_forms)}")
    return "\n\n".join(sections)


def dump_all_entries(entries: Iterable[Entry]) -> str:
    sep = "\n\n---\n"
    entry_strs = sep.join(
        dump_entry(entry, i)
        for i, entry in enumerate(entries, 1)
    )
    return sep + entry_strs + sep
