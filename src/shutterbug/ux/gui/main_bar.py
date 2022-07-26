#!/usr/bin/env python3
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFrame


class MainBar(QFrame):
    def __init__(self):
        QFrame.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        self.layout.addWidget(MainDropDown())
        self.layout.addWidget(MainTab())


class MainDropDown(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)


class MainTab(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)
