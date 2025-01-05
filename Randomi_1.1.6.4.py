# Размер текстового поля.
# QApplication - основные настройки, QWidget - отображение содержимого, QFileDialog - для диалога сохранения,QSlider - слайдер
# QTextEdit и QLineEdit - редактор текста, QV и QHBoxLayout - расположение виджетов, QLabel - отображение текста,
# QSplitter - изменение размера виджетов
# QTextCharFormat, QFont #Шрифт

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, \
    QSplitter, QFileDialog, QSlider
import random
from randomizer import TextRandomizer
from re import sub, split, findall  # стандартная библиотека для работы с текстом
from PyQt5.QtCore import QSettings, Qt  # для сохранения и загрузки
from PyQt5.QtGui import QTextCharFormat, QFont, QPalette, QColor, QTextOption
import re


class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()  # интерфейс
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')  # Инициализация QSettings
        self.loadSettings()  # Загрузка сохраненных настроек при инициализации

        # ограничители
        self.delimeter.setMinimumSize(0, 20)  # Задает минимальный размер 0x20 пикселей
        self.delimeter.setMaximumSize(30, 20)  # Задает максимальный размер 30x20 пикселей
        self.entry.setMinimumSize(200, 20)
        self.template_label.setMinimumSize(200, 20)
        self.result_output.setMinimumSize(200, 20)
        self.randomize_button.setMinimumSize(80, 20)
        self.save_button.setMinimumSize(50, 20)
        self.load_button.setMinimumSize(50, 20)

        """
        Форматирование текста
        """
        # Добавление элементов управления для изменения размера шрифта
        self.font_size_label = QLabel('Font Size:', self)
        self.font_size_slider = QSlider(Qt.Horizontal, self)
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(24)
        self.font_size_slider.setValue(12) # по умолчанию
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.font_size_slider.valueChanged.connect(self.changeFontSize)
        self.layout.addWidget(self.font_size_label)
        self.layout.addWidget(self.font_size_slider)

    # размер шрифта
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

    # жирный шрифт
    def applyFormattingToSelectedText(self, text_edit):
        cursor = text_edit.textCursor()
        if not cursor.hasSelection():
            return

        selected_text = cursor.selectedText()
        if not selected_text:
            return

        # Получение текущего формата символа
        char_format = cursor.charFormat()

        # Проверяем, включен ли уже жирный шрифт для выделенного текста
        is_bold = char_format.font().bold()

        # Применяем или убираем жирное форматирование в зависимости от текущего состояния
        char_format.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)

        # Устанавливаем формат символа для выделенного текста
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

    # Сброс форматирования
    def resetFormatting(self):
        # Сброс форматирования для поля entry
        try:
            cursor = self.entry.textCursor()
            cursor.beginEditBlock()

            default_format = QTextCharFormat()
            default_format.setFontWeight(QFont.Normal)
            default_format.setForeground(QColor(Qt.black))
            default_format.setBackground(QColor(Qt.white))  # Сброс цвета фона

            cursor.setCharFormat(default_format)
            cursor.clearSelection()

            cursor.endEditBlock()
            self.entry.setTextCursor(cursor)
        except Exception as e:
            print("Error resetting formatting for entry:", str(e))

        # Сброс форматирования для поля template_label
        try:
            cursor = self.template_label.textCursor()
            cursor.beginEditBlock()

            default_format = QTextCharFormat()
            default_format.setFontWeight(QFont.Normal)
            default_format.setForeground(QColor(Qt.black))
            default_format.setBackground(QColor(Qt.white))  # Сброс цвета фона

            cursor.setCharFormat(default_format)
            cursor.clearSelection()

            cursor.endEditBlock()
            self.template_label.setTextCursor(cursor)
        except Exception as e:
            print("Error resetting formatting for template_label:", str(e))

        # Сброс форматирования для поля result_output
        try:
            cursor = self.result_output.textCursor()
            cursor.beginEditBlock()

            default_format = QTextCharFormat()
            default_format.setFontWeight(QFont.Normal)
            default_format.setForeground(QColor(Qt.black))
            default_format.setBackground(QColor(Qt.white))  # Сброс цвета фона

            cursor.setCharFormat(default_format)
            cursor.clearSelection()

            cursor.endEditBlock()
            self.result_output.setTextCursor(cursor)
        except Exception as e:
            print("Error resetting formatting for result_output:", str(e))

    """
    Интерфейс
    """
    def initUI(self):
        self.layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Vertical, self)  # вертикальный разделитель для текстовых полей

        # поля
        self.entry = QTextEdit(self)  # Используется для многострочного ввода
        self.delimeter = QLineEdit(';', self)  # Разделитель поле ввода однострочного
        self.result_output = QTextEdit(self)  # Результат
        self.result_output.setReadOnly(False)  # Сделать поле только для чтения
        # подсказка
        self.template_label = QTextEdit('', self)
        self.template_label.setReadOnly(False)

        # кнопки
        self.randomize_button = QPushButton('Randomize', self)
        self.save_button = QPushButton('Save', self)
        self.load_button = QPushButton('Load', self)
        # Добавление элемента управления для форматирования текста
        self.bold_button = QPushButton('Bold', self)
        # Добавление кнопки для сброса форматирования
        self.reset_button = QPushButton('Reset Formatting', self)



        # функции кнопок
        self.randomize_button.clicked.connect(self.randomize_text)
        self.save_button.clicked.connect(self.saveToFile)
        self.load_button.clicked.connect(self.loadFromFile)
        self.bold_button.clicked.connect(self.toggleBold)
        self.reset_button.clicked.connect(self.resetFormatting)

        # Добавить виджеты в сплиттер
        self.splitter.addWidget(self.entry)
        self.splitter.addWidget(self.result_output)
        self.splitter.addWidget(self.template_label)

        # Горизонтальная планировка для кнопок и делиметра
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(QLabel('Delimiter:', self))
        self.hbox.addWidget(self.delimeter)
        self.hbox.addWidget(self.randomize_button)
        self.hbox.addWidget(self.save_button)
        self.hbox.addWidget(self.load_button)
        self.hbox.addStretch(1) # выравнивание по левому

        self.hbox2 = QHBoxLayout() # Второй ряд кнопок
        self.hbox2.addWidget(self.bold_button)
        self.hbox2.addWidget(self.reset_button)

        # Добавить сплиттер и hbox в основной макет (порядок в колонке)
        self.layout.addWidget(self.splitter)
        self.layout.addLayout(self.hbox)
        self.layout.addLayout(self.hbox2)


        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')  # название окна

    """
    Функции рандомайзера
    """

    # Умножение слов
    def expand_word_weight(self, input_text):
        import re
        pattern = r'(\w+)\*(\d+)'
        while True:
            match = re.search(pattern, input_text)
            if not match:
                break
            word, count = match.groups()
            expanded = f"{self.delimeter.text()}".join([word] * int(count))
            input_text = re.sub(re.escape(match.group(0)), expanded, input_text, count=1)
        return input_text

    def expand_random_count(self, text):
        # Сначала обработка вложенных функций в "<>"
        def process_nested_functions(text):
            nested_pattern = r'"(.*?)"'
            while findall(nested_pattern, text):
                for nested_formula in findall(nested_pattern, text):
                    expanded_nested = self.expand_random_count(nested_formula)  # Рекурсивный вызов для вложенных формул
                    text = text.replace(f'"{nested_formula}"', expanded_nested, 1)
            return text

        # Применение обработки вложенных функций
        text = process_nested_functions(text)

        # Основная обработка рандомных выборок
        pattern = r'%(\d+)-(\d+)\((.*?)\)'
        while True:
            match = findall(pattern, text)
            if not match:
                break
            for (min_count, max_count, words) in match:
                words_list = words.split(';')
                min_count, max_count = int(min_count), int(max_count)

                # Добавим отладочные сообщения
                print(f"Debug - formula: %{min_count}-{max_count}({words})")
                print(f"Debug - words_list: {words_list}")

                # Проверка и корректировка значений min_count и max_count
                if min_count > len(words_list):
                    min_count = len(words_list)
                if max_count > len(words_list):
                    max_count = len(words_list)

                if min_count > max_count:
                    min_count = max_count

                # Обработка пустых списков слов
                if not words_list:
                    selected_words = ''
                else:
                    num_words = random.randint(min_count, max_count)
                    selected_words = ','.join(random.sample(words_list, num_words))

                formula = f'%{min_count}-{max_count}({words})'
                text = text.replace(formula, selected_words, 1)

                # Еще одно отладочное сообщение
                print(f"Debug - selected_words: {selected_words}")
        return text

    """
    Нормализует шаблон, заменяя пользовательский разделитель на стандартный '|' для TextRandomizer.
    """

    def normalize_template(self, template, delim):
        # Используем делиметр только для разделения слов, а не в качестве разделителя между вариантами
        norm_template = sub(f"\s*{delim}\s*", "|", template)
        return norm_template

    # основной рандомизатор
    def randomize_text(self):
        try:
            template = self.entry.toPlainText()  # Получение текста из QTextEdit
            expanded_template = self.expand_word_weight(template)  # Умножение
            expanded_template = self.expand_random_count(expanded_template)  # Рандомная выборка
            norm_template = self.normalize_template(expanded_template, self.delimeter.text())
            text_rnd = TextRandomizer(norm_template)  # Delimer
            randomized_text = text_rnd.get_text()

            # Очистка от лишних знаков препинания и пробелов
            cleaned_text = sub(r'(?<!\S),\s*', '',
                               randomized_text)  # Удаление запятых, не стоящих после буквы или цифры
            cleaned_text = sub(r'\s*,\s*,+', ',', cleaned_text)  # Удаление лишних запятых
            cleaned_text = sub(r'\(\s*,\s*', '(',
                               cleaned_text)  # Удаление пробелов после открывающей скобки и перед запятой
            cleaned_text = sub(r'\s*,\s*\)', ')',
                               cleaned_text)  # Удаление пробелов после запятой и перед закрывающей скобкой
            cleaned_text = sub(r'\s*,\s*', ', ',
                               cleaned_text)  # Удаление пробелов вокруг запятых, оставляя один пробел после запятой

            # Удаление лишних пробелов, кроме новых строк
            cleaned_text = sub(r'[ \t]+(?=[^\S\n]*[ \t]+)', '', cleaned_text)
            cleaned_text = sub(r'[ \t]+(?=\n)', '', cleaned_text)
            cleaned_text = sub(r'\n+', '\n', cleaned_text)

            # Удаление запятых в начале строки
            cleaned_text = sub(r'^\s*,\s*', '', cleaned_text)

            self.result_output.setText(cleaned_text)  # Вывод результата в QTextEdit
        except Exception as e:
            self.result_output.setText(f"Error: {str(e)}")  # Вывод ошибки в QTextEdit
    """
    сохранение и загрузка
    """
    def saveToFile(self):
        filePath, _ = QFileDialog.getSaveFileName(self, "Save File", "", "Text Files (*.txt)")
        if filePath:
            try:
                with open(filePath, 'w', encoding='utf-8') as file:
                    file.write(self.entry.toPlainText() + '\n---END---\n')
                    file.write(self.result_output.toPlainText() + '\n---END---\n')
                    file.write(self.template_label.toPlainText() + '\n---END---\n')
            except Exception as e:
                self.result_output.setText(f"Error saving file: {str(e)}")

    def loadFromFile(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt)")
        if filePath:
            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    content = file.read()
                parts = content.split('---END---\n')
                if len(parts) >= 3:
                    self.entry.setPlainText(parts[0].strip())
                    self.result_output.setPlainText(parts[1].strip())
                    self.template_label.setPlainText(parts[2].strip())
            except Exception as e:
                self.result_output.setText(f"Error loading file: {str(e)}")

    # сохранении при закрытии
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


if __name__ == '__main__':
    app = QApplication([])
    window = TextRandomizerGUI()
    window.show()
    app.exec_()
