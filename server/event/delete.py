from flask_socketio import emit
from ..server import socketio, database


@socketio.on("delete")
def delete(data):
    try:
        if not isinstance(data, dict):
            # fmt: off
            return emit("delete", {"code": 400, "message": "'data' must be dict!"})
            # fmt: on

        if data.get("collection", None) is None:
            # fmt: off
            return emit("delete", {"code": 400, "message": "'collection' is required!"})
            # fmt: on

        if data.get("filter", None) is None:
            # fmt: off
            return emit("delete", {"code": 400, "message": "'filter' is required!"})
            # fmt: on

        if not isinstance(data['filter'], dict):
            # fmt: off
            return emit("delete", {"code": 400, "message": "'filter' must be dict!"})
            # fmt: on

        # fmt: off
        result = database().collection(f"{data['collection']}").delete(filter=data["filter"])
        # fmt: on

        return emit("delete", {"code": 200, "data": result})

    except Exception as e:
        return emit("delete", {"code": 500, "error": str(e)})
