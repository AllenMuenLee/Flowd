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
from PyQt6.Qsci import QsciScintilla, QsciLexerPython


def apply_editor_theme(code_editor: QsciScintilla) -> None:
    if not code_editor:
        return

    print("apply theme")
    code_editor.setObjectName("CodeEditor")
    code_editor.setUtf8(True)
    code_font = QFont("Cascadia Code", 14)
    code_editor.setFont(code_font)
    code_editor.setMarginsFont(code_font)
    code_editor.setMarginWidth(0, "0000")
    code_editor.setMarginType(0, QsciScintilla.MarginType.NumberMargin)
    code_editor.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)
    code_editor.setAutoIndent(True)
    code_editor.setIndentationsUseTabs(False)
    code_editor.setTabWidth(4)
    code_editor.setPaper(QColor("#10141c"))
    code_editor.setColor(QColor("#e7e9ee"))
    code_editor.setCaretForegroundColor(QColor("#3a7bff"))
    code_editor.setCaretLineVisible(True)
    code_editor.setCaretLineBackgroundColor(QColor("#101820"))
    code_editor.setSelectionBackgroundColor(QColor("#2a3446"))
    code_editor.setSelectionForegroundColor(QColor("#ffffff"))
    code_editor.setMarginsForegroundColor(QColor("#e7e9ee"))
    code_editor.setMarginsBackgroundColor(QColor("#10141c"))
    code_editor.zoomTo(10)
    code_editor.setExtraAscent(-5)
    code_editor.setExtraDescent(-5)


def apply_default_lexer(code_editor: QsciScintilla) -> None:
    if not code_editor:
        return
    lexer = QsciLexerPython(code_editor)
    font = code_editor.font()
    lexer.setDefaultFont(font)
    lexer.setDefaultPaper(QColor("#10141c"))
    lexer.setDefaultColor(QColor("#e7e9ee"))
    try:
        for style in range(128):
            lexer.setPaper(QColor("#10141c"), style)
            lexer.setColor(QColor("#e7e9ee"), style)
            lexer.setFont(font, style)
    except Exception:
        pass
    code_editor.setLexer(lexer)


def build_editor_panel(on_save):
    editor_panel = QWidget()
    editor_layout = QVBoxLayout(editor_panel)
    editor_layout.setContentsMargins(10, 10, 10, 0)

    code_editor = QsciScintilla()
    apply_editor_theme(code_editor)
    apply_default_lexer(code_editor)
    code_editor.setIndentationGuides(False)
    editor_layout.addWidget(code_editor)

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

    save_btn = QPushButton("Save")
    save_btn.setObjectName("SaveButton")
    save_btn.setToolTip("Save file")
    save_btn.clicked.connect(on_save)
    editor_layout.addWidget(save_btn)

    print("build editor")

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
