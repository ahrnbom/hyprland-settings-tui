from typing import List
from hyprland_schema import Schema
from textual.app import App
from textual.widgets import Header, TabbedContent, MarkdownViewer

from schema import get_schema


def get_main_sections(schema: Schema):
    sections: List[str] = []
    for opt in schema.options:
        sec = opt.section[0]
        if sec not in sections:
            sections.append(sec)
    return sections


class UI(App):
    def __init__(self, schema: Schema):
        self.schema = schema
        super().__init__()

        self.title = "Hyprland Settings TUI"
        self.sub_title = "A TUI editor for hyprland.lua"

        self.main_sections = get_main_sections(self.schema)
        self.special_sections = ["monitors", "keybinds"]
        self.all_sections = self.special_sections + self.main_sections

    def build_pane(self, section: str):
        return MarkdownViewer(section)

    def compose(self):
        header = Header()
        header.icon = "🔥"
        yield header

        with TabbedContent(*self.all_sections):
            for section in self.all_sections:
                yield self.build_pane(section)


def main():
    schema = get_schema()
    ui = UI(schema=schema)
    ui.run()


if __name__ == "__main__":
    main()
