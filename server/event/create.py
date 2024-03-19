
from ..server import socketio, emit


@socketio.on("create")
def create(data):
    try:
        if isinstance(data, dict):

            if data.get("type", None) is None:
                emit("create", {"code": 400, "message": "'type' is required!"})

    except Exception as e:
        print(e)
