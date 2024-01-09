import json

# Đọc file backup.json
with open("backup.json", "r") as file:
    data = json.load(file)

# Tạo một từ điển mới để lưu kết quả
new_data = {}

# Xử lý dữ liệu và cập nhật từ điển mới
for key, value in data.items():
    evaluation, count = value
    new_data[key] = evaluation / count

# Lưu kết quả vào file table.json
with open("table.json", "w") as file:
    json.dump(new_data, file, indent=4)

print("Đã cập nhật và lưu file table.json.")
