#!/usr/bin/env python3
import sys
from PySide6 import QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        pass


def run_gui():
    app = QtWidgets.QApplication([])

    main = MainWindow()
    main.resize(800, 600)
    main.show()

    sys.exit(app.exec())
