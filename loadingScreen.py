from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPainter, QColor, QPen
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


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
            painter.drawLine(0, int(-radius * 0.6), 0, int(-radius))
            painter.restore()
        painter.end()


class LoadingScreen(QWidget):
    """Semi-transparent overlay loading screen."""
    
    def __init__(self, parent=None, message="Loading..."):
        super().__init__(parent)
        
        # ✅ Make it an overlay
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # ✅ Semi-transparent dark background
        self.setStyleSheet("""
            QWidget {
                background: rgba(15, 23, 42, 200);
            }
            QLabel#LoadingLabel {
                color: #e2e8f0;
                font-size: 16px;
                font-weight: 600;
                background: transparent;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Container for spinner and label
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: #1e293b;
                border-radius: 12px;
                padding: 30px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(16)
        container_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        spinner = Spinner(self, size=56)
        label = QLabel(message)
        label.setObjectName("LoadingLabel")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        container_layout.addWidget(spinner, alignment=Qt.AlignmentFlag.AlignCenter)
        container_layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(container, alignment=Qt.AlignmentFlag.AlignCenter)

    def showEvent(self, event):
        """Resize to cover parent widget."""
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)
        self.raise_()  # Bring to front