from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton,
    QListWidget, QHBoxLayout, QInputDialog
)


class EditStepDialog(QDialog):
    def __init__(self, step_data, parent=None):
        super().__init__(parent)
        self.step_data = step_data
        self.setWindowTitle("Edit Step")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # Step ID (read-only)
        layout.addWidget(QLabel("Step ID:"))
        self.id_label = QLabel(step_data.get('id', ''))
        self.id_label.setStyleSheet("color: #94a3b8; font-weight: bold;")
        layout.addWidget(self.id_label)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_input = QTextEdit()
        self.desc_input.setPlainText(step_data.get('description', ''))
        self.desc_input.setFixedHeight(100)
        layout.addWidget(self.desc_input)
        
        # Filenames
        layout.addWidget(QLabel("Files to Generate:"))
        self.files_list = QListWidget()
        self.files_list.addItems(step_data.get('filenames', []))
        layout.addWidget(self.files_list)
        
        file_buttons = QHBoxLayout()
        add_file_btn = QPushButton("Add File")
        remove_file_btn = QPushButton("Remove File")
        add_file_btn.clicked.connect(self.add_file)
        remove_file_btn.clicked.connect(self.remove_file)
        file_buttons.addWidget(add_file_btn)
        file_buttons.addWidget(remove_file_btn)
        layout.addLayout(file_buttons)
        
        # Commands
        layout.addWidget(QLabel("Commands:"))
        self.commands_input = QTextEdit()
        # FIX: Use single backslash for newline
        self.commands_input.setPlainText('\n'.join(step_data.get('command', [])))
        self.commands_input.setFixedHeight(80)
        layout.addWidget(self.commands_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        cancel_btn = QPushButton("Cancel")
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
    
    def add_file(self):
        filename, ok = QInputDialog.getText(self, "Add File", "Filename:")
        if ok and filename:
            self.files_list.addItem(filename)
    
    def remove_file(self):
        current = self.files_list.currentRow()
        if current >= 0:
            self.files_list.takeItem(current)
    
    def get_step_data(self):
        """Return updated step data."""
        return {
            'id': self.step_data['id'],
            'description': self.desc_input.toPlainText(),
            'filenames': [self.files_list.item(i).text() 
                         for i in range(self.files_list.count())],
            # FIX: Use single backslash for newline
            'command': self.commands_input.toPlainText().split('\n'),
            'files_to_import': self.step_data.get('files_to_import', []),
            'children': self.step_data.get('children', [])
        }
