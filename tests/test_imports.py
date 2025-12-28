# tests/test_imports.py

def test_imports_core_modules():
    # если после разделения где-то криво прописаны импорты, это упадёт тут
    import randomi.errors
    import randomi.logging_setup
    import randomi.template_processor


def test_imports_gui_modules_if_available():
    # GUI тестировать мы не будем (это отдельный ад),
    # но хотя бы импорт проверим, если PyQt5 установлен.
    try:
        import PyQt5  # noqa: F401
    except Exception:
        return

    import randomi.gui.main_window  # noqa: F401
    import randomi.gui.find_replace_dialog  # noqa: F401
