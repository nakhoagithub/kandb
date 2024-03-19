
from .database import Database, Collection
from .server import Server
from .api import init_api
from .event import *

db = Database(collection_types=config.collection_types)
sv = Server(database=db)
init_api(sv)


def create_callback(name: str, data: dict):
    if sv.connected:
        sv.socket.emit(f"create.{name}", data)

def update_callback(name: str, data: dict):
    if sv.connected:
        sv.socket.emit(f"update.{name}", data)


def delete_callback(name: str, data: dict):
    if sv.connected:
        sv.socket.emit(f"delete.{name}", data)


sv.database._collection.create_callback = create_callback
sv.database._collection.update_callback = update_callback
sv.database._collection.delete_callback = delete_callback
