import json
import html as html_lib

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel, QLineEdit,
    QSplitter, QFileDialog, QSlider
)
from PyQt5.QtCore import QSettings, Qt
from PyQt5.QtGui import QTextCharFormat, QFont, QTextCursor

from text_randomizer import TextRandomizer

from ..logging_setup import log
from ..errors import TemplateError
from ..template_processor import TemplateProcessor
from .find_replace_dialog import FindReplaceDialog


class TextRandomizerGUI(QWidget):
    def __init__(self):
        super().__init__()
        log.info("Инициализация GUI TextRandomizerGUI")

        self.settings = QSettings("Randomi", "TextRandomizerGUI")
        self.last_focused_text_edit = None

        self.processor = TemplateProcessor()  # ядро (можно тестировать отдельно)

        self.init_ui()
        self.load_settings()

    # ---------- UI / helpers ----------

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Vertical, self)

        self.entry = QTextEdit(self)
        self.entry.setFocusPolicy(Qt.StrongFocus)

        self.result_output = QTextEdit(self)
        self.result_output.setReadOnly(False)
        self.result_output.setFocusPolicy(Qt.StrongFocus)

        self.template_label = QTextEdit("", self)
        self.template_label.setReadOnly(False)
        self.template_label.setFocusPolicy(Qt.StrongFocus)

        self.delimiter = QLineEdit(";", self)
        self.delimiter.setFocusPolicy(Qt.StrongFocus)

        self.func_delimiter = QLineEdit(",", self)
        self.func_delimiter.setFocusPolicy(Qt.StrongFocus)

        # фиксация активного поля
        self.entry.focusInEvent = self.make_focus_in_event(self.entry, "entry")
        self.template_label.focusInEvent = self.make_focus_in_event(self.template_label, "template_label")
        self.result_output.focusInEvent = self.make_focus_in_event(self.result_output, "result_output")

        self.splitter.addWidget(self.entry)
        self.splitter.addWidget(self.result_output)
        self.splitter.addWidget(self.template_label)

        # кнопки
        self.randomize_button = QPushButton("Randomize", self)
        self.save_button = QPushButton("Save", self)
        self.load_button = QPushButton("Load", self)
        self.bold_button = QPushButton("Bold", self)
        self.reset_button = QPushButton("Reset Formatting", self)
        self.find_replace_button = QPushButton("Find & Replace", self)

        self.randomize_button.clicked.connect(self.randomize_text)
        self.save_button.clicked.connect(self.save_to_file)
        self.load_button.clicked.connect(self.load_from_file)
        self.bold_button.clicked.connect(self.toggle_bold)
        self.reset_button.clicked.connect(self.reset_formatting)
        self.find_replace_button.clicked.connect(self.open_find_replace_dialog)

        # слайдер шрифта
        self.font_size_label = QLabel("Размер шрифта:", self)
        self.font_size_slider = QSlider(Qt.Horizontal, self)
        self.font_size_slider.setMinimum(8)
        self.font_size_slider.setMaximum(24)
        self.font_size_slider.setValue(12)
        self.font_size_slider.setTickInterval(2)
        self.font_size_slider.setTickPosition(QSlider.TicksBelow)
        self.font_size_slider.valueChanged.connect(self.change_font_size)

        # панель
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Delimiter:", self))
        hbox.addWidget(self.delimiter)
        hbox.addWidget(QLabel("Function Delimiter:", self))
        hbox.addWidget(self.func_delimiter)
        hbox.addWidget(self.randomize_button)
        hbox.addWidget(self.save_button)
        hbox.addWidget(self.load_button)
        hbox.addStretch(1)

        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.bold_button)
        hbox2.addWidget(self.reset_button)
        hbox2.addWidget(self.find_replace_button)

        self.layout.addWidget(self.splitter)
        self.layout.addLayout(hbox)
        self.layout.addLayout(hbox2)
        self.layout.addWidget(self.font_size_label)
        self.layout.addWidget(self.font_size_slider)

        self.setLayout(self.layout)
        self.setWindowTitle("Randomi")

    def make_focus_in_event(self, widget, name: str):
        def focus_in_event(event):
            self.last_focused_text_edit = widget
            log.info("Фокус перешёл в поле: %s", name)
            QTextEdit.focusInEvent(widget, event)
        return focus_in_event

    def get_current_text_edit(self):
        return self.last_focused_text_edit

    # ---------- formatting ----------

    def _apply_font_size_to_editor(self, editor: QTextEdit, value: int):
        font = editor.font()
        font.setPointSize(value)
        editor.setFont(font)

        fmt = QTextCharFormat()
        fmt.setFontPointSize(value)

        cursor = editor.textCursor()
        cursor.beginEditBlock()
        cursor.select(QTextCursor.Document)
        cursor.mergeCharFormat(fmt)
        cursor.clearSelection()
        editor.setTextCursor(cursor)
        cursor.endEditBlock()

    def change_font_size(self, value: int):
        log.debug("Изменение размера шрифта: %s", value)
        for ed in (self.entry, self.result_output, self.template_label):
            self._apply_font_size_to_editor(ed, value)

    def toggle_bold(self):
        text_edit = self.get_current_text_edit()
        if not text_edit:
            return

        cursor = text_edit.textCursor()
        if not cursor.hasSelection():
            return

        char_format = cursor.charFormat()
        is_bold = char_format.font().bold()
        char_format.setFontWeight(QFont.Bold if not is_bold else QFont.Normal)
        cursor.setCharFormat(char_format)

    def reset_formatting(self):
        text_edit = self.get_current_text_edit()
        if not text_edit:
            return

        cursor = text_edit.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(QTextCharFormat())
        cursor.clearSelection()
        text_edit.setTextCursor(cursor)

        # ещё раз применим текущий размер шрифта, чтобы “сброс” не ломал слайдер
        self.change_font_size(self.font_size_slider.value())

    # ---------- main action ----------

    def randomize_text(self):
        log.info("Запуск рандомизации текста")
        try:
            entry_plain = self.entry.toPlainText()
            entry_html = self.entry.toHtml()

            delimiter = self.delimiter.text()
            func_delimiter = self.func_delimiter.text()

            processed_html = self.processor.process_html(
                entry_html,
                entry_plain,
                delimiter=delimiter,
                func_delimiter=func_delimiter,
            )

            text_rnd = TextRandomizer(processed_html)
            final_html = text_rnd.get_text()

            self.result_output.setHtml(final_html)

        except TemplateError as te:
            self.show_template_error(te)
        except Exception as e:
            self.result_output.setHtml(f"<p>Error: {html_lib.escape(str(e))}</p>")
            log.error("Ошибка в randomize_text: %s", e, exc_info=True)

    def show_template_error(self, te: TemplateError):
        source_text = te.full_text or self.entry.toPlainText() or te.text or ""
        pos = te.full_pos if te.full_pos is not None else (te.pos or 0)
        pos = max(0, min(pos, len(source_text)))

        # строка/столбец
        line = source_text.count("\n", 0, pos) + 1
        last_nl = source_text.rfind("\n", 0, pos)
        col = pos + 1 if last_nl == -1 else (pos - last_nl)

        # сниппет
        snippet_start = max(0, pos - 40)
        snippet_end = min(len(source_text), pos + 40)
        snippet = source_text[snippet_start:snippet_end]

        marker = pos - snippet_start
        before = snippet[:marker]
        err_ch = snippet[marker:marker + 1]
        after = snippet[marker + 1:]

        snippet_html = (
            f"{html_lib.escape(before)}"
            f"<span style='background-color:#ffcccc;color:#000;'>"
            f"{html_lib.escape(err_ch) if err_ch else '⟂'}"
            f"</span>"
            f"{html_lib.escape(after)}"
        )

        user_msg = te.user_message or "Ошибка в шаблоне"
        html_msg = (
            f"<p><b>Ошибка в шаблоне:</b> {html_lib.escape(user_msg)}</p>"
            f"<p>Строка {line}, символ {col}</p>"
            f"<p><code>{snippet_html}</code></p>"
        )
        self.result_output.setHtml(html_msg)

        log.error("TemplateError: %s (line %d, col %d)", user_msg, line, col, exc_info=te.inner or True)

    # ---------- save/load/settings ----------

    def save_to_file(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save File", "", "JSON Files (*.json);;All Files (*)")
        if not file_path:
            return

        data = {
            "entry": self.entry.toHtml(),
            "result_output": self.result_output.toHtml(),
            "template_label": self.template_label.toHtml(),
            "delimiter": self.delimiter.text(),
            "func_delimiter": self.func_delimiter.text(),
        }
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            log.error("Ошибка при сохранении файла: %s", e, exc_info=True)
            self.result_output.setHtml(f"<p>Error saving file: {html_lib.escape(str(e))}</p>")

    def load_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open File", "", "JSON Files (*.json);;All Files (*)")
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.entry.setHtml(data.get("entry", ""))
            self.result_output.setHtml(data.get("result_output", ""))
            self.template_label.setHtml(data.get("template_label", ""))

            self.delimiter.setText(data.get("delimiter", ";"))
            self.func_delimiter.setText(data.get("func_delimiter", ","))

            self.change_font_size(self.font_size_slider.value())

        except Exception as e:
            log.error("Ошибка при загрузке файла: %s", e, exc_info=True)
            self.result_output.setHtml(f"<p>Error loading file: {html_lib.escape(str(e))}</p>")

    def load_settings(self):
        self.entry.setHtml(self.settings.value("entry", ""))
        self.result_output.setHtml(self.settings.value("result_output", ""))
        self.template_label.setHtml(self.settings.value("template_label", ""))

        self.delimiter.setText(self.settings.value("delimiter", ";"))
        self.func_delimiter.setText(self.settings.value("func_delimiter", ","))

        self.change_font_size(self.font_size_slider.value())

    def save_settings(self):
        self.settings.setValue("template_label", self.template_label.toHtml())
        self.settings.setValue("entry", self.entry.toHtml())
        self.settings.setValue("result_output", self.result_output.toHtml())
        self.settings.setValue("delimiter", self.delimiter.text())
        self.settings.setValue("func_delimiter", self.func_delimiter.text())

    def closeEvent(self, event):
        self.save_settings()
        super().closeEvent(event)

    def open_find_replace_dialog(self):
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()
