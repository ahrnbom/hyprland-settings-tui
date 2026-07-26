from typing import List
from hyprland_schema import HyprOption, Schema
from textual.app import App
from textual.widgets import Checkbox, Header, TabPane, TabbedContent, MarkdownViewer

from schema import get_schema


def get_main_sections(schema: Schema):
    sections: List[str] = []
    for opt in schema.options:
        sec = opt.section[0]
        if sec not in sections:
            sections.append(sec)
    return sections


def build_option_widget(opt: HyprOption):
    if opt.type == "bool":
        return Checkbox(f"{opt.name}: {opt.description}")
    return None


class UI(App):
    def __init__(self, schema: Schema):
        self.schema = schema
        super().__init__()

        self.title = "Hyprland Settings TUI"
        self.sub_title = "A TUI editor for hyprland.lua"

        self.schema_sections = get_main_sections(self.schema)
        self.special_sections = ["monitors", "keybinds"]
        self.all_sections = self.special_sections + self.schema_sections

    def build_pane(self, section: str):
        if section in self.schema_sections:
            opts = self.schema.get_section(section)
            for opt in opts:
                w = build_option_widget(opt)
                if w:
                    yield w
        else:
            yield MarkdownViewer(section)

    def compose(self):
        header = Header()
        header.icon = "🔥"
        yield header

        with TabbedContent(*self.all_sections):
            for section in self.all_sections:
                with TabPane(section):
                    for content in self.build_pane(section):
                        yield content


def main():
    schema = get_schema()
    ui = UI(schema=schema)
    ui.run()


if __name__ == "__main__":
    main()
