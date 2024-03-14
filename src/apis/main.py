from flask_restful import Api, Resource, request
from .middleware import authenticate
import bcrypt
import jwt
import config
import json
from datetime import datetime, timedelta

class LoginResource(Resource):
    def post(self):
        try:
            json_data = request.json
            username = json_data['username'] if "username" in json_data else None
            password = json_data['password'] if "password" in json_data else None
            users = db().collection("users", folder="auths").get(
                filter={"username": username})

            if len(users) == 0:
                return {"code": 404, "message": "Không tìm thấy người dùng"}, 401

            check = bcrypt.checkpw(bytes(password, "utf-8"),
                                   eval(users[0]['password']))

            if check is True:
                session = jwt.encode(
                    {"username": username}, config.jwt_secret, algorithm="HS256")

                current_time = datetime.utcnow()
                expires_time = current_time + timedelta(days=7)
                expires_str = expires_time.strftime(
                    '%a, %d %b %Y %H:%M:%S GMT')
                new_user = json.loads(json.dumps(users[0]))
                del new_user['password']
                return {"code": 200, "user": new_user}, 200, {"Set-Cookie": "session=%s; Max-Age=604800; Path=/; Expires=%s" % (session, expires_str)}

            return {"code": 401}, 401
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500


class AuthResource(Resource):
    @authenticate
    def get(self):
        try:
            if hasattr(self, "user"):
                return {"code": 200, "user": self.user}, 200
            return {"code": 401}, 401
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500


class RegisterResource(Resource):
    @authenticate
    def post(self):
        try:
            json = request.json
            name = json['name'] if "name" in json else None
            username = json['username'] if "username" in json else None
            password = json['password'] if "password" in json else None
            user = db()['users'].find_one({"username": username})

            if user is not None:
                return {"code": 403, "message": "Người dùng đã tồn tại"}, 403

            hashed = bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt())
            db()["users"].insert_one(
                {"name": name, "username": username, "password": str(hashed)})
            return {"code": 200}, 200

        except Exception as e:
            return {"code": 500, "error": str(e)}, 500


class UpdatePasswordResource(Resource):
    @authenticate
    def post(self):
        try:
            json = request.json
            username = json['username'] if "username" in json else None
            password = json['password'] if "password" in json else None

            hashed = bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt())
            db()["users"].update_one({"username": username}, {
                "$set": {"password": str(hashed)}})
            return {"code": 200}, 200

        except Exception as e:
            print(e)
            return {"code": 500, "error": str(e)}, 500


class LogoutResource(Resource):
    def get(self):
        try:
            return {"code": 200}, 200, {"Set-Cookie": "session=deleted; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Max-Age=0; Path=/;"}
        except Exception as e:
            return {"code": 500, "error": str(e)}, 500


def main_routes(api: Api):
    api.add_resource(LoginResource, "/login")
    api.add_resource(AuthResource, "/auth")
    api.add_resource(RegisterResource, "/register")
    api.add_resource(UpdatePasswordResource, "/update-password")
    api.add_resource(LogoutResource, "/logout")
