from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np

from utils.merge_box import merge_boxes
from utils.draw_boxes import draw_boxes_on_image
from core.ResultThread import VideoResultThread

class VideoStreamThread(QThread):
    frame_signal = pyqtSignal(np.ndarray)  # 定义一个信号，用于发送每一帧的图像

    def __init__(self, video_path:str=None):
        super().__init__()

        self.video_path = video_path
        self.capture = None
        self.models = []
        self.is_running = False
        self.is_continue = True
        self.result_thread = VideoResultThread()
        self.mode = "PREDICT"

    def run(self):
        if not self.video_path:
            self.capture = cv2.VideoCapture(self.video_path)
        if not self.capture.isOpened():
            print("Error: Could not open video.")
            self.capture.release()
            return None
        while self.is_running:
            if not self.is_continue:
                continue
            ret, frame = self.capture.read()
            if not ret:
                print("Error: Could not read frame.")
                break
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
                self.result_thread.get_info_signal.emit({
                    'type': 'video',
                    'path': self.video_path,
                    "mode": self.mode,
                    'result': {
                        'cls_dict': cls_dict
                    }
                })
                self.result_thread.start()
                annotated_img = draw_boxes_on_image(frame, merged_boxes)
            except IndexError:
                annotated_img = frame
            self.frame_signal.emit(annotated_img)
            self.mode = "PREDICT"
        self.result_thread.setMode("SAVE")
        self.result_thread.get_info_signal.emit({"mode": "SAVE"})
        self.result_thread.start()

    def getFirstFrame(self):
        if not self.capture:
            self.capture = cv2.VideoCapture(self.video_path)
        print(self.video_path)
        if not self.capture.isOpened():
            print("Error: Could not open video.")
            self.capture.release()
        ret, frame = self.capture.read()
        if ret:
            return frame
        else:
            return None

    def start(self):
        if not self.capture:
            self.capture = cv2.VideoCapture(self.video_path)
        if not self.capture.isOpened():
            print("Error: Could not open video.")
            return
        self.is_running = True
        self.is_continue = True
        super().start()
    
    def load_weights(self, models):
        self.models = models

    def stop(self):
        """
        stop the video stream and release resources.
        """
        self.is_running = False
        self.is_continue = True
    
    def another_video(self, video_path: str):
        """
        重新选择视频
        """
        self.video_path = video_path
        if self.capture:
            self.capture.release()
            self.capture = None

    def stop_frame(self):
        """
        top the stream
        """
        self.is_continue = False
    
    def continue_frame(self):
        self.is_continue = True
    
    def setMode(self, mode):
        """
        set the mode of the video stream
        """
        self.mode = mode