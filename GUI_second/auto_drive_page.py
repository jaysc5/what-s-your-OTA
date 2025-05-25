from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt  # 이 줄 주석 처리하면 Qt.AlignCenter 등 에러남

class AutoDrivePage(QWidget):
    def __init__(self, back_callback=None):
        super().__init__()

        layout = QVBoxLayout()

        btn_back = QPushButton("Back")
        if back_callback:
            btn_back.clicked.connect(back_callback)
        layout.addWidget(btn_back, alignment=Qt.AlignLeft)

        label = QLabel("여기는 원격 제어 페이지입니다.")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)
