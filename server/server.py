from flask import Flask, request
from flask_restful import Api, Resource
from flask_socketio import SocketIO, disconnect
from gevent.pywsgi import WSGIServer
import threading
import config
import bcrypt

from .database import Database


app = Flask(__name__)
socketio = SocketIO(async_mode="gevent", cors_allowed_origins="*")
api = Api()
db: Database = None


def database():
    global db
    return db


class Server():
    def __init__(
        self,
        database: Database,
        host=config.host,
        port=config.port,
        prefix_api="/api",
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
        self._init_server_info()

    def _init_user_default(self):
        user = self.database.collection("users")
        count_user = user.count()
        if count_user == 0:
            hashed = bcrypt.hashpw(
                bytes(self.password, "utf-8"), bcrypt.gensalt())
            # fmt: off
            master_user = {"username": self.username, "password": str(hashed), "state": "master"}
            # fmt: on
            user.insert(master_user)

    def _init_server_info(self):
        db_server = self.database.collection("server")
        datas = db_server.get()
        if len(datas) == 0:
            db_server.insert({
                "host": self.host,
                "port": self.port
            })
        else:
            self.host = datas[0]["host"] if "host" in datas[0] else config.host
            self.port = datas[0]["port"] if "port" in datas[0] else config.port

    def _create_flask(self):
        api.init_app(app)
        socketio.init_app(app)
        return app

    def _run(self):
        http_server = WSGIServer(
            (self.host, self.port), self._create_flask(), log=None)
        print(f"Running on IP: {self.host} | Port: {self.port}")
        self.connected = True
        http_server.serve_forever()

    def run(self):
        threading.Thread(target=self._run, daemon=True).start()
