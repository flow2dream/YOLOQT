from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage
import cv2
from ultralytics import YOLO
import numpy as np
import time

from utils.merge_box import merge_boxes
from utils.draw_boxes import draw_boxes_on_image
from utils.convert import cv_to_qpixmap, qpixmap_to_cv

class ImageThread(QThread):
    # 需要六个模型串行处理
    send_image_signal = pyqtSignal(QPixmap)
    send_image_folder = pyqtSignal(QPixmap)

    get_image_signal = pyqtSignal(QPixmap)
    image = None
    model = None
    models = []
    _instance = None
    def __init__(self):
        super().__init__()
        # self.weight_path = path
        self.get_image_signal.connect(self.get_image)
        self.isFolder = False

    @staticmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance
    
    def get_image(self, image):
        self.image = image

    def setMode(self, mode=False):
        self.isFolder = mode

    def run(self):
            if self.image:
                image = qpixmap_to_cv(self.image)
                cls_dict = {}
                for model in self.models:
                    results = model.predict(image, conf=0.7, verbose=False)
                    names = model.names
                    for result in results:
                        for item in result.boxes.data.tolist():
                            class_id = item[5]
                            class_name = names[int(class_id)]
                            cls_dict[tuple(item[:4])] = class_name
                try:
                    merged_boxes = merge_boxes(cls_dict, threshold=50)
                    print(merged_boxes)
                    annotated_img = draw_boxes_on_image(image, merged_boxes)
                except IndexError:
                    annotated_img = image
                if self.isFolder:
                    self.send_image_folder.emit(cv_to_qpixmap(annotated_img))
                else:
                    self.send_image_signal.emit(cv_to_qpixmap(annotated_img))
                self.image = None
            
    def load_weights(self, models:list=None):
        # self.model = YOLO(self.weight_path)
        if self.models == []:
            self.models = models
            print("image model is loaded")
        else:
            return

        