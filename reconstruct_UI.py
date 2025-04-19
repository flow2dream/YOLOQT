import sys, os
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMainWindow, QVBoxLayout,  QPushButton, QFileDialog, QLabel, QMessageBox
from ultralytics import YOLO
from PyQt5.QtGui import QPixmap
from PyQt5 import uic, QtCore
import logging

from UI.SignalLabel import SignalLabel
from UI.FolderLabel import FolderLabel
from UI.VideoLabel import VideoLabel
from UI.MointerLable import Moniter
from core.VideoThread import VideoStreamThread
from core.ImageThread import ImageThread


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
    # VideoThread = VideoDetectionThread()

    model_paths = [
        r"runs\Discuss\Discuss\weights\best.pt",
        r"runs\Handrise-Read-write\Handrise-Read-write\weights\best.pt",
        r"runs\Stand\Stand\weights\best.pt",
        r"runs\Talk\Talk\weights\best.pt"
    ]
    def __init__(self):
        super().__init__()
        self.load_models()
        self.imageThread = ImageThread.get_instance(cls=ImageThread)
        self.initOptionUI()
        self.initDisplayUI()
        
        self.signal_label = SignalLabel.get_instance(cls=SignalLabel, 
                                                     parent=self.stack_display.widget(0), 
                                                     selectImage=self.select_image, 
                                                     selectFolder=self.select_foler,
                                                     models=self.models)
        self.folder_label = FolderLabel.get_instance(cls=FolderLabel,
                                                     parent=self.stack_display.widget(0),
                                                     selectImage=self.select_image,
                                                     selectFolder=self.select_foler)
        self.video_label = VideoLabel.get_instance(cls=VideoLabel, 
                                                   parent=self.stack_display.widget(1), 
                                                #    selectVideo=self.select_video, 
                                                   models=self.models)
        self.moniter_label = Moniter.get_instance(cls=Moniter,
                                                  parent=self.stack_display.widget(2),
                                                  models=self.models)
        self.initConnection()
        
    def load_models(self):
        self.models = []
        for path in self.model_paths:
            self.models.append(YOLO(path))
    
    def load_image_model(self):
        self.imageThread.load_weights(self.models)
        self.imageThread.start()

    def start_image_folder(self):
        self.imageThread.setMode(True)
        image = self.folder_label.getCurrentImage()
        if image is None:
            return
        self.imageThread.get_image_signal.emit(image)

    def start_image_signal(self):
        self.imageThread.start(False)
        image = self.signal_label.getCurrentImage()
        if image is None:
            return
        self.imageThread.get_image_signal.emit(image)

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
        self.image_load:QPushButton = self.image_load
        # self.image_load.clicked.connect(self.load_image_model)
        # self.image_load.clicked.connect(SignalLabel.load_weight)

        self.image_start:QPushButton = self.image_start # 图片开始检测按钮
        self.image_save:QPushButton = self.image_save # 图片保存按钮
        self.image_load.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.image_start.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.image_save.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))

        # init button of video detection
        self.video_button:QPushButton = self.video_button
        self.video_load:QPushButton = self.video_load
        self.video_start:QPushButton = self.video_start
        self.video_end:QPushButton = self.video_end
        self.video_save:QPushButton = self.video_save
        self.video_load.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.video_start.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.video_end.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.video_save.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.video_load.hide()
        self.video_start.hide()
        self.video_end.hide()
        self.video_save.hide()

        # init button of moniter image detetcion
        self.moniter_button:QPushButton = self.moniter_button

        self.moniter_load:QPushButton = self.moniter_load

        self.moniter_start:QPushButton = self.moniter_start
        self.moniter_end:QPushButton = self.moniter_end
        
        self.moniter_load.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.moniter_start.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.moniter_end.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        # self.moniter_startVideo.hide()
        self.moniter_load.hide()
        self.moniter_start.hide()
        self.moniter_end.hide()
        self.buttons = {
            "image": [self.image_load, self.image_start, self.image_save, self.image_save],
            "video": [self.video_load, self.video_start, self.video_end, self.video_save],
            "moniter": [self.moniter_load, self.moniter_start, self.moniter_end]
        }
    
    def initDisplayUI(self):
        self.stack_display:QStackedWidget = self.stack_display
        self.stack_display.setCurrentIndex(0)
        self.select_image:QPushButton = self.select_image
        self.select_foler:QPushButton = self.select_foler
        self.select_video:QPushButton = self.select_video
        self.start_video:QPushButton = self.start_video

    def initConnection(self):
        self.imageThread.send_image_signal.connect(self.signal_label.get_predict_image) # 发送图片信号
        self.imageThread.send_image_folder.connect(self.folder_label.get_predict_image) # 发送图片信号

        self.image_button.clicked.connect(self.showImage) # 显示图片检测界面
        self.select_image.clicked.connect(self.signal_label.select_image) # 选择图片
        self.select_foler.clicked.connect(self.folder_label.select_Folder) # 选择文件夹
        self.image_load.clicked.connect(self.load_image_model) # 加载图片权重
        self.image_start.clicked.connect(self.start_image)

        self.select_video.clicked.connect(self.video_label.select_video) # 选择视频
        self.video_load.clicked.connect(self.video_label.load_models) # 视频流模型加载权重
        self.video_start.clicked.connect(self.video_label.start_predict) # 开始视频流
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageDetectionUI()
    window.show()
    sys.exit(app.exec_())