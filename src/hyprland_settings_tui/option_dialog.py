from dataclasses import dataclass
from typing import List
from textual.binding import Binding
from textual.containers import HorizontalGroup, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label, Select
from rich.text import Text


@dataclass
class OptionDialogOutput:
    opt: str = ""
    options_name: str = ""

    @property
    def success(self):
        return len(self.opt) > 0


class OptionDialog(ModalScreen[OptionDialogOutput]):
    BINDINGS = [
        Binding("down", "app.focus_next", show=False),
        Binding("right", "app.focus_next", show=False),
        Binding("up", "app.focus_previous", show=False),
        Binding("left", "app.focus_previous", show=False),
    ]

    DEFAULT_CSS = """
    OptionDialog {
        align: center middle;
        background: rgba(0, 0, 0, 0.5); /* Dims the background app */
    }

    #dialog-container {
        width: 80%;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 1 2;
        align: center middle;
    }

    Button {
        margin: 1 4;
    }

    Label {
        margin: 1 4;
    }

    .button-row {
        align: center bottom;
    }
    """

    def __init__(
        self, options: List[str], infos: List[str], options_name: str = "Pick one!"
    ):
        super().__init__()
        self.options = options
        self.infos = infos
        self.options_name = options_name

        _sel = {
            opt: Text.assemble(f"{opt}", (f"\n  {info}", "#aaaaaa italic"))
            for (opt, info) in zip(options, infos)
        }
        self.select = Select(
            [(sel, opt) for (opt, sel) in _sel.items()], classes="loose"
        )

    def compose(self):
        with Vertical(id="dialog-container"):
            yield Label(self.options_name)
            yield self.select

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="warning"),
                classes="button-row",
            )

    def on_button_pressed(self, event: Button.Pressed):
        out = OptionDialogOutput(options_name=self.options_name)

        if "confirm" in event.button.id and isinstance(self.select.value, str):
            out.opt = self.select.value

        self.dismiss(out)
