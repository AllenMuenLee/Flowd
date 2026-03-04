import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
from app.pages.projectBuilder import ProjectBuilderWidget
from app.pages.canva import CanvaWidget


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Vibe Coding App")  # Better title
    window.resize(900, 600)
    
    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Create canvas (will be empty initially)
    canvas = CanvaWidget()
    canvas.hide()
    
    def on_project_created(success):
        if success:
            # Hide builder
            builder.hide()
            
            # Recreate canvas with new project data
            layout.removeWidget(canvas)
            canvas.deleteLater()
            
            new_canvas = CanvaWidget()
            layout.addWidget(new_canvas)
            new_canvas.show()
            new_canvas.raise_()
        else:
            # Show error, keep builder visible
            canvas.hide()
            builder.show()
    
    builder = ProjectBuilderWidget(on_project_created=on_project_created)
    
    layout.addWidget(builder)
    layout.addWidget(canvas)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()