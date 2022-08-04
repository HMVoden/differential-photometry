#!/usr/bin/env python3
from typing import Optional
from PySide6.QtWidgets import QFrame, QLabel, QPushButton, QWidget, QHBoxLayout
from PySide6.QtGui import QIcon, QPixmap, Qt
from shutterbug.ux.gui import rc_icons


class IconButton(QPushButton):
    def __init__(self, icon: QIcon):
        QPushButton.__init__(self)

        self.setMinimumWidth(24)
        self.setMaximumWidth(24)

        self.setIcon(icon)


class DropdownButton(IconButton):
    def __init__(self):
        IconButton.__init__(self, QIcon(QPixmap(":/icons/nav-arrow-down")))


class CombinedDropdownButton(QFrame):
    def __init__(self, icon_pixmap: QPixmap, text: Optional[str]):
        QFrame.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        main_icon = QLabel()
        main_icon.setPixmap(icon_pixmap)
        self.layout.addWidget(main_icon)

        if text is not None:
            self.layout.addWidget(QLabel(text))

        dropdown_icon = QLabel()
        dropdown_icon.setPixmap(QPixmap(":/icons/nav_arrow_down"))
        self.layout.addWidget(dropdown_icon)


class ButtonCluster(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)
        self.layout.setContentsMargins(0, 0, 0, 0)

    def addWidget(
        self,
        arg__1: QWidget,
        stretch: int = 0,
        alignment: Qt.Alignment = Qt.Alignment(),
    ):
        self.layout.addWidget(arg__1, stretch, alignment)
