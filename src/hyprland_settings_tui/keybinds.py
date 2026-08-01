from dataclasses import dataclass, field
import enum
from typing import Dict, List
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

from hyprland_settings_tui.find_commands import (
    find_flatpak_commands,
    find_noctalia_commands,
)

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


class KeybindResult(enum.Enum):
    SUCCESS = enum.auto()
    IGNORE = enum.auto()
    REMOVE = enum.auto()


def get_random_row_key():
    return f"keybinds::{uuid4()}"


@dataclass
class Keybind:
    modifier: str = ""
    button: str = ""
    command: str = ""
    argument: str = ""
    row_key: str = field(default_factory=get_random_row_key)

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
        return (self.key_combo, f"{self.command}: {self.argument}")

    @property
    def conf_style(self):
        stuff = [self.modifier, self.button, self.command]
        if self.argument:
            stuff.append(self.argument)
        return ",".join(stuff)

    def __bool__(self):
        if (not self.command) or (not self.button):
            return False

        return True

    def matches(self, args: str):
        """
        This doesn't handle exactly every case right now, but you gotta start somewhere.
        Tries to determine if a keybind matches the "args" as they appear in the config document
        """
        canon_args = [x.strip().lower() for x in args.split(",")]
        return all(
            [
                x.strip().lower() in canon_args
                for x in (self.argument, self.button, self.modifier, self.command)
            ]
        )


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
                Button(
                    "autoconfig: flatpak run",
                    id="autoconfig-flatpak",
                    variant="primary",
                ),
                Button(
                    "autoconfig: noctalia command",
                    id="autoconfig-noctalia",
                    variant="primary",
                ),
            )

            yield Rule()

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="warning"),
                Button("Remove", id="remove-close", variant="error"),
                id="bottom-buttons",
            )

    def update_keybind(self):
        modifier = " ".join(self.modifiers.selected)
        button = self.button_input.value

        if not button or not modifier:
            keybind_errors.append("No button/modifier")
            return False

        cmd = self.cmd_select.value
        if isinstance(cmd, NoSelection):
            keybind_errors.append("No hyprland command selected")
            return False

        arg = self.arg_input.value
        if any(["," in x for x in (button, arg)]):
            keybind_errors.append("Commas are not supported at the moment, sorry :/")
            return False

        self.kb.argument = arg
        self.kb.command = cmd
        self.kb.modifier = modifier
        self.kb.button = button
        return True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        out: KeybindResult = KeybindResult.IGNORE
        if "confirm" in event.button.id:
            success = self.update_keybind()
            if success:
                out = KeybindResult.SUCCESS
        elif "remove" in event.button.id:
            out = KeybindResult.REMOVE

        if "close" in event.button.id:
            self.dismiss(
                out
            )  # Closes the popup, with return value provided to callback
            return

        if "autoconfig" in event.button.id:
            options: List[str] = []
            if "noctalia" in event.button.id:
                options = find_noctalia_commands()
            elif "flatpak" in event.button.id:
                options = find_flatpak_commands()

            # TODO do something with them!
            if options:
                keybind_errors.append("\n".join(options))


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
        if not kb:
            return

        if kb.row_key in self.keybinds:
            self.config.remove_where("bind", lambda args: kb.matches(args))

        self.config.append("bind", kb.conf_style)
        self.config.save()
        self.refresh_table()

    def remove_keybind(self, kb: Keybind):
        self.config.remove_where("bind", lambda args: kb.matches(args))

    def dialog_exit_callback(self, result: KeybindResult):
        if self.current_keybind is None:
            keybind_errors.append("No keybind!")
            return

        if result == KeybindResult.SUCCESS:
            self.apply_keybind(self.current_keybind)
        elif result == KeybindResult.REMOVE:
            self.remove_keybind(self.current_keybind)

        self.current_keybind = None
