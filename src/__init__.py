import threading
import config
from flask import Flask
from gevent.pywsgi import WSGIServer
from .routes import api
from .events import socketio

from .database import Database
socket_connected = False

def read_callback(name: str, data: dict):
    global socket_connected
    if socket_connected:
        event = f'read.{name}'
        socketio.emit(event, data)


def create_callback(name: str, data: dict):
    global socket_connected
    if socket_connected:
        event = f'create.{name}'
        socketio.emit(event, data)


def update_callback(name: str, data: dict):
    global socket_connected
    if socket_connected:
        event = f'update.{name}'
        socketio.emit(event, data)


def delete_callback(name: str, data: dict):
    global socket_connected
    if socket_connected:
        event = f'delete.{name}'
        socketio.emit(event, data)


db = Database(
    read_callback=read_callback,
    create_callback=create_callback,
    update_callback=update_callback,
    delete_callback=delete_callback
)


def _create_flask():
    app = Flask(__name__)
    api.init_app(app)
    socketio.init_app(app)
    return app


def _run_socket():
    http_server = WSGIServer(
        (config.host, config.port), _create_flask(), log=None)
    print("API | IP: %s | Port: %s" % (config.host, config.port))
    global socket_connected
    socket_connected = True
    http_server.serve_forever()


def run_server():
    threading.Thread(target=_run_socket, daemon=True).start()
