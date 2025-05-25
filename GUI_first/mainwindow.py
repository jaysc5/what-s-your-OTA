import sys
import os
import time
import signal
from PySide6.QtWidgets import (
    QSizePolicy, QApplication, QMainWindow, QLabel, QPushButton, QStackedWidget,
    QWidget, QVBoxLayout, QHBoxLayout, QProgressBar
)
from PySide6.QtGui import QPixmap, QFontDatabase, QFont
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from map_page import MapPage
from drive_page import DrivePage

PID_FILE = "pid.txt"


class DownloadThread(QThread):
    progress_changed = Signal(int)

    def run(self):
        for i in range(101):
            time.sleep(0.03)
            self.progress_changed.emit(i)


class DownloadWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OTA 다운로드")
        self.setFixedSize(320, 160)

        # 검정색 테두리 스타일 적용
        self.setStyleSheet("QWidget { border: 2px solid black; }")

        layout = QVBoxLayout()
        button_layout = QHBoxLayout()

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.start_button = QPushButton("다운로드 시작")
        self.start_button.clicked.connect(self.start_download)

        self.later_button = QPushButton("다음에 하기")
        self.later_button.clicked.connect(self.close)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.later_button)

        layout.addWidget(self.progress_bar)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.download_thread = DownloadThread()
        self.download_thread.progress_changed.connect(self.update_progress)

    def start_download(self):
        self.start_button.setEnabled(False)
        self.download_thread.start()

    def update_progress(self, value):
        self.progress_bar.setValue(value)
        if value == 100:
            self.start_button.setText("다운로드 완료")
            self.start_button.setEnabled(True)
            self.start_button.clicked.disconnect()
            self.start_button.clicked.connect(self.close)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map & Update Navigation")
        self.setGeometry(100, 100, 800, 420)

        # 폰트 설정
        font_id = QFontDatabase.addApplicationFont("./malgun.ttf")
        if font_id != -1:
            font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            app_font = QFont(font_family, 10)
            QApplication.setFont(app_font)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.stacked_widget = QStackedWidget()

        image_path1 = os.path.abspath("./img/map.png")
        image_path2 = os.path.abspath("./img/steering-wheel.png")
        pixmap1 = QPixmap(image_path1)
        pixmap2 = QPixmap(image_path2)

        self.page_home = QWidget()

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

        top_layout = QHBoxLayout()
        top_layout.addStretch(1)
        top_layout.addWidget(control_widget)
        top_layout.addSpacing(150)
        top_layout.addWidget(map_widget)
        top_layout.addStretch(1)

        layout_home = QVBoxLayout()
        layout_home.addStretch(1)
        layout_home.addLayout(top_layout)
        layout_home.addStretch(1)
        self.page_home.setLayout(layout_home)

        self.page_control = DrivePage(back_callback=self.goto_home_page)
        self.page_map = MapPage(back_callback=self.goto_home_page)

        self.stacked_widget.addWidget(self.page_home)
        self.stacked_widget.addWidget(self.page_control)
        self.stacked_widget.addWidget(self.page_map)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.stacked_widget)
        self.central_widget.setLayout(main_layout)

        self.stacked_widget.setCurrentIndex(0)

        self.download_window = None
        self.setup_signal_handling()

    def setup_signal_handling(self):
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        print(f"[MainWindow] PID {os.getpid()} saved to {PID_FILE}. Waiting for SIGUSR1...")

        signal.signal(signal.SIGUSR1, self.handle_ota_signal)

        self.timer = QTimer()
        self.timer.timeout.connect(lambda: None)
        self.timer.start(100)

    def handle_ota_signal(self, signum, frame):
        if signum == signal.SIGUSR1:
            print("[MainWindow] OTA 시그널 수신됨, 다운로드 창 띄우기")
            self.show_download_window()

    def show_download_window(self):
        if self.download_window is None or not self.download_window.isVisible():
            self.download_window = DownloadWindow(parent=self)
            self.download_window.setWindowModality(Qt.ApplicationModal)

            # 메인 윈도우 가운데로 위치 이동
            parent_geom = self.geometry()
            center_x = parent_geom.x() + (parent_geom.width() - self.download_window.width()) // 2
            center_y = parent_geom.y() + (parent_geom.height() - self.download_window.height()) // 2
            self.download_window.move(center_x, center_y)

            self.download_window.show()

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
