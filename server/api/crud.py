from flask_restful import Resource, request
from .middleware import authenticate
import ujson
from ..server import database


class CollectionResource(Resource):
    @authenticate
    def get(self, collection):
        try:
            args = request.args
            filter_arg = args.get("filter")
            filter_json = {}
            if filter_arg is not None:
                filter_json = ujson.loads(filter_arg)

            results = database().collection(collection).get(filter=filter_json)

            return {"code": 200, "datas": results}, 200

        except Exception as e:
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    def post(self, collection):
        try:
            json_data: dict = request.get_json(force=True)

            datas = json_data.get("datas", [])
            if len(datas) == 0:
                return {"code": 403, "message": "'datas' is required"}, 403

            datas_result = []
            for data in datas:
                if not isinstance(data, dict):
                    return {"code": 400, "message": "Item in 'datas' must be dict"}, 400

                result = database().collection(collection).insert(data=data)
                datas_result.append(result)

            return {"code": 200, "datas": datas_result}, 200

        except Exception as e:
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    def patch(self, collection):
        try:
            json_data: dict = request.get_json(force=True)
            data_json = json_data.get("data", {})
            filter_json = json_data.get("filter", {})
            is_create = json_data.get("create", False)
            # fmt: off
            result = database().collection(collection).update(filter=filter_json, data=data_json, create=is_create)
            # fmt: on

            return {"code": 200, "datas": result}, 200

        except Exception as e:
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    def put(self, collection):
        try:
            json_data: dict = request.get_json(force=True)
            data_json = json_data.get("data", {})
            filter_json = json_data.get("filter", {})
            is_create = json_data.get("create", False)
            # fmt: off
            result = database().collection(collection).update(filter=filter_json, data=data_json, replace=True, create=is_create)
            # fmt: on

            return {"code": 200, "datas": result}, 200

        except Exception as e:
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    def delete(self, collection):
        try:
            json_data: dict = request.get_json(force=True)
            filter_json = json_data.get("filter", {})
            # fmt: off
            result = database().collection(collection).delete(filter=filter_json)
            # fmt: on

            return {"code": 200, "datas": result}, 200
        except Exception as e:
            print(e)
            return {"code": 500, "error": str(e)}, 500
