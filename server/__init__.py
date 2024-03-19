
from .database import Database, Collection
from .server import Server
from .api import init_api
import config

db = Database(type_collection=config.type_data)
sv = Server(database=db)
init_api(sv)


def callback(type_callback: str, name: str, data: dict):
    if sv.connected:
        sv.socket.emit(f'{type_callback}.{name}', data)


sv.database._collection.callback = callback
