from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QWidget, QApplication
import sys
from PyQt5 import QtCore
class ImageButton(QWidget):
    def __init__(self, height):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setFixedHeight(int(height/3))
        self.setAutoFillBackground(True) 
        self.setStyleSheet("QWidget {background-color: red;}")
    def mousePressEvent(self, a0):
        print("123")
        return super().mousePressEvent(a0)
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ImageButton(300)
    widget.show()
    sys.exit(app.exec_())