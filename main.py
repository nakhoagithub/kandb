
from kandb import KanDB
import time

db = KanDB()

a = db.collection("users")

# f = a.find(filter={"_id": "65e17252b8942d1464643934"})
# a = a.where('_id', "65e17252b8942d1464643934")
print(a.get())

# for i in range(100000):
#     a.insert({"khoa": 1})

# a.save()
