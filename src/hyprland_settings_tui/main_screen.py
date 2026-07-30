from pathlib import Path
from typing import Dict, List
from hyprland_config import default_entrypoint, serialize_lua
from hyprland_schema import Schema
from hyprland_state import HyprlandState
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Label, TabPane, TabbedContent


from hyprland_settings_tui.dialog import Dialog
from hyprland_settings_tui.setting import to_setting, Setting

COLUMNS = ["Setting", "Status", "Value", "Default", "On disk", "Type", "Description"]


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
        Binding("ctrl+x", "save_exit", "Save pending changes and quit"),
        Binding("ctrl+o", "save_now", "Save pending changes"),
        Binding("ctrl+r", "revert", "Revert pending changes"),
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

    def __init__(self, schema: Schema, state: HyprlandState):
        self.schema = schema
        self.state = state
        self.current_setting: Setting | None = None
        super().__init__()

        self.title = "Hyprland Settings TUI"
        self.sub_title = "A TUI editor for hyprland.lua"

        self.schema_sections = get_sections(self.schema)
        self.special_sections = ["monitors", "keybinds"]

        self.settings: Dict[str, Setting] = {}
        self.tables: Dict[str, DataTable] = {}

    def compose(self):
        header = Header(show_clock=True)
        header.icon = "🔥"
        yield header

        with TabbedContent(*(self.special_sections + self.schema_sections)):
            for section in self.special_sections:
                yield self.make_special_section(section)

            for section in self.schema_sections:
                yield self.make_table(section)

        yield Footer()

    def make_table(self, section: str):
        table = DataTable(name=section, zebra_stripes=True, cursor_type="row")

        # auto-generated keys didn't work here (some were None), so we set keys explicitly
        table.add_columns(*[(col, col) for col in COLUMNS])

        for opt in self.schema.get_section(section):
            setting = to_setting(opt, self.state, section)
            key = f"{section}::{':'.join(opt.section)}::{opt.name}"
            row_key = table.add_row(*setting.row, key=key)
            assert row_key.value
            setting.row_key = row_key.value
            self.settings[row_key.value] = setting

        self.tables[section] = table
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

    def action_next_tab(self):
        self.switch_tab(1)

    def action_prev_tab(self):
        self.switch_tab(-1)

    def action_save_exit(self):
        if self.state.is_dirty():
            self.state.save()

        self.app.exit()

    def action_save_now(self):
        if not self.state.is_dirty():
            self.notify("No pending changes!", severity="warning")
            return

        self.state.save()
        self.reload_all_settings()
        self.notify("Settings changed!")

    def action_revert(self):
        self.state.discard()
        self.reload_all_settings()
        self.notify("Settings reverted!", severity="warning")

    def on_data_table_row_selected(self, event: DataTable.RowSelected):
        if not event.row_key.value:
            return

        setting = self.settings[event.row_key.value]
        self.current_setting = setting
        self.app.push_screen(Dialog(setting, self.state), self.setting_callback)

    def reload_row_for_setting(self, setting: Setting):
        row_key = setting.row_key
        section = setting.section
        table = self.tables.get(section)
        if table is None:
            raise ValueError(f"Could not find data table for {section}")

        setting.refresh(self.state)
        for col_key, value in zip(COLUMNS, setting.row):
            table.update_cell(
                row_key=row_key, column_key=col_key, value=value, update_width=True
            )

    def reload_all_settings(self):
        for setting in self.settings.values():
            self.reload_row_for_setting(setting)

    def setting_callback(self, value):
        if self.current_setting is None:
            raise ValueError(
                f"Received callback from setting dialog, without a setting"
            )
        self.reload_row_for_setting(self.current_setting)
        self.current_setting = None
