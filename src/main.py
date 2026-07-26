from hyprland_schema import Schema
from textual.app import App
from textual.widgets import Header

from schema import get_schema

class UI(App):
    def __init__(self, schema: Schema):
        self.schema = schema 
        super().__init__()

        self.title = "Hyprland Settings TUI"
        self.sub_title = "A TUI editor for hyprland.lua" 

    def compose(self):
        yield Header()

def main():
    schema = get_schema()
    ui = UI(schema=schema)
    ui.run()

if __name__ == "__main__":
    main()
