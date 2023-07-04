PUNCTUATION = ".,;:!?()[]{}<>"


# TODO: proper word stemming
def stem_word(word: str) -> str:
    """reduce a word to a normalized stem; e.g. running -> run"""
    return word.lower().strip(PUNCTUATION)


def make_en_terms(sentence: str) -> list[str]:
    """split a sentence into normalized word stems"""
    stems = []
    for word in sentence.split():
        stem = stem_word(word)
        if len(stem) > 2:
            stems.append(stem)
    return stems
