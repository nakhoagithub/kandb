from .extensions import socketio, request, disconnect
import jwt
import config


@socketio.on("connect")
def handle_connect():
    try:
        session = request.headers.get("Session")
        sid = request.sid
        payload = None
        try:
            payload = jwt.decode(
                session, config.jwt_secret, algorithms=["HS256"])
        except:
            pass

        payload = "1"

        if payload is not None:
            # db()["users"].update_one({"username": payload["username"]}, {
            #     "$set": {"sid": sid, "isOnline": True}})

            print("Client connected | %s" % (sid))
        else:
            disconnect(sid)

    except Exception as e:
        pass


@socketio.on("disconnect")
def handle_disconnect():
    try:
        sid = request.sid
        # db()["users"].update_one({"sid": sid}, {
        #     "$set": {"sid": None, "isOnline": False}})
        print("Client disconnected | %s" % (sid))
    except Exception as e:
        pass


@socketio.on("control")
def handle_device(data):
    try:
        sid = request.sid
        id = data["id"] if "id" in data else None
        control = data["control"] if "control" in data else None
        if control is not None:
            # control_device(id=id, control=control, access_auto=False, sid=sid)
            pass
    except Exception as e:
        pass
