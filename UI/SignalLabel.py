from PyQt5.QtWidgets import QPushButton, QLabel, QMenu, QAction, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from core.ImageThread import ImageThread

class SignalLabel(QLabel):
    _instance = None
    
    def __init__(self, parent=None, 
                 selectImage:QPushButton=None, 
                 selectFolder:QPushButton=None, 
                 models=[]):
        super().__init__(parent)
        self.imageThread = ImageThread.get_instance(cls=ImageThread)
        self.models = models
        self.selectImage = selectImage
        self.selectFolder = selectFolder
        self.parent = parent
        self.image = None
    
    @staticmethod
    def get_instance(cls, parent=None, 
                     selectImage:QPushButton=None, 
                     selectFolder:QPushButton=None, 
                     models=None):
        if not cls._instance:
            cls._instance = cls(parent, selectImage, selectFolder, models)
        return cls._instance

    def getCurrentImage(self):
        if self.image:
            return self.image
        return None

    def showCurrentImage(self, image:str|QPixmap):
        if isinstance(image, str):
            self.image = QPixmap(image)
        else:
            self.image = image
        self.setFixedSize(self.parent.width(),
                                self.parent.height())
        self.image = self.image.scaled(self.width(),
                    int(self.width() * self.image.height() / self.image.width()))
        self.setPixmap(self.image)
        self.show()

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            # 创建菜单栏
            menu = QMenu(self)
            # 创建菜单项
            action1 = QAction("关闭", self)
            action2 = QAction("更换图片", self)

            # 为菜单项添加触发事件
            action1.triggered.connect(self.close)
            action2.triggered.connect(self.select_image)

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
    
    def close(self):
        self.selectImage.show()
        self.selectFolder.show()
        self.image = None
        super().close()

    def select_image(self):
        self.selectImage.click()

    def get_predict_image(self, image:QPixmap):
        self.showCurrentImage(image)

    def load_weight(self):
        self.imageThread.load_weights(self.models)
        self.imageThread.start()
        print("load weight success")

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图片", "./", "Image Files(*.jpg *.png *.jpeg)")
        if file_path:
            self.selectImage.hide()
            self.selectFolder.hide()
            self.showCurrentImage(file_path)
    
    def get_model_stauts(self):
        return not self.imageThread.models == []
    