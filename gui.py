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

# Подключаем уже имеющийся, "идеальный" text_randomizer.py — как основной функционал
# (не меняем его, используем "как есть").
# И также у нас будет randomizer.py, который добавляет в него новые функции,
# но здесь, в gui.py, импортируем именно randomizer.py, потому что
# randomizer.py внутри себя импортирует text_randomizer.py и расширяет его
# нужными функциями.
from randomizer import TextRandomizer

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

        # Текстовые поля
        self.entry = QTextEdit(self)
        self.entry.setFocusPolicy(Qt.StrongFocus)

        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)
        self.result_output.setFocusPolicy(Qt.StrongFocus)

        self.template_label = QTextEdit('', self)
        self.template_label.setReadOnly(False)
        self.template_label.setFocusPolicy(Qt.StrongFocus)

        # Поля для пользовательских разделителей
        self.delimiter = QLineEdit(';', self)
        self.func_delimiter = QLineEdit(',', self)

        # Переопределяем focusInEvent, чтобы отслеживать, какой QTextEdit активен
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

        # Привязываем сигналы к слотам
        self.randomize_button.clicked.connect(self.randomize_text)
        self.save_button.clicked.connect(self.saveToFile)
        self.load_button.clicked.connect(self.loadFromFile)
        self.bold_button.clicked.connect(self.toggleBold)
        self.reset_button.clicked.connect(self.resetFormatting)
        self.find_replace_button.clicked.connect(self.open_find_replace_dialog)

        # Слайдер для изменения размера шрифта
        self.font_size_label = QLabel('Font Size:', self)
        self.font_size_slider = QSlider(Qt.Horizontal, self)
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(24)
        self.font_size_slider.setValue(12)
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.font_size_slider.valueChanged.connect(self.changeFontSize)

        # Добавляем поля в сплиттер
        self.splitter.addWidget(self.entry)
        self.splitter.addWidget(self.result_output)
        self.splitter.addWidget(self.template_label)

        # Горизонтальный макет для delimiter и кнопок
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

        # Складываем всё в основной layout
        self.layout.addWidget(self.splitter)
        self.layout.addLayout(self.hbox)
        self.layout.addLayout(self.hbox2)

        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')

    def make_focus_in_event(self, widget):
        """
        Обёртка над focusInEvent, чтобы запоминать, в каком QTextEdit сейчас фокус.
        """
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
        """
        Меняем шрифт во всех QTextEdit: entry, result_output, template_label.
        """
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
        """
        Обработка нажатия кнопки "Randomize":
        1. Забираем текст из self.entry (HTML).
        2. Создаём объект TextRandomizer (из randomizer.py).
        3. Вызываем process().
        4. Помещаем результат в self.result_output.
        """
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
        """
        Сохранение всех полей в JSON-файл.
        """
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
        """
        Загрузка из JSON-файла.
        """
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
        """
        Загружаем настройки из QSettings.
        """
        self.entry.setHtml(self.settings.value('entry', ''))
        self.result_output.setHtml(self.settings.value('result_output', ''))
        self.template_label.setHtml(self.settings.value('template_label', ''))
        self.delimiter.setText(self.settings.value('delimiter', ';'))
        self.func_delimiter.setText(self.settings.value('func_delimiter', ','))

    def saveSettings(self):
        """
        Сохраняем в QSettings.
        """
        self.settings.setValue('entry', self.entry.toHtml())
        self.settings.setValue('result_output', self.result_output.toHtml())
        self.settings.setValue('template_label', self.template_label.toHtml())
        self.settings.setValue('delimiter', self.delimiter.text())
        self.settings.setValue('func_delimiter', self.func_delimiter.text())

    def closeEvent(self, event):
        """
        Автосохранение при выходе.
        """
        self.saveSettings()
        super().closeEvent(event)

    def open_find_replace_dialog(self):
        """
        Открытие диалога "Найти и заменить" (find_replace_dialog.py).
        """
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()
