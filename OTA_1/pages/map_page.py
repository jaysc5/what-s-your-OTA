from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtCore import Qt

class MapPage(QWidget):
    def __init__(self, back_callback=None):
        super().__init__()

        layout = QVBoxLayout()

        label = QLabel("지도 페이지입니다 (WebEngine 없이)")
        label.setAlignment(Qt.AlignCenter)

        btn_back = QPushButton("뒤로가기")
        if back_callback:
            btn_back.clicked.connect(back_callback)

        layout.addWidget(label)
        layout.addWidget(btn_back)

        self.setLayout(layout)
