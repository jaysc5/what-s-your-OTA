
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFrame, QProgressBar
from PySide6.QtCore import Qt, QThread, Signal
import requests
import zipfile
import os
from ota import updater


class DownloadThread(QThread):
    progress_changed = Signal(int)
    finished_download = Signal()

    def run(self):
        latest_tag, zip_url = updater.get_latest_release()
        if not latest_tag or not zip_url:
            print("[OTA] 최신 릴리스를 가져오지 못했습니다.")
            return

        self.latest_tag = latest_tag
        print(f"[OTA] 다운로드할 태그: {latest_tag}")
        response = requests.get(zip_url, stream=True)
        total = int(response.headers.get("content-length", 0))
        downloaded = 0
        fallback_total = 10_000_000  # fallback fallback 최대 크기

        with open("latest_release.zip", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        percent = int((downloaded / total) * 100)
                    else:
                        percent = min(int((downloaded / fallback_total) * 100), 100)
                    self.progress_changed.emit(percent)

        self.finished_download.emit()

class DownloadWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("OTA 업데이트 알림")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(800, 480)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setAlignment(Qt.AlignCenter)

        self.popup = QFrame()
        self.popup.setFixedSize(500, 260)
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

        message = QLabel(
            "차량 시스템 업데이트가 준비되었습니다.\n"
            "지금 업데이트를 하시려면 [시작] 버튼을 누르십시오.\n"
            "업데이트 중에는 차량을 운행할 수 없습니다.\n"
            "예상 소요 시간: 약 25분\n"
            "자세한 내용을 보려면 [자세히 보기] 버튼을 누르십시오."
        )
        message.setAlignment(Qt.AlignLeft)
        message.setWordWrap(True)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

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
        popup_layout.addWidget(self.progress_bar)
        popup_layout.addLayout(button_layout)

        outer_layout.addWidget(self.popup)

    def start_update(self):
        self.progress_bar.setVisible(True)
        self.start_btn.setEnabled(False)

        self.thread = DownloadThread()
        self.thread.progress_changed.connect(self.progress_bar.setValue)
        self.thread.finished_download.connect(self.on_download_finished)
        self.thread.start()

    def on_download_finished(self):
        print("✅ 다운로드 완료됨")
        latest_tag, _ = updater.get_latest_release()
        current_tag = updater.read_current_tag()
        print(f"[OTA] Comparing tags - latest: {latest_tag}, current: {current_tag}")

        if latest_tag and latest_tag != current_tag:
            updater.write_current_tag(latest_tag)

            with zipfile.ZipFile("latest_release.zip", 'r') as zip_ref:
                zip_ref.extractall("temp_update")
            os.remove("latest_release.zip")

            updater.replace_app_code()
            pid = updater.read_pid()
            updater.send_signal(pid)
            updater.launch_app_and_kill_old(pid)
        else:
            print("[OTA] No update needed.")

        self.close()

    def show_details(self):
        print("[상세] 업데이트 상세 보기 클릭됨")
