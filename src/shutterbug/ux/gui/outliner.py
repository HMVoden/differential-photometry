#!/usr/bin/env python3
from PySide6.QtWidgets import (
    QLineEdit,
    QPushButton,
    QTreeView,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
)


class Outliner(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(OutlinerBar())
        self.layout.addWidget(OutlinerTree())


class OutlinerBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QPushButton())

        self.layout.addWidget(QLineEdit())
        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QPushButton())


class OutlinerTree(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(QTreeView())
