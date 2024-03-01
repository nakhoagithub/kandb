from .version import __version__
import ujson
from bson import ObjectId
from .storage import JsonStorage
import os


class Collection(object):
    def __init__(self, name: str = "_default", storage: JsonStorage = None):
        self.name = name
        self._storage = storage
        self._data = {}
        self._datas = []

        if self._storage is None:
            raise ValueError('`storage` parameter is required!')

        self._path = f'{self._storage.folder}/{name}.json'
        if os.path.exists(self._path):
            with open(self._path, encoding='utf-8', mode='r') as f:
                self._data = ujson.loads(f.read())
        else:

            json_object = ujson.dumps({}, indent=self._storage.indent)
            with open(self._path, "w") as f:
                f.write(json_object)

        self._datas = [v for k, v in self._data.items()]

    def itself(self):
        return self

    def get(self) -> list:
        return self._datas

    def insert(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError(f'data must be of type dict and not {type(data)}')

        _id = str(ObjectId())
        new_data = {**data, '_id': _id}
        self._data[_id] = new_data

    def save(self):
        json_object = ujson.dumps(self._data, indent=self._storage.indent)
        with open(self._path, encoding='utf-8', mode='w') as f:
            f.write(json_object)

    def where(self, key: str, value):
        results = [[k, v] for k, v in self._data.items()]
        if key == '_id':
            self._datas = [v for k, v in results if k == value]

        return self.itself()

    def find(self, filter: dict = None):
        results = [[k, v] for k, v in self._data.items()]

        if filter is None:
            return [v for k, v in results]

        if not isinstance(filter, dict):
            raise TypeError(
                f'filter must be of type dict and not {type(filter)}')

        # filter
        new_results = []

        # and
        for key_filter, value_filter in filter.items():
            if key_filter == '_id':
                new_results = [v for k, v in results if k == value_filter]
            else:
                new_results = [v for v in new_results]

        return new_results

    # def child(self, path: str = "_default"):
    #     new_path = f"{self._path}/{path}"
    #     paths = new_path.split("/")
    #     result = self._data
    #     try:
    #         for element in paths[1:]:
    #             result = result[element]
    #     except KeyError:
    #         print(f"Không tìm thấy đường dẫn {path} trong dữ liệu JSON.")
    #     collection = Collection(result, path=new_path)
    #     return collection

    # def is_empty(self):
    #     try:
    #         return len(self._data.keys()) == 0
    #     except:
    #         return False

    # def has_child(self):
    #     try:
    #         return type(self._data) is dict
    #     except:
    #         return False
