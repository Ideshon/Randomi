import sys
from PyQt5.QtWidgets import QApplication

from .logging_setup import log
from .gui.main_window import TextRandomizerGUI


def main():
    log.info("Запуск QApplication")
    app = QApplication(sys.argv)

    window = TextRandomizerGUI()
    window.show()

    exit_code = app.exec_()
    log.info("Приложение завершило работу с кодом %s", exit_code)
    sys.exit(exit_code)
