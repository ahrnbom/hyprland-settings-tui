from typing import List
from hyprland_schema import Schema
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Header, Label, TabPane, TabbedContent

from dialog import Dialog
from models import TableRow


def get_sections(schema: Schema):
    secs: List[str] = []
    for opt in schema.options:
        sec = opt.section[0]
        if sec not in secs:
            secs.append(sec)

    return secs


class MainScreen(Screen):
    BINDINGS = [
        Binding("left", "prev_tab", "Previous Tab", priority=True),
        Binding("right", "next_tab", "Next Tab", priority=True),
    ]
    DEFAULT_CSS = """
        TabPane {
            overflow: hidden;
        }

        DataTable {
            height: 1fr;
            overflow-x: hidden;
        }
    """

    def __init__(self, schema: Schema):
        self.schema = schema
        super().__init__()

        self.title = "Hyprland Settings TUI"
        self.sub_title = "A TUI editor for hyprland.lua"

        self.schema_sections = get_sections(self.schema)
        self.special_sections = ["monitors", "keybinds"]

    def compose(self):
        header = Header()
        header.icon = "🔥"
        yield header

        with TabbedContent(*(self.special_sections + self.schema_sections)):
            for section in self.special_sections:
                yield self.make_special_section(section)

            for section in self.schema_sections:
                yield self.make_table(section)

    def make_table(self, section: str):
        table = DataTable(name=section, zebra_stripes=True, cursor_type="row")
        table.add_columns("Setting", "Changed", "Value", "Default", "Description")

        for opt in self.schema.get_section(section):
            row = TableRow.from_opt(opt)
            table.add_row(*row.to_list())

        return table

    def make_special_section(self, section: str):
        return Label(section)

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
                next_pane.query_one("*").focus()
                break

    def action_next_tab(self) -> None:
        self.switch_tab(1)

    def action_prev_tab(self) -> None:
        self.switch_tab(-1)

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        row_data = event.data_table.get_row(event.row_key)
        row = TableRow.from_list(row_data)
        self.app.push_screen(Dialog(row))


def render_is_changed(is_changed: bool):
    if is_changed:
        return "O"
    return "-"
