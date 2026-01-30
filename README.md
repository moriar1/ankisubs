# AnkiSubs

Tool for creating Anki cards from Japanese subtitles using dictionaries and machine translation.
Works with `srt` subtitles only.

## Prerequisites

- [fugashi](https://github.com/polm/fugashi)
- [unidic](https://github.com/polm/unidic-py)
- unidic dictionary (see [unidic](https://github.com/polm/unidic-py)): `python -m unidic download`
- [jamdic, jamdic-data](https://github.com/neocl/jamdict)
- [deep-translator](https://github.com/nidhaloff/deep-translator)
- you may also need to install `sqlite` package using your OS package manager (and maybe something like `py311-sqlite3` package)

Example setup using `pip` with virtual environment:

```sh
git clone https://github.com/moriar1/ankisubs
cd ankisubs
python -m venv myenv
source myenv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m unidic download
```

## Example Usage

```sh
python subsparser.py your_subs.srt > temp.txt
python ankisubs.py temp.txt > out.txt
```

Example output. *Note: raw text output, not Anki cards yet.*

```text
御早う - オハヨー - good morning
お、おはようございます (おはよう) Oh, good morning
おはようございます… (おはよう) good morning…

笑顔 - エガオ - smiling face, smile
笑顔って難しい Smiling is difficult
```
