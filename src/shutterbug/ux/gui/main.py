#!/usr/bin/env python3
import sys
from PySide6.QtWidgets import (
    QHBoxLayout,
    QApplication,
    QVBoxLayout,
    QWidget,
)
from shutterbug.ux.gui.main_bar import MainBar
from shutterbug.ux.gui.outliner import Outliner
from shutterbug.ux.gui.properties import Properties
from shutterbug.ux.gui.status_bar import StatusBar
from shutterbug.ux.gui.viewport import ViewPort


class MainWindow(QWidget):
    """Main window of application, intentionally not using
    QMainWindow
    """

    def __init__(self):
        QWidget.__init__(self)
        self.setWindowTitle("Shutterbug")

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(MainBar())
        self.layout.addWidget(Workspace())
        self.layout.addWidget(StatusBar())


class Workspace(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(ViewPort())
        self.layout.addWidget(SideBar())


class SideBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(Outliner())
        self.layout.addWidget(Properties())


def run_gui():
    app = QApplication([])

    main = MainWindow()
    main.resize(800, 600)
    main.show()

    sys.exit(app.exec())
