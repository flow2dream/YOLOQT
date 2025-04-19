import sys, os
from PyQt5.QtWidgets import QApplication, QStackedWidget, QMainWindow, QVBoxLayout,  QPushButton, QFileDialog, QLabel, QMessageBox
from ultralytics import YOLO
from PyQt5.QtGui import QPixmap
from PyQt5 import uic, QtCore
import logging

from UI.SignalLabel import SignalLabel
from UI.FolderLabel import FolderLabel
from core.VideoThread import VideoDetectionThread
from core.ImageThread import ImageThread
from utils.select_image import get_image_paths

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
    # imageThread = ImageThread()
    VideoThread = VideoDetectionThread()

    model_paths = [
        r"runs\Discuss\Discuss\weights\best.pt",
        r"runs\Handrise-Read-write\Handrise-Read-write\weights\best.pt",
        r"runs\Stand\Stand\weights\best.pt",
        r"runs\Talk\Talk\weights\best.pt"
    ]
    
    def load_models(self):
        self.models = []
        for path in self.model_paths:
            self.models.append(YOLO(path))

    def __init__(self):
        super().__init__()
        self.initOption()
        self.initDisplay()
        # self.imageThread.send_image_signal.connect(self.acceptImage)
        self.VideoThread.frame_signal.connect(self.getVideoImage)
        
        self.load_models()


    def initOption(self):
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
        self.image_load.clicked.connect(SignalLabel.load_weight)

        self.image_start:QPushButton = self.image_start
        self.image_start.clicked.connect(self.startPredictImage)
        self.image_save:QPushButton = self.image_save
        self.image_load.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.image_start.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.image_save.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.image_button.clicked.connect(self.showImage)
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
        self.video_button.clicked.connect(self.showVideo)
        # init button of moniter image detetcion
        self.moniter_button:QPushButton = self.moniter_button
        self.moniter_startVideo:QPushButton = self.moniter_startVideo
        self.moniter_startVideo.clicked.connect(self.showMonitorVideo)
        self.moniter_load:QPushButton = self.moniter_load
        self.moniter_load.clicked.connect(self.load_moniter_model)
        self.moniter_start:QPushButton = self.moniter_start
        self.moniter_end:QPushButton = self.moniter_end
        self.moniter_end.clicked.connect(self.videoStop)
        self.moniter_startVideo.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.moniter_load.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.moniter_start.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.moniter_end.setFixedSize(int(self.parentWidth*0.9), int(self.parentHeight*0.6))
        self.moniter_startVideo.hide()
        self.moniter_load.hide()
        self.moniter_start.hide()
        self.moniter_end.hide()
        self.moniter_button.clicked.connect(self.showMoniter)
        self.buttons = {
            "image": [self.image_load, self.image_start, self.image_save, self.image_save],
            "video": [self.video_load, self.video_start, self.video_end, self.video_save],
            "moniter": [self.moniter_startVideo, self.moniter_load, self.moniter_start, self.moniter_end]
        }

    def load_moniter_model(self):
        # 加载模型
        self.VideoThread.load_weights(self.models)

    def initDisplay(self):
        self.stack_display:QStackedWidget = self.stack_display
        self.stack_display.setCurrentIndex(0)
        self.select_image:QPushButton = self.select_image
        self.select_image.clicked.connect(self.selectImage) # 绑定选择图片按钮
        self.select_foler:QPushButton = self.select_foler
        self.select_foler.clicked.connect(self.selectFolder) # 绑定选择图片文件夹按钮
        self.select_video:QPushButton = self.select_video
        self.select_video.clicked.connect(self.selectVideo)
        self.start_video:QPushButton = self.start_video
        self.start_video.clicked.connect(self.showMonitorVideo)

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
    
    def selectImage(self):
        """
        选择图片界面
        """
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "./", "Image Files(*.jpg *.png *.jpeg)")
        if file_path:
            self.select_image.hide()
            self.select_foler.hide()
            self.signal_label = SignalLabel.get_instance(SignalLabel,self.stack_display.widget(0), self.select_image, self.select_foler, file_path)

    def selectFolder(self):
        """
        选择图片文件夹
        """
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if folder_path:
            paths = get_image_paths(folder_path, IMAGE_EXTENSION)
            self.folder_label = FolderLabel.get_instance(FolderLabel,self.stack_display.widget(0), self.select_image, self.select_foler, paths)


    def showMonitorVideo(self):
        self.start_video.hide()
        self.VideoLabel = QLabel(self.stack_display.widget(2))
        self.VideoLabel.setFixedSize(self.stack_display.width(),
                                     self.stack_display.height())
        self.VideoLabel.show()
        self.VideoThread.start()
        
    def getVideoImage(self, image:QPixmap):
        image = image.scaled(
            self.VideoLabel.width(),
            int(self.VideoLabel.width() * image.height() / image.width())
        )
        
        self.VideoLabel.setPixmap(image)

    def videoStop(self):
        self.VideoThread.start_detetct = False
        self.VideoThread.stopThread()
        self.start_video.show()
        self.VideoLabel.close()

    # def load_image_model(self):
    #     self.imageThread.load_weights(self.models)
    #     self.imageThread.start()
        
    def startPredictImage(self):
        try:
            self.image = self.signal_label.getCurrentImage()
        except Exception as e:
            self.image = self.folder_label.getCurrentImage()
        finally:
            if self.imageThread.models == []:
                logger.info("请先加载模型")
                QMessageBox.information(self, '提示', '请先加载模型')
                return
            if self.image:
                self.imageThread.get_image_signal.emit(self.image)
            else:
                QMessageBox.information(self, '提示', '请先选择图片')
                return
    
    # def acceptImage(self, image:QPixmap):
    #     try:
    #         self.signal_label.showCurrentImage(image)
    #     except:
    #         self.folder_label.showCurrentImage(image)
    #     # self.image = image
    #     # self.label.setPixmap(self.image)

    def selectVideo(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择视频", "./", "Video Files(*.mp4 *.avi *.mkv *.flv)")
        if file_path:
            self.select_video.hide()
            self.start_video.show()
            self.video_label = QLabel(self.stack_display.widget(1))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageDetectionUI()
    window.show()
    sys.exit(app.exec_())