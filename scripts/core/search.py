import math
import time
from collections import Counter
from dataclasses import dataclass, field
from typing import List, Iterable, Generator, Union

from scripts.core.preprocess import preprocess_for_search


@dataclass(kw_only=True)
class DocumentDataclass:
    ID: int | str = field(default=int(time.time()*1000))
    title: str
    abstract: str
    url: str = None
    page: int = None
    pages: int = None
    term_frequencies: Counter = None

    @property
    def fulltext(self):
        return ' '.join([self.title, self.abstract])

    def preprocess_for_search(self):
        self.term_frequencies = Counter(preprocess_for_search(self.fulltext, True), )

    def term_frequency(self, term):
        return self.term_frequencies.get(term, 0)


class Index:
    def __init__(self):
        self.index = {}
        self.documents = {}

    def index_document(self, document):
        if document.ID not in self.documents:
            self.documents[document.ID] = document
            document.preprocess_for_search()

        for token in preprocess_for_search(document.fulltext):
            if token not in self.index:
                self.index[token] = set()
            self.index[token].add(document.ID)

    def document_frequency(self, token):
        return len(self.index.get(token, set()))

    def inverse_document_frequency(self, token):
        return math.log10(len(self.documents) / self.document_frequency(token))

    def _results(self, analyzed_query):
        return [self.index.get(token, set()) for token in analyzed_query]

    def search(self, query, search_type='AND', rank=False):
        documents = []
        if search_type not in ('AND', 'OR'):
            return []

        analyzed_query = preprocess_for_search(query)
        results = self._results(analyzed_query)
        if search_type == 'AND':
            documents = [self.documents[doc_id] for doc_id in set.intersection(*results)]
        elif search_type == 'OR':
            documents = [self.documents[doc_id] for doc_id in set.union(*results)]

        if rank:
            return self.rank(analyzed_query, documents)
        return documents

    def rank(self, analyzed_query: List[str], documents: List[DocumentDataclass]) -> sorted:
        results = []
        if not documents:
            return results
        for document in documents:
            score = 0.0
            for token in analyzed_query:
                tf = document.term_frequency(token)
                idf = self.inverse_document_frequency(token)
                score += tf * idf
            results.append((document, score))
        return sorted(results, key=lambda doc: doc[1], reverse=True)


def index_documents(documents: Union[Generator, Iterable[DocumentDataclass]], index: Index = Index()):
    for i, document in enumerate(documents):
        index.index_document(document)
    return index


