from typing import Optional

from textual.binding import Binding
from textual.containers import HorizontalGroup, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Input, Markdown

from hyprland_settings_tui.setting import Setting


def make_picker(setting: Setting):
    if setting.opt.type == "int":
        return Input(type="integer")


class Dialog(ModalScreen):
    DEFAULT_CSS = """
    Dialog {
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

    def __init__(self, setting: Setting):
        super().__init__()
        self.setting = setting
        self.opt = setting.opt
        self.picker: Input | None = None

    def compose(self):
        with Vertical(id="dialog-container"):
            md = "\n".join(
                [
                    f"# {self.setting.name}",
                    "---",
                    self.opt.description,
                    " ",
                    f"status: {self.setting.status.value}",
                    " ",
                    f"value: {self.setting.value}",
                ]
            )
            yield Markdown(md)

            picker = make_picker(self.setting)
            if picker:
                self.picker = picker
                yield picker

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="error"),
                id="bottom-buttons",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "close" in event.button.id:
            self.dismiss()  # Closes the popup and returns to the app
