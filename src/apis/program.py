from flask_restful import Api, Resource, request
from bson import ObjectId
from .middleware import authenticate


class ProgramResource(Resource):
    @authenticate
    def post(self, id, func):
        try:
            if func == "run":
                run_program(ObjectId(id))
                return {"code": 200}, 200

            if func == "stop":
                stop_program(ObjectId(id))
                return {"code": 200}, 200

            return {"code": 404}, 404
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500


class ProgramSequentialResource(Resource):
    @authenticate
    def post(self, id, func):
        try:
            if func == "reset":
                reset_sequential(ObjectId(id))
                return {"code": 200}, 200
            return {"code": 404}, 404
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500


def program_routes(api: Api):
    api.add_resource(ProgramResource,
                     "/program/<id>/<func>")
    api.add_resource(ProgramSequentialResource,
                     "/program-sequential/<id>/<func>")
