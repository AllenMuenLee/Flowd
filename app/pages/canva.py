import json
import os

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

from app.components.draggable_block import DraggableBlock
from src.utils.CacheMng import load_cache


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
    layout.setContentsMargins(24, 24, 24, 24)
    layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

    title = QLabel("Canvas")
    title.setObjectName("CanvasTitle")
    layout.addWidget(title)

    canvas = QWidget()
    canvas.setObjectName("CanvasArea")
    canvas.setStyleSheet("QWidget#CanvasArea { background: transparent; }")
    canvas.setMinimumHeight(400)
    layout.addWidget(canvas, 1)

    cache = load_cache()
    project_id = cache.get("current_project_id")
    steps = []
    if project_id:
        appdata_root = os.path.join(os.getenv("APPDATA", ""), "SVCA")
        flowchart_path = os.path.join(appdata_root, f"{project_id}.flowchart.json")
        if os.path.exists(flowchart_path):
            try:
                with open(flowchart_path, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
                steps = list((data.get("steps") or {}).values())
            except Exception:
                steps = []

    if not steps:
        empty = QLabel("No steps found for the current project.")
        empty.setStyleSheet("color: #94a3b8; font-size: 12px;")
        layout.addWidget(empty)
    else:
        x, y = 24, 24
        gap_x, gap_y = 16, 16
        max_width = 760
        for step in steps:
            name = step.get("id") or step.get("description") or "Step"
            block = DraggableBlock(name, parent=canvas)
            block.move(x, y)
            x += block.width() + gap_x
            if x + block.width() > max_width:
                x = 24
                y += block.height() + gap_y

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
