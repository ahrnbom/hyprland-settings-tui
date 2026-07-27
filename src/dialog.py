from textual.containers import HorizontalGroup, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Markdown

from setting import Setting


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

    def __init__(self, row_data: Setting):
        super().__init__()
        self.row_data = row_data
        self.opt = row_data.opt

    def compose(self):
        with Vertical(id="dialog-container"):
            md = "\n".join(
                [
                    f"# {self.row_data.name}",
                    "---",
                    self.opt.description,
                    " ",
                    f"status: {self.row_data.status.value}",
                ]
            )
            yield Markdown(md)

            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="error"),
                id="bottom-buttons",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "close" in event.button.id:
            self.dismiss()  # Closes the popup and returns to the app
