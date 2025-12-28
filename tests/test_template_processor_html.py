# tests/test_template_processor_html.py
import random
import pytest

from randomi.template_processor import TemplateProcessor
from randomi.errors import TemplateError


def _line_col(text: str, pos: int) -> tuple[int, int]:
    line = text.count("\n", 0, pos) + 1
    last_nl = text.rfind("\n", 0, pos)
    col = pos + 1 if last_nl == -1 else pos - last_nl
    return line, col


def test_process_html_replaces_delimiter_semicolon_to_pipe():
    p = TemplateProcessor()

    entry_html = "<p>{a;b;c}</p>"
    entry_plain = "{a;b;c}\n"

    out_html = p.process_html(entry_html, entry_plain, delimiter=";", func_delimiter=",")

    # process_html возвращает HTML-строку с экранированным текстом,
    # поэтому '{a|b|c}' должно появиться как текст.
    assert "{a|b|c}" in out_html


def test_process_html_expands_word_times_n_to_multiply_result():
    p = TemplateProcessor()

    entry_html = "<p>Тест: {слово*3}.</p>"
    entry_plain = "Тест: {слово*3}.\n"

    out_html = p.process_html(entry_html, entry_plain, delimiter=";", func_delimiter=",")

    assert "слово слово слово" in out_html
    assert "слово*3" not in out_html


def test_process_html_expands_randwords_syntax_percent():
    # Стабильность: одно слово => результат всегда оно.
    p = TemplateProcessor(rng=random.Random(123))

    entry_html = "<p>Тест: {%1-1(строгий)}.</p>"
    entry_plain = "Тест: {%1-1(строгий)}.\n"

    out_html = p.process_html(entry_html, entry_plain, delimiter=";", func_delimiter=",")

    assert "строгий" in out_html
    assert "%1-1(" not in out_html


def test_process_html_template_error_has_global_position():
    p = TemplateProcessor()

    # 3 параграфа => 3 строки в plain (с '\n')
    l1 = "ТЕСТ 2 — MULTIPLY: пропущен аргумент count"
    l2 = "Здесь намеренно сделана ошибка в функции:"
    l3 = "Стиль одежды {$MULTIPLY(классический)} и дальше текст."

    entry_plain = f"{l1}\n{l2}\n{l3}\n"
    entry_html = f"<p>{l1}</p><p>{l2}</p><p>{l3}</p>"

    with pytest.raises(TemplateError) as exc:
        p.process_html(entry_html, entry_plain, delimiter=";", func_delimiter=",")

    te = exc.value

    assert "отсутствует необходимый элемент" in te.user_message
    assert te.full_text == entry_plain
    assert te.full_pos is not None

    # Проверим, что позиция действительно попадает на строку 3, символ где '$'
    line, col = _line_col(entry_plain, te.full_pos)
    assert line == 3
    assert col == (l3.index("$") + 1)  # col 1-based
