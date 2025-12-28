# tests/test_template_processor_core.py
import random
import pytest

from randomi.template_processor import TemplateProcessor
from randomi.errors import TemplateError


def test_multiply_ok():
    p = TemplateProcessor()
    assert p.multiply("a", "3") == "a a a"


def test_multiply_empty_count_value_error():
    p = TemplateProcessor()
    with pytest.raises(ValueError):
        p.multiply("a", "")


def test_randwords_clamps_to_words_len():
    # min=5 max=10 при двух словах должен сжаться до 2..2 => оба слова
    p = TemplateProcessor(rng=random.Random(123))
    res = p.randwords("5", "10", "a", "b")
    parts = res.split()
    assert set(parts) == {"a", "b"}
    assert len(parts) == 2


def test_evaluate_nested_functions_stable():
    import random
    from randomi.template_processor import TemplateProcessor

    p = TemplateProcessor(rng=random.Random(999))

    # Реальный синтаксис: функции без фигурных скобок.
    text = "Комбинация: $MULTIPLY($RANDWORDS(1!1!строгий!)!2)."

    out = p.evaluate_functions_in_text(
        text,
        func_delimiter="!",
        full_text=None,
        base_offset=None,
    )

    assert "строгий строгий" in out
    assert "$MULTIPLY" not in out
    assert "$RANDWORDS" not in out



def test_missing_argument_raises_template_error_with_message_and_pos():
    p = TemplateProcessor()

    bad = "Стиль одежды {$MULTIPLY(классический)} и дальше текст."
    with pytest.raises(TemplateError) as exc:
        p.evaluate_functions_in_text(
            bad,
            func_delimiter=",",
            full_text=bad,
            base_offset=0,
        )

    te = exc.value
    assert "отсутствует необходимый элемент" in te.user_message
    assert te.pos == bad.index("$")  # позиция должна указывать на '$'


def test_invalid_count_raises_template_error_value_message():
    p = TemplateProcessor()

    bad = "Стиль одежды {$MULTIPLY(классический,)} и дальше текст."
    with pytest.raises(TemplateError) as exc:
        p.evaluate_functions_in_text(
            bad,
            func_delimiter=",",
            full_text=bad,
            base_offset=0,
        )

    te = exc.value
    assert "некорректное значение" in te.user_message
    assert te.pos == bad.index("$")

def test_curly_braces_are_not_removed_by_function_eval():
    import random
    from randomi.template_processor import TemplateProcessor

    p = TemplateProcessor(rng=random.Random(1))
    text = "X: {$MULTIPLY($RANDWORDS(1!1!a!)!2)}"
    out = p.evaluate_functions_in_text(text, func_delimiter="!", full_text=None, base_offset=None)

    # Скобки останутся, потому что это синтаксис TextRandomizer, а не нашего препроцессора.
    assert "{a a}" in out or "{{a a}}" in out
