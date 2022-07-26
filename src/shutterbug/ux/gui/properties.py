#!/usr/bin/env python3

from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QFrame,
    QLineEdit,
)


class Properties(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(PropertiesBar())
        self.layout.addWidget(PropertiesMainView())


class PropertiesBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        self.layout.addWidget(QPushButton())
        self.layout.addWidget(QLineEdit())
        self.layout.addWidget(QPushButton())


class PropertiesMainView(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(PropertiesTabs())
        self.layout.addWidget(PropertiesTabView())


class PropertiesTabs(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setMinimumWidth(40)
        self.setMaximumWidth(40)


class PropertiesTabView(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
