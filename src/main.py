from typing import Dict, List
from hyprland_schema import HyprOption, Schema
from textual.app import App
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widget import Widget
from textual.widgets import (
    Checkbox,
    Collapsible,
    DataTable,
    Header,
    Input,
    Label,
    TabPane,
    TabbedContent,
)

from schema import get_schema


def get_sections(schema: Schema):
    secs: List[str] = []
    for opt in schema.options:
        sec = opt.section[0]
        if sec not in secs:
            secs.append(sec)

    return secs


def build_option_widget(opt: HyprOption):
    if opt.type == "bool":
        return Checkbox(
            f"{opt.name}",
            tooltip=opt.description,
            compact=True,
            value=bool(opt.default),
        )
    elif opt.type == "int":
        return HorizontalGroup(
            Label(f"{opt.name}: "),
            Input(
                f"{opt.default}",
                type="integer",
                tooltip=f"{opt.description}  [{opt.min} - {opt.max}] - default: {opt.default}",
                compact=True,
            ),
        )
    elif opt.type == "float":
        return HorizontalGroup(
            Label(f"{opt.name}: "),
            Input(
                f"{opt.default}",
                type="number",
                tooltip=f"{opt.description}  [{opt.min} - {opt.max}] - default: {opt.default}",
                compact=True,
            ),
        )
    return Label(opt.name)


def render_is_changed(is_changed: bool):
    if is_changed:
        return "O"
    return "-"


class UI(App):
    BINDINGS = [
        Binding("left", "prev_tab", "Previous Tab", priority=True),
        Binding("right", "next_tab", "Next Tab", priority=True),
    ]
    CSS_PATH = "style.tcss"

    def __init__(self, schema: Schema):
        self.schema = schema
        super().__init__()

        self.title = "Hyprland Settings TUI"
        self.sub_title = "A TUI editor for hyprland.lua"

        self.schema_sections = get_sections(self.schema)
        self.special_sections = ["monitors", "keybinds"]
        self.all_sections = self.special_sections + self.schema_sections

    def build_pane_list(self, section: str):
        out: List[Widget] = []

        if section in self.schema_sections:
            for sub in self.schema_sections[section]:
                widgets: List[Widget] = []
                for opt in self.schema.get_subsection(section, sub):
                    widgets.append(build_option_widget(opt))
                out.append(Collapsible(*widgets, title=sub))
        else:
            out.append(Label(section))

        return out

    def compose(self):
        header = Header()
        header.icon = "🔥"
        yield header

        with TabbedContent(*self.all_sections):
            for section in self.all_sections:
                yield self.make_table(section)

    def make_table(self, section: str):
        table = DataTable(name=section, zebra_stripes=True, cursor_type="row")
        table.add_columns("Setting", "Changed", "Value", "Default", "Description")

        for opt in self.schema.get_section(section):
            name = opt.name
            if len(opt.section) > 1:
                parts = list(opt.section[1:])
                parts.append(name)
                name = ":".join(parts)

            # TODO
            is_changed = False
            value = opt.default

            table.add_row(
                name, render_is_changed(is_changed), value, opt.default, opt.description
            )

        return table

    def switch_tab(self, delta: int) -> None:
        tabbed_content = self.query_one(TabbedContent)
        panes = list(tabbed_content.query(TabPane))
        if not panes:
            return

        current_id = tabbed_content.active
        for i, pane in enumerate(panes):
            if pane.id == current_id:
                next_pane = panes[(i + delta) % len(panes)]
                tabbed_content.active = next_pane.id
                next_pane.query_one(DataTable).focus()
                break

    def action_next_tab(self) -> None:
        self.switch_tab(1)

    def action_prev_tab(self) -> None:
        self.switch_tab(-1)


def main():
    schema = get_schema()
    ui = UI(schema=schema)
    ui.run()


if __name__ == "__main__":
    main()
