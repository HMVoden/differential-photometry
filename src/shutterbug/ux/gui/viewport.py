#!/usr/bin/env python3
from PySide6.QtWidgets import QPushButton, QWidget, QHBoxLayout, QVBoxLayout


class ViewPort(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(ViewPortBar())


class ViewPortBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        self.layout.addWidget(MenuDropDown())
        self.layout.addWidget(MenuDropDown())
        self.layout.addWidget(MenuDropDown())

        self.layout.addWidget(MenuSelectDropDown())
        self.layout.addWidget(MenuSelectDropDown())
        self.layout.addWidget(MenuSelectDropDown())


class MenuDropDown(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)


class MenuSelectDropDown(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)
