import csv
import sys
import re
from deep_translator import GoogleTranslator  # ,MyMemoryTranslator
from jamdict import Jamdict
from pathlib import Path

# translator = MyMemoryTranslator(source='japanese', target='russian')
translator = GoogleTranslator(source="ja", target="ru")
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


writer = csv.writer(sys.stdout, delimiter=";")
text = Path(sys.argv[1]).read_text("utf-8")
MAX_SENTENCES = int(sys.argv[2]) if len(sys.argv) > 2 else 2

# NOTE: no check for empty lines or fields
for line in text.splitlines()[1:]:
    freq, word, readings, sentences = line.split(";")
    # TODO: if jmdic error skip it
    word_en = get_jmdic_translation(word) or "no jmdic tr"
    word_ru = ""  # TODO:  get_warodai_tr()
    sentences = sentences.split(", ")
    sentences_tr: list[str] = []
    for ex in sentences:
        # TODO: err handling
        tr = get_machine_translation(remove_text_in_braces(ex))
        sentences_tr.append(tr)

    sentences = ". ".join(sentences[:MAX_SENTENCES])
    sentences_tr = ". ".join(sentences_tr[:MAX_SENTENCES])

    # Used `Kaishi 1.5k Russian` deck as template: https://github.com/NeonGooRoo/KaishiRu
    writer.writerow(
        [
            word,  # Word
            readings,  # Word Reading
            word_en,  # Word Meaning
            word_ru,  # Word Meaning (Russian)
            "",  # Word Furigana
            "",  # Word Audio
            sentences,  # Sentence
            "",  # Sentence Meaning
            sentences_tr,  # Sentence Meaning (Russian)
            "",  # Sentence Furigana
            "",  # Sentence Audio
            "",  # Notes
            "",  # Notes (Russian)
            "",  # Pitch Accent
            "",  # Pitch Accent Notes
            "",  # Pitch Accent Notes (Russian)
            freq,  # Frequency
            "",  # Tags
        ]
    )
