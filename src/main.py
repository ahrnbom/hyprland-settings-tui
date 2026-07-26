from typing import Dict, List
from hyprland_schema import HyprOption, Schema
from textual.app import App
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import (
    Checkbox,
    Collapsible,
    Header,
    Label,
    ListItem,
    ListView,
    TabbedContent,
    MarkdownViewer,
)

from schema import get_schema


def get_sections(schema: Schema):
    """
    First output: A dictionary which maps all main sections to a list of its subsections (could be empty)
    Second output: A dictionary mapping all main sections to a list of all options which don't have a subsection
    """
    secs: Dict[str, List[str]] = {}
    nonsub: Dict[str, List[HyprOption]] = {}
    for opt in schema.options:
        sec = opt.section[0]
        if sec not in secs:
            secs[sec] = []
            nonsub[sec] = []

        if len(opt.section) == 2:
            subsec = opt.section[1]
            if subsec not in secs[sec]:
                secs[sec].append(subsec)
        elif len(opt.section) == 1:
            nonsub[sec].append(opt)

    return secs, nonsub


def build_option_widget(opt: HyprOption):
    if opt.type == "bool":
        return Checkbox(
            f"{opt.name}",
            tooltip=opt.description,
            compact=True,
            value=bool(opt.default),
        )
    return Label(opt.name)


class UI(App):
    def __init__(self, schema: Schema):
        self.schema = schema
        super().__init__()

        self.title = "Hyprland Settings TUI"
        self.sub_title = "A TUI editor for hyprland.lua"

        self.schema_sections, self.nonsub = get_sections(self.schema)
        self.special_sections = ["monitors", "keybinds"]
        self.all_sections = self.special_sections + list(self.schema_sections.keys())

    def build_pane_list(self, section: str):
        out: List[Widget] = []

        if section in self.schema_sections:
            for sub in self.schema_sections[section]:
                widgets: List[Widget] = []
                for opt in self.schema.get_subsection(section, sub):
                    widgets.append(build_option_widget(opt))
                out.append(Collapsible(*widgets, title=sub))

            for opt in self.nonsub[section]:
                out.append(build_option_widget(opt))

        else:
            out.append(ListItem(MarkdownViewer(section)))

        return out

    def compose(self):
        header = Header()
        header.icon = "🔥"
        yield header

        with TabbedContent(*self.all_sections):
            for section in self.all_sections:
                yield VerticalScroll(*self.build_pane_list(section))


def main():
    schema = get_schema()
    ui = UI(schema=schema)
    ui.run()


if __name__ == "__main__":
    main()
