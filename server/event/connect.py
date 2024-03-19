
from ..server import database, socketio, request, disconnect
import config
import jwt


@socketio.on("connect")
def handle_connect():
    try:
        db_user = database().collection("users", folder="admin")
        session = request.headers.get("Session")
        sid = request.sid
        payload = None
        try:
            payload = jwt.decode(
                session, config.jwt_secret, algorithms=["HS256"])
        except:
            pass

        if payload is not None:
            # fmt: off
            db_user.update(filter={"username": payload["username"]}, data={"sid": sid, "isOnline": True})
            # fmt: on
            print(f"Client connected | {sid} | {payload}")
        else:
            disconnect(sid)

    except Exception as e:
        disconnect(sid)
