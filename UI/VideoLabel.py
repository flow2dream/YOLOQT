from PyQt5.QtWidgets import QPushButton, QLabel, QMenu, QAction, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap
import cv2
import numpy as np
from core.VideoThread import VideoStreamThread

from utils.convert import cv_to_qpixmap

class VideoLabel(QLabel):
    _instance = None

    def __init__(self, parent=None, models=[], load_button:QPushButton=None):
        super().__init__(parent)
        self.parent = parent
        self.models = models
        self.video_thread:VideoStreamThread = VideoStreamThread("")
        self.load_button = load_button
        self.initMenu()

    def initMenu(self):
            # 创建菜单栏
            self.menu = QMenu(self)
            # 创建菜单项
            action1 = QAction("关闭", self)
            # action2 = QAction("重新播放", self)
            action3 = QAction("暂停播放", self)
            action4 = QAction("继续播放", self)
            # action5 = QAction("重新选择视频", self)

            # 为菜单项添加触发事件
            action1.triggered.connect(self.close_video)
            action3.triggered.connect(self.stop_video)
            action4.triggered.connect(self.continue_video)

            # 将菜单项添加到菜单栏
            self.menu.addAction(action1)
            self.menu.addAction(action3)
            self.menu.addAction(action4)
            self.menu.setStyleSheet("""QMenu {
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

    def select_video(self):
        video_path, _ = QFileDialog.getOpenFileName(self, "选择视频", "", "视频文件 (*.mp4 *.avi *.mov)")
        if video_path:
            if self.video_thread is not None:
                """
                重新选择视频
                """
                self.video_thread.another_video(video_path)
            else:
                """
                创建视频流
                """
                self.video_thread = VideoStreamThread(video_path)
            first_frame = self.video_thread.getFirstFrame()
            self.updateFrame(first_frame)

    def get_instance(cls, parent=None,  models=[], load_button:QPushButton=None):
        if not cls._instance:
            cls._instance = cls(parent, models, load_button)
        return cls._instance

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

    def start_predict(self):
        if self.video_thread.video_path == "":
            QMessageBox.warning(self, "Warning", "请先选择视频！")
            return
        if self.video_thread.models == []:
            QMessageBox.warning(self, "Warning", "请先加载模型！")
            return
        self.video_thread.frame_signal.connect(self.get_predict_frame)
        self.video_thread.finished.connect(self.close_video)
        self.video_thread.start()

    def get_predict_frame(self, image:QPixmap|np.ndarray):
        self.updateFrame(image)
    
    def load_models(self):
        self.video_thread.load_weights(self.models)
        self.load_button.setStyleSheet("color: green;")
        self.load_button.setText("加载成功")
        self.load_button.setEnabled(False)
        print("model is loaded successfully!")
    
    def close_video(self):

        # 停止视频线程
        self.video_thread.stop()

        self.video_thread.wait()
        self.video_thread.video_path = ""
        self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # 在鼠标点击位置显示菜单栏
            self.menu.exec_(self.mapToGlobal(event.pos()))
    
    def stop_video(self):
        if self.video_thread is not None:
            self.video_thread.stop_frame()
    
    def continue_video(self):
        if self.video_thread is not None:
            self.video_thread.continue_frame()
    
    def close_label(self):
        if self.video_thread is not None:
            self.video_thread.stop()
            self.video_thread.wait()
        self.hide()