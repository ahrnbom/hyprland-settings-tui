from dataclasses import dataclass
from uuid import uuid4
from hyprland_config import Assignment, load_lua, default_lua_entrypoint
from textual.widgets import DataTable

COLUMNS = ["Keys", "Action", "Comment"]


@dataclass
class Keybind:
    modifier: str = ""
    button: str = ""
    command: str = ""
    argument: str = ""
    comment: str = ""
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
            self.comment,
        )


def make_keybinds_table():
    path = default_lua_entrypoint()
    config = load_lua(path)

    table = DataTable(name="keybinds", zebra_stripes=True, cursor_type="row")
    table.add_columns(*[(col, col) for col in COLUMNS])

    for bind in config.find_all("bind"):
        if isinstance(bind, Assignment):
            continue

        keybind = Keybind.from_bind_value(bind.value)
        keybind.comment = bind.inline_comment
        keybind.row_key = f"keybinds::{uuid4()}"
        table.add_row(*keybind.row, key=keybind.row_key)

    return table
