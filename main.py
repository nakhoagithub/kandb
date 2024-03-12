
import time
import threading
from kandb import KanDB, db

database = KanDB()

a = db().collection("users")

begin = time.time()

for i in range(100):
    a.insert({"data": i}, save=False)
a.save()
end = time.time()
print(end - begin)

print(len(a.get()))



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
threading.Thread(target=r3, daemon=True).start()


# while True:
#     time.sleep(1)
