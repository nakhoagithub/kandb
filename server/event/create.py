
from ..server import socketio, emit, database


@socketio.on("create")
def create(data):
    try:
        if not isinstance(data, dict):
            # fmt: off
            return emit("create", {"code": 400, "message": "'data' must be dict!"})
            # fmt: on

        if data.get("collection", None) is None:
            # fmt: off
            return emit("create", {"code": 400, "message": "'collection' is required!"})
            # fmt: on

        if data.get("data", None) is None:
            # fmt: off
            return emit("create", {"code": 400, "message": "'data' is required!"})
            # fmt: on

        if not isinstance(data['data'], dict):
            # fmt: off
            return emit("create", {"code": 400, "message": "'data' must be dict!"})
            # fmt: on

        # fmt: off
        result = database().collection(f"{data['collection']}").insert({**data['data']})
        # fmt: on

        return emit("create", {"code": 200, "data": result})

    except Exception as e:
        return emit("create", {"code": 500, "error": str(e)})
