import dataclasses
import re
import string
from collections import Counter
from functools import wraps
from typing import Union, List
import pymorphy2
from Stemmer import Stemmer
from nltk.corpus import stopwords


@dataclasses.dataclass
class Word:
    frequency: int
    word: str


def tokenize(_tokens: Union[str, List[str]], t: bool) -> Union[str, List[str]]:
    if isinstance(_tokens, list):
        return ' '.join(_tokens) if not t else _tokens
    return _tokens.split() if t else _tokens


def tokenize_decorator(tokens: bool = True) -> callable:
    def token(func):
        @wraps(func)
        def tok(_tokens: Union[str, List[str]], t: bool = False) -> Union[str, List[str]]:
            _tokens = tokenize(_tokens, tokens)
            return tokenize(func(_tokens), t)

        return tok

    return token


@tokenize_decorator()
def lemmas(_text: Union[str, List[str]], t: bool = False) -> Union[str, List[str]]:
    _text = tokenize(_text, True)
    morph = pymorphy2.MorphAnalyzer()
    return tokenize([morph.parse(word)[0].normal_form for word in _text], t)


@tokenize_decorator()
def remove_stop_words(_text: Union[str, List[str]], ) -> Union[str, List[str]]:
    _text = tokenize(_text, True)
    stop_words = set(stopwords.words("russian"))
    return [word for word in _text if word.lower() not in stop_words]


@tokenize_decorator(False)
def cleanup(_text: str, full: bool = False, ) -> Union[str, List[str]]:
    return re.sub(
        r'[^\w\s]' if full else r'\b\w+[\.,!?;]*\w+\b',
        lambda x: re.sub(r'[\.,!?;]', '', x.group()),
        _text
    )


@tokenize_decorator()
def replace_newlines(_text: Union[str, List[str]], ) -> Union[str, List[str]]:
    _text = re.sub(r' +(?=\w)', ' ', _text.strip().replace('\n ', '\n'))
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


@tokenize_decorator()
def get_keywords(_text: Union[str, List[str]], _nk: int = None):
    _text = re.findall(r'\w+', remove_stop_words(lemmas(cleanup(_text.lower(), full=True))).lower())
    most_common = Counter(_text).most_common()
    return [
               Word(count, word).__dict__
               for word, count in most_common
               if count > len(_text) / set(_text).__len__()
           ][:_nk]


@tokenize_decorator(False)
def preprocess_page(_text: str):
    _text = [line for line in _text.split('\n') if "рисун" not in line.lower()]
    _text = cleanup(replace_newlines(_text, True), True)
    return _text


@tokenize_decorator()
def lowercase_filter(_text: Union[str, List[str]], ) -> Union[str, List[str]]:
    return [token.lower() for token in _text]


@tokenize_decorator()
def punctuation_filter(_text: Union[str, List[str]], ) -> Union[str, List[str]]:
    return [re.compile('[%s]' % re.escape(string.punctuation)).sub('', token) for token in _text]


@tokenize_decorator()
def stem_filter(_text: Union[str, List[str]], ) -> Union[str, List[str]]:
    return Stemmer('russian').stemWords(_text)


@tokenize_decorator()
def preprocess_for_search(_text: Union[str, List[str]], ) -> Union[str, List[str]]:
    _text = lowercase_filter(_text, True)
    _text = punctuation_filter(_text, True)
    _text = remove_stop_words(_text, True)
    _text = stem_filter(_text, True)
    return _text
