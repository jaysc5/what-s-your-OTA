import sys
import os
from PySide6.QtWidgets import QSizePolicy
from map_page import MapPage
from drive_page import DrivePage

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton,
    QStackedWidget, QWidget, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map & Update Navigation")
        self.setGeometry(100, 100, 800, 420)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.stacked_widget = QStackedWidget()

        # 이미지 로딩
        image_path1 = os.path.abspath("../../Downloads/map.png")
        image_path2 = os.path.abspath("../../Downloads/steering-wheel.png")
        pixmap1 = QPixmap(image_path1)
        pixmap2 = QPixmap(image_path2)

        # --- 페이지 0: 홈 ---
        self.page_home = QWidget()

        # 아이콘 위젯 구성
        # 수동 제어
        self.label_control = QLabel()
        self.label_control.setPixmap(pixmap2)
        self.label_control.setFixedSize(128, 128)
        self.label_control.setScaledContents(True)
        self.label_control.setAlignment(Qt.AlignCenter)
        self.label_control.mousePressEvent = self.goto_control_page

        self.label_control_text = QLabel("수동 제어")
        self.label_control_text.setAlignment(Qt.AlignCenter)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.label_control)
        control_layout.addWidget(self.label_control_text)
        control_layout.setAlignment(Qt.AlignHCenter)

        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # 지도
        self.label_map = QLabel()
        self.label_map.setPixmap(pixmap1)
        self.label_map.setFixedSize(128, 128)
        self.label_map.setScaledContents(True)
        self.label_map.setAlignment(Qt.AlignCenter)
        self.label_map.mousePressEvent = self.goto_map_page

        self.label_map_text = QLabel("지도")
        self.label_map_text.setAlignment(Qt.AlignCenter)

        map_layout = QVBoxLayout()
        map_layout.addWidget(self.label_map)
        map_layout.addWidget(self.label_map_text)
        map_layout.setAlignment(Qt.AlignHCenter)

        map_widget = QWidget()
        map_widget.setLayout(map_layout)
        map_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        # 가로 배치: 수동 제어 + 지도
        top_layout = QHBoxLayout()
        top_layout.addStretch(1)  # 좌측 여백
        top_layout.addWidget(control_widget)
        top_layout.addSpacing(150)  # 아이콘 간 간격
        top_layout.addWidget(map_widget)
        top_layout.addStretch(1)  # 우측 여백

        # 전체 홈 페이지 레이아웃
        layout_home = QVBoxLayout()
        layout_home.addStretch(1)
        layout_home.addLayout(top_layout)
        layout_home.addStretch(1)
        self.page_home.setLayout(layout_home)

        # --- 다른 페이지들 ---
        self.page_control = DrivePage(back_callback=self.goto_home_page)
        self.page_map = MapPage(back_callback=self.goto_home_page)

        # 스택에 추가
        self.stacked_widget.addWidget(self.page_home)     # index 0
        self.stacked_widget.addWidget(self.page_control)  # index 1
        self.stacked_widget.addWidget(self.page_map)      # index 2

        # 중앙 레이아웃 구성
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.central_widget.setLayout(main_layout)

        # 초기 페이지 설정
        self.stacked_widget.setCurrentIndex(0)

    # 페이지 전환 함수들
    def goto_control_page(self, event):
        self.stacked_widget.setCurrentIndex(1)

    def goto_map_page(self, event):
        self.stacked_widget.setCurrentIndex(2)

    def goto_home_page(self):
        self.stacked_widget.setCurrentIndex(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
