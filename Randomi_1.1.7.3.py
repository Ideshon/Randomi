import sys
import re
import random
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit,
    QSplitter, QFileDialog, QSlider, QDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QTextCharFormat, QFont, QTextCursor, QTextDocument
from text_randomizer import TextRandomizer


class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')
        self.loadSettings()
        self.last_focused_text_edit = None  # Для хранения последнего активного текстового поля

        # Ограничения размеров виджетов
        self.delimiter.setMinimumSize(0, 20)
        self.delimiter.setMaximumSize(30, 20)
        self.func_delimiter.setMinimumSize(0, 20)
        self.func_delimiter.setMaximumSize(30, 20)
        self.entry.setMinimumSize(200, 20)
        self.template_label.setMinimumSize(200, 20)
        self.result_output.setMinimumSize(200, 20)
        self.randomize_button.setMinimumSize(80, 20)
        self.save_button.setMinimumSize(50, 20)
        self.load_button.setMinimumSize(50, 20)

        # Элементы управления для изменения размера шрифта
        self.font_size_label = QLabel('Размер шрифта:', self)
        self.font_size_slider = QSlider(Qt.Horizontal, self)
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(24)
        self.font_size_slider.setValue(12)  # Значение по умолчанию
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.font_size_slider.valueChanged.connect(self.changeFontSize)
        self.layout.addWidget(self.font_size_label)
        self.layout.addWidget(self.font_size_slider)

    def changeFontSize(self, value):
        font = self.entry.font()
        font.setPointSize(value)
        self.entry.setFont(font)
        self.result_output.setFont(font)
        self.template_label.setFont(font)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Vertical, self)

        # Поля ввода и вывода
        self.entry = QTextEdit(self)
        self.entry.setFocusPolicy(Qt.StrongFocus)
        self.delimiter = QLineEdit(';', self)
        self.delimiter.setFocusPolicy(Qt.StrongFocus)
        self.func_delimiter = QLineEdit(',', self)
        self.func_delimiter.setFocusPolicy(Qt.StrongFocus)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)
        self.result_output.setFocusPolicy(Qt.StrongFocus)
        self.template_label = QTextEdit('', self)
        self.template_label.setReadOnly(False)
        self.template_label.setFocusPolicy(Qt.StrongFocus)

        # Переопределение событий фокуса
        self.entry.focusInEvent = self.make_focus_in_event(self.entry)
        self.template_label.focusInEvent = self.make_focus_in_event(self.template_label)
        self.result_output.focusInEvent = self.make_focus_in_event(self.result_output)

        # Кнопки
        self.randomize_button = QPushButton('Randomize', self)
        self.save_button = QPushButton('Save', self)
        self.load_button = QPushButton('Load', self)
        self.bold_button = QPushButton('Bold', self)
        self.reset_button = QPushButton('Reset Formatting', self)
        self.find_replace_button = QPushButton('Find & Replace', self)

        # Функции кнопок
        self.randomize_button.clicked.connect(self.randomize_text)
        self.save_button.clicked.connect(self.saveToFile)
        self.load_button.clicked.connect(self.loadFromFile)
        self.bold_button.clicked.connect(self.toggleBold)
        self.reset_button.clicked.connect(self.resetFormatting)
        self.find_replace_button.clicked.connect(self.open_find_replace_dialog)

        # Добавление виджетов в сплиттер
        self.splitter.addWidget(self.entry)
        self.splitter.addWidget(self.result_output)
        self.splitter.addWidget(self.template_label)

        # Горизонтальный макет для кнопок и разделителей
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(QLabel('Delimiter:', self))
        self.hbox.addWidget(self.delimiter)
        self.hbox.addWidget(QLabel('Function Delimiter:', self))
        self.hbox.addWidget(self.func_delimiter)
        self.hbox.addWidget(self.randomize_button)
        self.hbox.addWidget(self.save_button)
        self.hbox.addWidget(self.load_button)
        self.hbox.addStretch(1)

        self.hbox2 = QHBoxLayout()
        self.hbox2.addWidget(self.bold_button)
        self.hbox2.addWidget(self.reset_button)
        self.hbox2.addWidget(self.find_replace_button)

        # Добавление макетов в основной макет
        self.layout.addWidget(self.splitter)
        self.layout.addLayout(self.hbox)
        self.layout.addLayout(self.hbox2)

        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')
        
def make_focus_in_event(self, widget):
    def focus_in_event(event):
        self.last_focused_text_edit = widget
        QTextEdit.focusInEvent(widget, event)

    return focus_in_event


def applyFormattingToSelectedText(self, text_edit):
    cursor = text_edit.textCursor()
    if not cursor.hasSelection():
        return
    char_format = cursor.charFormat()
    is_bold = char_format.font().bold()
    char_format.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)
    cursor.setCharFormat(char_format)


def toggleBold(self):
    text_edit = self.get_current_text_edit()
    if text_edit:
        self.applyFormattingToSelectedText(text_edit)


def resetFormatting(self):
    text_edit = self.get_current_text_edit()
    if text_edit:
        cursor = text_edit.textCursor()
        cursor.select(cursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        text_edit.setTextCursor(cursor)


def randomize_text(self):
    try:
        template = self.entry.toHtml()
        delimiter = self.delimiter.text()
        func_delimiter = self.func_delimiter.text()

        parts = re.split('(<[^>]+>)', template)
        new_parts = []
        for part in parts:
            if part.startswith('<'):
                new_parts.append(part)
            else:
                if delimiter and delimiter != '|':
                    escaped_delim = re.escape(delimiter)
                    part = re.sub(rf'\s*{escaped_delim}\s*', '|', part)

                part = re.sub(
                    r'(\w+)\*(\d+)',
                    lambda m: '{$' + f'MULTIPLY({m.group(1)},{m.group(2)})' + '}',
                    part
                )

                def replace_randwords(match):
                    min_count = match.group(1)
                    max_count = match.group(2)
                    words = match.group(3)
                    return '{$RANDWORDS(' + f'{min_count}{func_delimiter}{max_count}{func_delimiter}{words}' + ')}'

                part = re.sub(r'%(\d+)-(\d+)\((.*?)\)', replace_randwords, part)

                part = self.evaluate_functions_in_text(part, func_delimiter)

                new_parts.append(part)

        randomized_html = ''.join(new_parts)

        text_rnd = TextRandomizer(randomized_html)

        final_html = text_rnd.get_text()

        self.result_output.setHtml(final_html)

    except Exception as e:
        self.result_output.setHtml(f"<p>Error: {str(e)}</p>")
    def make_focus_in_event(self, widget):
        def focus_in_event(event):
            self.last_focused_text_edit = widget
            QTextEdit.focusInEvent(widget, event)
        return focus_in_event

    def applyFormattingToSelectedText(self, text_edit):
        cursor = text_edit.textCursor()
        if not cursor.hasSelection():
            return
        char_format = cursor.charFormat()
        is_bold = char_format.font().bold()
        char_format.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)
        cursor.setCharFormat(char_format)

    def toggleBold(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            self.applyFormattingToSelectedText(text_edit)

    def resetFormatting(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            cursor = text_edit.textCursor()
            cursor.select(cursor.Document)
            cursor.setCharFormat(QTextCharFormat())
            cursor.clearSelection()
            text_edit.setTextCursor(cursor)

    def randomize_text(self):
        try:
            template = self.entry.toHtml()
            delimiter = self.delimiter.text()
            func_delimiter = self.func_delimiter.text()

            parts = re.split('(<[^>]+>)', template)
            new_parts = []
            for part in parts:
                if part.startswith('<'):
                    new_parts.append(part)
                else:
                    if delimiter and delimiter != '|':
                        escaped_delim = re.escape(delimiter)
                        part = re.sub(rf'\s*{escaped_delim}\s*', '|', part)

                    part = re.sub(
                        r'(\w+)\*(\d+)',
                        lambda m: '{$' + f'MULTIPLY({m.group(1)},{m.group(2)})' + '}',
                        part
                    )

                    def replace_randwords(match):
                        min_count = match.group(1)
                        max_count = match.group(2)
                        words = match.group(3)
                        return '{$RANDWORDS(' + f'{min_count}{func_delimiter}{max_count}{func_delimiter}{words}' + ')}'

                    part = re.sub(r'%(\d+)-(\d+)\((.*?)\)', replace_randwords, part)

                    part = self.evaluate_functions_in_text(part, func_delimiter)

                    new_parts.append(part)

            randomized_html = ''.join(new_parts)

            text_rnd = TextRandomizer(randomized_html)

            final_html = text_rnd.get_text()

            self.result_output.setHtml(final_html)

        except Exception as e:
            self.result_output.setHtml(f"<p>Error: {str(e)}</p>")
    def saveToFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;All Files (*)")
        if filePath:
            try:
                data = {
                    'entry': self.entry.toHtml(),
                    'result_output': self.result_output.toHtml(),
                    'template_label': self.template_label.toHtml(),
                    'delimiter': self.delimiter.text(),
                    'func_delimiter': self.func_delimiter.text()
                }
                with open(filePath, 'w', encoding='utf-8') as file:
                    json.dump(data, file, ensure_ascii=False, indent=4)
            except Exception as e:
                self.result_output.setHtml(f"<p>Error saving file: {str(e)}</p>")

    def loadFromFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json);;All Files (*)")
        if filePath:
            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                self.entry.setHtml(data.get('entry', ''))
                self.result_output.setHtml(data.get('result_output', ''))
                self.template_label.setHtml(data.get('template_label', ''))
                self.delimiter.setText(data.get('delimiter', ';'))
                self.func_delimiter.setText(data.get('func_delimiter', ','))
            except Exception as e:
                self.result_output.setHtml(f"<p>Error loading file: {str(e)}</p>")

    def loadSettings(self):
        entry_html = self.settings.value('entry', '')
        result_html = self.settings.value('result_output', '')
        template_html = self.settings.value('template_label', '')
        delimiter = self.settings.value('delimiter', ';')
        func_delimiter = self.settings.value('func_delimiter', ',')

        if entry_html:
            self.entry.setHtml(entry_html)
        if result_html:
            self.result_output.setHtml(result_html)
        if template_html:
            self.template_label.setHtml(template_html)
        if delimiter:
            self.delimiter.setText(delimiter)
        if func_delimiter:
            self.func_delimiter.setText(func_delimiter)

    def saveSettings(self):
        self.settings.setValue('template_label', self.template_label.toHtml())
        self.settings.setValue('entry', self.entry.toHtml())
        self.settings.setValue('result_output', self.result_output.toHtml())
        self.settings.setValue('delimiter', self.delimiter.text())
        self.settings.setValue('func_delimiter', self.func_delimiter.text())

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

    def open_find_replace_dialog(self):
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()

    def get_current_text_edit(self):
        return self.last_focused_text_edit

class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super(FindReplaceDialog, self).__init__(parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Find & Replace')

        self.find_label = QLabel('Find:', self)
        self.find_input = QLineEdit(self)

        self.replace_label = QLabel('Replace:', self)
        self.replace_input = QLineEdit(self)

        self.case_sensitive_checkbox = QCheckBox('Case Sensitive', self)

        self.find_next_button = QPushButton('Find Next', self)
        self.replace_button = QPushButton('Replace', self)
        self.replace_all_button = QPushButton('Replace All', self)
        self.close_button = QPushButton('Close', self)

        self.find_next_button.clicked.connect(self.find_next)
        self.replace_button.clicked.connect(self.replace)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.close_button.clicked.connect(self.close)

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

        text_edit = self.parent.get_current_text_edit()
        if not text_edit:
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to search.')
            return

        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

        found = text_edit.find(text_to_find, options)
        if not found:
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

        text_edit = self.parent.get_current_text_edit()
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

        text_edit = self.parent.get_current_text_edit()
        if not text_edit:
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to replace.')
            return

        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextRandomizerGUI()
    window.show()
    sys.exit(app.exec_())
