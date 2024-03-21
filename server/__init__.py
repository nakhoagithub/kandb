
from .database import Database, Collection
from .server import Server
from .api import init_api
from .event import *

db = Database(collection_types=config.collection_types)
sv = Server(database=db)
init_api(sv)


def callback(name: str, data: dict):
    if sv.connected:
        sv.socket.emit(f"on.{name}", data)


sv.database._collection.create_callback = callback
sv.database._collection.update_callback = callback
sv.database._collection.delete_callback = callback
