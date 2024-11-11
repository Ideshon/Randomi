import sys
import re
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, \
    QSplitter, QFileDialog, QSlider
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QTextCharFormat, QFont
from text_randomizer import TextRandomizer

class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')
        self.loadSettings()

        # Ограничения размеров виджетов
        self.delimiter.setMinimumSize(0, 20)
        self.delimiter.setMaximumSize(30, 20)
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
        self.delimiter = QLineEdit(';', self)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)
        self.template_label = QTextEdit('', self)
        self.template_label.setReadOnly(False)

        # Кнопки
        self.randomize_button = QPushButton('Randomize', self)
        self.save_button = QPushButton('Save', self)
        self.load_button = QPushButton('Load', self)
        self.bold_button = QPushButton('Bold', self)
        self.reset_button = QPushButton('Reset Formatting', self)

        # Функции кнопок
        self.randomize_button.clicked.connect(self.randomize_text)
        self.save_button.clicked.connect(self.saveToFile)
        self.load_button.clicked.connect(self.loadFromFile)
        self.bold_button.clicked.connect(self.toggleBold)
        self.reset_button.clicked.connect(self.resetFormatting)

        # Добавление виджетов в сплиттер
        self.splitter.addWidget(self.entry)
        self.splitter.addWidget(self.result_output)
        self.splitter.addWidget(self.template_label)

        # Горизонтальный макет для кнопок и разделителя
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(QLabel('Delimiter:', self))
        self.hbox.addWidget(self.delimiter)
        self.hbox.addWidget(self.randomize_button)
        self.hbox.addWidget(self.save_button)
        self.hbox.addWidget(self.load_button)
        self.hbox.addStretch(1)

        self.hbox2 = QHBoxLayout()
        self.hbox2.addWidget(self.bold_button)
        self.hbox2.addWidget(self.reset_button)

        # Добавление макетов в основной макет
        self.layout.addWidget(self.splitter)
        self.layout.addLayout(self.hbox)
        self.layout.addLayout(self.hbox2)

        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')

    def applyFormattingToSelectedText(self, text_edit):
        cursor = text_edit.textCursor()
        if not cursor.hasSelection():
            return
        char_format = cursor.charFormat()
        is_bold = char_format.font().bold()
        char_format.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)
        cursor.setCharFormat(char_format)

    def toggleBold(self):
        for text_edit in [self.entry, self.template_label, self.result_output]:
            try:
                self.applyFormattingToSelectedText(text_edit)
            except Exception as e:
                print(f"Error in {text_edit.objectName()}: {str(e)}")

    def resetFormatting(self):
        for text_edit in [self.entry, self.template_label, self.result_output]:
            try:
                cursor = text_edit.textCursor()
                cursor.select(cursor.Document)
                cursor.setCharFormat(QTextCharFormat())
                cursor.clearSelection()
                text_edit.setTextCursor(cursor)
            except Exception as e:
                print(f"Error resetting formatting for {text_edit.objectName()}: {str(e)}")

    def randomize_text(self):
        try:
            template = self.entry.toPlainText()
            delimiter = self.delimiter.text()

            # Замена пользовательского разделителя на '|'
            if delimiter and delimiter != '|':
                escaped_delim = re.escape(delimiter)
                template = re.sub(rf'\s*{escaped_delim}\s*', '|', template)

            # Замена умножения слов на функцию $MULTIPLY(word, count)
            template = re.sub(r'(\w+)\*(\d+)', lambda m: '{$' + f'MULTIPLY({m.group(1)},{m.group(2)})' + '}', template)

            # Замена %min-max(words) на функцию $RANDWORDS(min, max, words)
            def replace_randwords(match):
                min_count = match.group(1)
                max_count = match.group(2)
                words = match.group(3)
                return '{$RANDWORDS(' + f'{min_count},{max_count},{words}' + ')}'
            template = re.sub(r'%(\d+)-(\d+)\((.*?)\)', replace_randwords, template)

            # Предварительная обработка для разворачивания вложенных функций
            def evaluate_functions(s):
                def parse_function(s, start):
                    func_name = ''
                    i = start
                    while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                        func_name += s[i]
                        i += 1
                    if i >= len(s) or s[i] != '(':
                        return None, start
                    i += 1  # Пропускаем '('
                    args = []
                    arg = ''
                    depth = 1
                    while i < len(s) and depth > 0:
                        if s[i] == '(':
                            depth += 1
                            arg += s[i]
                        elif s[i] == ')':
                            depth -= 1
                            if depth == 0:
                                args.append(arg.strip())
                                i += 1  # Пропускаем ')'
                                break
                            else:
                                arg += s[i]
                        elif s[i] == ',' and depth == 1:
                            args.append(arg.strip())
                            arg = ''
                        else:
                            arg += s[i]
                        i += 1
                    else:
                        if depth > 0:
                            raise ValueError("Unmatched parenthesis in function call")
                    return {'name': func_name, 'args': args}, i

                def evaluate(s):
                    result = ''
                    i = 0
                    while i < len(s):
                        if s[i] == '$':
                            func_info, new_i = parse_function(s, i + 1)
                            if func_info:
                                evaluated_args = [evaluate(arg) for arg in func_info['args']]
                                if func_info['name'] == 'MULTIPLY':
                                    res = multiply(*evaluated_args)
                                elif func_info['name'] == 'RANDWORDS':
                                    res = randwords(*evaluated_args)
                                else:
                                    res = ''
                                result += res
                                i = new_i
                                continue
                            else:
                                result += s[i]
                        else:
                            result += s[i]
                        i += 1
                    return result

                return evaluate(s)

            # Определяем функции MULTIPLY и RANDWORDS для предварительной обработки
            def multiply(word, count):
                return ' '.join([word.strip()] * int(count))

            def randwords(min_count, max_count, *words):
                min_count = int(min_count)
                max_count = int(max_count)
                words = [w.strip() for w in words]
                max_count = min(max_count, len(words))
                min_count = min(min_count, max_count)
                num_words = random.randint(min_count, max_count)
                selected_words = random.sample(words, num_words)
                return ' '.join(selected_words)

            # Выполняем предварительную обработку шаблона
            template = evaluate_functions(template)

            # Создание объекта TextRandomizer
            text_rnd = TextRandomizer(template)

            randomized_text = text_rnd.get_text()

            # Очистка результата от лишних пробелов
            cleaned_text = re.sub(r'\s+', ' ', randomized_text).strip()

            self.result_output.setText(cleaned_text)
        except Exception as e:
            self.result_output.setText(f"Error: {str(e)}")

    def saveToFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Rich Text Files (*.html);;All Files (*)")
        if filePath:
            try:
                with open(filePath, 'w', encoding='utf-8') as file:
                    file.write(self.entry.toHtml() + '\n---END---\n')
                    file.write(self.result_output.toHtml() + '\n---END---\n')
                    file.write(self.template_label.toHtml() + '\n---END---\n')
            except Exception as e:
                self.result_output.setHtml(f"<p>Error saving file: {str(e)}</p>")

    def loadFromFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Rich Text Files (*.html);;All Files (*)")
        if filePath:
            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    content = file.read()
                parts = content.split('---END---\n')
                if len(parts) >= 3:
                    self.entry.setHtml(parts[0].strip())
                    self.result_output.setHtml(parts[1].strip())
                    self.template_label.setHtml(parts[2].strip())
            except Exception as e:
                self.result_output.setHtml(f"<p>Error loading file: {str(e)}</p>")

    def saveSettings(self):
        self.settings.setValue('template_label', self.template_label.toHtml())
        self.settings.setValue('entry', self.entry.toHtml())
        self.settings.setValue('result_output', self.result_output.toHtml())

    def loadSettings(self):
        entry_html = self.settings.value('entry', '')
        result_html = self.settings.value('result_output', '')
        template_html = self.settings.value('template_label', '')

        if entry_html:
            self.entry.setHtml(entry_html)
        if result_html:
            self.result_output.setHtml(result_html)
        if template_html:
            self.template_label.setHtml(template_html)

    def closeEvent(self, event):
        self.saveSettings()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextRandomizerGUI()
    window.show()
    sys.exit(app.exec_())
