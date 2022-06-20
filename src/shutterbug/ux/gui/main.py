from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.factory import Factory
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.gridlayout import GridLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.accordion import Accordion, AccordionItem
from shutterbug.application import initialize_application, make_file_loader, make_dataset, make_reader_writer
from pathlib import Path

from shutterbug.data.interfaces.external import Input

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

class DatasetAccordion(Accordion):
    dataset = ObjectProperty(None)
    title = StringProperty(None)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for loader in self.dataset:
            self.add_widget(DatasetItem(title=self.title, loader=loader))

class DatasetItem(AccordionItem):
    loader = ObjectProperty(None)
    view = ObjectProperty(None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name in self.loader.names:
            self.view.add_widget(Label(text=name, height=20, size_hint_x=1, size_hint_y=None))



class DatasetPanel(GridLayout):
    loadfile = ObjectProperty(None)
    scrollview = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        path = Path(filename[0])
        loader = make_file_loader(path)
        self.scrollview.add_widget(DatasetAccordion(title=path.stem, dataset=loader))
        self.dismiss_popup()


class Root(FloatLayout):
    pass


class Main(App):
    def build(self):
        config, database = initialize_application(debug=True)



def run_gui():
    Main().run()


Factory.register("Root", cls=Root)
Factory.register("LoadDialog", cls=LoadDialog)

if __name__ == "__main__":
    run_gui()
