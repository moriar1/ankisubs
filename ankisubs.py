import sys
import re
from deep_translator import GoogleTranslator  # ,MyMemoryTranslator
from jamdict import Jamdict
from pathlib import Path

# translator = MyMemoryTranslator(source='japanese', target='english')
translator = GoogleTranslator(source="ja", target="en")
jmd = Jamdict()


def remove_text_in_jbraces(s: str) -> str:
    return re.sub(r"\（.*?\）", "", s)


# TODO: DRY
def remove_text_in_braces(s: str) -> str:
    return re.sub(r"\(.*?\)", "", s)


def get_jmdic_translation(word: str) -> str:
    result = jmd.lookup(word)
    if not result.entries:
        return ""
    entry = result.entries[0]
    # senses = entry.senses[0].gloss[0].text

    meanings = []
    for sense in entry.senses[:3]:
        for g in sense.gloss[:3]:
            meanings.append(g.text)
    # print(word, meanings)
    return ", ".join(meanings)


def get_machine_translation(text: str) -> str:
    try:
        meaning = translator.translate(text)
    except Exception as e:
        print(f"err: {e} for text: {text}", file=sys.stderr)
        print("Press ENTER.", file=sys.stderr)
        input()
        meaning = ""
    return meaning


text = Path(sys.argv[1]).read_text("utf-8")
# NOTE: no check for empty lines or fields
for line in text.splitlines()[1:]:
    freq, word, readings, examples = line.split(";")
    # TODO: if jmdic error skip it
    word_jmdic = get_jmdic_translation(word) or "*no jmdic tr*"
    # TODO: word_warodai = get_warodai_tr()
    examples = examples.split(", ")  # NOTE: rarely there are commas (,) in subs
    print(word, readings, word_jmdic, sep=" - ")
    for ex in examples:
        ex_tr = get_machine_translation(remove_text_in_braces(ex))
        print(ex, ex_tr)
    print()
