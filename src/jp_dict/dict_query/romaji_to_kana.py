
ROMAJI_DICT = {

    "a": "あ",

    "i": "い",

    "u": "う",

    "e": "え",

    "o": "お",

    "ka": "か",
    "kka": "っか",
    "ga": "が",

    "ki": "き",
    "kki": "っき",
    "kya": "きゃ",
    "kyu": "きゅ",
    "kyo": "きょ",
    "gi": "ぎ",
    "gya": "ぎゃ",
    "gyu": "ぎゅ",
    "gyo": "ぎょ",

    "ku": "く",
    "kku": "っく",
    "gu": "ぐ",

    "ke": "け",
    "kke": "っけ",
    "ge": "げ",

    "ko": "こ",
    "kko": "っこ",
    "go": "ご",

    "sa": "さ",
    "ssa": "っさ",
    "za": "ざ",

    "si": "し",
    "shi": "し",
    "ssi": "っし",
    "sshi": "っし",
    "sya": "しゃ",
    "sha": "しゃ",
    "shya": "しゃ",
    "ssha": "っしゃ",
    "syu": "しゅ",
    "shu": "しゅ",
    "shyu": "しゅ",
    "sshu": "っしゅ",
    "syo": "しょ",
    "sho": "しょ",
    "shyo": "しょ",
    "ssho": "っしょ",
    "ji": "じ",
    "ja": "じゃ",
    "jya": "じゃ",
    "ju": "じゅ",
    "jyu": "じゅ",
    "jo": "じょ",
    "jyo": "じょ",

    "su": "す",
    "ssu": "っす",
    "zu": "ず",

    "se": "せ",
    "sse": "っせ",
    "ze": "ぜ",

    "so": "そ",
    "sso": "っそ",
    "zo": "ぞ",

    "ta": "た",
    "tta": "った",
    "da": "だ",

    "ti": "ち",
    "chi": "ち",
    "cchi": "っち",
    "cha": "ちゃ",
    "chya": "ちゃ",
    "ccha": "っちゃ",
    "chu": "ちゅ",
    "chyu": "ちゅ",
    "cchu": "っちゅ",
    "cho": "ちょ",
    "chyo": "ちょ",
    "ccho": "っちょ",
    "di": "ぢ",
    # "ji"  : "ぢ",  # would overwrite romaji for 'じ'

    "tu": "つ",
    "tsu": "つ",
    "ttu": "っつ",
    "ttsu": "っつ",
    "du": "づ",

    "te": "て",
    "tte": "って",
    "de": "で",

    "to": "と",
    "tto": "っと",
    "do": "ど",

    # NOTE: order matters for 'n' kana; try all possible 'n_' combinations
    # before consuming 'n'

    "na": "な",
    "nna": "んな",

    "ni": "に",
    "nni": "んに",
    "nya": "にゃ",
    "nyu": "にゅ",
    "nyo": "にょ",

    "nu": "ぬ",
    "nnu": "んぬ",

    "ne": "ね",
    "nne": "んね",

    "no": "の",
    "nno": "んの",

    "n'": "ん",
    "nn": "ん",
    "n": "ん",

    "ha": "は",
    "ba": "ば",
    "pa": "ぱ",
    "ppa": "っぱ",

    "hi": "ひ",
    "hya": "ひゃ",
    "hyu": "ひゅ",
    "hyo": "ひょ",
    "bi": "び",
    "bya": "びゃ",
    "byu": "びゅ",
    "byo": "びょ",
    "pi": "ぴ",
    "ppi": "っぴ",
    "pya": "ぴゃ",
    "ppya": "っぴゃ",
    "pyu": "ぴゅ",
    "ppyu": "っぴゅ",
    "pyo": "ぴょ",
    "ppyo": "っぴょ",

    # "hu" : "ふ",  # do not consider as valid romaji
    "fu": "ふ",
    "bu": "ぶ",
    "pu": "ぷ",
    "ppu": "っぷ",

    "he": "へ",
    "be": "べ",
    "pe": "ぺ",
    "ppe": "っぺ",

    "ho": "ほ",
    "bo": "ぼ",
    "po": "ぽ",
    "ppo": "っぽ",

    "ma": "ま",
    "mi": "み",
    "mya": "みゃ",
    "myu": "みゅ",
    "myo": "みょ",
    "mu": "む",
    "me": "め",
    "mo": "も",

    "ya": "や",
    "yu": "ゆ",
    "yo": "よ",

    "ra": "ら",
    "la": "ら",

    "ri": "り",
    "rya": "りゃ",
    "ryu": "りゅ",
    "ryo": "りょ",
    "li": "り",
    "lya": "りゃ",
    "lyu": "りゅ",
    "lyo": "りょ",

    "ru": "る",
    "lu": "る",

    "re": "れ",
    "le": "れ",

    "ro": "ろ",
    "lo": "ろ",

    "wa": "わ",
    "wi": "ゐ",
    # "we": "ゑ",
    "wo": "を",

}


LONGEST_ROMAJI = max(
    len(romaji)
    for romaji in ROMAJI_DICT.keys()
)


class KanaError(ValueError):
    pass


def pop_romaji(word: str) -> tuple[str, str]:
    """pop a single romaji from the left of word; return the kana representation
    and rest of word"""
    for romaji_len in range(LONGEST_ROMAJI, 0, -1):
        try:
            kana = ROMAJI_DICT[word[:romaji_len]]
        except KeyError:
            pass
        else:
            return kana, word[romaji_len:]
    raise KanaError(f"cannot pop kana from {word}")


def convert_romaji_to_kana(word: str) -> str:
    """attempt to convert ascii to kana, raising KanaError on failure.

    `nn` and `n'` will transcribe to `ん`.
    `n` will transcribe to `ん` if no other n-kana matches leading chars.
    """
    orig_word = word
    word = word.strip()
    kanas = []
    while word:
        try:
            kana, word = pop_romaji(word)
        except KanaError as error:
            raise KanaError(f"cannot convert {orig_word} to kana") from error
        kanas.append(kana)
    return "".join(kanas)
