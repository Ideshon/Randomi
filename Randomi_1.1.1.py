from re import sub  # стандартная библиотека для работы с текстом

from PyQt5.QtCore import QSettings  # для сохранения и загрузки
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit, QHBoxLayout
from text_randomizer import TextRandomizer


class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()  # запускаем инициализатор родительского класса
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')  # Инициализация QSettings
        self.initUI()  # интерфейс
        self.loadSettings()  # Загрузка сохраненных настроек при инициализации

        self.delimeter.setMinimumSize(0, 20)  # Задает минимальный размер 0x20 пикселей
        self.delimeter.setMaximumSize(60, 20)  # Задает максимальный размер 60x20 пикселей
        self.entry.setMinimumSize(200, 20)
        self.template_label.setMinimumSize(200, 20)
        self.result_output.setMinimumSize(200, 20)
        self.randomize_button.setMaximumSize(10000, 80)


    def initUI(self):
        self.layout = QVBoxLayout()
        self.delimeterL = QLabel('Delimeter', self)
        self.entry = QTextEdit(self)  # Используется для многострочного ввода
        self.delimeter = QLineEdit(';', self)  # Используется для однострочного ввода
        self.randomize_button = QPushButton('Randomize', self)
        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)  # Сделать поле только для чтения

        # подсказка
        self.template_label = QTextEdit(
                '\n\nКоманда "Синонимы" - {variant1 | variant2 | variant3} - вставляет один из вариантов в результирующую строку'
                '\nЕсли вы хотите пропустить текст - используйте вариант "пусто" - {|variant}'
                '\nКоманда Mixin = [ текст 1 | текст 2 | текст 3] - будет случайным образом миксовать эти варианты'
                '\nВы можете использовать разделитель в mixin - [+,+text 1|text2 ] - вы получите text2,text1. Разделитель может быть любым символом или набором символов: [+==+ a|b] - a==b или b==a'
                '\nЕсли вы хотите получить специальный символ в вашем результате (\{\, \}\, \[\, \]\, \|\, \+\) - используйте обратный слеш для него - {, }, [, ], |, \+'
                '\nВсе эти команды могут быть смешаны и вложены во все комбинации: \'начало {aa|bb|{cc1|cc2}} или [a1|{word1|word2}|a3| [aa1|aa2|aa3]]\''
                '\nВы можете использовать специальные предопределенные функции рандомизации в шаблонах - {случайное целое = $RANDINT(1,10), uuid = $UUID, сейчас = $NOW(%Y-%M-%d)}.'
                '\nРезультат будет = \'случайное целое = 4, uuid = 8ae6bdf4-d321-40f6-8c3c-81d20b158acb, сейчас = 2017-08-01\''
                '\nВы можете определить свои собственные функции рандомизации и использовать их в шаблонах. Читайте о функциях дальше.'
                , self
                )
        self.template_label.setReadOnly(False)

        self.randomize_button.clicked.connect(self.randomize_text)  # Кнопка

        # горизонтальный компоновщик для размещения метки и поля ввода разделителя рядом
        self.hbox = QHBoxLayout()
        self.hbox.addWidget(self.delimeterL)
        self.hbox.addWidget(self.delimeter)
        self.hbox.addStretch(1)  # Выравнивание по левому

        # перемещены в горизонт
        # self.layout.addWidget(self.delimeterL)
        # self.layout.addWidget(self.delimeter)

        # вертикальный компоновщик
        self.layout.addLayout(self.hbox)
        self.layout.addWidget(self.entry)
        self.layout.addWidget(self.randomize_button)
        self.layout.addWidget(self.result_output)  # Добавлено поле вывода результата
        self.layout.addWidget(self.template_label)

        self.setLayout(self.layout)
        self.setWindowTitle('Randomi')  # название окна


    # функция нормализации примера (для , ->  1,2,3 в {1|2|3})
    def normalize_template(self, template, delim):
        norm_template = sub(f"{delim}", "|", template)
        return norm_template


    def randomize_text(self):
        try:
            template = self.entry.toPlainText()  # Получение текста из QTextEdit
            norm_template = self.normalize_template(template, self.delimeter.text())
            text_rnd = TextRandomizer(norm_template)
            self.result_output.setText(text_rnd.get_text())  # Вывод результата в QTextEdit
        except Exception as e:
            self.result_output.setText(f"Error: {str(e)}")  # Вывод ошибки в QTextEdit


    def loadSettings(self):  # загрузка
        self.template_label.setText(self.settings.value('template_label', ''))
        self.entry.setPlainText(self.settings.value('entry', ''))
        self.result_output.setText(self.settings.value('result_output', ''))


    def saveSettings(self):  # сохранение
        self.settings.setValue('template_label', self.template_label.toPlainText())
        self.settings.setValue('entry', self.entry.toPlainText())
        self.settings.setValue('result_output', self.result_output.toPlainText())


    def closeEvent(self, event):  # действие при закрытии
        self.saveSettings()
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication([])
    window = TextRandomizerGUI()
    window.show()
    app.exec_()
