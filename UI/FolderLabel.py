from PyQt5.QtWidgets import QPushButton, QLabel, QMenu, QAction, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.ImageThread import ImageThread

from utils.select_image import get_image_paths

IMAGE_EXTENSION = ['.jpg', '.jpeg', '.png']

class FolderLabel(QLabel):
    _instance = None
    
    def __init__(self, parent=None, selectImage:QPushButton=None, selectFolder:QPushButton=None, models=[]):
        super().__init__(parent)
        self.imageThread = ImageThread.get_instance(cls=ImageThread)
        self.selectImage = selectImage
        self.selectFolder = selectFolder
        self.models = models
        self.index = -1
        self.parent = parent
        self.image = None
    
    @staticmethod
    def get_instance(cls, 
                     parent=None, 
                     selectImage:QPushButton=None, 
                     selectFolder:QPushButton=None,
                     models=[]):
        if not cls._instance:
            cls._instance = cls(parent, selectImage, selectFolder, models)
        return cls._instance
    
    def showCurrentImage(self, image:QPixmap=None):
        self.setFixedSize(self.parent.width(),
                        self.parent.height())
        if image:
            self.images[self.index] = image
            self.image = image
        else:
            self.image = QPixmap(self.images[self.index])
        self.image = self.image.scaled(self.width(),
            int(self.width() * self.image.height() / self.image.width()))   
        self.setPixmap(self.image)
        self.show()
    
    def select_Folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "./")
        if folder_path:
            self.images = get_image_paths(folder_path, IMAGE_EXTENSION)
            self.index = 0
            self.showCurrentImage()
    
    def getCurrentImage(self):
        if self.image:
            return self.image
        return None

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # 创建菜单栏
            menu = QMenu(self)
            # 创建菜单项
            action1 = QAction("关闭", self)
            action2 = QAction("上一张", self)
            action3 = QAction("下一张", self)

            # 为菜单项添加触发事件
            action1.triggered.connect(self.close)
            action2.triggered.connect(self.next_image)
            action3.triggered.connect(self.pre_image)

            # 将菜单项添加到菜单栏
            menu.addAction(action1)
            menu.addAction(action2)
            menu.addAction(action3)
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
    
    def close(self):
        self.selectImage.show()
        self.selectFolder.show()
        super().close()

    def next_image(self):
        self.index = (self.index + 1) % len(self.images)
        self.showCurrentImage()

    def pre_image(self):
        self.index = (self.index - 1) % len(self.images)
        self.showCurrentImage()
    
    def load_weights(self):
        self.imageThread.load_weights(self.models)
        self.imageThread.start()
        print("load weight success")

    def get_predict_image(self, image:QPixmap):
        self.showCurrentImage(image)