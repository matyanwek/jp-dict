from typing import Protocol
from collections.abc import Callable, Iterable, Sequence


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


QueryFunc = Callable[[str], Sequence[Entry]]
