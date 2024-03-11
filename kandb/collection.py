from .version import __version__
import ujson
from bson import ObjectId
from .storage import JsonStorage
import os


class Collection(object):

    def __init__(self, name: str = "_default", storage: JsonStorage = None, auto_save=True):
        self.name = name
        self._storage = storage
        self._auto_save = auto_save
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

    def insert(self, data: dict, save=None):
        if not isinstance(data, dict):
            raise TypeError(f'data must be of type dict and not {type(data)}')

        _id = str(ObjectId())
        new_data = {**data, '_id': _id}
        self._datas.append(new_data)
        self._convert_datas_to_data()

        if save is not None:
            if save:
                self.save()
        elif self._auto_save:
            self.save()

    def save(self):
        with open(self._path, encoding='utf-8', mode='w') as f:
            json_object = ujson.dumps(self._data, indent=self._storage.indent)
            f.write(json_object)

    def _convert_datas_to_data(self):
        for item in self._datas:
            self._data[item['_id']] = {**item}

    def _matches_filter(self, document, filter_query: dict):
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

    def _matches_condition(self, document, field, value):
        # Hàm này kiểm tra xem một điều kiện cụ thể có khớp với tài liệu không
        if field not in document:
            return False

        if isinstance(value, dict):
            for operator, condition_value in value.items():
                if operator == "$in":
                    # Xử lý trường hợp của $in
                    if document[field] in condition_value:
                        return True
                elif operator == "$ne":
                    # Xử lý trường hợp của $ne
                    if document[field] != condition_value:
                        return True
                elif operator == "$regex":
                    # Xử lý trường hợp của $regex
                    import re
                    regex_pattern = re.compile(condition_value)
                    if regex_pattern.match(str(document[field])) is not None:
                        return True

        else:
            # Xử lý so sánh bình thường
            if document[field] == value:
                return True

        return False

    def _sort(self, documents: list, sort: dict):

        sort_keys = [(key, order) for key, order in sort.items()]
        sort_keys.reverse()

        for document in documents:
            for key, order in sort_keys:
                if key in document:
                    reverse = order == -1
                    documents.sort(key=lambda x: x[key], reverse=reverse)

        return documents

    def find(self, filter: dict = None, sort: dict = None):
        results = [[k, v] for k, v in self._data.items()]

        if filter is not None and not isinstance(filter, dict):
            raise TypeError(
                f'filter must be of type dict and not {type(filter)}')

        if filter is None:
            self._datas = [v for k, v in results]
        else:
            # filter
            new_results = []
            for document in [v for k, v in results]:
                if self._matches_filter(document, filter):
                    new_results.append(document)

            self._datas = new_results

        if isinstance(sort, dict):
            self._datas = self._sort(self._datas, sort)

        return self

    def skip(self, count: int = 0):

        if not isinstance(count, int):
            raise TypeError(
                f'count must be of type int and not {type(count)}')
        self._datas = self._datas[count:]
        return self

    def limit(self, count: int = 0):

        if not isinstance(count, int):
            raise TypeError(
                f'count must be of type int and not {type(count)}')

        self._datas = self._datas[:count]
        return self

    def update(self, filter: dict = None, data_update: dict = None):

        if data_update is None or not isinstance(data_update, dict):
            raise TypeError(
                f'data_update must be of type dict and not {type(data_update)}')

        datas_filter = self._datas
        if filter is not None:
            import copy
            collection = copy.deepcopy(self)
            collection.find(filter=filter)
            datas_filter = collection._datas

        datas = []
        for data_filter in datas_filter:
            _id = data_filter['_id']
            index = next((i for i, item in enumerate(
                self._datas) if item['_id'] == _id), -1)
            if index != -1:
                new_data_update = {**data_update}
                if new_data_update.get('_id') is not None:
                    new_data_update.pop('_id')
                self._datas[index] = {
                    **(self._datas[index]), **(new_data_update)}
                datas.append({**(self._datas[index]), **(new_data_update)})

        self._convert_datas_to_data()
        if self._auto_save:
            self.save()

        return {
            "filter": filter,
            "datas": datas
        }

    def replace(self, filter: dict = None, data_replace: dict = None):
        if data_replace is None or not isinstance(data_replace, dict):
            raise TypeError(
                f'data_replace must be of type dict and not {type(data_replace)}')

        datas_filter = self._datas
        if filter is not None:
            import copy
            collection = copy.deepcopy(self)
            collection.find(filter=filter)
            datas_filter = collection._datas

        datas = []
        for data_filter in datas_filter:
            _id = data_filter['_id']
            index = next((i for i, item in enumerate(
                self._datas) if item['_id'] == _id), -1)
            if index != -1:
                self._datas[index] = {
                    '_id': self._datas[index]['_id'], **data_replace}
                datas.append({
                    '_id': self._datas[index]['_id'], **data_replace})

        self._convert_datas_to_data()
        if self._auto_save:
            self.save()
        return {
            "filter": filter,
            "datas": datas
        }

    def delete(self, filter: dict = None):
        datas_filter = []
        if filter is not None:
            import copy
            collection = copy.deepcopy(self)
            collection.find(filter=filter)
            datas_filter = collection._datas

        deleted = 0
        datas_after_deleted = []
        for i in self._datas:
            if i['_id'] not in [i1['_id'] for i1 in datas_filter]:
                datas_after_deleted.append(i)
        self._datas = datas_after_deleted

        self._convert_datas_to_data()
        if self._auto_save:
            self.save()
        return {
            "filter": filter,
            "deleted": deleted
        }
