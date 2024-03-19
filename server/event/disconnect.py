
from ..server import database, socketio, request


@socketio.on("disconnect")
def handle_disconnect():
    try:
        db_user = database().collection("users", folder="admin")
        sid = request.sid
        # fmt: off
        db_user.update(filter={"sid": sid}, data={"sid": None, "isOnline": False})
        # fmt: on
        print("Client disconnected | %s" % (sid))
    except Exception as e:
        pass
