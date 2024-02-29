import json
import bson
import sys

# Dữ liệu để biểu diễn
data = {
    "name": "John Doe",
    "age": 30,
    "is_student": False,
    "grades": [90, 85, 88]
}

# Biểu diễn dữ liệu bằng JSON
json_data = json.dumps(data, indent=2)
print(f"JSON size: {sys.getsizeof(json_data)} bytes")

# Biểu diễn dữ liệu bằng BSON
bson_data = bson.dumps(data)
print(f"BSON size: {sys.getsizeof(bson_data)} bytes")