from PyQt5.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QCheckBox
)
from PyQt5.QtGui import QTextCursor, QTextDocument

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Find & Replace')

        # Поля ввода для поиска и замены
        self.find_label = QLabel('Find:', self)
        self.find_input = QLineEdit(self)

        self.replace_label = QLabel('Replace:', self)
        self.replace_input = QLineEdit(self)

        # Флажок "Case Sensitive"
        self.case_sensitive_checkbox = QCheckBox('Case Sensitive', self)

        # Кнопки
        self.find_next_button = QPushButton('Find Next', self)
        self.replace_button = QPushButton('Replace', self)
        self.replace_all_button = QPushButton('Replace All', self)
        self.close_button = QPushButton('Close', self)

        # Подключаем сигналы
        self.find_next_button.clicked.connect(self.find_next)
        self.replace_button.clicked.connect(self.replace)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.close_button.clicked.connect(self.close)

        # Макеты
        layout = QVBoxLayout()

        form_layout = QHBoxLayout()
        form_layout.addWidget(self.find_label)
        form_layout.addWidget(self.find_input)
        layout.addLayout(form_layout)

        form_layout2 = QHBoxLayout()
        form_layout2.addWidget(self.replace_label)
        form_layout2.addWidget(self.replace_input)
        layout.addLayout(form_layout2)

        layout.addWidget(self.case_sensitive_checkbox)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.find_next_button)
        button_layout.addWidget(self.replace_button)
        button_layout.addWidget(self.replace_all_button)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def find_next(self):
        text_to_find = self.find_input.text()
        if not text_to_find:
            return

        text_edit = self.parent.last_focused_text_edit
        if not text_edit:
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to search.')
            return

        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

        found = text_edit.find(text_to_find, options)
        if not found:
            # Если ничего не найдено, вернуть курсор в начало текста и повторить поиск
            cursor = text_edit.textCursor()
            cursor.movePosition(QTextCursor.Start)
            text_edit.setTextCursor(cursor)
            found = text_edit.find(text_to_find, options)
            if not found:
                QMessageBox.information(self, 'Not Found', 'Text not found.')

    def replace(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        if not text_to_find:
            return

        text_edit = self.parent.last_focused_text_edit
        if not text_edit:
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to replace.')
            return

        cursor = text_edit.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == text_to_find:
            cursor.insertText(replace_with)
            text_edit.setTextCursor(cursor)
            self.find_next()
        else:
            self.find_next()

    def replace_all(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        if not text_to_find:
            return

        text_edit = self.parent.last_focused_text_edit
        if not text_edit:
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to replace.')
            return

        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

        # Начинаем групповое редактирование
        cursor = text_edit.textCursor()
        cursor.beginEditBlock()
        cursor.movePosition(QTextCursor.Start)
        text_edit.setTextCursor(cursor)

        replaced = 0
        while text_edit.find(text_to_find, options):
            cursor = text_edit.textCursor()
            cursor.insertText(replace_with)
            replaced += 1

        cursor.endEditBlock()
        QMessageBox.information(self, 'Replace All', f'Replaced {replaced} occurrences.')
