import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout

from app.pages.projectBuilder import ProjectBuilderWidget
from app.pages.canva import CanvaWidget


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Project Builder")
    window.resize(900, 600)

    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)

    canvas = CanvaWidget()
    canvas.hide()

    def on_project_created(success):
        if success:
            builder.hide()
            canvas.show()
            canvas.raise_()
        else:
            canvas.hide()
            builder.show()

    builder = ProjectBuilderWidget(on_project_created=on_project_created)

    layout.addWidget(builder)
    layout.addWidget(canvas)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
