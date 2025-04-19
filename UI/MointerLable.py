from PyQt5.QtWidgets import QLabel, QMenu, QAction
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
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
    def stop_frame(self):
        self.moniter_thread.stop_frame()
    def continue_frame(self):
        self.moniter_thread.continue_frame()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # 创建菜单栏
            menu = QMenu(self)
            # 创建菜单项
            action1 = QAction("暂停检测", self)
            action2 = QAction("继续检测", self)

            # 为菜单项添加触发事件
            action1.triggered.connect(self.stop_frame)
            action2.triggered.connect(self.continue_frame)

            # 将菜单项添加到菜单栏
            menu.addAction(action1)
            menu.addAction(action2)
            menu.setStyleSheet("""QMenu {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a2e, stop:1 #0f0c29);
    color: #e0e0ff;
    border: 1px solid #6a00ff;
    padding: 8px;
    font-family: 'Segoe UI', sans-serif;
    font-size: 12px;
}

QMenu::item {
    padding: 8px 30px 8px 20px;
    border: 1px solid transparent;
    background-color: transparent;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #3a1e6e, stop:1 #2a1459);
    border: 1px solid #8a2be2;
    color: #ffffff;
}

QMenu::icon {
    padding-left: 10px;
}

QMenu::separator {
    height: 1px;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #6a00ff, stop:1 #8a2be2);
    margin: 8px 0;
}

QMenu::item:disabled {
    color: #666699;
}""")
            # 在鼠标点击位置显示菜单栏
            menu.exec_(self.mapToGlobal(event.pos()))

