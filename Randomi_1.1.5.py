# Размер текстового поля.
# QApplication - основные настройки, QWidget - отображение содержимого, QFileDialog - для диалога сохранения,
# QTextEdit и QLineEdit - редактор текста, QV и QHBoxLayout - расположение виджетов, QLabel - отображение текста,
# QSplitter - изменение размера виджетов
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QSplitter, QFileDialog
from text_randomizer import TextRandomizer
from re import sub, split, findall  # стандартная библиотека для работы с текстом
from PyQt5.QtCore import QSettings, Qt  # для сохранения и загрузки

class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()  # интерфейс
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')  # Инициализация QSettings
        self.loadSettings()  # Загрузка сохраненных настроек при инициализации

        self.delimeter.setMinimumSize(0, 20)  # Задает минимальный размер 0x20 пикселей
        self.delimeter.setMaximumSize(30, 20)  # Задает максимальный размер 30x20 пикселей
        self.entry.setMinimumSize(200, 20)
        self.template_label.setMinimumSize(200, 20)
        self.result_output.setMinimumSize(200, 20)
        self.randomize_button.setMinimumSize(80, 20)
        self.save_button.setMinimumSize(50, 20)
        self.load_button.setMinimumSize(50, 20)

    def initUI(self):
        self.layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Vertical, self)  # вертикальный разделитель для текстовых полей

        self.entry = QTextEdit(self)  # Используется для многострочного ввода
        self.delimeter = QLineEdit(';', self)  # Разделитель поле ввода однострочного
        # кнопки
        self.randomize_button = QPushButton('Randomize', self)
        # Кнопки сохранения и загрузки
        self.save_button = QPushButton('Save', self)
        self.load_button = QPushButton('Load', self)

        self.result_output = QTextEdit(self) # Результат
        self.result_output.setReadOnly(False)  # Сделать поле только для чтения

        # подсказка
        self.template_label = QTextEdit(
            '\nСлово*количество - добавляет указанное количество слов при генерации'
            '\n\nКоманда "Синонимы" - {variant1 | variant2 | variant3} - вставляет один из вариантов в результирующую строку'
            '\nЕсли вы хотите пропустить текст - используйте вариант "пусто" - {|variant}'
            '\nКоманда Mixin = [ текст 1 | текст 2 | текст 3] - будет случайным образом миксовать эти варианты'
            '\nВы можете использовать разделитель в mixin - [+,+text 1|text2 ] - вы получите text2,text1. Разделитель может быть любым символом или набором символов: [+==+ a|b] - a==b или b==a'
            '\nЕсли вы хотите получить специальный символ в вашем результате (\{\, \}\, \[\, \]\, \|\, \+\) - используйте обратный слеш для него - {, }, [, ], |, \+'
            '\nВсе эти команды могут быть смешаны и вложены во все комбинации: \'начало {aa|bb|{cc1|cc2}} или [a1|{word1|word2}|a3| [aa1|aa2|aa3]]\''
            '\nВы можете использовать специальные предопределенные функции рандомизации в шаблонах - {случайное целое = $RANDINT(1,10), uuid = $UUID, сейчас = $NOW(%Y-%M-%d)}.'
            '\nРезультат будет = \'случайное целое = 4, uuid = 8ae6bdf4-d321-40f6-8c3c-81d20b158acb, сейчас = 2017-08-01\''
            '\nВы можете определить свои собственные функции рандомизации и использовать их в шаблонах. Читайте о функциях дальше.'
            , self)
        self.template_label.setReadOnly(False)


        # Добавить виджеты в сплиттер
        self.splitter.addWidget(self.entry)
        self.splitter.addWidget(self.result_output)
        self.splitter.addWidget(self.template_label)

        # Кнопки
        self.randomize_button.clicked.connect(self.randomize_text)
        self.save_button.clicked.connect(self.saveToFile)
        self.load_button.clicked.connect(self.loadFromFile)

        # Горизонтальная планировка для кнопок и делиметра
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(QLabel('Delimiter:', self))
        self.hbox.addWidget(self.delimeter)
        self.hbox.addWidget(self.randomize_button)
        self.hbox.addWidget(self.save_button)
        self.hbox.addWidget(self.load_button)
        self.hbox.addStretch(1)

        # Добавить сплиттер и hbox в основной макет
        self.layout.addWidget(self.splitter)
        self.layout.addLayout(self.hbox)

        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')  # название окна

    # Умножение слов
    def expand_text_input(self, input_text):
        import re
        pattern = r'(\w+)\*(\d+)'
        while True:
            match = re.search(pattern, input_text)
            if not match:
                break
            word, count = match.groups()
            expanded = '|'.join([word] * int(count))
            input_text = re.sub(re.escape(match.group(0)), expanded, input_text, count=1)
        return input_text

    # функция нормализации примера (для , ->  1,2,3 в {1|2|3})
    def normalize_template(self, template, delim):
        norm_template = sub(f"{delim}", "|", template)
        return norm_template

    # рандомизатор
    def randomize_text(self):
        try:
            template = self.entry.toPlainText() # Получение текста из QTextEdit
            expanded_template = self.expand_text_input(template) # Умножение
            norm_template = self.normalize_template(expanded_template,self.delimeter.text())
            text_rnd = TextRandomizer(norm_template) # Delimer
            self.result_output.setText(text_rnd.get_text()) # Вывод результата в QTextEdit
        except Exception as e:
            self.result_output.setText(f"Error: {str(e)}") # Вывод ошибки в QTextEdit

    # сохранение и загрузка в файл
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
