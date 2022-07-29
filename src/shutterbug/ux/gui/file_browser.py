#!/usr/bin/env python3
from PySide6 import QtWidgets
from PySide6.QtWidgets import (
    QFileSystemModel,
    QListView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFrame,
    QLabel,
)
from PySide6.QtCore import QStandardPaths, QStorageInfo
from PySide6.QtGui import QIcon, QPixmap
from shutterbug.ux.gui import rc_icons
from shutterbug.ux.gui.buttons import IconButton


class FileBrowser(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Lefthand side fast navigation placeholder
        self.layout.addWidget(FastNavigation())

        # Righthand side main file browser view
        self.layout.addWidget(FileView())


class FastNavigation(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setMinimumWidth(200)

        self.layout.addWidget(StorageVolumes())
        self.layout.addWidget(SystemFolders())
        self.layout.addWidget(Bookmarks())


class CollapsibleGroup(QFrame):
    def __init__(self, header_text: str):
        QFrame.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.setFrameStyle(QFrame.Raised)

        label = QLabel(text=header_text)
        self.layout.addWidget(label)


class ButtonBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Nav Group
        icon_back = QIcon(QPixmap(":/icons/arrow-left"))
        icon_fwd = QIcon(QPixmap(":/icons/arrow-right"))
        icon_up = QIcon(QPixmap(":/icons/long-arrow-left-up"))
        icon_refresh = QIcon(QPixmap(":/icons/refresh"))
        self.layout.addWidget(IconButton(icon_back))
        self.layout.addWidget(IconButton(icon_fwd))
        self.layout.addWidget(IconButton(icon_up))
        self.layout.addWidget(IconButton(icon_refresh))

        # Make Dir Group
        icon_add_dir = QIcon(QPixmap(":/icons/add-folder"))
        self.layout.addWidget(IconButton(icon_add_dir))

        # Directory and Search
        self.layout.addWidget(QLineEdit())
        self.layout.addWidget(QLineEdit())

        # Display Mode

        # Filter


class SaveBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QLineEdit())
        self.layout.addWidget(QPushButton("Cancel"))
        self.layout.addWidget(QPushButton("Save"))


class FileView(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(ButtonBar())
        file_model = QFileSystemModel()
        default_place = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        file_model.setRootPath(default_place)
        list_view = QListView()
        list_view.setModel(file_model)
        list_view.setRootIndex(file_model.index(file_model.rootPath()))
        self.layout.addWidget(list_view)
        self.layout.addWidget(SaveBar())


class StorageVolumes(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "Volumes")

        for volume in QStorageInfo().mountedVolumes():
            label = QLabel()
            label.setText(volume.displayName())
            self.layout.addWidget(label)


class SystemFolders(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "System")

        self.layout.addWidget(QLabel("Home"))
        self.layout.addWidget(QLabel("Desktop"))
        self.layout.addWidget(QLabel("Documents"))
        self.layout.addWidget(QLabel("Downloads"))
        self.layout.addWidget(QLabel("Videos"))
        self.layout.addWidget(QLabel("Music"))


class Bookmarks(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "Bookmarks")

        self.layout.addWidget(QPushButton(text="Add Bookmark"))
