from PyQt6.QtCore import Qt, QTimer, QRectF
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QWidget


class Spinner(QWidget):
    def __init__(self, parent=None, size=48, lines=12):
        super().__init__(parent)
        self._size = size
        self._lines = lines
        self._angle = 0
        self.setFixedSize(size, size)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(80)

    def _on_tick(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        center = self.rect().center()
        radius = self._size / 2.5

        for i in range(self._lines):
            alpha = int(255 * (i + 1) / self._lines)
            color = QColor(255, 255, 255, alpha)
            pen = QPen(color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            angle_deg = self._angle - (360 / self._lines) * i
            painter.save()
            painter.translate(center)
            painter.rotate(angle_deg)
            painter.drawLine(0, -radius * 0.6, 0, -radius)
            painter.restore()
        painter.end()


class LoadingScreen(QDialog):
    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setObjectName("LoadingScreen")

        self.setStyleSheet(
            """
            QDialog#LoadingScreen {
                background: #0b1f3a;
            }
            QLabel#LoadingLabel {
                color: #e2e8f0;
                font-size: 14px;
            }
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        spinner = Spinner(self, size=56)
        label = QLabel(message)
        label.setObjectName("LoadingLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

    def showEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)
