from flask_socketio import SocketIO, disconnect
from flask_restful import Api
from flask import request

socketio = SocketIO(async_mode="gevent")

api = Api(prefix="/api")
