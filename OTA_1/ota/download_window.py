from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame
from PySide6.QtCore import Qt, QSize
import subprocess
import os

class DownloadWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OTA 업데이트 알림")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(800, 480)  # 부모 창 크기와 맞추기

        # 반투명 배경
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignCenter)

        # 중앙 알림 박스
        self.popup = QFrame()
        self.popup.setFixedSize(500, 220)
        self.popup.setStyleSheet("""
            QFrame {
                background-color: rgba(30, 30, 30, 240);
                border-radius: 20px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: #444;
                color: white;
                padding: 8px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #666;
            }
        """)

        popup_layout = QVBoxLayout(self.popup)
        popup_layout.setContentsMargins(20, 20, 20, 20)
        popup_layout.setSpacing(20)

        # 메시지
        message = QLabel(
            "차량 시스템 업데이트가 준비되었습니다.\n"
            "지금 업데이트를 하시려면 [시작] 버튼을 누르십시오.\n"
            "업데이트 중에는 차량을 운행할 수 없습니다.\n"
            "예상 소요 시간: 약 25분\n"
            "자세한 내용을 보려면 [자세히 보기] 버튼을 누르십시오."
        )
        message.setAlignment(Qt.AlignLeft)
        message.setWordWrap(True)

        # 버튼
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("시작")
        self.start_btn.clicked.connect(self.start_update)

        self.detail_btn = QPushButton("자세히 보기")
        self.detail_btn.clicked.connect(self.show_details)

        self.later_btn = QPushButton("다음에 하기")
        self.later_btn.clicked.connect(self.close)

        button_layout.addStretch()
        button_layout.addWidget(self.start_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.detail_btn)
        button_layout.addSpacing(10)
        button_layout.addWidget(self.later_btn)
        button_layout.addStretch()

        popup_layout.addWidget(message)
        popup_layout.addLayout(button_layout)

        outer_layout.addWidget(self.popup)

    def start_update(self):
        updater_path = os.path.join("ota", "updater.py")
        if os.path.exists(updater_path):
            subprocess.Popen(["python3", updater_path])
        self.close()

    def show_details(self):
        print("[상세] 업데이트 상세 보기 클릭됨")
