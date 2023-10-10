import gzip
from xml import etree

import time

from scripts.core.search.documents import DocumentDataclass

def load_documents():
    start = time.time()
    with gzip.open('data/enwiki-latest-abstract.xml.gz', 'rb') as f:
        doc_id = 0
        for _, element in etree.iterparse(f, events=('end',), tag='doc'):
            title = element.findtext('./title')
            url = element.findtext('./url')
            abstract = element.findtext('./abstract')

            yield DocumentDataclass(ID=doc_id, title=title, url=url, abstract=abstract)

            doc_id += 1
            element.clear()
    end = time.time()
    print(f'Parsing XML took {end - start} seconds')
