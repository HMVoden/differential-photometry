import logging
from pathlib import Path

from kivy.app import App
from kivy.event import EventDispatcher
from kivy.factory import Factory
from kivy.logger import Logger
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.button import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.eventmanager import EventManagerBase
from kivy.core.window import WindowBase
from shutterbug.application import initialize_application, make_file_loader
from shutterbug.ux.gui.selectable import Selectable
from shutterbug.ux.gui.selection_manager import get_selection_manager
import matplotlib as plt


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class DatasetPanel(GridLayout):
    loadfile = ObjectProperty(None)
    scrollview = ObjectProperty(None)
    treeview = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        path = Path(filename[0])
        in_file = make_file_loader(path)
        file_node = self.treeview.add_node(TreeSelectable(text=path.stem))
        for dataset in in_file:
            for name in dataset.names:
                self.treeview.add_node(TreeSelectable(text=name), file_node)
        self.dismiss_popup()

    def remove_dataset(self):
        selected = self.treeview.selected_node
        if isinstance(selected, TreeViewLabel) and (selected != self.treeview.root):
            logging.info(f"Removing dataset {selected.text} from view")
            self.treeview.remove_node(selected)


class TreeSelectable(Selectable, TreeViewLabel):
    def on_release(self):
        manager = get_selection_manager()
        manager.select(self)

    def on_select(self):
        manager = get_selection_manager()
        if self == manager.active_selection:
            return True

    def on_unselect(self):
        pass


class Root(FloatLayout):
    pass


class Main(App):
    def build(self):
        get_selection_manager()
        pass


def run_gui():
    plt.use("module://shutterbug.ux.gui.kivy_matplotlib")
    Main().run()


if __name__ == "__main__":
    run_gui()
