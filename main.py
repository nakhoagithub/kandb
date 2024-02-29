
from db import KanDB
import time

db = KanDB()

a = db.collection("users")


while 1:
    print(a.data(), a.name)
    time.sleep(1)
