from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPoint

class ConnectionLine(QWidget):
    """Draws an arrow between two blocks."""
    
    def __init__(self, from_block, to_block, parent=None):
        super().__init__(parent)
        self.from_block = from_block
        self.to_block = to_block
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.update_position()
    
    def update_position(self):
        """Update line position based on block positions."""
        if not self.from_block or not self.to_block:
            return
        
        # Get center points of blocks
        from_center = self.from_block.geometry().center()
        to_center = self.to_block.geometry().center()
        
        # Set widget geometry to cover both points
        x = min(from_center.x(), to_center.x())
        y = min(from_center.y(), to_center.y())
        w = abs(to_center.x() - from_center.x())
        h = abs(to_center.y() - from_center.y())
        
        self.setGeometry(x, y, w + 10, h + 10)
        self.update()
    
    def paintEvent(self, event):
        """Draw the arrow."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(QColor("#60a5fa"), 2)  # Blue arrow
        painter.setPen(pen)
        
        # Calculate start and end points relative to widget
        from_center = self.from_block.geometry().center()
        to_center = self.to_block.geometry().center()
        
        start = QPoint(from_center.x() - self.x(), from_center.y() - self.y())
        end = QPoint(to_center.x() - self.x(), to_center.y() - self.y())
        
        # Draw line
        painter.drawLine(start, end)
        
        # TODO: Draw arrowhead at end point