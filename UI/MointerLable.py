from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap
import numpy as np
from core.MoniterThread import MoniterStreamThread
from utils.convert import cv_to_qpixmap


class Moniter(QLabel):
    _instance = None

    def __init__(self, parent=None, models=[], load_button=None):
        super().__init__(parent)
        self.parent = parent
        self.models = models
        self.load_button = load_button
        self.moniter_thread:MoniterStreamThread = MoniterStreamThread()
        self.moniter_thread.frame_signal.connect(self.updateFrame)
        self.moniter_thread.finished.connect(self.close_capture)

    def updateFrame(self, frame:np.ndarray|QPixmap):
        if isinstance(frame, np.ndarray):
            self.image = cv_to_qpixmap(frame)
        else:
            self.image = frame
        self.setFixedSize(self.parent.width(),
                                self.parent.height())
        try:
            self.image = self.image.scaled(self.width(),
                        int(self.width() * self.image.height() / self.image.width()))
        except ZeroDivisionError as e:
            print("Error: ", e)
        self.setPixmap(self.image)
        self.show()


    def get_instance(cls, parent=None, models=[], load_button=None):
        if not cls._instance:
            cls._instance = cls(parent, models, load_button)
        return cls._instance
    
    def start_predict(self):
        """
        start predict the video stream
        """
        print("start predict")
        self.moniter_thread.start_predict()

    def load_models(self):
        """
        load models
        """
        print("load models success")
        self.moniter_thread.load_models(self.models)
        self.load_button.setStyleSheet("color: green;")
        self.load_button.setText("加载成功")
        self.load_button.setEnabled(False)

    def open_moniter(self):
        """
        open the moniter stream
        """
        print("open moniter stream")
        self.moniter_thread.start()
    def close_label(self):
        """
        close the moniter stream
        """
        print("close moniter stream")
        self.moniter_thread.stop()
        # self.hide()
    
    def close_capture(self):
        """
        close the capture stream
        """
        # self.moniter_thread.close_capture()
        self.hide()

