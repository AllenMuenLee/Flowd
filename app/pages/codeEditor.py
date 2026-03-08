cthimport os
import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
    QPushButton, QListWidget, QSplitter, QLabel,
    QMessageBox, QInputDialog, QFrame, QApplication, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QEvent
from PyQt6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter
from src.utils.CacheMng import load_cache
from app.pages.loadingScreen import LoadingScreen
import src.core.Terminal as Terminal


class PythonHighlighter(QSyntaxHighlighter):
    """Simple syntax highlighter for Python code."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Define highlighting rules
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#c678dd"))  # Purple
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            'def', 'class', 'import', 'from', 'if', 'else', 'elif',
            'for', 'while', 'return', 'try', 'except', 'with', 'as',
            'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is',
            'async', 'await', 'break', 'continue', 'pass', 'raise'
        ]
        for word in keywords:
            pattern = f'\\b{word}\\b'
            self.highlighting_rules.append((pattern, keyword_format))
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#98c379"))  # Green
        self.highlighting_rules.append((r'"[^"\\]*(\\.[^"\\]*)*"', string_format))
        self.highlighting_rules.append((r"'[^'\\]*(\\.[^'\\]*)*'", string_format))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#5c6370"))  # Gray
        self.highlighting_rules.append((r'#[^\n]*', comment_format))
        
        # Functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#61afef"))  # Blue
        self.highlighting_rules.append((r'\bdef\s+(\w+)', function_format))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#d19a66"))  # Orange
        self.highlighting_rules.append((r'\b[0-9]+\b', number_format))
    
    def highlightBlock(self, text):
        import re
        for pattern, format_style in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), format_style)


# ============================================================================
# AIFixWorker class - CURRENTLY DISABLED
# This class was used for the "AI Fix Code" button functionality
# Keeping it commented out for future reference when implementing debugger improvements
# ============================================================================
#
# class AIFixWorker(QThread):
#     """Worker thread for AI code fixing using Debugger (WITHOUT langchain dependencies)."""
#     finished = pyqtSignal(bool, str)
#     progress = pyqtSignal(str)
#     
#     def __init__(self, project_root, flowchart_data, error_message=None):
#         super().__init__()
#         self.project_root = project_root
#         self.flowchart_data = flowchart_data
#         self.error_message = error_message
#     
#     def run(self):
#         try:
#             # Import the debugger class
#             from src.core.Debugger import debugger
#             
#             self.progress.emit("Initializing debugger...")
#             project_name = os.path.basename(self.project_root)
#             
#             # Create a new instance of the debugger class
#             debug_agent = debugger(project_name)
#             
#             if self.error_message:
#                 # Fix specific error
#                 self.progress.emit("Analyzing error message...")
#                 ai_response = debug_agent.extract_error_nova(self.error_message)
#                 
#                 self.progress.emit("Parsing error files...")
#                 debug_agent.parse_error_files(ai_response)
#                 
#                 self.progress.emit("Generating fixes...")
#                 edit = debug_agent.generate_edits(self.error_message)
#                 
#                 self.progress.emit("Applying fixes...")
#                 debug_agent.string_to_edit(edit)
#                 debug_agent.apply_edits()
#                 
#                 self.finished.emit(True, "Code fixes applied successfully!")
#             else:
#                 # General code review
#                 self.progress.emit("Performing general code review...")
#                 self.finished.emit(True, "Code analysis complete!")
#                 
#         except ImportError as e:
#             # ✅ Better error message for missing dependencies
#             missing_module = str(e).split("'")[1] if "'" in str(e) else "unknown"
#             self.finished.emit(
#                 False, 
#                 f"Missing dependency: {missing_module}\n\n"
#                 f"Please install it with:\n"
#                 f"pip install {missing_module}"
#             )
#         except Exception as e:
#             import traceback
#             traceback.print_exc()
#             self.finished.emit(False, f"Failed to fix code: {e}")
# ============================================================================


class AIChatWorker(QThread):
    """Worker thread for AI chat responses."""
    finished = pyqtSignal(str)
    
    def __init__(self, project_root, flowchart_data, user_message, conversation_history):
        super().__init__()
        self.project_root = project_root
        self.flowchart_data = flowchart_data
        self.user_message = user_message
        self.conversation_history = conversation_history
    
    def run(self):
        try:
            from openai import OpenAI
            from dotenv import load_dotenv
            import src.utils.SymbolExt as SymbolExt
            
            load_dotenv()
            
            # Create client with timeout settings
            client = OpenAI(
                api_key=os.getenv("NOVA_API_KEY"),
                base_url="https://api.nova.amazon.com/v1",
                timeout=60.0  # 60 second timeout
            )
            
            # Get project context
            ast_map = {}
            ast_map = SymbolExt.initialize_ast_map(self.project_root, ast_map)
            
            # Build context from project files
            context_lines = []
            for file_path, symbols in ast_map.items():
                rel_path = os.path.relpath(file_path, self.project_root)
                context_lines.append(f"\n## File: {rel_path}")
                
                if symbols:
                    for symbol in symbols[:10]:  # Limit to first 10 symbols per file
                        context_lines.append(
                            f"- [{symbol.get('kind', 'symbol')}] "
                            f"{symbol.get('name', '?')} "
                            f"(line {symbol.get('line', '?')})"
                        )
            
            context = "\n".join(context_lines)
            
            # Build conversation with context
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a helpful coding assistant. You have access to the user's project structure and code.
                    
PROJECT CONTEXT:
{context}

FLOWCHART:
Name: {self.flowchart_data.get('name', 'Unknown')}
Framework: {self.flowchart_data.get('framework', 'Unknown')}
Steps: {len(self.flowchart_data.get('steps', {}))}

Answer the user's questions about their code, help debug issues, and provide suggestions.
Be concise and helpful. Reference specific files and functions when relevant."""
                }
            ]
            
            # Add conversation history
            messages.extend(self.conversation_history)
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": self.user_message
            })
            
            # Call AI with retry logic
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    response = client.chat.completions.create(
                        model="nova-pro-v1",
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000
                    )
                    
                    ai_response = response.choices[0].message.content
                    self.finished.emit(ai_response)
                    return
                    
                except Exception as api_error:
                    if attempt < max_retries - 1:
                        # Wait and retry
                        import time
                        time.sleep(1)
                        continue
                    else:
                        # Last attempt failed
                        raise api_error
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            error_msg = str(e)
            
            # Provide helpful error message
            if "DecodingError" in error_msg or "decompressobj" in error_msg:
                self.finished.emit(
                    "Connection issue with AI service. This is usually temporary.\n\n"
                    "Try again in a moment, or ask a simpler question."
                )
            elif "timeout" in error_msg.lower():
                self.finished.emit(
                    "Request timed out. The AI service is taking too long to respond.\n\n"
                    "Try a shorter question."
                )
            else:
                self.finished.emit(f"Error: {error_msg}")


class ChatbotWidget(QWidget):
    """Chatbot sidebar widget with AI integration."""
    
    def __init__(self, project_root, flowchart_data, parent=None):
        super().__init__(parent)
        self.project_root = project_root
        self.flowchart_data = flowchart_data
        self.conversation_history = []
        self.current_worker = None
        
        self.setObjectName("ChatbotWidget")
        self.setFixedWidth(350)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel("AI Assistant")
        title.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #e2e8f0;
            padding: 10px;
        """)
        layout.addWidget(title)
        
        # Chat history
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setStyleSheet("""
            QTextEdit {
                background: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
            }
        """)
        layout.addWidget(self.chat_history)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QTextEdit()
        self.input_field.setMaximumHeight(60)
        self.input_field.setPlaceholderText("Ask about your code...")
        self.input_field.setStyleSheet("""
            QTextEdit {
                background: #1e293b;
                color: #e2e8f0;
                border: 1px solid #334155;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
        """)
        input_layout.addWidget(self.input_field)
        
        self.send_btn = QPushButton("Send")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #1d4ed8;
            }
            QPushButton:disabled {
                background: #64748b;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_btn)
        
        layout.addLayout(input_layout)
        
        # Store welcome message flag
        self._welcome_shown = False
    
    def showEvent(self, event):
        """Show welcome message when chat is first opened."""
        super().showEvent(event)
        if not self._welcome_shown:
            self._welcome_shown = True
            self.chat_history.append(
                "<b style='color: #60a5fa;'>AI:</b> "
                "Hello! I'm your AI coding assistant. I can help you with:\n"
                "• Understanding your code structure\n"
                "• Debugging issues\n"
                "• Suggesting improvements\n"
                "• Answering questions about your project\n\n"
                "How can I help you today?"
            )
    
    def closeEvent(self, event):
        """Clean up threads when widget is closed."""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.terminate()
            self.current_worker.wait(1000)  # Wait up to 1 second
        super().closeEvent(event)
    
    def send_message(self):
        message = self.input_field.toPlainText().strip()
        if not message or self.current_worker:
            return
        
        # Add user message to history
        self.chat_history.append(f"<b style='color: #e2e8f0;'>You:</b> {message}")
        self.input_field.clear()
        self.send_btn.setEnabled(False)
        
        # Show thinking indicator
        self.chat_history.append("<b style='color: #60a5fa;'>AI:</b> <i>Thinking...</i>")
        
        # Create worker
        self.current_worker = AIChatWorker(
            self.project_root,
            self.flowchart_data,
            message,
            self.conversation_history
        )
        
        def on_finished(response):
            # Remove "Thinking..." message
            cursor = self.chat_history.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.select(cursor.SelectionType.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.deletePreviousChar()  # Remove newline
            
            # Add AI response
            self.chat_history.append(f"<b style='color: #60a5fa;'>AI:</b> {response}\n")
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append({"role": "assistant", "content": response})
            
            # Re-enable send button
            self.send_btn.setEnabled(True)
            self.current_worker = None
        
        self.current_worker.finished.connect(on_finished)
        self.current_worker.start()


def build_code_editor(flowchart_data=None, on_back_to_canvas=None) -> QWidget:
    """Build the code editor view with improved layout."""
    
    root = QWidget()
    root.setObjectName("CodeEditorPage")
    
    # ✅ Main layout - vertical to stack toolbar, content, and terminal
    main_layout = QVBoxLayout(root)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)
    
    # Top toolbar
    toolbar = QWidget()
    toolbar.setObjectName("Toolbar")
    toolbar.setStyleSheet("""
        QWidget#Toolbar {
            background: #1e293b;
            border-bottom: 1px solid #334155;
        }
    """)
    toolbar_layout = QHBoxLayout(toolbar)
    toolbar_layout.setContentsMargins(10, 10, 10, 10)
    
    # Buttons
    refine_btn = QPushButton("← Refine Flowchart")
    refine_btn.setObjectName("ToolbarButton")
    refine_btn.clicked.connect(lambda: on_back_to_canvas() if on_back_to_canvas else None)
    
    open_terminal_btn = QPushButton("🖥 Open Terminal")
    open_terminal_btn.setObjectName("ToolbarButton")
    open_terminal_btn.setToolTip("Open system terminal in project folder")
    open_terminal_btn.clicked.connect(lambda: open_system_terminal(
        flowchart_data.get('project_root', '') if flowchart_data else ''
    ))
    
    run_btn = QPushButton("▶ Run Project")
    run_btn.setObjectName("PrimaryButton")
    run_btn.clicked.connect(lambda: on_run_project(root))
    
    # ai_fix_btn = QPushButton("🤖 AI Fix Code")
    # ai_fix_btn.setObjectName("PrimaryButton")
    # ai_fix_btn.clicked.connect(lambda: on_ai_fix(root))
    
    chatbot_btn = QPushButton("💬 AI Chat")
    chatbot_btn.setObjectName("ToolbarButton")
    chatbot_btn.setCheckable(True)
    chatbot_btn.clicked.connect(lambda checked: toggle_chatbot(root, checked))
    
    toolbar_layout.addWidget(refine_btn)
    toolbar_layout.addWidget(open_terminal_btn)
    toolbar_layout.addStretch()
    toolbar_layout.addWidget(run_btn)
    # toolbar_layout.addWidget(ai_fix_btn)
    toolbar_layout.addWidget(chatbot_btn)
    
    main_layout.addWidget(toolbar)
    
    # ✅ IMPROVED: Main content area (file browser + editor + chat)
    content_splitter = QSplitter(Qt.Orientation.Horizontal)
    
    # ✅ Left: File browser (narrower, extends to bottom)
    file_panel = QWidget()
    file_panel.setObjectName("FilePanel")
    file_layout = QVBoxLayout(file_panel)
    file_layout.setContentsMargins(10, 10, 10, 0)  # No bottom margin
    
    file_label = QLabel("Files")
    file_label.setStyleSheet("""
        font-size: 13px;
        font-weight: bold;
        color: #e2e8f0;
        padding-bottom: 5px;
    """)
    file_layout.addWidget(file_label)
    
    file_list = QListWidget()
    file_list.setObjectName("FileList")
    file_list.setStyleSheet("""
        QListWidget {
            background: #0b1f3a;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 5px;
            font-size: 12px;
        }
        QListWidget::item {
            padding: 6px;
            border-radius: 4px;
        }
        QListWidget::item:hover {
            background: #1e293b;
        }
        QListWidget::item:selected {
            background: #2563eb;
        }
    """)
    file_list.itemClicked.connect(lambda item: load_file(root, item.text()))
    file_layout.addWidget(file_list)
    
    file_panel.setMinimumWidth(180)  # ✅ Narrower
    file_panel.setMaximumWidth(220)  # ✅ Narrower
    content_splitter.addWidget(file_panel)
    
    # ✅ Middle: Code editor (MUCH BIGGER)
    editor_panel = QWidget()
    editor_layout = QVBoxLayout(editor_panel)
    editor_layout.setContentsMargins(10, 10, 10, 0)  # No bottom margin
    
    # Current file label
    current_file_label = QLabel("No file selected")
    current_file_label.setObjectName("CurrentFileLabel")
    current_file_label.setStyleSheet("""
        font-size: 12px;
        color: #94a3b8;
        padding-bottom: 5px;
    """)
    editor_layout.addWidget(current_file_label)
    
    # Code editor
    code_editor = QTextEdit()
    code_editor.setObjectName("CodeEditor")
    code_editor.setStyleSheet("""
        QTextEdit {
            background: #0b1f3a;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 10px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            line-height: 1.5;
        }
    """)
    
    # Add syntax highlighting
    highlighter = PythonHighlighter(code_editor.document())
    
    editor_layout.addWidget(code_editor)
    
    # Save button
    save_btn = QPushButton("💾 Save File")
    save_btn.setObjectName("SaveButton")
    save_btn.setStyleSheet("""
        QPushButton#SaveButton {
            background: #059669;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 14px;
            font-weight: 600;
            font-size: 12px;
        }
        QPushButton#SaveButton:hover {
            background: #047857;
        }
    """)
    save_btn.clicked.connect(lambda: save_file(root))
    editor_layout.addWidget(save_btn)
    
    content_splitter.addWidget(editor_panel)
    
    # ✅ Set stretch factors (file browser : editor : chat = 1 : 4 : 1.5)
    content_splitter.setStretchFactor(0, 1)   # File browser
    content_splitter.setStretchFactor(1, 4)   # Editor (much bigger!)
    
    main_layout.addWidget(content_splitter, stretch=3)  # Give more space to content
    
    # ✅ IMPROVED: Terminal at the very bottom (smaller, with input)
    terminal_container = QWidget()
    terminal_container.setObjectName("TerminalContainer")
    terminal_container.setStyleSheet("""
        QWidget#TerminalContainer {
            background: #1e293b;
            border-top: 1px solid #334155;
        }
    """)
    terminal_layout = QVBoxLayout(terminal_container)
    terminal_layout.setContentsMargins(10, 8, 10, 8)
    terminal_layout.setSpacing(5)
    
    # Terminal header
    terminal_header = QHBoxLayout()
    
    terminal_label = QLabel("Terminal")
    terminal_label.setStyleSheet("""
        font-size: 12px;
        font-weight: bold;
        color: #e2e8f0;
    """)
    terminal_header.addWidget(terminal_label)
    
    terminal_header.addStretch()
    
    clear_terminal_btn = QPushButton("Clear")
    clear_terminal_btn.setStyleSheet("""
        QPushButton {
            background: #334155;
            color: #e2e8f0;
            border: none;
            border-radius: 4px;
            padding: 3px 10px;
            font-size: 11px;
        }
        QPushButton:hover {
            background: #475569;
        }
    """)
    clear_terminal_btn.clicked.connect(lambda: root.terminal.clear())
    terminal_header.addWidget(clear_terminal_btn)
    
    terminal_layout.addLayout(terminal_header)
    
    # Terminal output (read-only display)
    terminal = QTextEdit()
    terminal.setObjectName("Terminal")
    terminal.setReadOnly(True)
    terminal.setMaximumHeight(120)  # ✅ Smaller terminal
    terminal.setStyleSheet("""
        QTextEdit {
            background: #000000;
            color: #00ff00;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px;
            font-family: 'Courier New', monospace;
            font-size: 11px;
        }
    """)
    terminal_layout.addWidget(terminal)
    
    # ✅ NEW: Terminal input (for typing commands)
    terminal_input_layout = QHBoxLayout()
    
    terminal_prompt = QLabel("$")
    terminal_prompt.setStyleSheet("""
        color: #00ff00;
        font-family: 'Courier New', monospace;
        font-size: 12px;
        font-weight: bold;
    """)
    terminal_input_layout.addWidget(terminal_prompt)
    
    terminal_input = QLineEdit()
    terminal_input.setObjectName("TerminalInput")
    terminal_input.setPlaceholderText("Type command and press Enter...")
    terminal_input.setStyleSheet("""
        QLineEdit {
            background: #000000;
            color: #00ff00;
            border: 1px solid #334155;
            border-radius: 4px;
            padding: 5px 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
        }
        QLineEdit:focus {
            border: 1px solid #2563eb;
        }
    """)
    terminal_input_layout.addWidget(terminal_input)
    
    run_command_btn = QPushButton("Run")
    run_command_btn.setStyleSheet("""
        QPushButton {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 15px;
            font-size: 11px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #1d4ed8;
        }
    """)
    run_command_btn.clicked.connect(lambda: execute_terminal_command(root))
    terminal_input_layout.addWidget(run_command_btn)
    
    # Stop button (hidden by default)
    stop_process_btn = QPushButton("⏹ Stop")
    stop_process_btn.setStyleSheet("""
        QPushButton {
            background: #dc2626;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 5px 15px;
            font-size: 11px;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #b91c1c;
        }
    """)
    stop_process_btn.clicked.connect(lambda: stop_running_process(root))
    stop_process_btn.hide()  # Hidden by default
    terminal_input_layout.addWidget(stop_process_btn)
    
    terminal_layout.addLayout(terminal_input_layout)
    
    main_layout.addWidget(terminal_container, stretch=1)  # Less space for terminal
    
    # Store references
    root.file_list = file_list
    root.code_editor = code_editor
    root.current_file_label = current_file_label
    root.terminal = terminal
    root.terminal_input = terminal_input
    root.stop_process_btn = stop_process_btn  # NEW: reference to stop button
    root.content_splitter = content_splitter
    root.flowchart_data = flowchart_data
    root.current_file = None
    root.chatbot_widget = None
    root.chatbot_btn = chatbot_btn
    root.running_process = None  # NEW: track running process
    
    # ✅ NEW: Connect Enter key in terminal input
    terminal_input.returnPressed.connect(lambda: execute_terminal_command(root))
    
    # Apply dark theme
    root.setStyleSheet("""
        QWidget#CodeEditorPage {
            background: #0f172a;
        }
        QWidget#FilePanel {
            background: #1e293b;
        }
        QPushButton#ToolbarButton {
            background: #1e293b;
            color: #e2e8f0;
            border: 1px solid #334155;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
        }
        QPushButton#ToolbarButton:hover {
            background: #334155;
        }
        QPushButton#ToolbarButton:checked {
            background: #2563eb;
            border-color: #2563eb;
        }
        QPushButton#PrimaryButton {
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 20px;
            font-weight: 600;
        }
        QPushButton#PrimaryButton:hover {
            background: #1d4ed8;
        }
    """)
    
    # Load files
    if flowchart_data:
        load_project_files(root)
    
    return root


def execute_terminal_command(root):
    """Execute command typed in terminal input."""
    command = root.terminal_input.text().strip()
    
    if not command:
        return
    
    # Clear input
    root.terminal_input.clear()
    
    # Show command in terminal
    root.terminal.append(f"$ {command}")
    
    # Get project root
    project_root = ""
    if root.flowchart_data:
        project_root = root.flowchart_data.get('project_root', '')
    
    # Check if this is a long-running command (like python app.py, npm start, etc.)
    long_running_commands = ['python', 'python3', 'node', 'npm', 'flask', 'django', 'uvicorn']
    interactive_patterns = ['input(', 'Scanner', 'readline', 'stdin']
    is_long_running = any(command.startswith(cmd) for cmd in long_running_commands)
    
    # Check if the file being run contains interactive input
    is_interactive = False
    if is_long_running and project_root:
        # Extract filename from command
        parts = command.split()
        if len(parts) > 1:
            filename = parts[1]
            filepath = os.path.join(project_root, filename)
            if os.path.exists(filepath):
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                        is_interactive = any(pattern in content for pattern in interactive_patterns)
                except:
                    pass
    
    if is_interactive:
        root.terminal.append(
            f"\n⚠️  This program requires user input (interactive).\n"
            f"   The built-in terminal cannot handle interactive input.\n\n"
            f"   📌 SOLUTION: Open your system terminal and run:\n"
            f"   cd {project_root}\n"
            f"   {command}\n"
        )
        
        # Ask user if they want to open system terminal
        reply = QMessageBox.question(
            root,
            "Interactive Program Detected",
            f"This program requires user input and cannot run in the built-in terminal.\n\n"
            f"Would you like to open your system terminal?\n\n"
            f"You can then run:\n"
            f"cd {project_root}\n"
            f"{command}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            open_system_terminal(project_root, command)
        return
    
    if is_long_running and not command.endswith('--help') and not command.endswith('--version'):
        root.terminal.append(
            f"⚠️  This looks like a long-running command (web server, etc.)\n"
            f"   Use the ⏹ Stop button to stop it.\n"
        )
        # Show stop button
        root.stop_process_btn.show()
    
    # Execute command in background thread
    import subprocess
    import threading
    
    def run_command():
        try:
            QApplication.processEvents()
            
            # Start process
            process = subprocess.Popen(
                command,
                shell=True,
                cwd=project_root if project_root else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Store process reference for cleanup
            root.running_process = process
            
            # Read output line by line
            for line in iter(process.stdout.readline, ''):
                if line:
                    root.terminal.append(line.rstrip())
                    QApplication.processEvents()
                
                # Check if process was killed
                if root.running_process is None:
                    break
            
            process.wait()
            root.running_process = None
            root.stop_process_btn.hide()
            
            if process.returncode == 0:
                root.terminal.append(f"\n✓ Process exited successfully\n")
            elif process.returncode == -15 or process.returncode == -9:
                root.terminal.append(f"\n⏹ Process stopped by user\n")
            else:
                root.terminal.append(f"\n✗ Process exited with code {process.returncode}\n")
                
        except Exception as e:
            root.terminal.append(f"Error: {e}\n")
            root.running_process = None
            root.stop_process_btn.hide()
    
    # Start thread
    thread = threading.Thread(target=run_command, daemon=True)
    thread.start()


def open_system_terminal(project_root, command=None):
    """Open the system terminal in the project directory."""
    import subprocess
    import platform
    
    system = platform.system()
    
    try:
        if system == "Darwin":  # macOS
            # Open Terminal app and cd to project
            script = f'cd "{project_root}"'
            if command:
                script += f' && {command}'
            subprocess.Popen([
                'osascript', '-e',
                f'tell application "Terminal" to do script "{script}"'
            ])
        elif system == "Windows":
            # Open cmd in project directory
            subprocess.Popen(['cmd', '/K', f'cd /d "{project_root}"'])
        else:  # Linux
            # Try common terminal emulators
            terminals = ['gnome-terminal', 'konsole', 'xterm']
            for term in terminals:
                try:
                    subprocess.Popen([term, '--working-directory', project_root])
                    break
                except:
                    continue
    except Exception as e:
        print(f"Failed to open terminal: {e}")


def stop_running_process(root):
    """Stop the currently running terminal process."""
    if root.running_process:
        root.terminal.append("\n⏹ Stopping process...\n")
        try:
            root.running_process.terminate()
            root.running_process = None
            root.stop_process_btn.hide()
        except Exception as e:
            root.terminal.append(f"Error stopping process: {e}\n")


def load_project_files(root):
    """Load all project files (excluding .json) into file list."""
    
    if not root.flowchart_data:
        return
    
    project_root = root.flowchart_data.get('project_root', '')
    if not project_root or not os.path.exists(project_root):
        root.terminal.append("⚠ Project root not found")
        return
    
    root.file_list.clear()
    root.terminal.append(f"$ Loading files from {project_root}")
    
    # Walk through project directory
    file_count = 0
    for dirpath, dirnames, filenames in os.walk(project_root):
        # Skip hidden directories and common ignore patterns
        dirnames[:] = [
            d for d in dirnames 
            if not d.startswith('.') 
            and d not in ['__pycache__', 'node_modules', 'venv', 'env']
        ]
        
        for filename in filenames:
            # Skip .json files and other unwanted files
            if (filename.endswith('.json') or 
                filename.endswith('.pyc') or
                filename.startswith('.')):
                continue
            
            full_path = os.path.join(dirpath, filename)
            relative_path = os.path.relpath(full_path, project_root)
            root.file_list.addItem(relative_path)
            file_count += 1
    
    root.terminal.append(f"$ Loaded {file_count} files\n")


def load_file(root, filename):
    """Load a file into the code editor."""
    
    if not root.flowchart_data:
        return
    
    project_root = root.flowchart_data.get('project_root', '')
    file_path = os.path.join(project_root, filename)
    
    if not os.path.exists(file_path):
        QMessageBox.warning(root, "Error", f"File not found: {filename}")
        return
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        root.code_editor.setPlainText(content)
        root.current_file_label.setText(f"Editing: {filename}")
        root.current_file = file_path
        root.terminal.append(f"$ Opened {filename}")
        
    except Exception as e:
        QMessageBox.critical(root, "Error", f"Failed to load file: {e}")
        root.terminal.append(f"✗ Error loading {filename}: {e}")


def save_file(root):
    """Save the current file."""
    
    if not root.current_file:
        QMessageBox.warning(root, "No File", "No file is currently open.")
        return
    
    try:
        content = root.code_editor.toPlainText()
        
        with open(root.current_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        filename = os.path.basename(root.current_file)
        root.terminal.append(f"✓ Saved {filename}")
        QMessageBox.information(root, "Success", f"File saved: {filename}")
        
    except Exception as e:
        QMessageBox.critical(root, "Error", f"Failed to save file: {e}")
        root.terminal.append(f"✗ Error saving file: {e}")


def on_run_project(root):
    """Run the project and capture output in terminal."""
    
    if not root.flowchart_data:
        QMessageBox.warning(root, "Error", "No project loaded!")
        return
    
    project_root = root.flowchart_data.get('project_root', '')
    
    # Ask user what to run
    main_file, ok = QInputDialog.getText(
        root, 
        "Run Project", 
        "Enter the main file to run (e.g., main.py):",
        text="main.py"
    )
    
    if not ok or not main_file:
        return
    
    main_file_path = os.path.join(project_root, main_file)
    
    if not os.path.exists(main_file_path):
        QMessageBox.warning(root, "Error", f"File not found: {main_file}")
        return
    
    root.terminal.append(f"\n$ Running {main_file}...\n")
    QApplication.processEvents()
    
    try:
        # Determine how to run the file based on extension
        if main_file.endswith('.py'):
            command = f"python {main_file}"
        elif main_file.endswith('.js'):
            command = f"node {main_file}"
        else:
            QMessageBox.warning(root, "Error", "Unsupported file type!")
            return
        
        # Run command
        output = Terminal.run_command(command, cwd=project_root, timeout=30)
        
        # Display output
        if output:
            root.terminal.append(output)
        else:
            root.terminal.append("✓ Process completed with no output")
        
        root.terminal.append("\n$ Process finished\n")
        
    except Exception as e:
        error_msg = str(e)
        root.terminal.append(f"\n✗ Error: {error_msg}\n")

"""
def on_ai_fix(root, error_message=None):
    # Run AI to fix code issues.
    
    if not root.flowchart_data:
        QMessageBox.warning(root, "Error", "No project loaded!")
        return
    
    project_root = root.flowchart_data.get('project_root', '')
    
    loading = LoadingScreen(root, "AI is analyzing your code...")
    loading.show()
    QApplication.processEvents()
    
    # Create worker
    worker = AIFixWorker(project_root, root.flowchart_data, error_message)
    
    def on_progress(message):
        root.terminal.append(f"  {message}")
    
    def on_finished(success, message):
        loading.close()
        if success:
            root.terminal.append(f"✓ {message}\n")
            QMessageBox.information(root, "Success", message)
            
            # Reload current file if one is open
            if root.current_file:
                try:
                    with open(root.current_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    root.code_editor.setPlainText(content)
                    root.terminal.append("✓ Reloaded current file with fixes")
                except:
                    pass
        else:
            root.terminal.append(f"✗ {message}\n")
            QMessageBox.critical(root, "Error", message)
    
    worker.progress.connect(on_progress)
    worker.finished.connect(on_finished)
    worker.start()
    
    # Store worker reference
    root.ai_worker = worker
"""

def toggle_chatbot(root, show):
    """Toggle chatbot sidebar."""
    
    if show:
        # Create and show chatbot
        if not root.chatbot_widget:
            root.chatbot_widget = ChatbotWidget(
                root.flowchart_data.get('project_root', ''),
                root.flowchart_data,
                parent=root
            )
            root.content_splitter.addWidget(root.chatbot_widget)
            # Update stretch factors (must be integers!)
            root.content_splitter.setStretchFactor(2, 2)  # Chat
        root.chatbot_widget.show()
    else:
        # Hide chatbot
        if root.chatbot_widget:
            root.chatbot_widget.hide()


class CodeEditorWidget(QWidget):
    """Main code editor widget wrapper."""
    
    def __init__(self, flowchart_data=None, on_back_to_canvas=None):
        super().__init__()
        self.setObjectName("CodeEditorWidget")
        self.running_process = None  # Track running terminal process
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        editor_widget = build_code_editor(flowchart_data, on_back_to_canvas)
        layout.addWidget(editor_widget)
        
        # Store reference to editor widget for cleanup
        self.editor_widget = editor_widget
    
    def closeEvent(self, event):
        """Clean up running processes when closing."""
        # Kill any running terminal process
        if hasattr(self.editor_widget, 'running_process') and self.editor_widget.running_process:
            try:
                self.editor_widget.running_process.terminate()
                self.editor_widget.running_process.wait(timeout=1)
            except:
                pass
        
        # Clean up worker threads
        if hasattr(self.editor_widget, 'ai_worker'):
            try:
                self.editor_widget.ai_worker.terminate()
                self.editor_widget.ai_worker.wait(1000)
            except:
                pass
        
        # Clean up chatbot
        if hasattr(self.editor_widget, 'chatbot_widget') and self.editor_widget.chatbot_widget:
            try:
                self.editor_widget.chatbot_widget.close()
            except:
                pass
        
        super().closeEvent(event)