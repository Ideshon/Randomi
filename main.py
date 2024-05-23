from PyQt5.QtWidgets import QApplication
from gui import TextRandomizerGUI

if __name__ == '__main__':
    app = QApplication([])
    window = TextRandomizerGUI()
    window.show()
    app.exec_()
