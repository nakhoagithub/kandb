from flask_socketio import emit
from ..server import socketio, database


@socketio.on("update")
def update(data):
    try:
        if not isinstance(data, dict):
            # fmt: off
            return emit("update", {"code": 400, "message": "'data' must be dict!"})
            # fmt: on

        if data.get("collection", None) is None:
            # fmt: off
            return emit("update", {"code": 400, "message": "'collection' is required!"})
            # fmt: on

        if data.get("data", None) is None:
            # fmt: off
            return emit("update", {"code": 400, "message": "'data' is required!"})
            # fmt: on

        if not isinstance(data['data'], dict):
            # fmt: off
            return emit("update", {"code": 400, "message": "'data' must be dict!"})
            # fmt: on

        if data.get("filter", None) is None:
            # fmt: off
            return emit("update", {"code": 400, "message": "'filter' is required!"})
            # fmt: on

        if not isinstance(data['filter'], dict):
            # fmt: off
            return emit("update", {"code": 400, "message": "'filter' must be dict!"})
            # fmt: on

        create = False
        if data.get("create", None) is not None and isinstance(data.get("create"), bool):
            create = data["create"]
        replace = False
        if data.get("replace", None) is not None and isinstance(data.get("replace"), bool):
            replace = data["replace"]

        # fmt: off
        result = database().collection(f"{data['collection']}").update(filter=data["filter"], data=data['data'], replace=replace, create=create)
        # fmt: on

        return emit("update", {"code": 200, "data": result})

    except Exception as e:
        return emit("update", {"code": 500, "error": str(e)})
