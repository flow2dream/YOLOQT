import numpy as np

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
