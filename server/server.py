from flask import Flask, request
from flask_restful import Api, Resource
from flask_socketio import SocketIO, disconnect
from gevent.pywsgi import WSGIServer
import threading
import jwt
import config
import bcrypt

from .database import Database


app = Flask(__name__)
socketio = SocketIO(async_mode="gevent")
api = Api()
db: Database = None


class Server():
    def __init__(
        self,
        database: Database,
        host="0.0.0.0",
        port=3000,
        prefix_api='/api',
        username_default=config.username_default,
        password_default=config.password_default
    ) -> None:
        global db
        db = database
        self.database = database
        self.host = host
        self.port = port
        self.connected = False
        api.prefix = prefix_api
        self.username = username_default
        self.password = password_default
        self.api = api
        self.socket = socketio
        self.request = request
        self.disconnect = disconnect
        self._init_user_default()

    def _init_user_default(self):
        user = self.database.collection("users", folder="admin")
        count_user = user.count()
        if count_user == 0:
            hashed = bcrypt.hashpw(
                bytes(self.password, "utf-8"), bcrypt.gensalt())
            # fmt: off
            master_user = {"username": self.username, "password": str(hashed), "state": "master"}
            # fmt: on
            user.insert(master_user)

    def _init_port_default(self):
        db_server = self.database.collection("port", folder="server")

    def create_api(resource: Resource, urls: str):
        api.add_resource(resource=resource, urls=urls)

    def _create_flask(self):
        api.init_app(app)
        socketio.init_app(app)
        return app

    def _run(self):
        http_server = WSGIServer(
            (self.host, self.port), self._create_flask(), log=None)
        print(f'API | IP: {self.host} | Port: {self.port}')
        self.connected = True
        http_server.serve_forever()

    def run(self):
        threading.Thread(target=self._run, daemon=True).start()


@socketio.on("connect")
def handle_connect():
    try:
        db_user = db.collection("users", folder="admin")
        session = request.headers.get("Session")
        sid = request.sid
        payload = None
        try:
            payload = jwt.decode(
                session, config.jwt_secret, algorithms=["HS256"])
        except:
            pass

        if payload is not None:
            # fmt: off
            db_user.update(filter={"username": payload["username"]}, data={"sid": sid, "isOnline": True})
            # fmt: on
            print(f'Client connected | {sid} | {payload}')
        else:
            disconnect(sid)

    except Exception as e:
        disconnect(sid)


@socketio.on("disconnect")
def handle_disconnect():
    try:
        db_user = db.collection("users", folder="admin")
        sid = request.sid
        # fmt: off
        db_user.update(filter={"sid": sid}, data={"sid": None, "isOnline": False})
        # fmt: on
        print("Client disconnected | %s" % (sid))
    except Exception as e:
        pass


@socketio.on("control")
def handle_device(data):
    try:
        sid = request.sid
        id = data["id"] if "id" in data else None
        control = data["control"] if "control" in data else None
        if control is not None:
            # control_device(id=id, control=control, access_auto=False, sid=sid)
            pass
    except Exception as e:
        pass
