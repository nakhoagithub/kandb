import ujson
import os
import copy
import time
import struct
import socket
import random
import threading
import binascii
import shutil
import datetime
import socketserver


lock = threading.Lock()

database = None


def dir_exists(path):
    return os.path.exists(path) and os.path.isdir(path)


def file_exists(path):
    return os.path.isfile(path)


def create_json(path: str, data: dict = None, indent: int = 0):
    new_path = path
    if not path.endswith('.json'):
        new_path += '.json'

    if not file_exists(new_path):
        with open(new_path, 'w') as outfile:
            ujson.dump(data if data is not None else {},
                       outfile, indent=indent)


def delete_file(path: str):
    if file_exists(path):
        os.remove(path)
        return True

    return False


def delete_all_file(path: str):
    for file in os.listdir(path):
        delete_file(f'{path}/{file}')


def compress_to_zip(folder_path: str, zip_filename: str):
    shutil.make_archive(zip_filename, 'gztar', folder_path)


def extract_zip(zip_filename: str, extract_path: str):
    shutil.unpack_archive(zip_filename, extract_path, 'gztar')


class ID():
    '''Use ObjectId generation algorithm in `bson`
    Source: https://github.com/py-bson/bson
    Re-edit by Anh Khoa
    '''

    _inc = random.randint(0, 0xFFFFFF)
    _inc_lock = threading.Lock()

    def __init__(self, id=None) -> None:
        if id is None:
            self.__generate()
        elif isinstance(id, bytes) and len(id) == 12:
            self.__id = id
        else:
            self.__validate(id)

    def _fnv_1a_24(self, data, prime=0x01000193, offset_basis=0x811C9D):
        hash_value = offset_basis
        for byte in data:
            hash_value ^= byte
            hash_value *= prime
            hash_value &= 0xFFFFFF  # Giữ giá trị không vượt quá 24-bit
        return hash_value

    def _machine_bytes(self):
        return struct.pack("<I", self._fnv_1a_24(socket.gethostname().encode()))[:3]

    def __generate(self):
        # 4 bytes current time
        oid = struct.pack(">i", int(time.time()))

        # 3 bytes machine
        oid += self._machine_bytes()

        # 2 bytes pid
        oid += struct.pack(">H", os.getpid() % 0xFFFF)

        # 3 bytes inc
        with ID._inc_lock:
            oid += struct.pack(">i", ID._inc)[1:4]
            ID._inc = (ID._inc + 1) % 0xFFFFFF

        self.__id = oid

    def binary(self):
        return self.__id

    def is_valid(oid):
        if not oid:
            return False
        try:
            ID(oid)
            return True
        except Exception:
            return False

    def __validate(self, oid):
        if isinstance(oid, ID):
            self.__id = self.binary()
        elif isinstance(oid, str):
            if len(oid) == 24:
                try:
                    self.__id = bytes.fromhex(oid)
                except (TypeError, ValueError):
                    raise ValueError(oid)
            else:
                raise ValueError(oid)
        else:
            raise TypeError(
                f'id must be an instance of (bytes, {str.__name__}, ID), not {type(oid)}')

    def __getstate__(self):
        return self.__id

    def __setstate__(self, value):
        if isinstance(value, dict):
            oid = value["_ID__id"]
        else:
            oid = value
        if isinstance(oid, str):
            self.__id = oid.encode('latin-1')
        else:
            self.__id = oid

    def __str__(self):
        return binascii.hexlify(self.__id).decode()

    def __repr__(self):
        return "ID('%s')" % (str(self),)

    def __eq__(self, other):
        if isinstance(other, ID):
            return self.__id == other.binary()
        return NotImplemented

    def __ne__(self, other):
        if isinstance(other, ID):
            return self.__id != other.binary()
        return NotImplemented

    def __lt__(self, other):
        if isinstance(other, ID):
            return self.__id < other.binary()
        return NotImplemented

    def __le__(self, other):
        if isinstance(other, ID):
            return self.__id <= other.binary()
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, ID):
            return self.__id > other.binary()
        return NotImplemented

    def __ge__(self, other):
        if isinstance(other, ID):
            return self.__id >= other.binary()
        return NotImplemented

    def __hash__(self):
        return hash(self.__id)


class Collection():
    def __init__(self, path: str = None, indent: int = 2) -> None:
        self.path = path
        self.indent = indent

    def _get_files(self) -> list:
        if not dir_exists(self.path):
            return []

        return sorted(os.listdir(self.path), key=lambda x: ID(x[:-1 * len('.json')]))

    def _path(self, id: str | ID):
        '''return `path` from id'''
        if isinstance(id, ID):
            return f'{self.path}/{id.__str__()}.json'
        return f'{self.path}/{id}.json'

    def _read_file(self, path: str):
        with open(path, mode="r", encoding='utf-8') as file:
            json_obj = ujson.loads(file.read())
            file.close()
            return json_obj

    def _update_file(self, path: str, data: dict = {}):
        with lock:
            with open(path, mode="w", encoding='utf-8') as file:
                file.write(ujson.dumps(data, indent=self.indent))
                return True

    def _matches_condition(self, document: dict, field: str, value: dict):
        # Hàm này kiểm tra xem một điều kiện cụ thể có khớp với tài liệu không
        # if field not in document:
        #     return False

        if isinstance(value, dict):
            for operator, condition_value in value.items():
                if operator == "$in":
                    # Xử lý trường hợp của $in
                    if document.get(field, None) in condition_value:
                        return True
                elif operator == "$ne":
                    # Xử lý trường hợp của $ne
                    if document.get(field, None) != condition_value:
                        return True
                elif operator == "$regex":
                    # Xử lý trường hợp của $regex
                    import re
                    regex_pattern = re.compile(condition_value)
                    if regex_pattern.match(str(document.get(field, None))) is not None:
                        return True
                elif operator == "$gt":
                    # Xử lý trường hợp của $gt
                    if document.get(field, None) > condition_value:
                        return True
                elif operator == "$gte":
                    # Xử lý trường hợp của $gte
                    if document.get(field, None) >= condition_value:
                        return True
                elif operator == "$lt":
                    # Xử lý trường hợp của $lt
                    if document.get(field, None) < condition_value:
                        return True
                elif operator == "$lte":
                    # Xử lý trường hợp của $lte
                    if document.get(field, None) <= condition_value:
                        return True

        else:
            # Xử lý so sánh bình thường
            if document.get(field, None) == value:
                return True

        return False

    def _matches_filter(self, document: dict, filter_query: dict):
        # Hàm này kiểm tra xem một tài liệu có khớp với điều kiện lọc không
        for operator, conditions in filter_query.items():
            if operator == "$and":
                # Toán tử $and: tất cả các điều kiện phải đúng
                if all(self._matches_filter(document, condition) for condition in conditions):
                    return True
            elif operator == "$or":
                # Toán tử $or: ít nhất một điều kiện phải đúng
                if any(self._matches_filter(document, condition) for condition in conditions):
                    return True
            elif operator == "$not":
                # Toán tử $not: phải không khớp với tất cả các điều kiện
                if all(not self._matches_filter(document, condition) for condition in conditions):
                    return True
            else:
                # Xử lý các điều kiện khác (ví dụ: $in, so sánh bình thường)
                if self._matches_condition(document, operator, conditions):
                    return True

        return False

    def _sort(self, documents: list, sort: dict):
        if not isinstance(sort, dict):
            raise ValueError('`sort` must be of type dict!')

        if len(sort.items()) == 0:
            return documents

        sort_keys = [(key, order) for key, order in sort.items()]
        sort_keys.reverse()

        for document in documents:
            for key, order in sort_keys:
                if key in document:
                    reverse = order == -1
                    documents.sort(key=lambda x: x[key], reverse=reverse)

        return documents

    def get(self, filter: dict = {}, sort: dict = {}, limit: int = 0, skip: int = 0):
        results = []
        files = self._get_files()
        for file in files:
            data = self._read_file(f'{self.path}/{file}')

            if len(filter.items()) > 0:
                if self._matches_filter(data, filter):
                    results.append(data)
            else:
                results.append(data)

        results_sort = self._sort(results, sort)

        if not isinstance(limit, int):
            raise TypeError(
                f'limit must be of type int and not {type(limit)}')

        if not isinstance(skip, int):
            raise TypeError(
                f'skip must be of type int and not {type(skip)}')

        return results_sort[skip:len(results_sort)]

    def count(self):
        return len(self._get_files())

    def insert(self, data: dict):
        if not isinstance(data, dict):
            raise ValueError('`data` must be of type dict!')

        _id = ID()
        new_data = {'_id': _id.__str__(), **data}
        file_path = f'{self.path}/{str(_id)}.json'
        create_json(file_path, new_data, indent=self.indent)
        return new_data

    def update(self, filter: dict = {}, data: dict = None, replace: bool = False, create: bool = False):
        '''
        `create = True` create file if not exists
        `replace = True` replace data file
        '''
        if not isinstance(data, dict):
            raise ValueError('`data` must be of type dict!')

        datas_update = self.get(filter=filter)

        datas_updated = []

        for data_local in datas_update:
            if '_id' not in data_local:
                continue

            new_data_update = {'_id': data_local['_id']}

            if not replace:
                new_data_update = {**new_data_update, **data_local}

            new_data_update = {**new_data_update, **data}

            path = self._path(data_local['_id'])

            completed = False
            if file_exists(path):
                completed = self._update_file(path, data=new_data_update)
            else:
                if create:
                    new_data_create = {**data}
                    if new_data_create.get('_id', None) is not None:
                        new_data_create.pop('_id')
                    self.insert({**new_data_create})
                    completed = True

            if completed:
                datas_updated.append(data)

        return datas_updated

    def delete(self, filter: dict = {}):
        datas_delete = self.get(filter=filter)

        datas_deleted = []
        for data in datas_delete:
            result = delete_file(self._path(data['_id']))
            if result:
                datas_deleted.append(data)

        return datas_deleted

    def delete_all(self):
        delete_all_file(self.path)


class Database():
    def __init__(self, folder: str = "./__db/", indent: int = 2, hostname: str = "localhost", port = 8000) -> None:
        self.folder = folder[:-1] if folder.endswith('/') else folder
        self.indent = indent
        self.hostname = hostname
        self.port = port
        self._init_folder()
        self._collection_default = Collection(indent=indent)

    def _init_folder(self):
        os.makedirs(f'{self.folder}/datas/', exist_ok=True)

    def collection(self, name: str = "__default") -> Collection:
        path = f'{self.folder}/datas/{name}'
        os.makedirs(path, exist_ok=True)
        new_collection = copy.deepcopy(self._collection_default)
        new_collection.path = path
        return new_collection

    def backup(self, path_to: str = "./backup"):
        path_source = self.folder
        name = f'backup-{datetime.datetime.now().strftime("%d%m%Y-%H%M%S")}'
        path_file_backup = os.path.join(path_to, name)
        if dir_exists(path_source):
            os.makedirs(path_to, exist_ok=True)
            compress_to_zip(path_source, path_file_backup)

    def restore(self, path_file: str):
        extract_zip(path_file, self.folder)

    def run_socket(self):
        server = socketserver.TCPServer((self.hostname, self.port), DatabaseTCPHandler)
        server.serve_forever()

class DatabaseTCPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        print(f"Received data: {data}")