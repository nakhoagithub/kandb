import ujson
import os
import copy
import time
import struct
import socket
import random
import threading
import binascii

database = None


def dir_exists(path):
    return os.path.exists(path) and os.path.isdir(path)


def file_exists(path):
    return os.path.isfile(path)


def touch(path):
    if not file_exists(path):
        with open(path, 'w') as outfile:
            ujson.dump({}, outfile)


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
