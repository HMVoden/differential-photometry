#!/usr/bin/env python3
from PySide6.QtWidgets import QPushButton, QWidget, QHBoxLayout
from PySide6.QtGui import QIcon, Qt


class IconButton(QPushButton):
    def __init__(self, icon: QIcon):
        QPushButton.__init__(self)

        self.setMinimumWidth(24)
        self.setMaximumWidth(24)

        self.setIcon(icon)


class DropdownButton(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)


class ButtonCluster(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)

    def addWidget(
        self,
        arg__1: QWidget,
        stretch: int = 0,
        alignment: Qt.Alignment = Qt.Alignment(),
    ):
        self.layout.addWidget(arg__1, stretch, alignment)
