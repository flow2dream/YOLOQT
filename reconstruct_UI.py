import sys, os
from PyQt5.QtWidgets import (QApplication, QStackedWidget, 
                             QMainWindow, QVBoxLayout,  QPushButton, 
                             QLabel, QMessageBox, QWidget, QHBoxLayout)
from ultralytics import YOLO
from PyQt5.QtGui import QIcon
from PyQt5 import uic
from PyQt5.QtCore import Qt
import logging

from UI.SignalLabel import SignalLabel
from UI.FolderLabel import FolderLabel
from UI.VideoLabel import VideoLabel
from UI.MointerLable import Moniter
from core.ImageThread import ImageThread

from UI.myButtons import CyberButton
from utils.myImage import myImage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
# 设置日志输出格式
formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler.setFormatter(formatter)
# 将处理器添加到自定义日志记录器
logger.addHandler(handler)

IMAGE_EXTENSION = ['.jpg', '.jpeg', '.png']


class ImageDetectionUI(QMainWindow):
    imageButtonShow = True
    VideoButtonsShow = False
    MoniterButtonsShow = False
    image = None

    model_paths = [
        r"retrain_runs\bow head_turn head\bow head_turn head\weights\best.pt",
        r"retrain_runs\discuss_talk\discuss_talk\weights\best.pt",
        r"retrain_runs\hand-raise_write_use phone\hand-raise_write_use phone\weights\best.pt",
        # r"runs\Talk\Talk\weights\best.pt"
    ]
    def __init__(self):
        super().__init__()
        self.load_models()
        self.imageThread:ImageThread = ImageThread.get_instance(cls=ImageThread)
        self.initOptionUI()
        self.initDisplayUI()
        
        self.signal_label:SignalLabel = SignalLabel.get_instance(cls=SignalLabel, 
                                                     root=self,
                                                     parent=self.stack_display.widget(0), 
                                                     selectImage=self.select_image, 
                                                     selectFolder=self.select_foler,
                                                     models=self.models)
        self.folder_label:FolderLabel = FolderLabel.get_instance(cls=FolderLabel,
                                                     parent=self.stack_display.widget(0),
                                                     selectImage=self.select_image,
                                                     selectFolder=self.select_foler)
        self.video_label:VideoLabel = VideoLabel.get_instance(cls=VideoLabel, 
                                                   parent=self.stack_display.widget(1),  
                                                   models=self.models,
                                                   load_button=self.video_load)
        self.moniter_label:Moniter = Moniter.get_instance(cls=Moniter,
                                                  parent=self.stack_display.widget(2),
                                                  models=self.models,
                                                  load_button=self.moniter_load)
        self.initConnection()

    def load_models(self):
        self.models = []
        for path in self.model_paths:
            self.models.append(YOLO(path))
    
    def load_image_model(self):
        self.imageThread.load_weights(self.models)
        self.imageThread.start()
        self.image_load.setStyleSheet("color: green;")
        self.image_load.setText("加载成功")
        self.image_load.setEnabled(False)

    def start_image_folder(self):
        self.imageThread.setMode(True)
        result = self.folder_label.getCurrentImage()
        image = myImage(result["path"], result["image"])
        self.imageThread.get_image_signal.emit(image)
        self.imageThread.start()

    def start_image_signal(self):
        self.imageThread.setMode(False)
        image = self.signal_label.getCurrentImage()
        image = myImage(image["path"], image["image"])
        self.imageThread.get_image_signal.emit(image)
        self.imageThread.start()

    def start_image(self):
        if self.imageThread.models == []:
            QMessageBox.warning(self, "Warning", "请先加载模型！")
            return
        if self.signal_label.getCurrentImage() is not None:
            self.start_image_signal()
        elif self.folder_label.getCurrentImage() is not None:
            self.start_image_folder()
        else:
            QMessageBox.warning(self, "Warning", "请先选择图片或文件夹！")
            return
    
    def initOptionUI(self):
        self.setWindowTitle("课堂行为检测")
        uic.loadUi("UI/mainWindow.ui", self)
        self.displayLayout: QVBoxLayout = self.display_layout
        self.optionLayout: QVBoxLayout = self.option_layout
        # init button of image detection
        self.image_button:QPushButton = self.image_button
        self.parentWidth = self.image_button.width()
        self.parentHeight = self.image_button.height()
        """
        replace the button of bar
        """
        optionLayout = self.findChild(QVBoxLayout, "option_layout")
        old_button = self.findChild(QPushButton, "image_button")
        index = optionLayout.indexOf(old_button)
        optionLayout.removeWidget(old_button)
        old_button.deleteLater()
        self.image_button = CyberButton("图片检测", self.option, icon_path="assets/image_detect.png")
        optionLayout.insertWidget(index, self.image_button, alignment=Qt.AlignHCenter)
        self.image_button.setFixedSize(self.parentWidth, self.parentHeight)

        optionLayout = self.findChild(QVBoxLayout, "option_layout")
        old_button = self.findChild(QPushButton, "video_button")
        index = optionLayout.indexOf(old_button)
        optionLayout.removeWidget(old_button)
        old_button.deleteLater()
        self.video_button = CyberButton("视频检测", self.option, icon_path="assets/video_detect.png")
        optionLayout.insertWidget(index, self.video_button, alignment=Qt.AlignHCenter)
        self.video_button.setFixedSize(self.parentWidth, self.parentHeight)

        optionLayout = self.findChild(QVBoxLayout, "option_layout")
        old_button = self.findChild(QPushButton, "moniter_button")
        index = optionLayout.indexOf(old_button)
        optionLayout.removeWidget(old_button)
        old_button.deleteLater()
        self.moniter_button = CyberButton("实时监测", self.option, icon_path="assets/moniter_detect.png")
        optionLayout.insertWidget(index, self.moniter_button, alignment=Qt.AlignHCenter)
        self.moniter_button.setFixedSize(self.parentWidth, self.parentHeight)



        self.image_load:QPushButton = self.image_load
        self.image_start:QPushButton = self.image_start # 图片开始检测按钮
        self.image_save:QPushButton = self.image_save # 图片保存按钮
        self.image_load.setFixedSize(int(self.parentWidth*0.8), int(self.parentHeight*0.9))
        self.image_start.setFixedSize(int(self.parentWidth*0.8), int(self.parentHeight*0.9))
        self.image_save.setFixedSize(int(self.parentWidth*0.8), int(self.parentHeight*0.9))

        # init button of video detection
        self.video_button:QPushButton = self.video_button
        self.video_load:QPushButton = self.video_load
        self.video_start:QPushButton = self.video_start
        self.video_end:QPushButton = self.video_end
        self.video_load.setFixedSize(int(self.parentWidth*0.8), int(self.parentHeight*0.9))
        self.video_start.setFixedSize(int(self.parentWidth*0.8), int(self.parentHeight*0.9))
        self.video_end.setFixedSize(int(self.parentWidth*0.8), int(self.parentHeight*0.9))
        self.video_load.hide()
        self.video_start.hide()
        self.video_end.hide()

        # init button of moniter image detetcion
        self.moniter_button:QPushButton = self.moniter_button

        self.moniter_load:QPushButton = self.moniter_load

        self.moniter_start:QPushButton = self.moniter_start
        self.moniter_end:QPushButton = self.moniter_end
        
        self.moniter_load.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.9))
        self.moniter_start.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.9))
        self.moniter_end.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.9))
        self.moniter_load.hide()
        self.moniter_start.hide()
        self.moniter_end.hide()
        self.buttons = {
            "image": [self.image_load, self.image_start, self.image_save],
            "video": [self.video_load, self.video_start, self.video_end],
            "moniter": [self.moniter_load, self.moniter_start, self.moniter_end]
        }
    
    def initDisplayUI(self):
        self.stack_display:QStackedWidget = self.stack_display
        self.stack_display.setCurrentIndex(0)
        self.select_image:QPushButton = self.select_image
        self.select_image.setIcon(QIcon("assets/image.png"))
        self.select_foler:QPushButton = self.select_foler
        self.select_foler.setIcon(QIcon("assets/folder.png"))
        self.select_video:QPushButton = self.select_video
        self.select_video.setIcon(QIcon("assets/video.png"))
        self.start_video:QPushButton = self.start_video
        self.start_video.setIcon(QIcon("assets/moniter.png"))

    def initConnection(self):
        self.imageThread.send_image_signal.connect(self.signal_label.get_predict_image) # 发送图片信号
        self.imageThread.send_image_folder.connect(self.folder_label.get_predict_image) # 发送图片信号

        self.image_button.clicked.connect(self.showImage) # 显示图片检测界面
        self.select_image.clicked.connect(self.signal_label.select_image) # 选择图片
        self.select_foler.clicked.connect(self.folder_label.select_Folder) # 选择文件夹
        self.image_load.clicked.connect(self.load_image_model) # 加载图片权重
        self.image_start.clicked.connect(self.start_image)
        self.image_save.clicked.connect(self.imageThread.result_thread.start)

        self.select_video.clicked.connect(self.video_label.select_video) # 选择视频
        self.video_load.clicked.connect(self.video_label.load_models) # 视频流模型加载权重
        self.video_start.clicked.connect(self.video_label.start_predict) # 开始视频流
        self.video_end.clicked.connect(self.video_label.close_video) # 关闭视频流
        self.video_button.clicked.connect(self.showVideo) # 显示视频检测界面
        
        self.moniter_load.clicked.connect(self.moniter_label.load_models) # 加载监控模型权重
        self.start_video.clicked.connect(self.moniter_label.open_moniter) # 打开监控
        self.moniter_start.clicked.connect(self.moniter_label.start_predict) # 开始监控检测
        self.moniter_end.clicked.connect(self.moniter_label.close_label) # 关闭监控检测
        self.moniter_button.clicked.connect(self.showMoniter) # 显示监控检测界面

    def showImage(self):
        if self.imageButtonShow:
            self.imageButtonShow = False
            self.VideoButtonsShow = False
            self.MoniterButtonsShow = False
            for vi, mo, im in zip(self.buttons["video"], self.buttons["moniter"], self.buttons["image"]):
                try:
                    vi.hide()
                    mo.hide()
                    im.hide()
                except:
                    pass
        else:
            self.imageButtonShow = True
            self.VideoButtonsShow = False
            self.MoniterButtonsShow = False
            self.stack_display.setCurrentIndex(0)
            for vi, mo, im in zip(self.buttons["video"], self.buttons["moniter"], self.buttons["image"]):
                try:
                    vi.hide()
                    mo.hide()
                    im.show()
                except:
                    pass

    def showVideo(self):
        if self.VideoButtonsShow:
            self.VideoButtonsShow = False
            self.imageButtonShow = False
            self.MoniterButtonsShow = False
            for im, mo, vi in zip(self.buttons["image"], self.buttons["moniter"], self.buttons["video"]):
                try:
                    im.hide()
                    mo.hide()
                    vi.hide()
                except:
                    pass
        else:
            self.VideoButtonsShow = True
            self.imageButtonShow = False
            self.MoniterButtonsShow = False
            self.stack_display.setCurrentIndex(1)
            for im, mo, vi in zip(self.buttons["image"], self.buttons["moniter"], self.buttons["video"]):
                try:
                    im.hide()
                    mo.hide()
                    vi.show()
                except:
                    pass

    def showMoniter(self):
        if self.MoniterButtonsShow:
            self.MoniterButtonsShow = False
            self.imageButtonShow = False
            self.VideoButtonsShow = False
            for im, vi, mo in zip(self.buttons["image"], self.buttons["video"], self.buttons["moniter"]):
                try:
                    im.hide()
                    vi.hide()
                    mo.hide()
                except:
                    pass
        else:
            self.MoniterButtonsShow = True
            self.imageButtonShow = False
            self.VideoButtonsShow = False
            self.stack_display.setCurrentIndex(2)
            for im, vi, mo in zip(self.buttons["image"], self.buttons["video"], self.buttons["moniter"]):
                try:
                    im.hide()
                    vi.hide()
                    mo.show()
                except:
                    pass

class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # 主窗口引用
        self.setup_ui()

    def setup_ui(self):
        # 标题栏布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)  # 移除边距

        # 标题文本
        self.title_label = QLabel("YOLO教室行为检测系统")
        self.title_label.setStyleSheet("color: white; font-size: 20px;padding: 8px 8px;")
        # self.title_label.setStyleSheet("")
        self.setFixedHeight(35)
        # 最小化、关闭按钮
        self.btn_min = QPushButton("—")
        self.btn_close = QPushButton("×")

        # 设置按钮样式（使用 QSS）
        button_style = """
            QPushButton {
                background-color: transparent;
                color: white;
                border: none;
                font-size: 20px;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
            QPushButton#close:hover {
                background-color: #ff0000;
            }
        """
        self.btn_close.setObjectName("close")  # 单独标识关闭按钮
        self.setStyleSheet(button_style)

        # 添加到布局
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.btn_min)
        layout.addWidget(self.btn_close)

        # 连接按钮信号
        self.btn_min.clicked.connect(self.parent.showMinimized)
        self.btn_close.clicked.connect(self.parent.close)
    
    def mousePressEvent(self, event):
        """鼠标按下时记录起始位置"""
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.globalPos()  # 获取全局坐标
    def mouseMoveEvent(self, event):
        """鼠标移动时更新窗口位置"""
        if self.drag_start_position:
            delta = event.globalPos() - self.drag_start_position  # 计算移动偏移
            self.parent.move(self.parent.pos() + delta)          # 更新窗口位置
            self.drag_start_position = event.globalPos()         # 更新起始位置
    def mouseReleaseEvent(self, event):
        """鼠标释放时清空记录"""
        self.drag_start_position = None
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageDetectionUI()
    window.setWindowFlags(Qt.FramelessWindowHint)
    titlebar = CustomTitleBar(window)
    window.setMenuWidget(titlebar)  # 设置自定义标题栏
    window.show()
    sys.exit(app.exec_())