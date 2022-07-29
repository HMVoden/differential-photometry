#!/usr/bin/env python3
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon


class IconButton(QPushButton):
    def __init__(self, icon: QIcon):
        QPushButton.__init__(self)

        self.setMinimumWidth(24)
        self.setMaximumWidth(24)

        self.setIcon(icon)


class DropdownButton(QPushButton):
    pass
