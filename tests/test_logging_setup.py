# tests/test_logging_setup.py

def test_logger_does_not_duplicate_handlers():
    from randomi.logging_setup import setup_logger

    log1, _ = setup_logger("randomi_test_logger")
    handlers_count_1 = len(log1.handlers)

    log2, _ = setup_logger("randomi_test_logger")
    handlers_count_2 = len(log2.handlers)

    assert log1 is log2
    assert handlers_count_1 == handlers_count_2
    assert handlers_count_1 > 0
