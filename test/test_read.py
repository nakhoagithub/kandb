import ujson
import os
import time
from functools import lru_cache

@lru_cache(maxsize=None)
def read_json_files(directory):
    start_time = time.time()

    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            file_path = os.path.join(directory, filename)
            with open(file_path, encoding="utf-8", mode='r') as file:
                data = ujson.load(file)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f'Total time taken: {elapsed_time} seconds')


# Thay thế 'path/to/your/directory' bằng đường dẫn thư mục chứa các file JSON của bạn
read_json_files('test/data_test/')
