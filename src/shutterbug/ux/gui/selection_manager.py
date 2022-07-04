import logging
from kivy.event import EventDispatcher
from kivy.properties import ListProperty

from shutterbug.ux.gui.selectable import Selectable

manager = None


class SelectionManager(EventDispatcher):
    selections = ListProperty([])
    _last_selection = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def active_selection(self):
        return self._last_selection

    def select(self, selection: Selectable, multi: bool = False) -> bool:
        if selection in self.selections:
            return False  # Don't double select
        if selection == self.active_selection:
            return False  # Don't try to select twice
        logging.info("Selected")
        self.selections.append(selection)
        if not multi:
            if self.active_selection is not None:
                self.active_selection.on_unselect()
            self.clear_selection()
        self._last_selection = selection
        return True

    def unselect(self, selection: Selectable, multi: bool = False) -> bool:
        if selection not in self.selections:
            return False
        self.selections.remove(selection)
        self.dispatch("on_unselect")
        logging.info("Unselected")
        return True

    def clear_selection(self) -> bool:
        for selection in self.selections[:]:
            self.unselect(selection)
        self._last_selection = None
        return True


def get_selection_manager() -> SelectionManager:
    global manager
    if manager is None:
        manager = SelectionManager()
        return manager
    else:
        return manager
