import json
import csv
import sys
import re
from deep_translator import GoogleTranslator  # ,MyMemoryTranslator
from jamdict import Jamdict
from pathlib import Path
from pydantic.dataclasses import dataclass as pyd_dataclass
from dataclasses import field


@pyd_dataclass
class Header:
    """Заголовок карточки/статьи с первеводом"""

    kana: str
    kanji: str | None  # FIXME: MAYBE MANY KANJIS
    transcription: str
    corpus: str | None
    id: str


@pyd_dataclass
class Rubric:
    """Рубрика с переводами, примерами, идиомами и т.д."""

    translation: str
    examples: list[str] = field(default_factory=list)  # в т.ч. идиомы


@pyd_dataclass
class Section:
    """Несколько рубрик объединённые в секции/группы (разделяются числами с точкой на отдельной строке)."""

    rubrics: list[Rubric] = field(default_factory=list)


@pyd_dataclass
class Entry:
    """Карточка/статья с переводом"""

    header: Header
    sections: list[Section] = field(default_factory=list)
    common_note: str | None = None


@pyd_dataclass
class WarodaiDictionary:
    """Основной класс хранящий все карточки/статьи с переводами"""

    entries: list[Entry] = field(default_factory=list)


# translator = MyMemoryTranslator(source='japanese', target='russian')
translator = GoogleTranslator(source="ja", target="ru")
jmd = Jamdict()
warodai = WarodaiDictionary(
    **json.loads(Path("warodai_out.json").read_text(encoding="utf-8"))
)


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


def get_warodai_translation(word: str) -> str:
    dictionary_entries = warodai.entries

    for entry in dictionary_entries:
        # print(f"Слово: {entry.header.kana}")
        if word != entry.header.kana and word != str(entry.header.kanji):
            continue

        translations: list[str] = []
        for i, section in enumerate(entry.sections, start=1):
            # print(f"Секция: {i}.")

            for j, rubric in enumerate(section.rubrics, start=1):
                translations.append(rubric.translation)
                # print(f" Перевод {j}: {rubric.translation}")

                for k, example in enumerate(rubric.examples, start=1):
                    pass
                    # print(f"  Пример {k}. {example}")
        return ". ".join(translations)

        # print()
    return ""


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
    word_ru = (
        get_warodai_translation(word).replace("<i>", "*").replace("</i>", "*")
        or f"jamdic: {word_en}"
    )
    sentences = sentences.split(", ")[:MAX_SENTENCES]
    sentences_tr: list[str] = []
    for ex in sentences:
        # TODO: err handling
        tr = get_machine_translation(remove_text_in_braces(ex))
        sentences_tr.append(tr)

    sentences = ". ".join(sentences)
    sentences_tr = ". ".join(sentences_tr)

    # Used `Kaishi 1.5k Russian` deck as template: https://github.com/NeonGooRoo/KaishiRu
    writer.writerow(
        [
            word,  # Word
            readings,  # Word Reading
            word_en,  # Word Meaning
            word_ru,  # Word Meaning (Russian)
            word,  # Word Furigana
            "",  # Word Audio
            sentences,  # Sentence
            "",  # Sentence Meaning
            sentences_tr,  # Sentence Meaning (Russian)
            sentences,  # Sentence Furigana
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
