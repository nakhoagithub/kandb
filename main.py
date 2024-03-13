
import time
import threading
from kandb.database import Database

database = Database()
users = database.collection("users")

# users.delete_all()

# import random
# for i in range(50):
#     users.insert({"count": i, "data_random": random.randint(1, 0xFFFF)})

# users.update(data={"abc": 10}, filter={"count": {"$in": [0, 1, 2, 3, 4, 5]}})

# deleted = users.delete(filter={"count": {"$in": [10, 20]}})
# print(deleted)

datas = users.get()

# for data in datas:
#     print(data)

print(len(datas))

def r1():
    count = 1
    while True:
        # a.update(filter={"_id": "65eec6deb8942d2d385f681a"},
        #          data_update={"data": count})
        count += 1
        time.sleep(0.2)


def r2():
    data1 = True
    while True:
        # a.update(filter={"_id": "65eec6deb8942d2d385f681a"},
        #          data_update={"data1": data1})
        if data1:
            data1 = False
        else:
            data1 = True
        time.sleep(0.2)


def r3():
    while True:
        # print(a.find({'_id': "65eec6deb8942d2d385f681a"}).get())
        time.sleep(0.2)


# threading.Thread(target=r1, daemon=True).start()
# threading.Thread(target=r2, daemon=True).start()
# threading.Thread(target=r3, daemon=True).start()


# while True:
#     time.sleep(1)
