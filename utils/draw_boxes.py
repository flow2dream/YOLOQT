import cv2

color_map = {
    'bow head': (0, 255, 0),  # 绿色
    'turn head': (255, 0, 0),  # 蓝色
    'discuss': (0, 0, 255),  # 红色
    'talk': (255, 255, 0),  # 黄色
    'hand-raise': (0, 255, 255),  # 青色
    'write': (255, 0, 255),  # 洋红色
    'use phone': (128, 0, 128),  # 紫色
    'reading': (255, 165, 0),  # 橙色
    'lean table': (0, 128, 128),  # 深绿色
    'stand': (128, 128, 0),  # 橄榄色
}

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
    return image