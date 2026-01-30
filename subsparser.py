from fugashi import Tagger
from pathlib import Path
import sys
import re


HIRAGANA = "いのたなてにっしとかはるうがをんでだられもくこそまありすきよさけちつえわどおやじめろゃみせねずばげほふょゆひびむへごぶぐぎぼべざぞぱぬぜぽづぴゅぷぺぁゐぇぉぅぢぃゑゔゎゖゕゞゝ"
KATAKANA = "ーンスルイトロクッラリアレドカシタコマバテフキツサメズジナエムオチデホミニャプウィヘノケブボパグモガダュビハギヒソベョワェザヤネァゴセピペポゲヴユヨゼォヌゥゾヶヲヅヱヵヂヰヺヹヸヷ于ヮヾヽ"
PUNCUTATION = "、。」「….!？・』『！?―(〈〉)（）:］［＃～,〟〝-》《=】─/【}[;〔>_※<]＝*＊`{＋＼&+．：⊥〕×＜∴％＞＆÷∵%≦－⊆⊃Ｌ≡≒⊂≧#^／∋∩≠θ∀ψ⊇∠“”±≪≫∬‥，∈‐〆"
ICONS = "★○◇♪→☆■↓●㊦◎†㌧㍗〒↑㌔←㍉♂㌦△▽▼▲㌣⇒⇔◆㌃㍑㈱㌘㌍㌻㊥□㍍㊧㊤㌶㌫♀㌢㈹㍊㊨㈲"
ALPHANUMERIC = "1P7239L5iAp40VSHt6O8rolIFDMBhneECgTfρm①Rηba２UN１suωGＡκQσcφKΦYqdZγ３jk０ζＤ４ＭＢ５vJδτＳyＯＣ∫W８Ｔ￠X６Ｉ９７℃μλξＫＲＥπ"
SKIP_WORDS = (  # Skip words with only one (non-kanji) character
    list(HIRAGANA)
    + list(KATAKANA)
    + list(PUNCUTATION)
    + list(ICONS)
    + list(ALPHANUMERIC)
)


def remove_text_in_braces(s: str) -> str:
    return re.sub(r"\（.*?\）", "", s)


known_words = ["そう-様態"] + SKIP_WORDS  # TODO: read text file for known_words
text = remove_text_in_braces(Path(sys.argv[1]).read_text("utf-8"))
sentences = [s for s in text.splitlines() if s.strip()]
tagger = Tagger("-Owakati")

# ditinoary for for word frequency, and examples in context
data = {}

for sentence in sentences:
    words = tagger(sentence)
    for word in words:
        lemma = str(word.feature.lemma).strip()
        if not lemma or lemma == "None" or lemma in known_words:
            continue

        # Add word and its info
        if lemma not in data:
            data[lemma] = {"frequency": 0, "sentences": set(), "readings": set()}

        data[lemma]["frequency"] += 1
        data[lemma]["sentences"].add((sentence, str(word)))
        data[lemma]["readings"].add(str(word.feature.pronBase))

# Sort by frequency
sorted_words = sorted(data.items(), key=lambda item: item[1]["frequency"], reverse=True)

# Output
print("freq;word;readings;examples")
for word, info in sorted_words:
    frequency = info["frequency"]
    print(f"{frequency};{word};", end="")

    print(", ".join(info["readings"]), end="")
    print(";", end="")

    # Print examples with word form in (brackets) if word and word_form are different
    for i, (s, w) in enumerate(info["sentences"]):
        word_form = f" ({w})" if w != word else ""
        sep = ", " if i != len(info["sentences"]) - 1 else ""
        print(f"{s}{word_form}{sep}", end="")
    print()
