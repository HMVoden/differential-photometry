#!/usr/bin/env python3
from PySide6.QtWidgets import QWidget, QPushButton, QHBoxLayout, QFrame
from shutterbug.ux.gui.buttons import ButtonCluster, IconButton
from PySide6.QtGui import QIcon, QPixmap


class MainBar(QFrame):
    def __init__(self):
        QFrame.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.setMinimumHeight(32)
        self.setMaximumHeight(32)

        # Main Menu
        self.main_menu = ButtonCluster()
        self.main_menu.addWidget(IconButton(QIcon(QPixmap(":/icons/placeholder"))))
        self.main_menu.addWidget(QPushButton("File"))
        self.main_menu.addWidget(QPushButton("Edit"))
        self.main_menu.addWidget(QPushButton("Window"))
        self.main_menu.addWidget(QPushButton("Help"))

        self.layout.addWidget(self.main_menu)

        # Main Tabs
        self.main_nav = ButtonCluster()
        self.main_nav.addWidget(QPushButton("Graphing"))
        self.main_nav.addWidget(QPushButton("Image Processing"))
        self.main_nav.addWidget(QPushButton("Compositing"))
        self.main_nav.addWidget(IconButton(QIcon(QPixmap(":/icons/plus"))))

        self.layout.addWidget(self.main_nav)


class MainDropDown(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)


class MainTab(QPushButton):
    def __init__(self):
        QPushButton.__init__(self)
