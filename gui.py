from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QSplitter, QFileDialog, QSlider
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QTextCharFormat, QFont, QPalette, QColor
from text_randomizer import TextRandomizer
from random_functions import expand_word_weight, expand_random_count, normalize_template, randomize_text
from save import saveToFile, loadFromFile
import re

class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')
        self.loadSettings()

        # ограничители
        self.delimeter.setMinimumSize(0, 20)
        self.delimeter.setMaximumSize(30, 20)
        self.entry.setMinimumSize(200, 20)
        self.template_label.setMinimumSize(200, 20)
        self.result_output.setMinimumSize(200, 20)
        self.randomize_button.setMinimumSize(80, 20)
        self.save_button.setMinimumSize(50, 20)
        self.load_button.setMinimumSize(50, 20)

        self.font_size_label = QLabel('Font Size:', self)
        self.font_size_slider = QSlider(Qt.Horizontal, self)
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(24)
        self.font_size_slider.setValue(12)
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.font_size_slider.valueChanged.connect(self.changeFontSize)
        self.layout.addWidget(self.font_size_label)
        self.layout.addWidget(self.font_size_slider)

    def changeFontSize(self, value):
        font = self.entry.font()
        font.setPointSize(value)
        self.entry.setFont(font)
        font = self.result_output.font()
        font.setPointSize(value)
        self.result_output.setFont(font)
        font = self.template_label.font()
        font.setPointSize(value)
        self.template_label.setFont(font)

    def applyFormattingToSelectedText(self, text_edit):
        cursor = text_edit.textCursor()
        if not cursor.hasSelection():
            return

        selected_text = cursor.selectedText()
        if not selected_text:
            return

        char_format = cursor.charFormat()
        is_bold = char_format.font().bold()
        char_format.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)
        cursor.setCharFormat(char_format)

    def toggleBold(self):
        try:
            self.applyFormattingToSelectedText(self.entry)
        except Exception as e:
            print("Error in entry:", str(e))
        try:
            self.applyFormattingToSelectedText(self.template_label)
        except Exception as e:
            print("Error in template_label:", str(e))
        try:
            self.applyFormattingToSelectedText(self.result_output)
        except Exception as e:
            print("Error in result_output:", str(e))

    def resetFormatting(self):
        try:
            cursor = self.entry.textCursor()
            cursor.beginEditBlock()
            default_format = QTextCharFormat()
            default_format.setFontWeight(QFont.Normal)
            default_format.setForeground(QColor(Qt.black))
            default_format.setBackground(QColor(Qt.white))
            cursor.setCharFormat(default_format)
            cursor.clearSelection()
            cursor.endEditBlock()
            self.entry.setTextCursor(cursor)
        except Exception as e:
            print("Error resetting formatting for entry:", str(e))

        try:
            cursor = self.template_label.textCursor()
            cursor.beginEditBlock()
            default_format = QTextCharFormat()
            default_format.setFontWeight(QFont.Normal)
            default_format.setForeground(QColor(Qt.black))
            default_format.setBackground(QColor(Qt.white))
            cursor.setCharFormat(default_format)
            cursor.clearSelection()
            cursor.endEditBlock()
            self.template_label.setTextCursor(cursor)
        except Exception as e:
            print("Error resetting formatting for template_label:", str(e))

        try:
            cursor = self.result_output.textCursor()
            cursor.beginEditBlock()
            default_format = QTextCharFormat()
            default_format.setFontWeight(QFont.Normal)
            default_format.setForeground(QColor(Qt.black))
            default_format.setBackground(QColor(Qt.white))
            cursor.setCharFormat(default_format)
            cursor.clearSelection()
            cursor.endEditBlock()
            self.result_output.setTextCursor(cursor)
        except Exception as e:
            print("Error resetting formatting for result_output:", str(e))

    def initUI(self):
        self.layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Vertical, self)

        self.entry = QTextEdit(self)
        self.delimeter = QLineEdit(';', self)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)
        self.template_label = QTextEdit('', self)
        self.template_label.setReadOnly(False)

        self.randomize_button = QPushButton('Randomize', self)
        self.save_button = QPushButton('Save', self)
        self.load_button = QPushButton('Load', self)
        self.bold_button = QPushButton('Bold', self)
        self.reset_button = QPushButton('Reset Formatting', self)

        self.randomize_button.clicked.connect(self.randomize_text)
        self.save_button.clicked.connect(self.saveToFile)
        self.load_button.clicked.connect(self.loadFromFile)
        self.bold_button.clicked.connect(self.toggleBold)
        self.reset_button.clicked.connect(self.resetFormatting)

        self.splitter.addWidget(self.entry)
        self.splitter.addWidget(self.result_output)
        self.splitter.addWidget(self.template_label)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(QLabel('Delimiter:', self))
        self.hbox.addWidget(self.delimeter)
        self.hbox.addWidget(self.randomize_button)
        self.hbox.addWidget(self.save_button)
        self.hbox.addWidget(self.load_button)
        self.hbox.addStretch(1)

        self.hbox2 = QHBoxLayout()
        self.hbox2.addWidget(self.bold_button)
        self.hbox2.addWidget(self.reset_button)

        self.layout.addWidget(self.splitter)
        self.layout.addLayout(self.hbox)
        self.layout.addLayout(self.hbox2)

        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')

    def randomize_text(self):
        try:
            template = self.entry.toPlainText()
            delimiter = self.delimeter.text()
            cleaned_text = randomize_text(template, delimiter, expand_word_weight, expand_random_count)
            self.result_output.setText(cleaned_text)
        except Exception as e:
            self.result_output.setText(f"Error: {str(e)}")

    def saveToFile(self):
        saveToFile(self)

    def loadFromFile(self):
        loadFromFile(self)

    def loadSettings(self):
        self.entry.setPlainText(self.settings.value('entry', ''))
        self.result_output.setPlainText(self.settings.value('result_output', ''))
        self.template_label.setPlainText(self.settings.value('template_label', ''))

    def saveSettings(self):
        self.settings.setValue('template_label', self.template_label.toPlainText())
        self.settings.setValue('entry', self.entry.toPlainText())
        self.settings.setValue('result_output', self.result_output.toPlainText())

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

# штука
if (__name__ == '__main__'):
    main()