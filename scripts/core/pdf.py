from io import BytesIO
from typing import List

import fitz
from fastapi import (
    File,
    HTTPException
)


async def read_pdf(file: File, exception: Exception = HTTPException(409, 'Incorrect file')) -> List[str]:
    pages = []
    try:
        doc = fitz.open('pdf', BytesIO(await file.read()))
        for page_ind in range(doc.page_count):
            pages.append(doc.load_page(page_ind).get_text('text'))
        return pages
    except fitz.fitz.FileDataError:
        raise exception
