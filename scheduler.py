import asyncio
import os
import pickle
from io import BytesIO

import aioschedule
import dotenv
from tortoise import Tortoise

from scripts.core.file_tables import FileTable
from scripts.core.search import index_documents, DocumentDataclass
from scripts.models import pg

dotenv.load_dotenv()


async def index_document():
    await Tortoise.init(
        db_url='postgres://docker:docker@localhost:5432/docker',
        modules={"pg": ['scripts.models.pg']},
    )

    async def job():
        index = index_documents(
            map(
                lambda x: DocumentDataclass(
                    ID=x.ID,
                    title=x.path,
                    abstract=FileTable.open(x.path),
                ),
                await pg.Page.filter(deleted=False, document__deleted=False)
            )
        )
        FileTable(os.getenv('PATH_TO_INDEX')).add_file(BytesIO(pickle.dumps(index, fix_imports=True)), postfix='.pkl')
    aioschedule.every(2).minutes.do(job)

    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


asyncio.run(index_document())
