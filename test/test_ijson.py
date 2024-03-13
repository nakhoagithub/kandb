import ijson
import json


with open('large_data.json', 'r') as file:
    # Sử dụng ijson để tạo một đối tượng JSON parser
    parser = ijson.parse(file)

    # Mở tệp JSON để ghi (hoặc thay thế bằng stdout, file, socket, ...)
    with open('output_data.json', 'w') as output_file:
        # Đối tượng để ghi vào tệp JSON mới
        output_data = {"new_key": "new_value"}

        # Xử lý từng sự kiện JSON một cách tuần tự
        for prefix, event, value in parser:
            # Xử lý sự kiện JSON ở đây
            if event == 'map_key' and value == 'your_target_key':
                # Thực hiện thay đổi giá trị hoặc thêm dữ liệu mới
                output_data["new_key_2"] = "new_value_2"

        # Ghi dữ liệu vào tệp JSON mới
        json.dump(output_data, output_file, indent=2)
