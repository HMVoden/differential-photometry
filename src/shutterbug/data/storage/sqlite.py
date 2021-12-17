from typing import Iterable
from shutterbug.data.core.interface.storage import StorageInterface

from functools import singledispatchmethod

from shutterbug.data.core.star import Star

class StoreSQLite(StorageInterface):
    @singledispatchmethod
    def store(self, data: Star):
        pass

    @store.register
    def _(self, data: Iterable[Star]):
        pass
