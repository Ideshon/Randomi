from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import QSettings  # Добавлено для работы с настройками
from text_randomizer import TextRandomizer
from re import sub # стандартная библиотека для работы с текстом

class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')  # Инициализация QSettings
        self.initUI()
        self.loadSettings()  # Загрузка сохраненных настроек при инициализации

        self.delimeter.setMinimumSize(0, 20)
        self.delimeter.setMaximumSize(60, 20)
        self.entry.setMinimumSize(200, 20)
        self.template_label.setMinimumSize(200, 20)
        self.result_output.setMinimumSize(200, 20)
        self.randomize_button.setMaximumSize(10000, 80)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.delimeterL = QLabel('Delimeter', self)
        self.entry = QTextEdit(self)
        self.delimeter = QLineEdit(',', self)
        self.randomize_button = QPushButton('Randomize', self)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)

        # Текстовое поле для инструкций
        self.template_label = QTextEdit(self)
        self.template_label.setReadOnly(False)

        self.randomize_button.clicked.connect(self.randomize_text)

        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.delimeterL)
        self.hbox.addWidget(self.delimeter)
        self.hbox.addStretch(1)

        self.layout.addLayout(self.hbox)
        self.layout.addWidget(self.entry)
        self.layout.addWidget(self.randomize_button)
        self.layout.addWidget(self.result_output)
        self.layout.addWidget(self.template_label)

        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')

    def normalize_template(self, template, delim):
        norm_template = sub(f"{delim}", "|", template)
        return norm_template

    def randomize_text(self):
        try:
            template = self.entry.toPlainText()
            norm_template = self.normalize_template(template, self.delimeter.text())
            text_rnd = TextRandomizer(norm_template)
            self.result_output.setText(text_rnd.get_text())
        except Exception as e:
            self.result_output.setText(f"Error: {str(e)}")

    def loadSettings(self):
        self.template_label.setText(self.settings.value('template_label', ''))
        self.entry.setPlainText(self.settings.value('entry', ''))
        self.result_output.setText(self.settings.value('result_output', ''))

    def saveSettings(self):
        self.settings.setValue('template_label', self.template_label.toPlainText())
        self.settings.setValue('entry', self.entry.toPlainText())
        self.settings.setValue('result_output', self.result_output.toPlainText())

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    window = TextRandomizerGUI()
    window.show()
    app.exec_()
