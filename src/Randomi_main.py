import sys
import os
import logging
import re
import random
import json
import html
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit,
    QSplitter, QFileDialog, QSlider, QDialog, QMessageBox, QCheckBox
)
from PyQt5.QtCore import QSettings, Qt

from PyQt5.QtGui import QTextCharFormat, QFont, QTextCursor, QTextDocument
from text_randomizer import TextRandomizer

# =========================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# =========================

def get_base_dir():
    """
    Базовая папка для логов и прочего:
    - при запуске .py: рядом с файлом;
    - при запуске .exe (PyInstaller): рядом с exe.
    """
    if getattr(sys, "frozen", False):
        # "Замороженное" приложение (PyInstaller)
        return os.path.dirname(sys.executable)
    # Обычный скрипт
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = get_base_dir()
LOG_DIR = os.path.join(BASE_DIR, "logs_Randomi")

try:
    os.makedirs(LOG_DIR, exist_ok=True)
except Exception as e:
    # Если даже папку создать не можем – логируем хоть в stdout
    print("Не удалось создать папку логов:", LOG_DIR, e)

LOG_PATH = os.path.join(LOG_DIR, "randomi.log")

# Свой отдельный логгер, не зависящий от basicConfig
log = logging.getLogger("randomi")
log.setLevel(logging.DEBUG)
log.propagate = False  # чтобы не дублировать сообщения выше

# Чтобы при повторном запуске модуля не копились хендлеры
if not log.handlers:
    # Пишем в консоль (если она есть)
    try:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
        ))
        log.addHandler(console_handler)
    except Exception:
        pass  # в windowed-режиме stdout может быть None – не страшно

    # Пишем в файл рядом с exe / .py
    try:
        file_handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s %(name)s: %(message)s'
        ))
        log.addHandler(file_handler)
    except Exception as e:
        # Последний шанс что-то увидеть
        print("Не удалось открыть лог-файл:", LOG_PATH, e)

log.info("Логирование инициализировано, BASE_DIR=%s, LOG_PATH=%s", BASE_DIR, LOG_PATH)

class TemplateError(Exception):
    """
    Ошибка в шаблоне пользователя.

    local_text  – кусок текста, в котором нашли ошибку (как сейчас)
    local_pos   – позиция символа внутри этого куска
    full_text   – весь текст пользователя
    full_pos    – позиция символа во всём тексте
    """
    def __init__(self, user_message, local_text, local_pos,
                 inner=None, full_text=None, full_pos=None):
        super().__init__(user_message)
        self.user_message = user_message
        self.text = local_text
        self.pos = local_pos
        self.inner = inner
        self.full_text = full_text
        self.full_pos = full_pos


class TextRandomizerGUI(QWidget):
    def __init__(self):
        log.info("Инициализация GUI TextRandomizerGUI")
        super().__init__()
        self.initUI()
        self.settings = QSettings('Randomi', 'TextRandomizerGUI')

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

        # Подгружаем настройки после того, как всё создано
        self.loadSettings()
        log.info("GUI инициализирован, настройки загружены")

    def changeFontSize(self, value):
        """Изменение размера шрифта во всех основных полях."""
        log.debug("Изменение размера шрифта: %s", value)
        font = self.entry.font()
        font.setPointSize(value)
        self.entry.setFont(font)
        self.result_output.setFont(font)
        self.template_label.setFont(font)

        # применение размера шрифта ко всему тексту
        fmt = QTextCharFormat()
        fmt.setFontPointSize(value)

        for editor in (self.entry, self.result_output, self.template_label):
            cursor = editor.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.Document)  # выделяем весь документ
            cursor.mergeCharFormat(fmt)  # меняем size, не трогая остальное форматирование
            cursor.clearSelection()
            editor.setTextCursor(cursor)
            cursor.endEditBlock()

        for editor in (self.entry, self.result_output, self.template_label):
            cursor = editor.textCursor()
            cursor.beginEditBlock()
            cursor.select(QTextCursor.Document)  # выделяем весь документ
            cursor.mergeCharFormat(fmt)  # меняем size, не трогая остальное форматирование
            cursor.clearSelection()
            editor.setTextCursor(cursor)
            cursor.endEditBlock()
            log.info("Размер шрифта изменен")


    def initUI(self):
        log.debug("Создание элементов UI")
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
        self.entry.focusInEvent = self.make_focus_in_event(self.entry, "entry")
        self.template_label.focusInEvent = self.make_focus_in_event(self.template_label, "template_label")
        self.result_output.focusInEvent = self.make_focus_in_event(self.result_output, "result_output")

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
        log.debug("UI создан")

    def make_focus_in_event(self, widget, name: str):
        """Обёртка для событий фокуса, чтобы помнить последнее активное поле и логировать переключения."""

        def focus_in_event(event):
            self.last_focused_text_edit = widget
            log.info("Фокус перешёл в поле: %s", name)
            QTextEdit.focusInEvent(widget, event)

        return focus_in_event

    def applyFormattingToSelectedText(self, text_edit):
        """Переключение жирности у выделенного текста."""
        cursor = text_edit.textCursor()
        if not cursor.hasSelection():
            log.debug("Попытка применить форматирование без выделения текста")
            return
        char_format = cursor.charFormat()
        is_bold = char_format.font().bold()
        char_format.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)
        cursor.setCharFormat(char_format)
        log.info("Форматирование жирности переключено (текущее состояние: %s)", "bold" if not is_bold else "normal")

    def toggleBold(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            log.info("Нажата кнопка Bold для текущего поля")
            self.applyFormattingToSelectedText(text_edit)
        else:
            log.info("Нажатие Bold без активного текстового поля")

    def resetFormatting(self):
        text_edit = self.get_current_text_edit()
        if text_edit:
            log.info("Сброс форматирования для текущего поля")
            cursor = text_edit.textCursor()
            cursor.select(cursor.Document)
            cursor.setCharFormat(QTextCharFormat())
            cursor.clearSelection()
            text_edit.setTextCursor(cursor)
        else:
            log.info("Попытка сбросить форматирование без активного текстового поля")

    def randomize_text(self):
        """Основной метод: парсинг HTML, подготовка шаблонов и запуск TextRandomizer."""
        log.info("Запуск рандомизации текста")
        try:
            # Полный текст пользователя (для глобальных строк/символов)
            full_text = self.entry.toPlainText()
            self._full_text = full_text  # на всякий случай сохраним в объекте

            template = self.entry.toHtml()
            delimiter = self.delimiter.text()
            func_delimiter = self.func_delimiter.text()
            log.debug("Получен HTML из поля ввода, delimiter=%r, func_delimiter=%r",
                      delimiter, func_delimiter)

            parts = re.split(r'(<[^>]+>)', template)
            new_parts = []

            # будем искать каждый текстовый кусок в full_text, двигаясь вперёд
            search_from = 0

            for part in parts:
                if part.startswith('<'):
                    new_parts.append(part)
                else:
                    original_part = part  # оригинальный текст без наших преобразований

                    # Пытаемся найти этот кусок в полном тексте, чтобы знать глобальное смещение
                    base_offset = None
                    if full_text:
                        idx = full_text.find(original_part, search_from)
                        if idx != -1:
                            base_offset = idx
                            search_from = idx + len(original_part)
                        # если не нашли, НИЧЕГО не придумываем — base_offset остаётся None

                    # дальше твоя существующая обработка:
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

                    # ВАЖНО: передаём base_offset внутрь evaluate_functions_in_text
                    part = self.evaluate_functions_in_text(part, func_delimiter,
                                                           base_offset=base_offset)

                    new_parts.append(part)

            randomized_html = ''.join(new_parts)
            text_rnd = TextRandomizer(randomized_html)
            final_html = text_rnd.get_text()
            log.info("Получен рандомизированный HTML")
            self.result_output.setHtml(final_html)

        except TemplateError as te:
            # наш кастомный разбор ошибки с позицией
            self.show_template_error(te)

        except Exception as e:
            # прочие ошибки
            self.result_output.setHtml(f"<p>Error: {html.escape(str(e))}</p>")
            log.error("Ошибка в randomize_text: %s", e, exc_info=True)

    def evaluate_functions_in_text(self, text, func_delimiter, base_offset=0):
        """
        Разворачивает функции $MULTIPLY и $RANDWORDS в строке `text`.
        base_offset — индекс начала этого текста во всём шаблоне.
        При ошибках кидает TemplateError с глобальными координатами.
        """
        log.debug("Старт evaluate_functions_in_text, func_delimiter=%r, base_offset=%s",
                  func_delimiter, base_offset)

        full_text = getattr(self, "_full_text", None)  # полный текст из randomize_text

        def make_error(msg, local_pos, inner=None):
            """Упаковываем всё в TemplateError с глобальной позицией."""
            if full_text is not None and base_offset is not None:
                full_pos = base_offset + local_pos
                ft = full_text
            else:
                # глобальную позицию вычислить не удалось — будем работать только с локальным куском
                full_pos = None
                ft = None

            raise TemplateError(
                msg,
                text,  # локальный кусок
                local_pos,  # позиция внутри локального куска
                inner=inner,
                full_text=ft,  # либо весь текст, либо None
                full_pos=full_pos,
            )

        def parse_function(s, start):
            func_name = ''
            i = start
            while i < len(s) and (s[i].isalnum() or s[i] == '_'):
                func_name += s[i]
                i += 1
            if i >= len(s) or s[i] != '(':
                return None, start

            i += 1  # пропускаем '('
            log.debug("Найден вызов функции %r", func_name)
            args = []
            arg = ''
            depth = 1
            while i < len(s) and depth > 0:
                if depth == 1 and s[i:i + len(func_delimiter)] == func_delimiter:
                    args.append(arg)
                    arg = ''
                    i += len(func_delimiter)
                elif s[i] == '(':
                    depth += 1
                    arg += s[i]
                    i += 1
                elif s[i] == ')':
                    depth -= 1
                    if depth == 0:
                        args.append(arg)
                        i += 1
                        log.debug("Закрыта функция %r, аргументы=%r", func_name, args)
                        break
                    else:
                        arg += s[i]
                        i += 1
                else:
                    arg += s[i]
                    i += 1
            else:
                if depth > 0:
                    make_error(f"Несовпадающая скобка в вызове функции {func_name}",
                               start - 1)
            return {'name': func_name, 'args': args}, i

        def evaluate(s):
            log.debug("Запуск evaluate для строки длиной %d", len(s))
            result = ''
            i = 0
            while i < len(s):
                if s[i] == '$':
                    func_info, new_i = parse_function(s, i + 1)
                    if func_info:
                        try:
                            # рекурсивно разворачиваем аргументы,
                            # но ошибки изнутри перевешиваем на текущую функцию
                            try:
                                evaluated_args = [evaluate(arg) for arg in func_info['args']]
                            except TemplateError as inner_te:
                                # ошибка внутри аргумента — считаем ошибкой в этом вызове
                                make_error(inner_te.user_message, i, inner=inner_te)

                            if func_info['name'] == 'MULTIPLY':
                                res = self.multiply(*evaluated_args)
                            elif func_info['name'] == 'RANDWORDS':
                                res = self.randwords(*evaluated_args)
                            else:
                                make_error(f"Неизвестная функция {func_info['name']}", i)


                        except TypeError as e:
                            # не хватает аргументов: MULTIPLY(x) без count и т.п.
                            log.error("TypeError при вызове функции %s: %s",
                                      func_info['name'], e)
                            make_error("отсутствует необходимый элемент в функции",
                                       i, inner=e)

                        except ValueError as e:
                            # аргументы есть, но кривые (пустая строка вместо числа и т.п.)
                            log.error("ValueError при вызове функции %s: %s",
                                      func_info['name'], e)
                            make_error("некорректное значение параметра в функции",
                                       i, inner=e)

                        result += res
                        i = new_i
                        continue
                    else:
                        # просто символ '$'
                        result += s[i]
                        i += 1
                else:
                    result += s[i]
                    i += 1
            return result

        processed = evaluate(text)
        log.debug("evaluate_functions_in_text завершён")
        return processed

    def multiply(self, word, count):
        log.debug("Сработала функция MULTIPLY: word=%r, count=%r", word, count)
        if str(count).strip() == "":
            raise ValueError("параметр count пустой")
        return ' '.join([word] * int(count))

    def randwords(self, min_count, max_count, *words):
        log.debug("Сработала функция RANDWORDS: min=%r, max=%r, words=%r",
                  min_count, max_count, words)
        if str(min_count).strip() == "" or str(max_count).strip() == "":
            raise ValueError("минимум/максимум пустые")
        min_count = int(min_count)
        max_count = int(max_count)
        words = [w.strip() for w in words]
        max_count = min(max_count, len(words))
        min_count = min(min_count, max_count)
        if max_count <= 0:
            log.debug("RANDWORDS: max_count <= 0, возвращаем пустую строку")
            return ''
        num_words = random.randint(min_count, max_count)
        selected_words = random.sample(words, num_words)
        res = ' '.join(selected_words)
        log.debug("RANDWORDS выбрал %d слов: %r", num_words, res)
        return res

    def saveToFile(self):
        """Сохранение текущего состояния в JSON-файл."""
        filePath, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "JSON Files (*.json);;All Files (*)"
        )
        if filePath:
            log.info("Сохранение в файл: %s", filePath)
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
                log.error("Ошибка при сохранении файла: %s", e, exc_info=True)
                self.result_output.setHtml(f"<p>Error saving file: {str(e)}</p>")

    def loadFromFile(self):
        """Загрузка состояния из JSON-файла."""
        filePath, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "JSON Files (*.json);;All Files (*)"
        )
        if filePath:
            log.info("Загрузка из файла: %s", filePath)
            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                self.entry.setHtml(data.get('entry', ''))
                self.result_output.setHtml(data.get('result_output', ''))
                self.template_label.setHtml(data.get('template_label', ''))
                self.delimiter.setText(data.get('delimiter', ';'))
                self.func_delimiter.setText(data.get('func_delimiter', ','))
                self.changeFontSize(self.font_size_slider.value()) # применяем текущий размер шрифта ко всему загруженному тексту
            except Exception as e:
                log.error("Ошибка при загрузке файла: %s", e, exc_info=True)
                self.result_output.setHtml(f"<p>Error loading file: {str(e)}</p>")

    def loadSettings(self):
        # Загрузка настроек из QSettings.
        log.debug("Загрузка настроек из QSettings")
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
        log.info("Настройки загружены")
        self.changeFontSize(self.font_size_slider.value())
        log.info("Размер шрифта применён")

    def saveSettings(self):
        """Сохранение настроек в QSettings."""
        log.info("Сохранение настроек в QSettings")
        self.settings.setValue('template_label', self.template_label.toHtml())
        self.settings.setValue('entry', self.entry.toHtml())
        self.settings.setValue('result_output', self.result_output.toHtml())
        self.settings.setValue('delimiter', self.delimiter.text())
        self.settings.setValue('func_delimiter', self.func_delimiter.text())

    def closeEvent(self, event):
        """Обработка закрытия окна: сохраняем настройки."""
        log.info("Окно закрывается, сохраняем настройки")
        self.saveSettings()
        super().closeEvent(event)

    def open_find_replace_dialog(self):
        """Открытие диалога поиска/замены."""
        log.info("Открытие окна Find & Replace")
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()

    def get_current_text_edit(self):
        """Возвращаем последнее активное текстовое поле."""
        return self.last_focused_text_edit

    def show_template_error(self, te: TemplateError):
        """
        Красивый вывод ошибки шаблона:
        – сообщение,
        – строка и столбец,
        – кусок текста вокруг ошибки.
        """
        import html as _html

        # 1) ЛОКАЛЬНЫЙ текст и позиция (то, с чем работал парсер)
        local_text = te.text or ""
        local_pos = te.pos or 0
        local_pos = max(0, min(local_pos, len(local_text)))

        # Локальный сниппет вокруг ошибки
        loc_snippet_start = max(0, local_pos - 40)
        loc_snippet_end = min(len(local_text), local_pos + 40)
        loc_snippet = local_text[loc_snippet_start:loc_snippet_end]

        loc_marker = local_pos - loc_snippet_start
        loc_before = loc_snippet[:loc_marker]
        loc_error_char = loc_snippet[loc_marker:loc_marker + 1]
        loc_after = loc_snippet[loc_marker + 1:]

        # По локальному тексту пока считаем строку/символ
        loc_line = local_text.count('\n', 0, local_pos) + 1
        loc_last_nl = local_text.rfind('\n', 0, local_pos)
        if loc_last_nl == -1:
            loc_col = local_pos + 1
        else:
            loc_col = local_pos - loc_last_nl

        # 2) ПЫТАЕМСЯ пересчитать координаты по всему тексту из QTextEdit
        full_text = self.entry.toPlainText()
        global_line = loc_line
        global_col = loc_col
        snippet_for_search = loc_snippet

        if full_text and snippet_for_search.strip():
            idx = full_text.find(snippet_for_search)
            if idx != -1:
                global_pos = idx + loc_marker
                global_pos = max(0, min(global_pos, len(full_text)))

                global_line = full_text.count('\n', 0, global_pos) + 1
                g_last_nl = full_text.rfind('\n', 0, global_pos)
                if g_last_nl == -1:
                    global_col = global_pos + 1
                else:
                    global_col = global_pos - g_last_nl

        # 3) Используем локальный сниппет для отображения (он уже нормальный)
        snippet_html = (
            f"{_html.escape(loc_before)}"
            f"<span style='background-color:#ffcccc;color:#000;'>"
            f"{_html.escape(loc_error_char) if loc_error_char else '⟂'}"
            f"</span>"
            f"{_html.escape(loc_after)}"
        )

        user_msg = te.user_message or "Ошибка в шаблоне"

        html_msg = (
            f"<p><b>Ошибка в шаблоне:</b> {_html.escape(user_msg)}</p>"
            f"<p>Строка {global_line}, символ {global_col}</p>"
            f"<p><code>{snippet_html}</code></p>"
        )

        self.result_output.setHtml(html_msg)

        log.error(
            "TemplateError: %s (global line %d, col %d, loc line %d, col %d, context=%r)",
            user_msg, global_line, global_col, loc_line, loc_col, loc_snippet,
            exc_info=te.inner or True
        )


class FindReplaceDialog(QDialog):
    def __init__(self, parent=None):
        super(FindReplaceDialog, self).__init__(parent)
        self.parent = parent
        log.debug("Инициализация FindReplaceDialog")
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Find & Replace')

        # Поля ввода для поиска и замены
        self.find_label = QLabel('Find:', self)
        self.find_input = QLineEdit(self)

        self.replace_label = QLabel('Replace:', self)
        self.replace_input = QLineEdit(self)

        # Флажок для учета регистра
        self.case_sensitive_checkbox = QCheckBox('Case Sensitive', self)

        # Кнопки
        self.find_next_button = QPushButton('Find Next', self)
        self.replace_button = QPushButton('Replace', self)
        self.replace_all_button = QPushButton('Replace All', self)
        self.close_button = QPushButton('Close', self)

        # Подключение сигналов к слотам
        self.find_next_button.clicked.connect(self.find_next)
        self.replace_button.clicked.connect(self.replace)
        self.replace_all_button.clicked.connect(self.replace_all)
        self.close_button.clicked.connect(self.close)

        # Макеты
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
            log.debug("Find Next: пустая строка поиска")
            return

        # Получаем текущее текстовое поле из родительского окна
        text_edit = self.parent.get_current_text_edit()
        if not text_edit:
            log.warning("Find Next без выбранного текстового поля")
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to search.')
            return

        # Установка опций поиска
        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

        # Поиск текста
        found = text_edit.find(text_to_find, options)
        if not found:
            # Если не найдено, начать с начала документа
            cursor = text_edit.textCursor()
            cursor.movePosition(QTextCursor.Start)
            text_edit.setTextCursor(cursor)
            found = text_edit.find(text_to_find, options)
            if not found:
                log.info("Текст '%s' не найден при поиске", text_to_find)
                QMessageBox.information(self, 'Not Found', 'Text not found.')
        else:
            log.debug("Найдено вхождение '%s'", text_to_find)

    def replace(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        if not text_to_find:
            log.debug("Replace: пустая строка поиска")
            return

        text_edit = self.parent.get_current_text_edit()
        if not text_edit:
            log.warning("Replace без выбранного текстового поля")
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to replace.')
            return

        cursor = text_edit.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == text_to_find:
            cursor.insertText(replace_with)
            text_edit.setTextCursor(cursor)
            log.debug("Replace: одно вхождение '%s' заменено на '%s'", text_to_find, replace_with)
            self.find_next()
        else:
            self.find_next()

    def replace_all(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        if not text_to_find:
            log.debug("Replace All: пустая строка поиска")
            return

        text_edit = self.parent.get_current_text_edit()
        if not text_edit:
            log.warning("Replace All без выбранного текстового поля")
            QMessageBox.warning(self, 'No Text Field Selected', 'Please select a text field to replace.')
            return

        # Установка опций поиска
        options = QTextDocument.FindFlags()
        if self.case_sensitive_checkbox.isChecked():
            options |= QTextDocument.FindCaseSensitively

        cursor = text_edit.textCursor()
        cursor.beginEditBlock()

        # Перемещаем курсор в начало
        cursor.movePosition(QTextCursor.Start)
        text_edit.setTextCursor(cursor)

        replaced = 0
        while text_edit.find(text_to_find, options):
            cursor = text_edit.textCursor()
            cursor.insertText(replace_with)
            replaced += 1

        cursor.endEditBlock()
        log.info("Replace All: заменено %d вхождений '%s' на '%s'",
                 replaced, text_to_find, replace_with)
        QMessageBox.information(self, 'Replace All', f'Replaced {replaced} occurrences.')


if __name__ == '__main__':
    log.info("Запуск QApplication")
    app = QApplication(sys.argv)
    window = TextRandomizerGUI()
    window.show()
    exit_code = app.exec_()
    log.info("Приложение завершило работу с кодом %s", exit_code)
    sys.exit(exit_code)
