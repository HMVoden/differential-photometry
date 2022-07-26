#!/usr/bin/env python3

from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout


class StatusBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)
