import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QStackedWidget
from app.pages.projectBuilder import ProjectBuilderWidget
from app.pages.canva import CanvaWidget
from app.pages.codeEditor import CodeEditorWidget
from src.utils.CacheMng import load_cache
import os
import json


def main():
    app = QApplication(sys.argv)
    window = QWidget()
    window.setWindowTitle("Vibe Coding App")
    window.resize(1200, 800)
    
    layout = QVBoxLayout(window)
    layout.setContentsMargins(0, 0, 0, 0)
    
    # Use stacked widget to switch between views
    stacked = QStackedWidget()
    
    # Helper function to load fresh flowchart data
    def load_flowchart_data():
        """Load the current flowchart data from cache."""
        cache = load_cache()
        project_id = cache.get("current_project_id")
        
        if not project_id:
            return None
        
        appdata_root = os.path.join(os.getenv("APPDATA", ""), "SVCA")
        flowchart_path = os.path.join(appdata_root, f"{project_id}.flowchart.json")
        
        if os.path.exists(flowchart_path):
            try:
                with open(flowchart_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading flowchart: {e}")
                return None
        return None
    
    # Page navigation callbacks
    def on_project_created(success):
        """Called after project creation - navigate to Canvas."""
        if success:
            print("✓ Project created, navigating to Canvas...")
            
            # Load the flowchart data
            flowchart_data = load_flowchart_data()
            
            # Remove old canvas if it exists
            if stacked.count() > 1:
                old_canvas = stacked.widget(1)
                stacked.removeWidget(old_canvas)
                old_canvas.deleteLater()
            
            # Create fresh canvas with callback
            canvas = CanvaWidget()
            canvas.on_code_generated = on_code_generated
            
            # Insert at index 1
            stacked.insertWidget(1, canvas)
            stacked.setCurrentIndex(1)  # Navigate to canvas
    
    def on_code_generated():
        """Called after code generation - navigate to Code Editor."""
        print("✓ Code generated, navigating to Editor...")
        
        # Load fresh flowchart data
        flowchart_data = load_flowchart_data()
        
        if not flowchart_data:
            print("⚠ Warning: Could not load flowchart data for editor")
            return
        
        # Remove old editor if it exists
        if stacked.count() > 2:
            old_editor = stacked.widget(2)
            stacked.removeWidget(old_editor)
            old_editor.deleteLater()
        
        # Create fresh editor with callback
        editor = CodeEditorWidget(flowchart_data, on_back_to_canvas)
        
        # Insert at index 2
        stacked.insertWidget(2, editor)
        stacked.setCurrentIndex(2)  # Navigate to editor
    
    def on_back_to_canvas():
        """Called when user wants to refine flowchart - go back to Canvas."""
        print("✓ Returning to Canvas...")
        
        # Load fresh flowchart data
        flowchart_data = load_flowchart_data()
        
        # Remove old canvas if it exists
        if stacked.count() > 1:
            old_canvas = stacked.widget(1)
            stacked.removeWidget(old_canvas)
            old_canvas.deleteLater()
        
        # Create fresh canvas with callback
        canvas = CanvaWidget()
        canvas.on_code_generated = on_code_generated
        
        # Insert at index 1
        stacked.insertWidget(1, canvas)
        stacked.setCurrentIndex(1)  # Navigate to canvas
    
    # Create initial pages
    # ✅ Always start with Project Builder
    builder = ProjectBuilderWidget(on_project_created=on_project_created)
    stacked.addWidget(builder)  # Index 0
    
    # Add to layout
    layout.addWidget(stacked)
    
    # ✅ Always start at Project Builder (Index 0)
    stacked.setCurrentIndex(0)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()