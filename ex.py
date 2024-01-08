import json

# Đường dẫn của tập tin chứa từ điển JSON
file_path = "full_edge_data.json"

# Đọc từ điển từ tập tin JSON
with open(file_path, 'r') as json_file:
    loaded_dict = json.load(json_file)

# Bây giờ loaded_dict chứa dữ liệu từ tập tin JSON
print(loaded_dict)
