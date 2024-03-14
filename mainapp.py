import sys  # sys нужен для передачи argv в QApplication

from PyQt5 import QtWidgets, QtCore

import design


class ExampleApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна

        self.AddBlockButton.clicked.connect(self.add_tab)
        self.buttonEvent= self.tabWidget.tabCloseRequested
        self.buttonEvent.connect(self.purge_tab)


    def pb1click(self):
        self.lineEdit.setText("sghetbrr")


    def add_tab(self):
        tab_name = "block"
        tab = QtWidgets.QWidget()
        tab.setObjectName(tab_name)
        tab_Layout = QtWidgets.QGridLayout(tab)
        tab_Layout.setObjectName(tab_name + "_Layout")
        tab_comboBox = QtWidgets.QComboBox(tab)
        tab_comboBox.setObjectName(tab_name + "_comboBox")
        tab_Layout.addWidget(tab_comboBox, 0, 1, 1, 1)
        tab_DelimeterLineEdit = QtWidgets.QLineEdit(tab)
        tab_DelimeterLineEdit.setMinimumSize(QtCore.QSize(0, 20))
        tab_DelimeterLineEdit.setMaximumSize(QtCore.QSize(80, 20))
        tab_DelimeterLineEdit.setObjectName(tab_name + "_DelimeterLineEdit")
        tab_DelimeterLineEdit.setPlaceholderText("Delimeter")
        tab_Layout.addWidget(tab_DelimeterLineEdit, 0, 0, 1, 1)
        tab_textEdit = QtWidgets.QTextEdit(tab)
        tab_textEdit.setObjectName(tab_name + "_textEdit")
        tab_Layout.addWidget(tab_textEdit, 1, 0, 1, 2)
        self.tabWidget.addTab(tab, tab_name)


    def purge_tab(self,index):
        self.tabWidget.removeTab(index)



def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение


if (__name__ == '__main__'):
    main()
