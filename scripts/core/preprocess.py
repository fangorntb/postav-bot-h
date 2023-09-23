import dataclasses
import re
from collections import Counter

import pymorphy2
from nltk.corpus import stopwords


@dataclasses.dataclass
class Word:
    frequency: int
    word: str


def lemmas(_text: str, ):
    _text = _text.split()
    morph = pymorphy2.MorphAnalyzer()
    return ' '.join([morph.parse(word)[0].normal_form for word in _text])


def remove_stop_word(_text: str):
    _text = _text.split()
    stop_words = set(stopwords.words("russian"))
    return " ".join([word for word in _text if word.lower() not in stop_words])


def cleanup(_text: str, full: bool = False) -> str:
    return re.sub(
        r'[^\w\s]' if full else r'\b\w+[\.,!?;]*\w+\b',
        lambda x: re.sub(r'[\.,!?;]', '', x.group()),
        _text
    )


def replace_newlines(_text: str):
    _text = re.sub(r' +(?=\w)', ' ', _text.strip(' ').strip().replace('\n ', '\n'))
    lines = [i.strip().split(' ') for i in _text.split('\n')]
    _text = ''
    for line in lines:
        s = ''
        if line[-1].endswith('.'):
            if line[0][0].isupper():
                _text += ' '.join(line) + '\n'
                continue
        for word in line:
            s += f' {word}'
        _text += s
    return re.sub(r'\b\n\b', ' ', _text)


def get_keywords(_text: str, _nk: int = None):
    _text = re.findall(r'\w+', remove_stop_word(lemmas(cleanup(_text.lower(), full=True))).lower())
    most_common = Counter(_text).most_common()
    return [
               Word(count, word).__dict__
               for word, count in most_common
               if count > len(_text) / set(_text).__len__()
           ][:_nk]


def preprocess_page(_text: str):
    _text = '\n'.join(
        [line for line in _text.split('\n') if "рисун" not in line.lower()]
    )
    _text = cleanup(replace_newlines(_text))
    return _text


print(preprocess_page(
    open('/home/localhost/py/postav-bot-h/data/base/09-24-23/0/c9d1ee1d-232b-4455-b6ba-5a8dbe99477c').read())
)
