from version import __version__
from db_types import CollectionType
import ujson


class Collection(object):
    def __init__(self, name: str = "_default", storage: CollectionType = {'_version': __version__, '_seq': 0, '_data': {}}):
        self.name = name
        self._storage = storage
        self._seq = storage['_seq']
        self._data = storage['_data']

    def itself(self):
        return self

    def data(self):
        '''
        Trả về dữ liệu của collection
        '''
        return self._data

    def json(self) -> dict:
        return ujson.loads(ujson.dumps(self._storage))

    def value(self):
        return self._storage

    def insert(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError(f'data must be of type dict and not {type(data)}')

        print(data)

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
