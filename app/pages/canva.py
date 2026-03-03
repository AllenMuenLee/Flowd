from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt


def build_canva() -> QWidget:
    root = QWidget()
    root.setStyleSheet(
        """
        QWidget {
            background: #0b1f3a;
            color: #e2e8f0;
        }
        QLabel#CanvasTitle {
            font-size: 20px;
            font-weight: 600;
        }
        """
    )

    layout = QVBoxLayout(root)
    layout.setContentsMargins(32, 32, 32, 32)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    title = QLabel("Canvas")
    title.setObjectName("CanvasTitle")
    layout.addWidget(title)

    return root


class CanvaWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(build_canva())

    def showEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)
