#!/usr/bin/env python3
import logging
from typing import Generator, List, Union, Optional
from PySide6.QtWidgets import (
    QFileSystemModel,
    QListView,
    QSpacerItem,
    QTableView,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QFrame,
    QLabel,
)
from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    QStandardPaths,
    QStorageInfo,
    Qt,
    Signal,
    Slot,
)
from PySide6.QtGui import QIcon, QPixmap
from shutterbug.ux.gui import rc_icons
from shutterbug.ux.gui.buttons import (
    DropdownButton,
    IconButton,
    ButtonCluster,
    CombinedDropdownButton,
)


class FileBrowser(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.fast_navigation = FastNavigation()
        self.file_view = FileView()
        # Lefthand side fast navigation placeholder
        self.layout.addWidget(self.fast_navigation)

        # Righthand side main file browser view
        self.layout.addWidget(self.file_view)

        # Signals/Slots
        self.fast_navigation.nav_changed.connect(self.file_view.change_viewed_directory)


class FastNavigation(QWidget):

    nav_changed = Signal(str, name="navChanged")

    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.setMinimumWidth(200)
        self.setMaximumWidth(200)
        self.storage = StorageVolumes()
        self.system = SystemFolders()
        self.bookmarks = Bookmarks()

        self.system.folder_selected.connect(self.nav_changed)
        self.storage.folder_selected.connect(self.nav_changed)

        self.layout.addWidget(self.storage)
        self.layout.addWidget(self.system)
        self.layout.addWidget(self.bookmarks)


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

        self.layout.setSpacing(8)
        self.setContentsMargins(0, 0, 0, 0)

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
        self.layout.addWidget(filter_cluster)

    @Slot(str, name="setDirectory")
    def set_directory(self, path: str):
        self.directory_field.setText(path)


class SaveBar(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)
        self.layout.addWidget(QLineEdit())
        self.cancel = QPushButton("Cancel")
        self.layout.addWidget(self.cancel)
        self.layout.addWidget(QPushButton("Save"))


class FileView(QWidget):

    directory_changed = Signal(str, name="directoryChanged")

    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button_bar = ButtonBar()

        self.layout.addWidget(self.button_bar)
        self.file_model = QFileSystemModel()
        default_place = QStandardPaths.standardLocations(QStandardPaths.HomeLocation)[0]
        self.view = QTableView()
        self.view.setCornerButtonEnabled(False)
        self.view.setAlternatingRowColors(True)
        self.view.setShowGrid(False)
        vert_header = self.view.verticalHeader()
        vert_header.setDisabled(True)
        vert_header.setHidden(True)

        self.view.setModel(self.file_model)
        self.layout.addWidget(self.view)
        self.layout.addWidget(SaveBar())

        # Signals/Slots
        self.directory_changed.connect(self.button_bar.set_directory)
        self.view.doubleClicked.connect(self.double_click_item)

        # Final init
        self.change_viewed_directory(default_place)

    @Slot(str, name="changeViewedDirectory")
    def change_viewed_directory(self, path: str):
        self.file_model.setRootPath(path)
        self.view.setRootIndex(self.file_model.index(self.file_model.rootPath()))
        self.directory_changed.emit(path)

    @Slot(QModelIndex, name="DoubleClickItem")
    def double_click_item(self, index: QModelIndex):
        if self.file_model.isDir(index):
            dir_name = self.file_model.data(index, role=0)
            current_dir = self.file_model.rootDirectory()
            current_dir.cd(dir_name)
            logging.debug(f"Opening folder: {current_dir.absolutePath()}")
            self.change_viewed_directory(current_dir.absolutePath())


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

    folder_selected = Signal(str, name="folderSelected")

    def __init__(self):
        CollapsibleGroup.__init__(self, "Volumes")

        volumes = list(self.readable_storage_volumes())

        self.model = StaticStringListModel(volumes)
        self.view = QListView()
        self.view.setModel(self.model)

        self.layout.addWidget(self.view)

        self.view.clicked.connect(self.select_folder)

    @staticmethod
    def readable_storage_volumes() -> Generator[str, None, None]:
        for storage in QStorageInfo.mountedVolumes():
            if (
                storage.isValid()
                and storage.isReady()
                and not storage.isReadOnly()
                and (storage.fileSystemType() != "tmpfs")
                and (storage.fileSystemType() != "vfat")
            ):
                yield storage.displayName()

    @Slot(int, name="selectFolder")
    def select_folder(self, index: QModelIndex):
        location = self.model.data(index, role=0)
        self.folder_selected.emit(location)


class SystemFolders(CollapsibleGroup):

    folder_selected = Signal(str, name="folderSelected")

    sys_folders = {
        "Home": QStandardPaths.HomeLocation,
        "Desktop": QStandardPaths.DesktopLocation,
        "Documents": QStandardPaths.DocumentsLocation,
        "Downloads": QStandardPaths.DownloadLocation,
        "Videos": QStandardPaths.MoviesLocation,
        "Music": QStandardPaths.MusicLocation,
    }

    def __init__(self):
        CollapsibleGroup.__init__(self, "System")

        location_titles = list(self.sys_folders.keys())
        self.model = StaticStringListModel(location_titles)
        self.view = QListView()
        self.view.setModel(self.model)
        self.view.clicked.connect(self.select_folder)
        self.layout.addWidget(self.view)

    @Slot(int, name="selectFolder")
    def select_folder(self, index: QModelIndex):
        name = self.model.data(index, Qt.DisplayRole)
        if name is not None:
            location = self.sys_folders.get(name)
            path = QStandardPaths.standardLocations(location)
            if len(path) > 0:
                self.folder_selected.emit(path[0])


class Bookmarks(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "Bookmarks")

        self.layout.addWidget(QPushButton(text="Add Bookmark"))


class Recents(CollapsibleGroup):
    def __init__(self):
        CollapsibleGroup.__init__(self, "Recent")

    def get_most_recent(self) -> Union[None, str]:
        return None
