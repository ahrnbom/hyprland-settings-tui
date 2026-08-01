from dataclasses import dataclass
import enum
from typing import Dict, List, Literal
from uuid import uuid4
from hyprland_config import Assignment
from hyprland_state import HyprlandState
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.screen import ModalScreen
from textual.types import NoSelection
from textual.widgets import (
    Button,
    DataTable,
    Input,
    Label,
    Rule,
    Select,
    SelectionList,
)
from rich.text import Text

COLUMNS = ["Keys", "Action", "Status"]
NEW_KEYBIND_ROW_KEY = "<NEW_KEYBIND>"
MODIFIERS = ["ctrl", "alt", "shift", "super"]
ACTION_TYPES = ["hyprland command", "shell command", "flatpak run", "noctalia command"]
HYPRLAND_COMMANDS = [
    "exec",
    "killactive",
    "togglefloating",
    "movefocus",
    "workspace",
    "movetoworkspace",
    "togglespecialworkspace",
    "changegroupactive",
    "moveintogroup",
    "moveoutofgroup",
    "resizeactive",
    "setprop",
    "swapwindow",
    "tagwindow",
    "layoutmsg",
]

keybind_errors: List[str] = []


class Status(enum.Enum):
    SAVED = Text("Saved", style="bright_blue")
    PENDING = Text("pending", style="yellow")


@dataclass
class Keybind:
    modifier: str = ""
    button: str = ""
    command: str = ""
    argument: str = ""
    row_key: str = ""
    status: Status = Status.SAVED

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
        return (self.key_combo, f"{self.command}: {self.argument}", self.status)

    @property
    def conf_style(self):
        stuff = [self.modifier, self.button, self.command]
        if self.argument:
            stuff.append(self.argument)
        return ",".join(stuff)


class KeybindDialog(ModalScreen):
    DEFAULT_CSS = """
    KeybindDialog {
        align: center middle;
        background: rgba(0, 0, 0, 0.5); /* Dims the background app */
    }

    #dialog-container {
        width: 50%;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 1 2;
        align: center middle;
    }
    
    Input {
        max-width: 50%
    }

    Button {
        margin: 1 4;
    }

    Markdown {
        margin: 1 0;
    }

    #bottom-buttons {
        align: center bottom;
    }
    """

    BINDINGS = [
        Binding("down", "app.focus_next", show=False),
        Binding("right", "app.focus_next", show=False),
        Binding("up", "app.focus_previous", show=False),
        Binding("left", "app.focus_previous", show=False),
    ]

    def __init__(self, kb: Keybind):
        super().__init__()
        self.kb = kb

        self.modifiers = SelectionList(*[(v, v) for v in MODIFIERS])
        self.button_input = Input()

        self.cmd_select = Select([(v, v) for v in HYPRLAND_COMMANDS])
        self.arg_input = Input(placeholder="command/argument")

    def compose(self):
        with VerticalScroll(id="dialog-container"):
            yield Label("Modifiers")
            yield self.modifiers

            yield Label("Button")
            yield self.button_input

            yield Rule()

            yield HorizontalGroup(self.cmd_select, self.arg_input)
            yield HorizontalGroup(
                Button("autoconfig: flatpak run", id="autoconfig-flatpak"),
                Button("autoconfig: noctalia command", id="autoconfig-noctalia"),
            )

            yield Rule()

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="error"),
                id="bottom-buttons",
            )

    def update_keybind(self):
        modifier = " ".join(self.modifiers.selected)
        button = self.button_input.value

        if not button or not modifier:
            keybind_errors.append("No button/modifier")
            return

        cmd = self.cmd_select.value
        if isinstance(cmd, NoSelection):
            keybind_errors.append("No hyprland command selected")
            return

        arg = self.arg_input.value

        self.kb.argument = arg
        self.kb.command = cmd
        self.kb.modifier = modifier
        self.kb.button = button

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "confirm" in event.button.id:
            self.update_keybind()

        if "close" in event.button.id:
            self.dismiss()  # Closes the popup


class KeybindManager:
    def __init__(self, state: HyprlandState):
        self.keybinds: Dict[str, Keybind] = {}
        self.state = state
        self.config = state.document
        self.current_keybind: Keybind | None = None

        self.table = DataTable(name="keybinds", zebra_stripes=True, cursor_type="row")
        self.table.add_columns(*[(col, col) for col in COLUMNS])
        self.refresh_table()

    def refresh_table(self):
        for key in list(self.table.rows.keys()):
            self.table.remove_row(key)

        for bind in self.config.find_all("bind"):
            if isinstance(bind, Assignment):
                continue

            keybind = Keybind.from_bind_value(bind.value)
            keybind.row_key = f"keybinds::{uuid4()}"
            self.keybinds[keybind.row_key] = keybind
            self.table.add_row(*keybind.row, key=keybind.row_key)

        # Final "add a new keybind" row
        new_text = Text(" < new > ", style="yellow")
        self.table.add_row(new_text, new_text, key=NEW_KEYBIND_ROW_KEY)

    def make_dialog(self, row_key: str) -> ModalScreen | None:
        kb = self.keybinds.get(row_key)
        if not kb:
            kb = Keybind()

        self.current_keybind = kb
        return KeybindDialog(kb)

    def apply_keybind(self, kb: Keybind):
        self.config.set("bind", kb.conf_style)

    def dialog_exit_callback(self):
        if self.current_keybind is None:
            keybind_errors.append("No keybind!")
            return

        self.apply_keybind(self.current_keybind)
        self.current_keybind = None
