import ujson
import os
import copy
import hashlib
import time

database = None


def dir_exists(path):
    return os.path.exists(path) and os.path.isdir(path)


def file_exists(path):
    return os.path.isfile(path)


def touch(path):
    if not file_exists(path):
        with open(path, 'w') as outfile:
            ujson.dump({}, outfile)


def generate_id(path):
    while True:
        unique_value = str(time.time()).encode('utf-8')
        unique_hash = hashlib.md5(unique_value).hexdigest()[:8]

        filename = os.path.join(path, unique_hash)

        # Kiểm tra xem tên file đã tồn tại chưa
        if not os.path.exists(filename):
            return filename


print(generate_id("12321"))


class Collection():
    def __init__(self, path: str = None, indent: int = 2) -> None:
        self.path = path
        self.indent = indent

    def _get_files(self) -> list:
        if not dir_exists(self.path):
            return []
        return sorted(os.listdir(self.path), key=lambda x: os.path.getctime(f'{self.path}/{x}'))

    def _get_file(self, path: str):
        with open(path, mode="r", encoding='utf-8') as file:
            json_obj = ujson.loads(file.read())
            return json_obj

    def get(self):
        results = []
        files = self._get_files()
        for file in files:
            data = self._get_file(f'{self.path}/{file}')
            results.append(data)
        return results

    def insert(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError('`data` must be of type dict!')

        print(self.path)


class Database():
    def __init__(self, folder: str = "./__db/", indent: int = 2) -> None:
        self.folder = folder[:-1] if folder.endswith('/') else folder
        self.indent = indent
        self._init_folder()
        self._collection_default = Collection(indent=indent)

    def _init_folder(self):
        os.makedirs(f'{self.folder}/indexs/', exist_ok=True)
        os.makedirs(f'{self.folder}/datas/', exist_ok=True)

    def collection(self, name: str = "__default") -> Collection:
        path = f'{self.folder}/datas/{name}'
        os.makedirs(path, exist_ok=True)
        new_collection = copy.deepcopy(self._collection_default)
        new_collection.path = path
        return new_collection
