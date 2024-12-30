import sys
from PyQt5.QtWidgets import QApplication
from gui import TextRandomizerGUI

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TextRandomizerGUI()
    window.show()
    sys.exit(app.exec_())
