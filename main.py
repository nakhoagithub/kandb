
import time
from server import sv
import datetime
import threading

sv.run()
db_server = sv.database.collection("server")

def r1():
    sv_data = db_server.get()
    while True:
        if len(sv_data) > 0:
            db_server.update(filter={"_id": sv_data[0]['_id']}, data={
                "time": datetime.datetime.now().timestamp()})
        time.sleep(1)


# threading.Thread(target=r1, daemon=True).start()


while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        print("Server stoped!")
        break
    except Exception as e:
        pass
