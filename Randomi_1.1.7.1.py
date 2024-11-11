import sys
import re
import random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, \
    QSplitter, QFileDialog, QSlider, QDialog
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
        self.delimiter = QLineEdit(';', self)
        self.func_delimiter = QLineEdit(',', self)  # Добавлено поле для разделителя функций
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
            func_delimiter = self.func_delimiter.text()

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
                return '{$RANDWORDS(' + f'{min_count}{func_delimiter}{max_count}{func_delimiter}{words}' + ')}'
            template = re.sub(r'%(\d+)-(\d+)\((.*?)\)', replace_randwords, template)

            # Предварительная обработка для разворачивания вложенных функций
            def evaluate_functions(s, delimiter=func_delimiter):
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
                        # Проверяем на разделитель функций
                        if depth == 1 and s[i:i+len(delimiter)] == delimiter:
                            args.append(arg.strip())
                            arg = ''
                            i += len(delimiter)
                        elif s[i] == '(':
                            depth += 1
                            arg += s[i]
                            i += 1
                        elif s[i] == ')':
                            depth -= 1
                            if depth == 0:
                                args.append(arg.strip())
                                i += 1  # Пропускаем ')'
                                break
                            else:
                                arg += s[i]
                                i += 1
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
                                i += 1
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
                if max_count <= 0:
                    return ''
                num_words = random.randint(min_count, max_count)
                selected_words = random.sample(words, num_words)
                return ' '.join(selected_words)

            # Выполняем предварительную обработку шаблона
            template = evaluate_functions(template)

            # Создание объекта TextRandomizer
            text_rnd = TextRandomizer(template)

            randomized_text = text_rnd.get_text()

            # Очистка результата, сохраняя двойные переводы строк как абзацы
            # 1. Заменяем последовательности из трех и более новых строк на двойные новые строки
            text = re.sub(r'\n{3,}', '\n\n', randomized_text)
            # 2. Заменяем двойные новые строки на уникальный маркер
            text = text.replace('\n\n', '<<<PARAGRAPH_BREAK>>>')
            # 3. Заменяем оставшиеся пробельные символы и одинарные новые строки на пробел
            text = re.sub(r'[ \t\r\f\v]+', ' ', text)
            text = re.sub(r'\n', ' ', text)
            text = text.strip()
            # 4. Восстанавливаем маркеры в двойные новые строки
            cleaned_text = text.replace('<<<PARAGRAPH_BREAK>>>', '\n\n')

            self.result_output.setPlainText(cleaned_text)
        except Exception as e:
            self.result_output.setPlainText(f"Error: {str(e)}")

    def saveToFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Rich Text Files (*.html);;All Files (*)")
        if filePath:
            try:
                with open(filePath, 'w', encoding='utf-8') as file:
                    file.write(self.entry.toHtml() + '\n---END---\n')
                    file.write(self.result_output.toHtml() + '\n---END---\n')
                    file.write(self.template_label.toHtml() + '\n---END---\n')
                    file.write(self.delimiter.text() + '\n---END---\n')
                    file.write(self.func_delimiter.text() + '\n---END---\n')
            except Exception as e:
                self.result_output.setHtml(f"<p>Error saving file: {str(e)}</p>")

    def loadFromFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Rich Text Files (*.html);;All Files (*)")
        if filePath:
            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    content = file.read()
                parts = content.split('---END---\n')
                if len(parts) >= 5:
                    self.entry.setHtml(parts[0].strip())
                    self.result_output.setHtml(parts[1].strip())
                    self.template_label.setHtml(parts[2].strip())
                    self.delimiter.setText(parts[3].strip())
                    self.func_delimiter.setText(parts[4].strip())
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextRandomizerGUI()
    window.show()
    sys.exit(app.exec_())
