import os
import sys
import logging


def get_base_dir() -> str:
    """
    Базовая папка для логов и прочего:
    - при запуске .py: рядом со скриптом;
    - при запуске .exe (PyInstaller): рядом с exe.
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def setup_logger(name: str = "randomi") -> tuple[logging.Logger, str]:
    base_dir = get_base_dir()
    log_dir = os.path.join(base_dir, "logs_Randomi")
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print("Не удалось создать папку логов:", log_dir, e)

    log_path = os.path.join(log_dir, "randomi.log")

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        # консоль (если есть)
        try:
            ch = logging.StreamHandler(sys.stdout)
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))
            logger.addHandler(ch)
        except Exception:
            pass

        # файл
        try:
            fh = logging.FileHandler(log_path, encoding="utf-8")
            fh.setLevel(logging.DEBUG)
            fh.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s'))
            logger.addHandler(fh)
        except Exception as e:
            print("Не удалось открыть лог-файл:", log_path, e)

    logger.info("Логирование инициализировано, BASE_DIR=%s, LOG_PATH=%s", base_dir, log_path)
    return logger, log_path


log, LOG_PATH = setup_logger()
