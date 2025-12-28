from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QCheckBox
)
from PyQt5.QtGui import QTextCursor, QTextDocument

from ..logging_setup import log


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Find & Replace")

        self.find_label = QLabel("Find:", self)
        self.find_input = QLineEdit(self)

        self.replace_label = QLabel("Replace:", self)
        self.replace_input = QLineEdit(self)

        self.case_sensitive_checkbox = QCheckBox("Case Sensitive", self)

        self.find_next_button = QPushButton("Find Next", self)
        self.replace_button = QPushButton("Replace", self)
        self.replace_all_button = QPushButton("Replace All", self)
        self.close_button = QPushButton("Close", self)

        self.find_next_button.clicked.connect(self.find_next)
        self.replace_button.clicked.connect(self.replace)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()

        row1 = QHBoxLayout()
        row1.addWidget(self.find_label)
        row1.addWidget(self.find_input)
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(self.replace_label)
        row2.addWidget(self.replace_input)
        layout.addLayout(row2)

        layout.addWidget(self.case_sensitive_checkbox)

        buttons = QHBoxLayout()
        buttons.addWidget(self.find_next_button)
        buttons.addWidget(self.replace_button)
        buttons.addWidget(self.replace_all_button)
        buttons.addWidget(self.close_button)

        layout.addLayout(buttons)
        self.setLayout(layout)

    def _get_editor(self):
        editor = self.parent.get_current_text_edit() if self.parent else None
        if not editor:
            QMessageBox.warning(self, "No Text Field Selected", "Please select a text field to search.")
        return editor

    def find_next(self):
        text_to_find = self.find_input.text()
        if not text_to_find:
            return

        editor = self._get_editor()
        if not editor:
            return

        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

        found = editor.find(text_to_find, options)
        if not found:
            cursor = editor.textCursor()
            cursor.movePosition(QTextCursor.Start)
            editor.setTextCursor(cursor)

            found = editor.find(text_to_find, options)
            if not found:
                log.info("Не найдено: %r", text_to_find)
                QMessageBox.information(self, "Not Found", "Text not found.")

    def replace(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        if not text_to_find:
            return

        editor = self._get_editor()
        if not editor:
            return

        cursor = editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == text_to_find:
            cursor.insertText(replace_with)
            editor.setTextCursor(cursor)
            self.find_next()
        else:
            self.find_next()

    def replace_all(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        if not text_to_find:
            return

        editor = self._get_editor()
        if not editor:
            return

        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

        cursor = editor.textCursor()
        cursor.beginEditBlock()

        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)

        replaced = 0
        while editor.find(text_to_find, options):
            c = editor.textCursor()
            c.insertText(replace_with)
            replaced += 1

        cursor.endEditBlock()
        QMessageBox.information(self, "Replace All", f"Replaced {replaced} occurrences.")
