#!/usr/bin/env python3
import sys
from PySide6 import QtWidgets
from shutterbug.ux.gui.file_browser import FileBrowser


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        pass


def run_gui():
    app = QtWidgets.QApplication([])

    main = FileBrowser()
    main.resize(800, 600)
    main.show()

    sys.exit(app.exec())
