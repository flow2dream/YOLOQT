import sys
from PyQt5.QtWidgets import (QApplication, QPushButton, QWidget, 
                            QVBoxLayout, QGraphicsDropShadowEffect, QSizePolicy)
from PyQt5.QtCore import (Qt, QPropertyAnimation, QRect, QSize,
                         QPoint, QTimer, pyqtProperty)
from PyQt5.QtGui import (QColor, QPainter, QLinearGradient,QIcon,
                        QPen, QConicalGradient, QFontMetrics)

class CyberButton(QPushButton):
    def __init__(self, text="CYBER 2077", parent=None, icon_path=None):
        super().__init__(text, parent)
        self._glow_angle = 0
        self._scan_pos = 0
        self.icon_path = icon_path  # 新增图标路径属性
        
        # 初始化自适应设置
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Preferred)
        self.min_width = 120  # 最小宽度限制
        self.h_padding = 40    # 水平内边距
        self.v_padding = 20    # 垂直内边距
        
        self.setup_ui()
        self.setup_effects()
        self.setup_animations()

    def setup_ui(self):
        self.setCursor(Qt.PointingHandCursor)
        font = self.font()
        font.setBold(True)
        font.setPointSize(14)
        self.setFont(font)
        
        self.setStyleSheet("""
            QPushButton {
                color: #ffffff;
                border: 2px solid #40c4ff;
                border-radius: 12px;
                text-transform: uppercase;
                background: transparent;
            }
            /* 新增悬浮效果 */
            QPushButton:hover {
                border-width: 3px;
                background-color: rgba(100, 255, 218, 0.1);
            }
            /* 新增按压效果 */
            QPushButton:pressed {
                border-width: 1px;
                background-color: rgba(0, 188, 212, 0.2);
                margin: 1px;
            }
        """)

    def sizeHint(self):
        # 根据文本内容和图标计算理想尺寸
        metrics = QFontMetrics(self.font())
        text_width = metrics.width(self.text())
        text_height = metrics.height()
        icon_width = 20 if self.icon_path else 0  # 图标宽度
        return QSize(
            max(text_width + self.h_padding + icon_width, self.min_width),
            text_height + self.v_padding
        )

    def setup_effects(self):
        self.shadow_effect = QGraphicsDropShadowEffect(self)
        self.shadow_effect.setColor(QColor(64, 196, 255, 150))
        self.shadow_effect.setBlurRadius(15)
        self.shadow_effect.setOffset(0, 4)
        self.setGraphicsEffect(self.shadow_effect)

    def setup_animations(self):
        # 扫描线动画
        self.scan_animation = QPropertyAnimation(self, b"scan_pos")
        self.scan_animation.setDuration(1800)
        self.scan_animation.setLoopCount(-1)
        
        # 流光边框动画
        self.glow_animation = QPropertyAnimation(self, b"glow_angle")
        self.glow_animation.setDuration(2800)
        self.glow_animation.setLoopCount(-1)
        
        # 延迟启动动画
        QTimer.singleShot(100, self.start_animations)

    def start_animations(self):
        # 动态设置动画范围（根据当前尺寸）
        self.scan_animation.setStartValue(0)
        self.scan_animation.setEndValue(self.height())
        self.glow_animation.setStartValue(0)
        self.glow_animation.setEndValue(359)
        self.scan_animation.start()
        self.glow_animation.start()

    @pyqtProperty(int)
    def scan_pos(self):
        return self._scan_pos

    @scan_pos.setter
    def scan_pos(self, value):
        self._scan_pos = value
        self.update()

    @pyqtProperty(int)
    def glow_angle(self):
        return self._glow_angle

    @glow_angle.setter
    def glow_angle(self, value):
        self._glow_angle = value % 360
        self.update()

    def resizeEvent(self, event):
        # 尺寸变化时重置动画参数
        self.start_animations()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 动态计算尺寸相关参数
        current_width = self.width()
        current_height = self.height()

        border_radius = min(12, current_height//2)  # 调整圆角计算方式
        
        # 绘制背景渐变（保持原有渐变）
        gradient = QLinearGradient(0, 0, current_width, 0)
        gradient.setColorAt(0, QColor(26, 35, 126))
        gradient.setColorAt(0.5, QColor(57, 73, 171))
        gradient.setColorAt(1, QColor(83, 109, 254))
        painter.fillRect(self.rect(), gradient)

        # 扫描线效果
        scan_gradient = QLinearGradient(0, self.scan_pos, 0, self.scan_pos+current_height//4)
        scan_gradient.setColorAt(0, QColor(255, 255, 255, 0))
        scan_gradient.setColorAt(0.5, QColor(255, 255, 255, 30))
        scan_gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(scan_gradient)
        painter.drawRect(0, self.scan_pos, current_width, current_height//4)

        # 流光边框
        glow_gradient = QConicalGradient(self.rect().center(), self.glow_angle)
        glow_gradient.setColorAt(0, QColor(64, 196, 255, 0))
        glow_gradient.setColorAt(0.2, QColor(100, 255, 218, 150))
        glow_gradient.setColorAt(0.5, QColor(64, 196, 255, 0))
        glow_gradient.setColorAt(0.7, QColor(100, 255, 218, 150))
        glow_gradient.setColorAt(1, QColor(64, 196, 255, 0))
        
        pen = QPen(glow_gradient, max(2, current_height//20))
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), border_radius, border_radius)

        # 自适应文字绘制
        self.draw_adaptive_text(painter, current_width, current_height)

    def draw_adaptive_text(self, painter, width, height):
        # 文字缩放逻辑
        text = self.text()
        font = self.font()
        metrics = QFontMetrics(font)
        text_width = metrics.width(text)
        
        # 自动调整字体大小
        # max_font_size = 
        min_font_size = min(height//2, 15)
        while True:
            if text_width + self.h_padding < width or font.pointSize() <= min_font_size:
                break
            font.setPointSize(font.pointSize()-1)
            metrics = QFontMetrics(font)
            text_width = metrics.width(text)
        
        painter.setFont(font)
        
        # 绘制图标
        if self.icon_path:
            icon = QIcon(self.icon_path)
            icon_size = QSize(height//2, height//2)
            icon_rect = QRect(10, (height - icon_size.height())//2, 
                            icon_size.width(), icon_size.height())
            icon.paint(painter, icon_rect)
        
        # 文字光晕
        for i in range(5, 0, -1):
            alpha = 50 - i*10
            painter.setPen(QColor(64, 196, 255, alpha))
            painter.drawText(self.rect().adjusted(-i, -i, i, i), 
                            Qt.AlignCenter, text)
        
        # 主文字
        painter.setPen(Qt.white)
        painter.drawText(self.rect(), Qt.AlignCenter, text)


