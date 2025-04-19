import os

# 定义标签文件所在的路径
label_path = r'dataset\hand-raise_write_use phone\labels\train'

# 初始化一个字典来存储类别及其数量
class_count = {}

# 遍历路径下的所有文件
for filename in os.listdir(label_path):
    if filename.endswith('.txt'):
        file_path = os.path.join(label_path, filename)
        with open(file_path, 'r') as file:
            # 逐行读取文件
            for line in file:
                # 获取类别编号
                class_id = int(line.split()[0])
                # 更新类别数量
                if class_id in class_count:
                    class_count[class_id] += 1
                else:
                    class_count[class_id] = 1

# 输出统计结果
print(f"类别数量: {len(class_count)}")
print("各类别的数量统计:")
for class_id, count in sorted(class_count.items()):
    print(f"类别 {class_id}: {count}")
