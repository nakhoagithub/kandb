from typing import Dict
import ujson
from .collection import Collection
from copy import deepcopy
from .storage import JsonStorage
import os


class KanDB():
    def __init__(self, folder="./__db", indent: int = 2) -> None:
        self.folder = folder
        self.indent = indent
        self.storage = JsonStorage(folder=folder, indent=indent)

        if not os.path.exists(folder):
            os.makedirs(folder)

        self.collections: Dict[str, Collection] = {}

        files = [file for file in os.scandir(
            folder) if file.is_file() and file.name.endswith(".json")]
        for file in files:
            name = file.name[:len(file.name) - len('.json')]
            collection_data = Collection(name=name, storage=self.storage)
            self.collections[name] = collection_data

    def collection(self, name: str) -> Collection:
        '''
        Nhận về một `Collection` tương đương một file `.json`
        '''
        if type(name) is not str:
            raise TypeError(
                "The 'name' parameter must be of type string (str)")

        if self.collections.get(name, None) is not None:
            return self.collections[name]

        return Collection(name=name, storage=self.storage)
