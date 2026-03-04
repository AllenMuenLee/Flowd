from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt

class DraggableBlock(QLabel):
    def __init__(self, step_id, step_data, parent=None):
        super().__init__(step_id, parent)
        self.step_id = step_id
        self.step_data = step_data
        self.setObjectName("DraggableBlock")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedSize(150, 80)
        self.setStyleSheet("""
            QLabel {
                background: #1e293b;
                color: #e2e8f0;
                border: 2px solid #334155;
                border-radius: 10px;
                padding: 15px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        self._drag_offset = None
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_offset = event.position().toPoint()
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton and self._drag_offset:
            new_pos = self.mapToParent(event.position().toPoint() - self._drag_offset)
            self.move(new_pos)
            
            # Update connection lines if parent has them
            if self.parent():
                from app.components.ConnectionLine import ConnectionLine
                for child in self.parent().children():
                    if isinstance(child, ConnectionLine):
                        child.update_position()
        
        super().mouseMoveEvent(event)