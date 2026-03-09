from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QCheckBox,
)
from PyQt6.QtGui import QFont, QColor
from PyQt6.Qsci import QsciScintilla


def build_editor_panel(on_save):
    editor_panel = QWidget()
    editor_layout = QVBoxLayout(editor_panel)
    editor_layout.setContentsMargins(10, 10, 10, 0)  # No bottom margin

    current_file_label = QLabel("No file selected")
    current_file_label.setObjectName("CurrentFileLabel")
    editor_layout.addWidget(current_file_label)

    find_row = QHBoxLayout()
    find_label = QLabel("Find")
    find_label.setObjectName("FindLabel")
    find_input = QLineEdit()
    find_input.setObjectName("FindInput")
    find_input.setPlaceholderText("Search in file...")
    find_prev_btn = QPushButton("Prev")
    find_prev_btn.setObjectName("FindButton")
    find_next_btn = QPushButton("Next")
    find_next_btn.setObjectName("FindButton")
    find_case = QCheckBox("Case")
    find_case.setObjectName("FindCase")

    find_row.addWidget(find_label)
    find_row.addWidget(find_input, stretch=1)
    find_row.addWidget(find_prev_btn)
    find_row.addWidget(find_next_btn)
    find_row.addWidget(find_case)
    find_bar = QWidget()
    find_bar.setObjectName("FindBar")
    find_bar.setLayout(find_row)
    find_bar.setVisible(False)
    editor_layout.addWidget(find_bar)

    code_editor = QsciScintilla()
    code_editor.setObjectName("CodeEditor")
    code_editor.setUtf8(True)
    code_font = QFont("Cascadia Code", 13)
    code_editor.setFont(code_font)
    code_editor.setMarginsFont(code_font)
    code_editor.setMarginWidth(0, "0000")
    code_editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
    code_editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
    code_editor.setAutoIndent(True)
    code_editor.setIndentationsUseTabs(False)
    code_editor.setTabWidth(4)
    code_editor.setCaretForegroundColor(QColor("#a277ff"))
    code_editor.setCaretLineVisible(True)
    code_editor.setCaretLineBackgroundColor(QColor("#312d45"))
    code_editor.setPaper(QColor("#15141b"))
    code_editor.setColor(QColor("#edecee"))
    code_editor.setSelectionBackgroundColor(QColor("#6b657a"))
    code_editor.setSelectionForegroundColor(QColor("#ffffff"))
    code_editor.setMarginsForegroundColor(QColor("#edecee"))
    code_editor.setMarginsBackgroundColor(QColor("#15141b"))
    code_editor.setIndentationGuides(False)
    editor_layout.addWidget(code_editor)

    save_btn = QPushButton("Save")
    save_btn.setObjectName("SaveButton")
    save_btn.setToolTip("Save file")
    save_btn.clicked.connect(on_save)
    editor_layout.addWidget(save_btn)

    return (
        editor_panel,
        code_editor,
        current_file_label,
        find_bar,
        find_input,
        find_prev_btn,
        find_next_btn,
        find_case,
    )
