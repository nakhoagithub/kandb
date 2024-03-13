from services.extensions import api
from flask_restful import Api, Resource, request
from .middleware import authenticate, collection_exists, access_collection, access_collection_user
import json


class CollectionResource(Resource):
    @authenticate
    @access_collection
    def get(self, coll):
        try:
            args = request.args
            filter_arg = args.get("filter")
            filter_json = {}
            if filter_arg is not None:
                filter_json = json.loads(filter_arg)

            data = db()[coll].find(filter_json)
            results = [json.loads(dumps(i)) for i in data]
            return {"code": 200, "datas": results}, 200
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    @access_collection
    def post(self, coll):
        try:
            json_data: dict = request.get_json(force=True)

            datas = json_data.get("datas", [])
            if len(datas) == 0:
                return {"code": 403, "message": "'datas' is required"}, 403

            for data in datas:
                del data['_id']
                data = loads(json.dumps(data))
                db()[coll].insert_one(data)

            return {"code": 200}, 200
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    @access_collection
    def patch(self, coll):
        try:
            json_data: dict = request.get_json(force=True)

            datas = json_data.get("datas", [])
            if len(datas) == 0:
                return {"code": 403, "message": "'datas' is required"}, 403

            key_update = json_data.get("keyUpdate", None)
            if key_update is None:
                return {"code": 403, "message": "'keyUpdate' is required"}, 403

            for data in datas:
                data = loads(json.dumps(data))
                if key_update != "_id":
                    del data['_id']

                db()[coll].update_many(
                    {key_update: data[key_update]}, {"$set": {**data}}, upsert=True)

            return {"code": 200}, 200
        except Exception as e:
            print("Error", type(e), e)
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    @access_collection
    def put(self, coll):
        try:
            json_data: dict = request.get_json(force=True)

            datas = json_data.get("datas", [])
            if len(datas) == 0:
                return {"code": 403, "message": "'datas' is required"}, 403

            key_update = json_data.get("keyUpdate", None)
            if key_update is None:
                return {"code": 403, "message": "'keyUpdate' is required"}, 403

            for data in datas:
                data = loads(json.dumps(data))
                if key_update != "_id":
                    del data['_id']
                db()[coll].delete_many({key_update: data[key_update]})
                db()[coll].update_many(
                    {key_update: data[key_update]}, {"$set": {**data}}, upsert=True)

            return {"code": 200}, 200
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500

    @authenticate
    @access_collection
    @access_collection_user
    def delete(self, coll):
        try:
            json_data: dict = request.get_json(force=True)
            datas = json_data.get("datas", [])
            if len(datas) == 0:
                return {"code": 400, "message": "'datas' is required"}, 400

            key_delete = json_data.get("keyDelete", None)
            if key_delete is None:
                return {"code": 400, "message": "'keyDelete' is required"}, 400

            for data in datas:
                if key_delete == "_id":
                    data['_id'] = loads(json.dumps(data['_id']))
                db()[coll].delete_many({key_delete: data[key_delete]})

            return {"code": 200}, 200
        except Exception as e:
            print(e)
            return {"code": 500, "error": str(e)}, 500


def collection_routes(api: Api):
    api.add_resource(CollectionResource, "/collection/<coll>")
