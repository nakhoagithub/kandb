
import time
from server import sv

sv.run()
# users = sv.database.collection("users")

# def r1():
#     count = 1
#     while True:
#         update = users.update(
#             filter={"_id": "65f15e6fc016f34918bf20c6"}, data={"int": count})
#         if len(update) > 0:
#             count += 1
#         time.sleep(3)


# def r2():
#     data1 = True
#     while True:
#         update = users.update(
#             filter={"_id": "65f15e6fc016f34918bf20c7"}, data={"bool": data1})
#         if len(update) > 0:
#             if data1:
#                 data1 = False
#             else:
#                 data1 = True
#         time.sleep(3)


# def r3():
#     pass


# threading.Thread(target=r1, daemon=True).start()
# # threading.Thread(target=r2, daemon=True).start()
# # threading.Thread(target=r3, daemon=True).start()
# database.run_server()


while True:
    time.sleep(1)
