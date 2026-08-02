from copy import deepcopy
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

from hyprland_settings_tui.common_special_buttons import SPECIAL_BUTTONS
from hyprland_settings_tui.find_commands import (
    find_flatpak_commands,
    find_noctalia_commands,
)
from hyprland_settings_tui.option_dialog import OptionDialog, OptionDialogOutput

COLUMNS = ["Keys", "Action", "Status"]
NEW_KEYBIND_ROW_KEY = "<NEW_KEYBIND>"
MODIFIERS = ["ctrl", "alt", "shift", "super"]
HYPRLAND_COMMANDS = [
    "exec",
    "killactive",
    "togglefloating",
    "movefocus",
    "workspace",
    "movewindow",
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

    def lowerify(self):
        self.modifier = self.modifier.lower()
        self.command = self.command.lower()
        if len(self.button.strip()) == 1:
            self.button = self.button.strip().lower()

    @property
    def key_combo(self):
        if self.modifier:
            buttons = [x for x in self.modifier.split(" ") if x]
            buttons.append(self.button)
            return " + ".join(buttons)

        return self.button

    @property
    def row(self):
        arg_str = f": {self.argument}" if self.argument else ""
        return (self.key_combo, f"{self.command}{arg_str}")

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
        width: 90%;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 1 2;
        align: center middle;
    }
    
    Input {
        max-width: 50%;
    }

    Button {
        margin: 1 4;
    }

    #button-input {
        margin: 1 4;
    }

    .button-row {
        align: center bottom;
    }

    Label {
        margin: 1 0 0 0;
    }
    """

    BINDINGS = [
        Binding("down", "app.focus_next", show=False),
        Binding("right", "app.focus_next", show=False),
        Binding("up", "app.focus_previous", show=False),
        Binding("left", "app.focus_previous", show=False),
        Binding("escape", "cancel", show=False),
    ]

    def __init__(self, kb: Keybind):
        super().__init__()
        kb.lowerify()
        self.kb = kb

        self.modifiers = SelectionList(*[(v, v, (v in kb.modifier)) for v in MODIFIERS])
        self.button_input = Input(value=kb.button, id="button-input")

        cmd_val = kb.command if kb.command else HYPRLAND_COMMANDS[0]
        self.cmd_select = Select(
            [(v, v) for v in HYPRLAND_COMMANDS], allow_blank=False, value=cmd_val
        )

        arg_val = kb.argument if kb.argument else None
        self.arg_input = Input(value=arg_val, placeholder="command/argument")

    def compose(self):
        with VerticalScroll(id="dialog-container"):
            yield Label("Modifiers")
            yield self.modifiers

            yield Label("Button")
            yield HorizontalGroup(
                self.button_input,
                Button("Special buttons", variant="primary", id="special-buttons"),
            )

            yield Rule()

            yield HorizontalGroup(self.cmd_select, self.arg_input)
            yield HorizontalGroup(
                Button(
                    "autoconfig: flatpak run",
                    id="autoconfig-flatpak",
                    variant="primary",
                ),
                Button(
                    "autoconfig: noctalia v5 command",
                    id="autoconfig-noctalia",
                    variant="primary",
                ),
                classes="button-row",
            )

            yield Rule()

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="warning"),
                Button("Remove", id="remove-close", variant="error"),
                classes="button-row",
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

    def on_button_pressed(self, event: Button.Pressed):
        out: KeybindResult = KeybindResult.IGNORE
        if "confirm" in event.button.id:
            success = self.update_keybind()
            if success:
                out = KeybindResult.SUCCESS
        elif "remove" in event.button.id:
            out = KeybindResult.REMOVE

        if "close" in event.button.id:
            # Closes the popup, with return value provided to callback
            self.dismiss(out)
            return

        if "autoconfig" in event.button.id:
            options: List[str] = []
            infos: List[str] = []
            name = ""
            if "noctalia" in event.button.id:
                options, infos = find_noctalia_commands()
                name = "Noctalia v5 commands"
            elif "flatpak" in event.button.id:
                options, infos = find_flatpak_commands()
                name = "Flatpak apps"
            if options:
                self.app.push_screen(
                    OptionDialog(options, infos, name), self.autoconfig_callback
                )
        elif event.button.id == "special-buttons":
            buttons = [x[1] for x in SPECIAL_BUTTONS]
            button_infos = [x[0] for x in SPECIAL_BUTTONS]
            self.app.push_screen(
                OptionDialog(buttons, button_infos, "Special buttons"),
                self.special_buttons_callback,
            )

    def action_cancel(self):
        self.dismiss(KeybindResult.IGNORE)

    def special_buttons_callback(self, out):
        if not isinstance(out, OptionDialogOutput) or not out.success:
            return

        self.button_input.value = out.opt

    def autoconfig_callback(self, out):
        if not isinstance(out, OptionDialogOutput) or not out.success:
            return

        if "flatpak" in out.options_name.lower():
            self.arg_input.value = f"flatpak run {out.opt}"
        elif "noctalia" in out.options_name.lower():
            self.arg_input.value = f"noctalia msg {out.opt}"


class KeybindManager:
    def __init__(self, state: HyprlandState):
        self.keybinds: Dict[str, Keybind] = {}
        self.state = state
        self.config = state.document
        self.current_keybind: Keybind | None = None
        self.old_keybind: Keybind | None = None

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
        self.old_keybind = deepcopy(kb)
        return KeybindDialog(kb)

    def apply_keybind(self, kb: Keybind, old_kb: Keybind):
        if not kb:
            return

        if kb.row_key in self.keybinds:
            self.config.remove_where("bind", lambda args: old_kb.matches(args))

        self.config.append("bind", kb.conf_style)
        self.config.save()
        self.refresh_table()

    def remove_keybind(self, kb: Keybind):
        self.config.remove_where("bind", lambda args: kb.matches(args))

    def dialog_exit_callback(self, result: KeybindResult):
        if self.current_keybind is None or self.old_keybind is None:
            keybind_errors.append("No keybind!")
            return

        if result == KeybindResult.SUCCESS:
            self.apply_keybind(self.current_keybind, self.old_keybind)
        elif result == KeybindResult.REMOVE:
            self.remove_keybind(self.old_keybind)

        self.current_keybind = None
