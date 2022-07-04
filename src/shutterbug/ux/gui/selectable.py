from kivy.properties import BooleanProperty
from kivy.event import EventDispatcher
from kivy.uix.behaviors import ButtonBehavior


class Selectable(ButtonBehavior, EventDispatcher):
    selected = BooleanProperty(False)  # Start unselected

    def __init__(self, **kwargs):
        self.register_event_type("on_select")
        self.register_event_type("on_unselect")
        super().__init__(**kwargs)

    def on_release(self):
        pass

    def on_select(self):
        pass

    def on_unselect(self):
        pass

    def _toggle_select(self):
        if self.selected:
            self.selected = BooleanProperty(False)
        else:
            self.selected = BooleanProperty(True)
