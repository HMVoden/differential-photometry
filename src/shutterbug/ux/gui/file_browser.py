#!/usr/bin/env python3
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFrame,
    QTreeView,
)


class FileBrowser(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Lefthand side fast navigation placeholder
        self.layout.addWidget(FastNavigation())

        # Righthand side main file browser view
        self.layout.addWidget(FileView())


class FastNavigation(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setMinimumWidth(200)

        self.layout.addWidget(QFrame())
        self.layout.addWidget(QFrame())
        self.layout.addWidget(QFrame())
        self.layout.addWidget(QFrame())


class ButtonBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QLineEdit())
        self.layout.addWidget(QLineEdit())


class SaveBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QLineEdit())
        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QPushButton())


class FileView(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(ButtonBar())
        self.layout.addWidget(QTreeView())
        self.layout.addWidget(SaveBar())
