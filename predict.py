import cv2

from ultralytics import YOLO
import numpy as np

color_map = {
    'read': (0, 255, 0),  # 绿色
    'write': (255, 0, 0),  # 蓝色
    'discuss': (0, 0, 255),  # 红色
    'stand': (255, 255, 0)  # 黄色
}

def predictVideo(model, video_path):
    cap = cv2.VideoCapture(video_path)

    # Loop through the video frames
    while cap.isOpened():
        # Read a frame from the video
        success, frame = cap.read()

        if success:
            # Run YOLO inference on the frame
            # results = model(frame)
            results = model.predict(frame, conf=0.7)
            print(results)
            # Visualize the results on the frame
            annotated_frame = results[0].plot()

            # Display the annotated frame
            cv2.imshow("YOLO Inference", annotated_frame)

            # Break the loop if 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        else:
            # Break the loop if the end of the video is reached
            break

    # Release the video capture object and close the display window
    cap.release()
    cv2.destroyAllWindows()


class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x != root_y:
            if self.rank[root_x] > self.rank[root_y]:
                self.parent[root_y] = root_x
            elif self.rank[root_x] < self.rank[root_y]:
                self.parent[root_x] = root_y
            else:
                self.parent[root_y] = root_x
                self.rank[root_x] += 1

def calculate_centers(boxes):
    boxes = np.array(boxes)
    centers = np.column_stack(((boxes[:, 0] + boxes[:, 2]) / 2, (boxes[:, 1] + boxes[:, 3]) / 2))
    return centers

def calculate_distances(centers):
    num_centers = len(centers)
    distances = np.zeros((num_centers, num_centers))
    for i in range(num_centers):
        for j in range(i + 1, num_centers):
            distances[i, j] = np.linalg.norm(centers[i] - centers[j])
            distances[j, i] = distances[i, j]
    return distances

def merge_boxes(box_dict, threshold=5):
    boxes = list(box_dict.keys())
    labels = list(box_dict.values())
    num_boxes = len(boxes)

    # 计算中心点
    centers = calculate_centers(boxes)

    # 计算距离矩阵
    distances = calculate_distances(centers)

    # 使用并查集合并框
    uf = UnionFind(num_boxes)
    for i in range(num_boxes):
        for j in range(i + 1, num_boxes):
            if distances[i, j] < threshold:
                uf.union(i, j)

    # 合并框和标签
    merged_boxes = {}
    for i in range(num_boxes):
        root = uf.find(i)
        if root not in merged_boxes:
            merged_boxes[root] = {'boxes': [boxes[i]], 'labels': [labels[i]]}
        else:
            merged_boxes[root]['boxes'].append(boxes[i])
            merged_boxes[root]['labels'].append(labels[i])

    final_merged_dict = {}
    for group in merged_boxes.values():
        group_boxes = group['boxes']
        group_labels = group['labels']
        min_x1 = min([box[0] for box in group_boxes])
        min_y1 = min([box[1] for box in group_boxes])
        max_x2 = max([box[2] for box in group_boxes])
        max_y2 = max([box[3] for box in group_boxes])
        merged_box = (min_x1, min_y1, max_x2, max_y2)
        merged_label = ', '.join(set(group_labels))
        final_merged_dict[merged_box] = merged_label

    return final_merged_dict

def draw_boxes_on_image(image, box_dict):

    for box, label in box_dict.items():
        x1, y1, x2, y2 = [int(coord) for coord in box]
        # 根据标签获取颜色，如果标签不在映射中，使用默认颜色（白色）
        color = color_map.get(label.split(', ')[0], (0, 0, 0))
        # 绘制矩形框
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        # 绘制标签
        # 设置字体大小和厚度
        font_size = 0.6
        font_thickness = 1

        # 获取文本尺寸
        (text_width, text_height), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_size, font_thickness)

        # 计算背景矩形的坐标
        background_x1 = x1
        background_y1 = y1 - 10 - 5  # 增加一些额外的空间
        background_x2 = x1 + text_width + 5
        background_y2 = y1

        # 绘制背景矩形
        cv2.rectangle(image, (background_x1, background_y1), (background_x2, background_y2), color, -1)

        # 绘制标签
        cv2.putText(image, label, (x1, y1), cv2.FONT_HERSHEY_SIMPLEX, font_size, (0, 0, 0), font_thickness)

    # 显示图像
    cv2.imshow('Merged Boxes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def predictImage(model, img_path):
    # Read the image
    img = cv2.imread(img_path)

    # Run YOLO inference on the image
    # results = model.predict(img, conf=0.7)
    cls_dict = {}
    cls_map = {
        0: "Disscuss",
        1: "Handrise",
        2: "read",
        3: "write",
        4: "stand",
        5: "talk"
    }
    cls_weight = {
        r"runs\Discuss\Discuss\weights\best.pt",
        r"runs\Handrise-Read-write\Handrise-Read-write\weights\best.pt",
        r"runs\Stand\Stand\weights\best.pt",
        r"runs\Talk\Talk\weights\best.pt"
    }
    models = []
    for path in cls_weight:
        models.append(YOLO(path))
    for model in models:
        names = model.names
        results = model.predict(img, conf=0.7)
        for result in results:
            for item in result.boxes.data.tolist():
                x1, y1, x2, y2, conf, class_id = item
                class_name = names[int(class_id)]
                cls_dict[tuple(item[:4])] = class_name
        # img = results[0].plot()
    print(cls_dict)
    # Merge boxes based on distance threshold
    merged_boxes = merge_boxes(cls_dict)
    draw_boxes_on_image(img, merged_boxes)
    print(merged_boxes)
    # annotated_img = img

    # # Display the annotated image
    # cv2.imshow("YOLO Inference", annotated_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
if __name__ == '__main__':
    # Load the YOLO model
    model = YOLO(r"runs\Discuss\Discuss\weights\best.pt")

    # Open the video file
    video_path = r"D:\bishe\code\class_detector\raw_data\234903191-1-16.mp4"
    img_path = r"data\SCB5-Discuss-2024-9-17\images\train\6_000752.jpg"
    predictImage(model, img_path)
    # predictVideo(model, video_path)
