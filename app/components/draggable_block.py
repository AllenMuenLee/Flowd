from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QLabel


class DraggableBlock(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setObjectName("DraggableBlock")
        self.setFixedSize(180, 48)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(
            """
            QLabel#DraggableBlock {
                background: #111827;
                color: #e2e8f0;
                border: 1px solid #1f2937;
                border-radius: 10px;
                font-size: 12px;
                font-weight: 600;
            }
            """
        )
        self._drag_offset = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.position().toPoint()
            self.raise_()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            parent = self.parentWidget()
            if not parent:
                return
            new_pos = self.mapToParent(event.position().toPoint() - self._drag_offset)
            self.move(new_pos)
        super().mouseMoveEvent(event)
