import os
import uuid
from glob import glob
from io import BytesIO
from pathlib import Path
from typing import Tuple, Union

from starlette.background import BackgroundTasks

from scripts.core.simple import (
    get_date,
    empty_str,
    stringify_return,
)


class FileTable:
    def __init__(
            self,
            _data: Union[str, Path, os.PathLike] = None,
            part_sz: int = None,
            preprocess: callable = None,
    ):
        if _data is None:
            _data = os.getenv('FILE_TABLE_PATH')
        if part_sz is None:
            part_sz = int(os.getenv('FILE_TABLE_SZ'))
        self.data = Path(_data)
        self.part_sz = part_sz
        self.preprocess = preprocess
        os.makedirs(_data, exist_ok=True)

    @property
    def latest(self) -> int:
        layer = tuple(map(lambda x: int(Path(x).parent.name), self.listing(self.first_layer, dirs=True)))
        return int(
            tuple(
                sorted(layer, key=lambda x: os.path.getctime(self.data / self.first_layer / f'{x}'), ))[-1]
        ) if layer.__len__() else 0

    @property
    def first_layer(self) -> str:
        return get_date()

    def write(self, path: Union[str, os.PathLike, Path], _file: BytesIO, ):
        with open(path, 'wb') as file:
            file.write(self.preprocess(_file.read()) if self.preprocess is not None else _file.read())

    def listing(self, _date: str = None, _part: int = None, dirs: bool = False) -> Tuple:
        return tuple(
            filter(
                lambda x: (not Path(x).is_dir()) or dirs,
                glob(pathname=f'{self.data / empty_str(_date) / empty_str(_part) / "*"}'.replace('**', '*'))
            )
        )

    def _add_first_layer(self, first_layer: str):
        if not (self.data / first_layer).exists():
            os.makedirs(self.data / first_layer, exist_ok=True)

    def _add_part(
            self,
            first_layer: str,
            latest: int,
    ) -> Path:
        listing = self.listing(first_layer, latest, dirs=True).__len__()
        path = Path(self.data / first_layer / f'{latest}')
        if listing == 0:
            os.makedirs(path, exist_ok=True)
        elif listing >= self.part_sz:
            path = Path(self.data / first_layer / f'{latest + 1}')
            os.makedirs(path, exist_ok=True)
            return path
        return path

    @stringify_return
    def add_file(
            self,
            _file: BytesIO = None,
            _uuid: uuid.UUID = None,
            back: BackgroundTasks = None,
    ):
        latest = self.latest
        first_layer = self.first_layer
        self._add_first_layer(first_layer)
        path = self._add_part(first_layer, latest)
        path = path / str(uuid.uuid4()) if _uuid is None else str(_uuid)
        if back is not None:
            back.add_task(self.write, path, _file, )
            return path
        self.write(path, _file,)
        return path

    @staticmethod
    def open(path: Union[str, Path, os.PathLike]):
        with open(path, 'r') as f:
            return f.read()

    @staticmethod
    def unlink(path: Union[str, Path, os.PathLike]):
        return Path(path).unlink(missing_ok=True)