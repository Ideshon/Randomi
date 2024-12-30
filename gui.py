import re
import random
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit,
    QSplitter, QFileDialog, QSlider, QMessageBox
)
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QTextCharFormat, QFont, QTextCursor
from find_replace_dialog import FindReplaceDialog
from text_randomizer import TextRandomizer


class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')
        self.loadSettings()
        self.last_focused_text_edit = None  # Для хранения последнего активного текстового поля

    def initUI(self):
        self.layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Vertical, self)

        # Поля ввода и вывода
        self.entry = QTextEdit(self)
        self.entry.setFocusPolicy(Qt.StrongFocus)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)
        self.result_output.setFocusPolicy(Qt.StrongFocus)
        self.template_label = QTextEdit('', self)
        self.template_label.setReadOnly(False)
        self.template_label.setFocusPolicy(Qt.StrongFocus)
        self.delimiter = QLineEdit(';', self)
        self.func_delimiter = QLineEdit(',', self)

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

        # Элементы управления для изменения размера шрифта
        self.font_size_label = QLabel('Font Size:', self)
        self.font_size_slider = QSlider(Qt.Horizontal, self)
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(24)
        self.font_size_slider.setValue(12)
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.font_size_slider.valueChanged.connect(self.changeFontSize)

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
        self.hbox2.addWidget(self.font_size_label)
        self.hbox2.addWidget(self.font_size_slider)

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
        text_edit = self.last_focused_text_edit
        if text_edit:
            self.applyFormattingToSelectedText(text_edit)

    def resetFormatting(self):
        text_edit = self.last_focused_text_edit
        if text_edit:
            cursor = text_edit.textCursor()
            cursor.select(QTextCursor.Document)
            cursor.setCharFormat(QTextCharFormat())
            cursor.clearSelection()
            text_edit.setTextCursor(cursor)

    def changeFontSize(self, value):
        font = QFont()
        font.setPointSize(value)

        for text_edit in [self.entry, self.result_output, self.template_label]:
            cursor = text_edit.textCursor()
            cursor.select(QTextCursor.Document)
            char_format = QTextCharFormat()
            char_format.setFontPointSize(value)
            cursor.mergeCharFormat(char_format)
            text_edit.setTextCursor(cursor)

    def randomize_text(self):
        try:
            template = self.entry.toHtml()
            delimiter = self.delimiter.text()
            func_delimiter = self.func_delimiter.text()

            text_randomizer = TextRandomizer(template, delimiter, func_delimiter)
            randomized_html = text_randomizer.process()
            self.result_output.setHtml(randomized_html)
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
        self.entry.setHtml(self.settings.value('entry', ''))
        self.result_output.setHtml(self.settings.value('result_output', ''))
        self.template_label.setHtml(self.settings.value('template_label', ''))
        self.delimiter.setText(self.settings.value('delimiter', ';'))
        self.func_delimiter.setText(self.settings.value('func_delimiter', ','))

    def saveSettings(self):
        self.settings.setValue('entry', self.entry.toHtml())
        self.settings.setValue('result_output', self.result_output.toHtml())
        self.settings.setValue('template_label', self.template_label.toHtml())
        self.settings.setValue('delimiter', self.delimiter.text())
        self.settings.setValue('func_delimiter', self.func_delimiter.text())

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

    def open_find_replace_dialog(self):
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()
