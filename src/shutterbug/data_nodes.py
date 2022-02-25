from __future__ import annotations
from pathlib import Path

from sqlalchemy.engine.base import Engine
from shutterbug.data import Star, FileInput, DBWriter, DBReader
from shutterbug.interfaces.external import ControlNode
from attr import field, define
from typing import Iterable, Generator, List


@define
class LoadNode(ControlNode):
    urls: List[Path] = field()

    def execute(self) -> Generator[Iterable[Star], None, None]:
        for url in self.urls:
            yield from FileInput(url)


@define
class DBStoreNode(ControlNode):
    loader: LoadNode = field()
    engine: Engine = field()
    dataset: str = field()

    def execute(self) -> None:
        data = self.loader.execute()
        writer = DBWriter(engine=self.engine, dataset=self.dataset)
        for star in data:
            writer.write(star)
