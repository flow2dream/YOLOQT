import cv2
from PyQt5.QtGui import QPixmap, QImage
import numpy as np

def cv_to_qpixmap(cv_image):
    # 获取图像的高度、宽度和通道数
    height, width, channel = cv_image.shape
    # 将 OpenCV 的 BGR 颜色空间转换为 RGB 颜色空间
    rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    # 创建 QImage 对象
    bytes_per_line = 3 * width
    q_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
    # 将 QImage 转换为 QPixmap
    qpixmap = QPixmap.fromImage(q_image)
    return qpixmap

def qpixmap_to_cv(qpixmap):
# 将 QPixmap 转换为 QImage
    qimage = qpixmap.toImage()
    # 获取图像的宽度、高度和字节数
    width = qimage.width()
    height = qimage.height()
    bytes_per_line = qimage.bytesPerLine()
    # 根据图像格式进行处理
    if qimage.format() == QImage.Format_RGB32:
        # 如果是 RGB32 格式，转换为 numpy 数组
        img = np.frombuffer(qimage.bits().asstring(height * bytes_per_line), dtype=np.uint8)
        img = img.reshape((height, width, 4))
        # 从 BGRA 转换为 BGR
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    elif qimage.format() == QImage.Format_RGB888:
        # 如果是 RGB888 格式，转换为 numpy 数组
        img = np.frombuffer(qimage.bits().asstring(height * bytes_per_line), dtype=np.uint8)
        img = img.reshape((height, width, 3))
        # 从 RGB 转换为 BGR
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    else:
        # 对于其他格式，暂时不处理，可根据需求扩展
        print("Unsupported image format.")
        return None
    return img