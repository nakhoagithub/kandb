from flask import Request
from flask_restful import request, wraps, abort
import jwt
import config
import ujson

from ..database import db


# def auth_middleware(request: Request):
#     session = request.cookies.get("session")
#     payload = None
#     try:
#         payload = jwt.decode(
#             session, config.jwt_secret, algorithms=["HS256"])
#     except:
#         pass

#     if payload is not None:
#         user = db()['users'].find_one(
#             {"username": payload['username']})
#         if user is not None:
#             return True, json.loads(dumps(user))

#     return False, None


def authenticate(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        session = request.cookies.get("session")
        payload = None
        try:
            payload = jwt.decode(
                session, config.jwt_secret, algorithms=["HS256"])
        except:
            pass

        if payload is not None:
            # fmt: off
            users = db().collection("users", folder="admin").get(filter={"username": payload['username']})
            # fmt: on

            if len(users) == 0:
                abort(401, message="Unauthorized")
            else:
                user_data = ujson.loads(ujson.dumps(users[0]))
                del user_data['password']
                self.user = user_data

        return func(self, *args, **kwargs)
    return wrapper


def access_collection(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):

        # check collection
        coll = kwargs['coll']

        # check access
        access = True

        if not access:
            abort(403, message="Forbidden")

        return func(self, *args, **kwargs)
    return wrapper


def access_collection_user(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        access = True

        # check collection
        coll = kwargs['coll']
        method = request.method
        if coll == "users":
            if method == "DELETE":
                json_data: dict = request.get_json(force=True)
                datas = json_data.get("datas", [])
                if len(datas) == 0:
                    abort(400)

                key_delete = json_data.get("keyDelete", None)
                if key_delete is None:
                    abort(400)

                for data in datas:
                    if key_delete == "_id":
                        data['_id'] = ujson.loads(ujson.dumps(data['_id']))
                    user = db()[coll].find_one(
                        {key_delete: data[key_delete]})

                    if user is not None and user['username'] == "admin":
                        access = False

        if not access:
            abort(403, message="Forbidden")

        return func(self, *args, **kwargs)
    return wrapper


def collection_exists(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):

        # check collection
        coll = kwargs['coll']
        colls = [i['name'] for i in db().list_collections()]
        if coll not in colls:
            abort(404, message="Not Found")

        # check access
        access = True

        if not access:
            abort(403, message="Forbidden")

        return func(self, *args, **kwargs)
    return wrapper
