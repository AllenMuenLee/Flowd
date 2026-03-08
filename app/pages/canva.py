import sys
import os
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QScrollArea, QMessageBox,
    QTextEdit, QFrame, QDialog, QListWidget, QInputDialog
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPainter, QPen, QColor
from app.components.draggable_block import DraggableBlock
from src.utils.CacheMng import load_cache
from app.pages.loadingScreen import LoadingScreen
from app.components.ConnectionLine import ConnectionLine
from PyQt6.QtCore import QThread, pyqtSignal


def build_canva(flowchart_data=None) -> QWidget:
    """Build the canvas page with flowchart visualization."""
    
    root = QWidget()
    root.setObjectName("CanvaPage")
    
    # Main horizontal layout: canvas on left, details on right
    main_layout = QHBoxLayout(root)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Left side: Canvas area
    left_container = QWidget()
    left_layout = QVBoxLayout(left_container)
    left_layout.setContentsMargins(10, 10, 10, 10)
    
    # Toolbar
    toolbar = QHBoxLayout()
    
    add_step_btn = QPushButton("+ Add Step")
    add_step_btn.setObjectName("ToolbarButton")
    add_step_btn.clicked.connect(lambda: on_add_step(root))
    
    delete_step_btn = QPushButton("🗑 Delete Step")
    delete_step_btn.setObjectName("ToolbarButton")
    delete_step_btn.clicked.connect(lambda: on_delete_step(root))
    
    generate_btn = QPushButton("⚡ Generate Code")
    generate_btn.setObjectName("PrimaryButton")
    generate_btn.clicked.connect(lambda: on_generate_code(root))
    
    toolbar.addWidget(add_step_btn)
    toolbar.addWidget(delete_step_btn)
    toolbar.addStretch()
    toolbar.addWidget(generate_btn)
    
    left_layout.addLayout(toolbar)
    
    # Canvas scroll area
    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setObjectName("CanvasScroll")
    
    # ✅ BIGGER canvas for scrolling
    canvas = QWidget()
    canvas.setObjectName("Canvas")
    canvas.setMinimumSize(1400, 2500)  # ✅ Much taller
    
    scroll.setWidget(canvas)
    left_layout.addWidget(scroll)
    
    # Right side: Details panel
    details_panel = QWidget()
    details_panel.setObjectName("DetailsPanel")
    details_panel.setFixedWidth(350)
    details_layout = QVBoxLayout(details_panel)
    details_layout.setContentsMargins(20, 20, 20, 20)
    
    # Details panel title
    details_title = QLabel("Step Details")
    details_title.setObjectName("DetailsPanelTitle")
    details_title.setStyleSheet("""
        font-size: 18px;
        font-weight: bold;
        color: #e2e8f0;
        margin-bottom: 10px;
    """)
    details_layout.addWidget(details_title)
    
    # Step ID (read-only)
    step_id_label = QLabel("Step ID:")
    step_id_label.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 10px;")
    details_layout.addWidget(step_id_label)
    
    step_id_value = QLabel("No step selected")
    step_id_value.setObjectName("StepIdValue")
    step_id_value.setStyleSheet("color: #e2e8f0; font-size: 14px; font-weight: 600;")
    details_layout.addWidget(step_id_value)
    
    # Description
    desc_label = QLabel("Description:")
    desc_label.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 15px;")
    details_layout.addWidget(desc_label)
    
    desc_value = QTextEdit()
    desc_value.setObjectName("DescValue")
    desc_value.setReadOnly(False)
    desc_value.setPlaceholderText("Select a step to edit")
    desc_value.setMaximumHeight(100)
    desc_value.setStyleSheet("""
        QTextEdit {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 10px;
            font-size: 13px;
        }
    """)
    details_layout.addWidget(desc_value)
    
    # Files
    files_label = QLabel("Files to Generate:")
    files_label.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 15px;")
    details_layout.addWidget(files_label)
    
    files_list = QListWidget()
    files_list.setObjectName("FilesList")
    files_list.setMaximumHeight(100)
    files_list.setStyleSheet("""
        QListWidget {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 5px;
            font-size: 12px;
        }
    """)
    details_layout.addWidget(files_list)
    
    # File buttons
    file_buttons = QHBoxLayout()
    add_file_btn = QPushButton("+ File")
    remove_file_btn = QPushButton("- File")
    add_file_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
    remove_file_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
    add_file_btn.clicked.connect(lambda: on_add_file(root))
    remove_file_btn.clicked.connect(lambda: on_remove_file(root))
    file_buttons.addWidget(add_file_btn)
    file_buttons.addWidget(remove_file_btn)
    details_layout.addLayout(file_buttons)
    
    # ✅ Children/Connections editor
    children_label = QLabel("Next Steps (Children):")
    children_label.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 15px;")
    details_layout.addWidget(children_label)
    
    children_list = QListWidget()
    children_list.setObjectName("ChildrenList")
    children_list.setMaximumHeight(80)
    children_list.setStyleSheet("""
        QListWidget {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 5px;
            font-size: 12px;
        }
    """)
    details_layout.addWidget(children_list)
    
    # Children buttons
    children_buttons = QHBoxLayout()
    add_child_btn = QPushButton("+ Connect")
    remove_child_btn = QPushButton("- Remove")
    add_child_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
    remove_child_btn.setStyleSheet("font-size: 11px; padding: 4px 8px;")
    add_child_btn.clicked.connect(lambda: on_add_child(root))
    remove_child_btn.clicked.connect(lambda: on_remove_child(root))
    children_buttons.addWidget(add_child_btn)
    children_buttons.addWidget(remove_child_btn)
    details_layout.addLayout(children_buttons)
    
    # Commands
    commands_label = QLabel("Commands:")
    commands_label.setStyleSheet("color: #94a3b8; font-size: 12px; margin-top: 15px;")
    details_layout.addWidget(commands_label)
    
    commands_value = QTextEdit()
    commands_value.setObjectName("CommandsValue")
    commands_value.setReadOnly(False)
    commands_value.setMaximumHeight(80)
    commands_value.setPlaceholderText("One command per line")
    commands_value.setStyleSheet("""
        QTextEdit {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 10px;
            font-size: 12px;
            font-family: monospace;
        }
    """)
    details_layout.addWidget(commands_value)
    
    # Save button
    save_btn = QPushButton("💾 Save Changes")
    save_btn.setObjectName("SaveButton")
    save_btn.setStyleSheet("""
        QPushButton#SaveButton {
            background: #059669;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px;
            font-size: 13px;
            font-weight: 600;
            margin-top: 15px;
        }
        QPushButton#SaveButton:hover {
            background: #047857;
        }
    """)
    save_btn.clicked.connect(lambda: on_save_changes(root))
    details_layout.addWidget(save_btn)
    
    details_layout.addStretch()
    
    # Add both sides to main layout
    main_layout.addWidget(left_container, stretch=1)
    main_layout.addWidget(details_panel)
    
    # Store references
    root.canvas = canvas
    root.details_panel = {
        'step_id': step_id_value,
        'description': desc_value,
        'files': files_list,
        'children': children_list,
        'commands': commands_value
    }
    root.blocks = {}
    root.connections = []
    root.selected_step_id = None
    root.flowchart_data = flowchart_data
    
    if flowchart_data:
        load_flowchart(root, flowchart_data)
    
    return root


def load_flowchart(root, flowchart_data):
    """Load flowchart data and create visual blocks."""
    
    canvas = root.canvas
    steps = flowchart_data.get('steps', {})
    
    # Clear existing
    for block in root.blocks.values():
        block.deleteLater()
    for conn in root.connections:
        conn.deleteLater()
    
    root.blocks.clear()
    root.connections.clear()
    
    # Vertical layout
    start_id = flowchart_data.get('start_id')
    x_center = 600
    y_offset = 50
    y_spacing = 150
    
    visited = set()
    positions = {}
    max_y = y_offset
    
    def assign_positions(step_id, x_pos, y_pos, depth=0):
        nonlocal max_y
        
        if step_id in visited or step_id not in steps:
            return y_pos
        
        visited.add(step_id)
        positions[step_id] = (x_pos, y_pos)
        max_y = max(max_y, y_pos)
        
        step_data = steps[step_id]
        children = step_data.get('children', [])
        
        current_y = y_pos + y_spacing
        
        if len(children) == 0:
            return current_y
        elif len(children) == 1:
            return assign_positions(children[0], x_pos, current_y, depth + 1)
        else:
            x_spread = 250
            start_x = x_pos - (len(children) - 1) * x_spread / 2
            
            max_child_y = current_y
            for i, child_id in enumerate(children):
                child_x = start_x + i * x_spread
                child_y = assign_positions(child_id, child_x, current_y, depth + 1)
                max_child_y = max(max_child_y, child_y)
            
            return max_child_y
    
    if start_id and start_id in steps:
        assign_positions(start_id, x_center, y_offset)
    
    orphan_y = y_offset
    for step_id in steps:
        if step_id not in positions:
            positions[step_id] = (x_center + 350, orphan_y)
            orphan_y += y_spacing
            max_y = max(max_y, orphan_y)
    
    # ✅ Resize canvas dynamically
    canvas.setMinimumHeight(max(2500, max_y + 300))
    
    # Create blocks
    for step_id, step_data in steps.items():
        block = DraggableBlock(step_id, step_data, parent=canvas)
        
        if step_id in positions:
            x_pos, y_pos = positions[step_id]
            # ✅ FIX: Convert to int
            block.move(int(x_pos - 75), int(y_pos))
        else:
            # ✅ FIX: Convert to int
            block.move(int(x_center - 75), int(y_offset))
        
        block.show()
        
        def make_click_handler(sid, sd):
            def handler(event):
                on_block_click(root, sid, sd, event)
            return handler
        
        block.mousePressEvent = make_click_handler(step_id, step_data)
        root.blocks[step_id] = block
    
    # Draw connections
    for step_id, step_data in steps.items():
        from_block = root.blocks.get(step_id)
        if not from_block:
            continue
        
        children = step_data.get('children', [])
        for child_id in children:
            to_block = root.blocks.get(child_id)
            if to_block:
                line = ConnectionLine(from_block, to_block, parent=canvas)
                line.lower()
                line.show()
                root.connections.append(line)


def on_block_click(root, step_id, step_data, event):
    root.selected_step_id = step_id
    root.details_panel['step_id'].setText(step_id)
    root.details_panel['description'].setPlainText(step_data.get('description', ''))
    
    files_list = root.details_panel['files']
    files_list.clear()
    files_list.addItems(step_data.get('filenames', []))
    
    children_list = root.details_panel['children']
    children_list.clear()
    children_list.addItems(step_data.get('children', []))
    
    commands = step_data.get('command', [])
    root.details_panel['commands'].setPlainText('\n'.join(commands))
    
    for block in root.blocks.values():
        block.setStyleSheet("""
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
    
    root.blocks[step_id].setStyleSheet("""
        QLabel {
            background: #1e40af;
            color: #e2e8f0;
            border: 2px solid #60a5fa;
            border-radius: 10px;
            padding: 15px;
            font-size: 13px;
            font-weight: 600;
        }
    """)


def on_save_changes(root):
    if not root.selected_step_id:
        QMessageBox.warning(root, "No Selection", "Please select a step first.")
        return
    
    try:
        updated_data = {
            'id': root.selected_step_id,
            'description': root.details_panel['description'].toPlainText(),
            'filenames': [
                root.details_panel['files'].item(i).text() 
                for i in range(root.details_panel['files'].count())
            ],
            'children': [
                root.details_panel['children'].item(i).text() 
                for i in range(root.details_panel['children'].count())
            ],
            'command': root.details_panel['commands'].toPlainText().split('\n'),
            'files_to_import': root.flowchart_data['steps'][root.selected_step_id].get('files_to_import', [])
        }
        
        root.flowchart_data['steps'][root.selected_step_id] = updated_data
        save_flowchart_to_file(root.flowchart_data)
        load_flowchart(root, root.flowchart_data)
        
        QMessageBox.information(root, "Success", "Changes saved! Connections updated.")
    except Exception as e:
        QMessageBox.critical(root, "Error", f"Failed to save: {e}")


def on_add_file(root):
    if not root.selected_step_id:
        QMessageBox.warning(root, "No Selection", "Please select a step first.")
        return
    filename, ok = QInputDialog.getText(root, "Add File", "Enter filename:")
    if ok and filename:
        root.details_panel['files'].addItem(filename)


def on_remove_file(root):
    files_list = root.details_panel['files']
    current_row = files_list.currentRow()
    if current_row >= 0:
        files_list.takeItem(current_row)
    else:
        QMessageBox.warning(root, "No Selection", "Please select a file to remove.")


def on_add_child(root):
    if not root.selected_step_id:
        QMessageBox.warning(root, "No Selection", "Please select a step first.")
        return
    
    available_steps = [
        step_id for step_id in root.flowchart_data['steps'].keys()
        if step_id != root.selected_step_id
    ]
    
    if not available_steps:
        QMessageBox.warning(root, "No Steps", "No other steps available to connect.")
        return
    
    child_id, ok = QInputDialog.getItem(
        root, "Add Connection", "Select next step:", available_steps, 0, False
    )
    
    if ok and child_id:
        current_children = [
            root.details_panel['children'].item(i).text() 
            for i in range(root.details_panel['children'].count())
        ]
        
        if child_id in current_children:
            QMessageBox.warning(root, "Duplicate", f"Already connected to {child_id}!")
            return
        
        root.details_panel['children'].addItem(child_id)


def on_remove_child(root):
    children_list = root.details_panel['children']
    current_row = children_list.currentRow()
    if current_row >= 0:
        children_list.takeItem(current_row)
    else:
        QMessageBox.warning(root, "No Selection", "Please select a connection to remove.")


def on_add_step(root):
    step_id, ok = QInputDialog.getText(root, "Add Step", "Enter step ID (e.g., step5):")
    if not ok or not step_id:
        return
    
    if step_id in root.flowchart_data['steps']:
        QMessageBox.warning(root, "Duplicate ID", f"Step '{step_id}' already exists!")
        return
    
    new_step = {
        'id': step_id,
        'description': 'New step - edit description here',
        'filenames': [],
        'files_to_import': [],
        'command': [],
        'children': []
    }
    
    root.flowchart_data['steps'][step_id] = new_step
    save_flowchart_to_file(root.flowchart_data)
    load_flowchart(root, root.flowchart_data)
    
    QMessageBox.information(root, "Success", f"Step '{step_id}' added!")


def on_delete_step(root):
    if not root.selected_step_id:
        QMessageBox.warning(root, "No Selection", "Please select a step to delete.")
        return
    
    step_id = root.selected_step_id
    
    reply = QMessageBox.question(
        root, "Confirm Delete", f"Delete step '{step_id}'?",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    
    if reply == QMessageBox.StandardButton.No:
        return
    
    del root.flowchart_data['steps'][step_id]
    
    for step_data in root.flowchart_data['steps'].values():
        if step_id in step_data.get('children', []):
            step_data['children'].remove(step_id)
    
    save_flowchart_to_file(root.flowchart_data)
    load_flowchart(root, root.flowchart_data)
    
    root.selected_step_id = None
    root.details_panel['step_id'].setText("No step selected")
    root.details_panel['description'].setPlainText("")
    root.details_panel['files'].clear()
    root.details_panel['children'].clear()
    root.details_panel['commands'].setPlainText("")
    
    QMessageBox.information(root, "Success", f"Step '{step_id}' deleted!")


def save_flowchart_to_file(flowchart_data):
    cache = load_cache()
    project_id = cache.get("current_project_id")
    
    if not project_id:
        raise Exception("No project ID found in cache")
    
    appdata_root = os.path.join(os.getenv("APPDATA", ""), "SVCA")
    flowchart_path = os.path.join(appdata_root, f"{project_id}.flowchart.json")
    
    with open(flowchart_path, 'w', encoding='utf-8') as f:
        json.dump(flowchart_data, f, indent=2)

class CodeGenerationWorker(QThread):
    """Worker thread for code generation."""
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, flowchart_dict, project_root):
        super().__init__()
        self.flowchart_dict = flowchart_dict
        self.project_root = project_root
    
    def run(self):
        """Run code generation in background thread."""
        try:
            from src.core.Flowchart import Flowchart
            from src.core.CodeGen import CodingAgent
            
            flowchart = Flowchart(name="", framework="", project_root=self.project_root)
            flowchart = flowchart.dictionary_to_flowchart(self.flowchart_dict)
            
            agent = CodingAgent(flowchart.project_root)
            start_step = flowchart.get_start()
            start_step_dict = start_step.step_to_dictionary()
            
            agent.generate(self.flowchart_dict, start_step_dict)
            
            self.finished.emit(True, "Code generated successfully!")
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.finished.emit(False, f"Code generation failed: {e}")
            

def on_generate_code(root):
    """Generate code from flowchart."""
    from PyQt6.QtWidgets import QApplication
    
    cache = load_cache()
    project_id = cache.get("current_project_id")
    
    if not project_id:
        QMessageBox.warning(None, "Error", "No project loaded!")
        return
    
    appdata_root = os.path.join(os.getenv("APPDATA", ""), "SVCA")
    flowchart_path = os.path.join(appdata_root, f"{project_id}.flowchart.json")
    
    if not os.path.exists(flowchart_path):
        QMessageBox.warning(None, "Error", "Flowchart file not found!")
        return
    
    try:
        with open(flowchart_path, 'r', encoding='utf-8') as f:
            flowchart_dict = json.load(f)
    except Exception as e:
        QMessageBox.critical(None, "Error", f"Failed to load flowchart: {e}")
        return
    
    project_root = flowchart_dict.get('project_root', '')
    if not project_root:
        QMessageBox.critical(None, "Error", "Project root not found in flowchart data")
        return
    
    # ✅ Show loading screen IMMEDIATELY
    loading = LoadingScreen(root, "Generating code...")
    loading.show()
    QApplication.processEvents()  # Force immediate display
    
    # ✅ Create worker thread
    worker = CodeGenerationWorker(flowchart_dict, project_root)
    
    # ✅ Connect completion signal
    def on_finished(success, message):
        loading.close()
        if success:
            QMessageBox.information(None, "Success", message)
            
            # ✅ IMPROVED: Find and call the callback by walking up widget tree
            callback_found = False
            widget = root
            
            # Try up to 10 levels up the widget tree
            for level in range(10):
                if not widget:
                    break
                
                # Check if this widget has the callback
                if hasattr(widget, 'on_code_generated') and widget.on_code_generated:
                    print(f"✓ Found callback on {type(widget).__name__} (level {level})")
                    widget.on_code_generated()
                    callback_found = True
                    break
                
                # Move to parent
                widget = widget.parent()
            
            if not callback_found:
                print("⚠ Warning: on_code_generated callback not found!")
                print("   Code was generated successfully but cannot navigate automatically.")
        else:
            QMessageBox.critical(None, "Error", message)
    
    worker.finished.connect(on_finished)
    
    # ✅ Start generation in background
    worker.start()
    
    # Store worker reference so it doesn't get garbage collected
    root.worker = worker

class CanvaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("CanvaWidget")
        self.on_code_generated = None  # ✅ Store callback
        
        self.setStyleSheet("""
            QWidget#CanvaWidget { background: #0f172a; }
            QWidget#CanvaPage { background: #0f172a; }
            QWidget#Canvas { background: #0b1f3a; }
            QScrollArea#CanvasScroll { background: #0b1f3a; border: none; }
            QWidget#DetailsPanel { background: #1e293b; border-left: 1px solid #334155; }
            QPushButton#ToolbarButton { background: #1e293b; color: #e2e8f0; border: 1px solid #334155; border-radius: 6px; padding: 8px 16px; font-size: 13px; }
            QPushButton#ToolbarButton:hover { background: #334155; }
            QPushButton#PrimaryButton { background: #2563eb; color: white; border: none; border-radius: 6px; padding: 8px 20px; font-size: 13px; font-weight: 600; }
            QPushButton#PrimaryButton:hover { background: #1d4ed8; }
        """)
        
        cache = load_cache()
        project_id = cache.get("current_project_id")
        flowchart_data = None
        
        if project_id:
            appdata_root = os.path.join(os.getenv("APPDATA", ""), "SVCA")
            flowchart_path = os.path.join(appdata_root, f"{project_id}.flowchart.json")
            
            if os.path.exists(flowchart_path):
                try:
                    with open(flowchart_path, "r", encoding="utf-8") as f:
                        flowchart_data = json.load(f)
                except Exception as e:
                    print(f"Error loading flowchart: {e}")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        canvas_widget = build_canva(flowchart_data)
        self.canvas_widget = canvas_widget  # ✅ Store reference
        layout.addWidget(canvas_widget)
    
    def showEvent(self, event):
        if self.parent():
            self.setGeometry(self.parent().rect())
        super().showEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = build_canva()
    window.show()
    sys.exit(app.exec())
