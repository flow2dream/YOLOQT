from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np

from utils.merge_box import merge_boxes
from utils.draw_boxes import draw_boxes_on_image

class MoniterStreamThread(QThread):

    frame_signal = pyqtSignal(np.ndarray)  # 定义一个信号，用于发送每一帧的图像

    def __init__(self):
        """
        initialize the thread
        """
        super().__init__()
        self.is_running = False
        self.open = False
        self.models = []
        self.capture:cv2.VideoCapture = None
        # self.finished.connect(self.finish)

    def run(self):
        """
        running the thread
        """
        while self.is_running:
            if not self.capture.isOpened():
                print("Error: Could not open video.")
                self.capture.release()
                break
            ret, frame = self.capture.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            if self.open:
                """
                open the video and start prediction
                """
                cls_dict = {}
                for model in self.models:
                    results = model.predict(frame, conf=0.7, verbose=False)
                    names = model.names
                    for result in results:
                        for item in result.boxes.data.tolist():
                            class_id = item[5]
                            class_name = names[int(class_id)]
                            cls_dict[tuple(item[:4])] = class_name
                try:
                    merged_boxes = merge_boxes(cls_dict, threshold=50)
                    annotated_img = draw_boxes_on_image(frame, merged_boxes)
                except:
                    annotated_img = frame
            else:
                """
                only open the video
                """
                annotated_img = frame
            self.frame_signal.emit(annotated_img)
        
    
    def start(self):
        """
        start the thread
        """
        if self.capture is None:
            self.capture = cv2.VideoCapture(0)
        
        self.is_running = True
        return super().start()
    
    def load_models(self, models:list=[]):
        """
        load models
        """
        self.models = models
    
    def start_predict(self):
        """
        start predict the video stream
        """
        self.is_running = True
        self.open = True

    def stop(self):
        """
        stop the video thread
        """
        self.is_running = False
        self.open = False
        self.wait()
        if self.capture:
            self.capture.release()
            self.capture = None
        