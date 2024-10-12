import os
import sys
from PyQt5.QtCore import Qt, QTimer, QTime
from PyQt5.QtWidgets import (QApplication, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QAction, QWidget, QColorDialog, qApp, QSlider, QDialog)
from PyQt5.QtGui import QFont, QColor, QIcon, QPainter, QFontMetrics

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)

class TransparentClock(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.bg_color = QColor(0, 0, 0, 150)
        self.font_color = QColor(255, 255, 255)
        self.font_opacity = 1.0
        self.desired_height = 100
        self.movable = True
        self.offset = None

        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("color: white;")

        layout = QVBoxLayout()
        layout.addWidget(self.time_label)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.set_font_style()

        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)
        self.update_time()
        self.adjust_font_size_and_window_width()

        tray_icon = QSystemTrayIcon(self)
        # tray_icon.setIcon(QIcon("icon.png"))  # 替换为你的图标路径
        tray_icon.setIcon(QIcon(resource_path('icon.png')) )  # 替换为你的图标路径

        menu = QMenu()
        bg_color_action = QAction("设置背景颜色", self)
        bg_color_action.triggered.connect(self.set_bg_color)

        set_height_action = QAction("设置窗口高度", self)
        set_height_action.triggered.connect(self.open_height_slider)

        set_bg_opacity_action = QAction("调整背景透明度", self)
        set_bg_opacity_action.triggered.connect(self.open_bg_opacity_slider)

        set_font_opacity_action = QAction("调整文字透明度", self)
        set_font_opacity_action.triggered.connect(self.open_font_opacity_slider)

        always_on_top_action = QAction("置顶显示", self, checkable=True)
        always_on_top_action.toggled.connect(self.toggle_always_on_top)

        lock_position_action = QAction("固定位置", self, checkable=True)
        lock_position_action.toggled.connect(self.toggle_movable)

        exit_action = QAction("退出", self)
        exit_action.triggered.connect(qApp.quit)

        menu.addAction(bg_color_action)
        menu.addAction(set_height_action)
        menu.addAction(set_bg_opacity_action)
        menu.addAction(set_font_opacity_action)
        menu.addAction(always_on_top_action)
        menu.addAction(lock_position_action)
        menu.addAction(exit_action)

        tray_icon.setContextMenu(menu)
        tray_icon.show()

        self.show()

    def update_time(self):
        current_time = QTime.currentTime().toString('HH:mm:ss')
        self.time_label.setText(current_time)

    def adjust_font_size_and_window_width(self):
        rect = self.rect()
        font = QFont()
        font.setPointSize((self.desired_height - 10) // 2)  # 字体大小根据窗口高度调整，考虑10像素的留白
        self.time_label.setFont(font)

        font_metrics = QFontMetrics(self.time_label.font())
        text_width = font_metrics.horizontalAdvance(self.time_label.text())

        self.setFixedSize(text_width + 20, self.desired_height)

    def set_font_style(self):
        font = QFont()
        font.setPointSize((self.desired_height - 10) // 2)
        self.time_label.setFont(font)
        self.adjust_font_size_and_window_width()


    def set_bg_color(self):
        color = QColorDialog.getColor(self.bg_color, self)
        if color.isValid():
            self.bg_color.setRed(color.red())
            self.bg_color.setGreen(color.green())
            self.bg_color.setBlue(color.blue())
            self.update()

    def open_height_slider(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("调整窗口高度")
        dialog.setWindowFlags(Qt.Tool)
        dialog.resize(300, 100)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(50)
        slider.setMaximum(500)
        slider.setValue(self.desired_height)
        slider.valueChanged.connect(self.set_window_height)

        layout = QVBoxLayout()
        layout.addWidget(slider)
        dialog.setLayout(layout)

        dialog.show()

    def open_bg_opacity_slider(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("调整背景透明度")
        dialog.setWindowFlags(Qt.Tool)
        dialog.resize(300, 100)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(255)
        slider.setValue(self.bg_color.alpha())
        slider.valueChanged.connect(self.set_bg_opacity)

        layout = QVBoxLayout()
        layout.addWidget(slider)
        dialog.setLayout(layout)

        dialog.show()

    def open_font_opacity_slider(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("调整文字透明度")
        dialog.setWindowFlags(Qt.Tool)
        dialog.resize(300, 100)

        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(0)
        slider.setMaximum(100)
        slider.setValue(int(self.font_opacity * 100))
        slider.valueChanged.connect(self.set_font_opacity)

        layout = QVBoxLayout()
        layout.addWidget(slider)
        dialog.setLayout(layout)

        dialog.show()

    def set_window_height(self, height):
        self.desired_height = height
        self.adjust_font_size_and_window_width()

    def set_bg_opacity(self, value):
        self.bg_color.setAlpha(value)
        self.update()

    def set_font_opacity(self, value):
        self.font_opacity = value / 100
        self.time_label.setStyleSheet(f"color: rgba(255, 255, 255, {int(self.font_opacity * 255)})")

    def toggle_always_on_top(self, checked):
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()

    def toggle_movable(self, checked):
        self.movable = not checked

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.movable:
            self.offset = event.globalPos() - self.pos()

    def mouseMoveEvent(self, event):
        if self.offset is not None and self.movable:
            self.move(event.globalPos() - self.offset)

    def mouseReleaseEvent(self, event):
        self.offset = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(self.bg_color)
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    clock = TransparentClock()
    sys.exit(app.exec_())
