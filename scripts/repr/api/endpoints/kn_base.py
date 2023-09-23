from io import BytesIO
from typing import Dict, Annotated

from fastapi import UploadFile, BackgroundTasks, Depends, HTTPException
from tortoise.query_utils import Prefetch

from scripts.core.file_tables import FileTable
from scripts.core.pdf import read_pdf
from scripts.core.preprocess import (
    get_keywords,
    preprocess_page
)
from scripts.core.security import permission_setter

from scripts.core.simple import (
    remove_none_from_dct,
    flatten_nested_decorator, all_is_none, delete_keys
)

from scripts.models.pg import Document, Page
from scripts.repr.api.tools.user import get_current_user


async def add_files_to_base(
        back: BackgroundTasks,
        file: UploadFile,
        doc_name: str,
        user: Annotated[Dict, Depends(permission_setter())]
):
    document = await Document.create(name=doc_name, user=await get_current_user(user))

    async def upload():
        pages = await read_pdf(file)
        ft = FileTable()
        indexes = [ft.add_file(BytesIO(preprocess_page(page).encode())) for page in pages]
        keywords = list(map(lambda x: get_keywords(x, 40), pages))

        return [
            await Page.create(document=document, keywords=k, path=i, number=num)
            for (num, (i, k)) in enumerate(zip(indexes, keywords))
        ]

    back.add_task(upload)
    return document


@flatten_nested_decorator('document')
async def get_meta(
        user: Annotated[Dict, Depends(permission_setter())],
        doc_name: str = None,
        doc_id: int = None,
        page_num: int = None,
        page_id: int = None,
        deleted: bool = None,
        deleted_pages: bool = None,
):
    doq_q = remove_none_from_dct(
        {
            'ID': doc_id,
            'name__icontains': doc_name,
            'deleted': deleted,
        }
    )
    page_q = remove_none_from_dct({
        'page__id': page_id,
        'page__number': page_num,
        'page__deleted': deleted_pages
    })
    return await Document.filter(user=await get_current_user(user), **doq_q, ).prefetch_related(
        Prefetch('page', Page.filter(**page_q))
    ).filter(**page_q).values(
        'page__number',
        'page__ID',
        'ID',
        'deleted',
        'page__deleted',
        'page__keywords',
        'name'
    )


async def delete_data(
        user: Annotated[Dict, Depends(permission_setter())],
        doc_id: int = None,
        doc_name: str = None,
        page_num: int = None,
        page_id: int = None,
        force: bool = False,
):
    if all_is_none(doc_id, doc_name, page_num, page_id):
        raise HTTPException(406)
    doq_q = remove_none_from_dct(
        {
            'ID': doc_id,
            'name__icontains': doc_name,
        }
    )
    page_q = remove_none_from_dct(
        {
            'id': page_id,
            'number': page_num,
        }
    )
    document = Document.filter(user=await get_current_user(user), **doq_q, )
    page = Page.filter(document_id__in=list(map(lambda x: x.ID, await document)), **page_q)
    await page.delete() if force else await page.update(deleted=True)
    await document.delete() if force else await document.update(deleted=True)
    tuple(map(lambda x: FileTable.unlink(x.path), await page))
    return {'result': 'Success'}


@flatten_nested_decorator('document')
async def get_pages(
        user: Annotated[Dict, Depends(permission_setter())],
        doc_id: int = None,
        doc_name: str = None,
        page_num: int = None,
        page_id: int = None,
        start: int = 0,
        stop: int = 10
):
    doq_q = remove_none_from_dct(
        {
            'ID': doc_id,
            'name__icontains': doc_name,
        }
    )
    page_q = remove_none_from_dct(
        {
            'id': page_id,
            'number': page_num,
        }
    )
    return list(
        map(
            lambda x: {"page__data": FileTable.open(x.get('page__path')), **delete_keys(x, 'page__path')},
            (
                await Document.filter(user=await get_current_user(user), **doq_q, ).prefetch_related(
                    Prefetch('page', Page.filter(**page_q))
                ).filter(**page_q).values(
                    'page__number',
                    'page__path',
                    'ID',
                    'deleted',
                    'name'
                )
            )[start:stop]
        )
    )
