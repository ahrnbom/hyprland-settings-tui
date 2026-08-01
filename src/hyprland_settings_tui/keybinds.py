from dataclasses import dataclass
from typing import Dict
from uuid import uuid4
from hyprland_config import Assignment
from hyprland_state import HyprlandState
from textual.screen import ModalScreen
from textual.widgets import DataTable
from rich.text import Text

COLUMNS = ["Keys", "Action"]
NEW_KEYBIND_ROW_KEY = "<NEW_KEYBIND>"


@dataclass
class Keybind:
    modifier: str = ""
    button: str = ""
    command: str = ""
    argument: str = ""
    row_key: str = ""

    @classmethod
    def from_bind_value(cls, val: str):
        elems = [x.strip() for x in val.split(",")]
        if len(elems) == 4:
            mod, but, cmd, arg = elems
        elif len(elems) == 3:
            mod, but, cmd = elems
            arg = ""
        return cls(modifier=mod, button=but, command=cmd, argument=arg)

    @property
    def key_combo(self):
        if self.modifier:
            return f"{self.modifier} + {self.button}"

        return self.button

    @property
    def row(self):
        return (
            self.key_combo,
            f"{self.command}: {self.argument}",
        )

    @property
    def conf_style(self):
        stuff = [self.modifier, self.button, self.command]
        if self.argument:
            stuff.append(self.argument)
        return ",".join(stuff)


class KeybindManager:
    def __init__(self, state: HyprlandState):
        self.keybinds: Dict[str, Keybind] = {}
        self.state = state
        self.config = state.document

        table = DataTable(name="keybinds", zebra_stripes=True, cursor_type="row")
        table.add_columns(*[(col, col) for col in COLUMNS])

        for bind in self.config.find_all("bind"):
            if isinstance(bind, Assignment):
                continue

            keybind = Keybind.from_bind_value(bind.value)
            keybind.row_key = f"keybinds::{uuid4()}"
            self.keybinds[keybind.row_key] = keybind
            table.add_row(*keybind.row, key=keybind.row_key)

        # Final "add a new keybind" row
        new_text = Text(" < new > ", style="yellow")
        table.add_row(new_text, new_text, key=NEW_KEYBIND_ROW_KEY)

        self.table = table

    def make_dialog(self, row_key: str) -> ModalScreen | None:
        kb = self.keybinds.get(row_key)
        if not kb:
            return None

        # TODO make the actual dialog and return it

    def apply_keybind(self, kb: Keybind):
        self.config.set("bind", kb.conf_style)

    def dialog_exit_callback(self, _):
        pass
