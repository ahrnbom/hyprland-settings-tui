from hyprland_socket import CommandError
from hyprland_state import HyprlandState
from textual.binding import Binding
from textual.containers import HorizontalGroup, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

from hyprland_settings_tui.picker import Picker, make_picker
from hyprland_settings_tui.setting import Setting


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

    def __init__(self, setting: Setting, state: HyprlandState):
        super().__init__()
        self.setting = setting
        self.opt = setting.opt
        self.picker: Picker | None
        self.state = state

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

            self.picker = make_picker(self.setting)
            if self.picker is not None:
                yield self.picker.widget

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="warning"),
                id="bottom-buttons",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "confirm" in event.button.id and self.picker is not None:
            success: bool
            value = self.picker.get_value()
            try:
                success = self.state.apply(self.setting.full_name, value)
            except (ValueError, CommandError):
                success = False

            if success:
                self.notify(f"Applied setting {self.setting.name} to {value}")
            else:
                self.notify(
                    f"Failed to apply setting {self.setting.name}", severity="warning"
                )

        if "close" in event.button.id:
            self.dismiss()  # Closes the popup
