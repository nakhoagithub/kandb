from pathlib import Path
from threading import Lock
from typing import Dict
import ujson

from collection import Collection


class KanDB():
    def __init__(self, folder_name: str = "./__db", indent: int = 2) -> None:
        self._folder_name = folder_name
        self.indent = indent

        # dữ liệu mặc định của một file `.json`
        self._default_collection = Collection()

        path = Path(self._folder_name)
        # tạo thư mục nếu thư mục không tồn tại
        if not path.exists():
            path.mkdir()

        # dữ liệu collection
        self.collections: Dict[str, Collection] = {}

        # tải dữ liệu vô `self.collections`
        files = [file for file in path.iterdir() if file.is_file()
                 and file.name.endswith(".json")]

        for file in files:
            file_name = file.name[:len(".json") * -1]
            self._read_file(file_name)

    def _init_if_not_exists(self, name: str):
        '''
        Khởi tạo file `.json` nếu file này không tồn tại
        '''
        path = Path(self._folder_name).joinpath(f'{name}.json')
        if not path.exists():
            with open(str(path), encoding='utf-8', mode='w') as f:
                ujson.dump(self._default_collection.value(),
                           f, indent=self.indent)

            self.collections[name] = self._default_collection

    def _read_file(self, name: str):
        '''
        Đọc dữ liệu từ folder
        '''
        path = Path(self._folder_name).joinpath(f'{name}.json')

        with open(str(path), encoding='utf-8', mode='r') as f:
            collection_data = Collection(name=name, storage=ujson.load(f))
            self.collections[name] = collection_data.itself()
            return collection_data

    def collection(self, name: str) -> Collection:
        '''
        Nhận về một `Collection` tương đương một file `.json`
        '''
        if type(name) is not str:
            raise TypeError(
                "The 'name' parameter must be of type string (str)")

        self._init_if_not_exists(name)
        return self._read_file(name)

    def run(self):
        pass
