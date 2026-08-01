from dataclasses import dataclass
from typing import Dict
from uuid import uuid4
from hyprland_config import Assignment
from hyprland_state import HyprlandState
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    DataTable,
    Input,
    Label,
    Rule,
    Select,
    SelectionList,
    TabbedContent,
)
from rich.text import Text

from hyprland_settings_tui.widgets import LimitedFocusRadioSet

COLUMNS = ["Keys", "Action"]
NEW_KEYBIND_ROW_KEY = "<NEW_KEYBIND>"
MODIFIERS = ["ctrl", "alt", "shift", "super"]
ACTION_TYPES = ["hyprland command", "shell command", "flatpak run", "noctalia command"]
HYPRLAND_COMMANDS = [
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
        self.action_type_picker = LimitedFocusRadioSet(*ACTION_TYPES)

    def compose(self):
        with VerticalScroll(id="dialog-container"):
            yield Label("Modifiers")
            yield self.modifiers

            yield Label("Button")
            yield Input()

            yield Rule()

            with TabbedContent(*ACTION_TYPES):
                yield Select([(c, c) for c in HYPRLAND_COMMANDS])
                yield Input(placeholder="shell command")
                yield Select([("flatpaks here", "flatpaks here")])
                yield Select([("todo", "todo"), ("whatever", "whatever")])

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="error"),
                id="bottom-buttons",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "confirm" in event.button.id:
            pass

        if "close" in event.button.id:
            self.dismiss()  # Closes the popup


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

        return KeybindDialog(kb)

    def apply_keybind(self, kb: Keybind):
        self.config.set("bind", kb.conf_style)

    def dialog_exit_callback(self, _):
        pass
