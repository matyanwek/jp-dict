from dataclasses import dataclass


@dataclass
class Entry:
    id: int
    rank: int
    kanjis: list[str]
    kanas: list[str]
    meanings: list[tuple[str, str]]

    @property
    def kanji(self) -> str:
        """first kanji"""
        try:
            return self.kanjis[0]
        except IndexError:
            return ""

    @property
    def kana(self) -> str:
        """first kana"""
        assert self.kanas  # no kana forms indicates malformed entry
        return self.kanas[0]

    @property
    def alt_forms(self) -> list[str]:
        """subsequent kanji and first kana"""
        alt_forms = self.kanjis[1:]
        try:
            alt_forms.insert(1, self.kanas[1])
        except IndexError:
            pass
        return alt_forms

    def __hash__(self) -> int:
        return hash(self.id)
