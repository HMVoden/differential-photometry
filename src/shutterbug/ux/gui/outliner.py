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
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.layout.addWidget(OutlinerBar())
        self.treeview = QTreeView()
        self.layout.addWidget(self.treeview)

        self.treeview.setHeaderHidden(True)


class OutlinerBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(1, 1, 1, 1)

        self.setMinimumHeight(40)
        self.setMaximumHeight(40)

        self.layout.addWidget(QLineEdit())
