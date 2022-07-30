#!/usr/bin/env python3
from typing import List, Union, Optional
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
    QTreeView,
)
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QStandardPaths,
    QStorageInfo,
    Qt,
)
from PySide6.QtGui import QIcon, QPixmap
from shutterbug.ux.gui import rc_icons
from shutterbug.ux.gui.buttons import DropdownButton, IconButton, ButtonCluster


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
        self.setMaximumWidth(200)

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

        nav_cluster = ButtonCluster()
        self.nav_cluster = nav_cluster
        nav_cluster.addWidget(IconButton(icon_back))
        nav_cluster.addWidget(IconButton(icon_fwd))
        nav_cluster.addWidget(IconButton(icon_up))
        nav_cluster.addWidget(IconButton(icon_refresh))
        self.layout.addWidget(nav_cluster)

        # Make Dir Group
        icon_add_dir = QIcon(QPixmap(":/icons/add-folder"))
        self.layout.addWidget(IconButton(icon_add_dir))

        # Directory and Search
        self.directory_field = QLineEdit()
        self.layout.addWidget(self.directory_field)
        self.search_field = QLineEdit()
        self.layout.addWidget(self.search_field)

        # Display Mode

        # Filter

        filter_cluster = ButtonCluster()
        icon_filter = QIcon(QPixmap(":/icons/filter"))

        filter_cluster.addWidget(IconButton(icon_filter))
        filter_cluster.addWidget(DropdownButton())


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
        view = QTreeView()
        view.setItemsExpandable(False)

        view.hideColumn(1)
        view.setModel(file_model)
        view.setRootIndex(file_model.index(file_model.rootPath()))
        self.layout.addWidget(view)
        self.layout.addWidget(SaveBar())


class StaticStringListModel(QAbstractListModel):
    def __init__(self, data: List[str]):
        QAbstractListModel.__init__(self)

        self.m_itemData = data.copy()

    def rowCount(self, parent: QModelIndex) -> int:
        return len(self.m_itemData)

    def data(self, index: QModelIndex, role: int) -> Optional[str]:
        if index.isValid() and role == Qt.DisplayRole:
            return self.m_itemData[index.row()]
        else:
            return None


class StorageVolumes(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "Volumes")

        volumes = list(map(lambda x: x.displayName(), QStorageInfo.mountedVolumes()))

        model = StaticStringListModel(volumes)
        view = QListView()
        view.setModel(model)

        self.layout.addWidget(view)


class SystemFolders(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "System")

        sys_folders = ["Home", "Desktop", "Documents", "Downloads", "Videos", "Music"]

        model = StaticStringListModel(sys_folders)
        view = QListView()
        view.setModel(model)

        self.layout.addWidget(view)


class Bookmarks(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "Bookmarks")

        self.layout.addWidget(QPushButton(text="Add Bookmark"))


class Recents(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "Recent")

    def get_most_recent(self) -> Union[None, str]:
        return None
