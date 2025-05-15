from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QLineEdit, 
                             QApplication, QMessageBox)
from PyQt5.QtGui import QFont, QPalette, QColor, QLinearGradient
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QPushButton

from core.AnalyizeThread import AnalyizeThread


from logging import getLogger
logger = getLogger()
POSITIVE = ['discuss', 'hand-raise', 'write', 'read']
NEGATIVE = ['bow head', 'turn head', 'talk','use phone', 'lean table', 'stand']

class AnalyizeDataUI(QWidget):
    def __init__(self, json_path=None):
        super().__init__()
        self.initUI()
        self.setWindowTitle("数据分析")
        self.resize(800, 600)
        self.setFixedSize(800, 600)  # 固定窗口大小
        self.setStyle()  # 添加样式设置
        logger.info("数据分析界面初始化完成")
        self.board = AnalyizeThread(json_path)
        self.board.send_data_signal.connect(self.get_result)
        self.board.start()

    def get_result(self, result):
        print(result.get_result())
        self.result:dict = result.get_result()
        self.set_table_data(result.get_result().get('result'))
        self.set_file_name(result.get_result().get('file_name'))

    def setStyle(self):
        # 设置窗口背景渐变
        palette = self.palette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(50, 50, 60))  # 调整为更亮的深蓝灰
        gradient.setColorAt(1, QColor(30, 30, 40))  # 调整为更亮的深黑
        palette.setBrush(QPalette.Window, gradient)
        self.setPalette(palette)

        # 设置全局字体
        font = QFont("Segoe UI", 10)
        self.setFont(font)

        # 设置文件名显示样式
        self.file_label.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.file_name.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
                border: 1px solid #00FFFF;
                border-radius: 5px;
                padding: 5px;
            }
        """)

        # 更新表格样式
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.05);
                color: #00FFFF;
                border: 1px solid #00FFFF;
                border-radius: 5px;
                font-size: 14px;  /* 增大表格字体 */
            }
            QTableWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(0, 255, 255, 0.2);
                border-right: 1px solid rgba(0, 255, 255, 0.2);
                background-color: rgba(30, 30, 40, 0.8);
                font-size: 16px;  /* 增大item字体 */
                font-weight: bold;
                text-align: center;  /* 文字居中 */
            }
            QTableWidget::item:selected {
                background-color: rgba(0, 255, 255, 0.5);
                color: #FFFFFF;
            }
            QTableWidget::item:last {
                border-bottom: none;
            }
            QTableWidget::item:right {
                border-right: none;
            }
        """)

        # 设置结果标签样式
        self.result_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 255, 255, 0.1);
                color: #00FFFF;
                border: 1px solid #00FFFF;
                border-radius: 5px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
        """)

        # 修改水平行标题样式
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: rgba(30, 30, 40, 0.8);  /* 使用更深的背景色 */
                color: #FFFFFF;  /* 修改文字颜色为白色 */
                border: 1px solid rgba(0, 255, 255, 0.2);
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
            }
        """)

        # 设置总人数输入框样式
        self.total_label.setStyleSheet("""
            QLabel {
                color: #00FFFF;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.total_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                color: #FFFFFF;
                border: 1px solid #00FFFF;
                border-radius: 5px;
                padding: 5px;
                font-size: 14px;
            }
        """)

    def initUI(self):
        # 主布局
        layout = QVBoxLayout()

        # 文件名显示
        self.file_label = QLabel("当前文件：")
        self.file_name = QLineEdit()
        self.file_name.setReadOnly(True)
        layout.addWidget(self.file_label)
        layout.addWidget(self.file_name)

        # 添加总人数输入框
        self.total_label = QLabel("总人数：")
        self.total_input = QLineEdit()
        self.total_input.setPlaceholderText("请输入总人数")
        layout.addWidget(self.total_label)
        layout.addWidget(self.total_input)

        # 表格
        self.table = QTableWidget(10, 2)
        self.table.horizontalHeader().setVisible(True)
        
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(True)
        self.table.setSizeAdjustPolicy(QTableWidget.AdjustToContents)
        
        # 设置行高
        for i in range(10):
            self.table.setRowHeight(i, 40)
        
        # 平分列宽
        table_width = self.table.width()
        self.table.setColumnWidth(0, int(table_width / 4))
        self.table.setColumnWidth(1, int(table_width / 4)*3)
        
        # 设置文字居中
        for i in range(10):
            for j in range(2):
                item = QTableWidgetItem()
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
        
        # 添加测试数据
        self.table.setItem(0, 0, QTableWidgetItem("测试数据1"))
        self.table.setItem(0, 1, QTableWidgetItem("测试数据2"))
        
        layout.addWidget(self.table)

        # 添加开始分析按钮
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 255, 255, 0.2);
                color: #00FFFF;
                border: 1px solid #00FFFF;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(0, 255, 255, 0.3);
            }
            QPushButton:pressed {
                background-color: rgba(0, 255, 255, 0.4);
            }
        """)
        layout.addWidget(self.analyze_btn)
        self.analyze_btn.clicked.connect(self.start)

        # 分析结果
        self.result_label = QLabel("分析结果：")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setWordWrap(True)  # 允许自动换行
        layout.addWidget(self.result_label)

        # 设置布局间距和边距
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        self.setLayout(layout)
    def start(self):
        # 这里可以添加开始分析的逻辑
        # 例如，获取输入的总人数并进行处理
        total_people = self.total_input.text()
        if not total_people:
            QMessageBox.warning(self, "警告", "请输入总人数")
            return
        if not total_people.isdigit():
            QMessageBox.warning(self, "警告", "总人数必须是数字")
            return
        total_people = int(total_people)
        positive, negative = 0, 0
        for k in POSITIVE:
            positive += self.result.get('result').get(k, 0)
        for k in NEGATIVE:
            negative += self.result.get('result').get(k, 0)
        
        positive_possibility = positive / (positive + negative) * 100
        negative_possibility = negative / (positive + negative) * 100
        positive_rate = positive / total_people * 100
        negative_rate = negative / total_people * 100

        self.result_label.setText(f"分析结果：\n"
                                  f"积极行为占比：{positive_possibility:.2f}%\n"
                                  f"消极行为占比：{negative_possibility:.2f}%\n"
                                  f"积极行为人数占比：{positive_rate:.2f}%\n"
                                  f"消极行为人数占比：{negative_rate:.2f}%")

    def set_file_name(self, name):
        self.file_name.setText(name)

    def set_table_data(self, data):
        for row, (key, value) in enumerate(data.items()):
            self.table.setItem(row, 0, QTableWidgetItem(str(key)))
            self.table.setItem(row, 1, QTableWidgetItem(str(value)))

    def set_result(self, text):
        self.result_label.setText(f"分析结果：{text}")


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # 创建界面实例
    window = AnalyizeDataUI()
    
    # 设置示例数据
    window.set_file_name("example_data.csv")
    window.set_table_data({
        "低头": 100,
        "转头": 23.5,
        "讨论": 15,
        "说话": 8.9,
        "举手": 50,
        "写字": 10,
        "使用手机": 5.6,
        "读书": 2.3,
        "靠在桌子上": 1.2,
        "站立": 0.5
    })
    window.set_result("数据分析完成，共处理100条记录")
    
    # 显示窗口
    window.show()
    sys.exit(app.exec_())