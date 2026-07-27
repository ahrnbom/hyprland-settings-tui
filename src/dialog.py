from textual.containers import HorizontalGroup, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Label

from models import TableRow


class Dialog(ModalScreen):
    DEFAULT_CSS = """
    Dialog {
        align: center middle;
        background: rgba(0, 0, 0, 0.5); /* Dims the background app */
    }

    #dialog-container {
        width: 75%;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 1 2;
        align: center middle;
    }
    
    Button {
        margin: 1 4;
    }

    #bottom-buttons {
        align: center bottom;
    }
    """

    def __init__(self, row: TableRow):
        super().__init__()
        self.row = row

    def compose(self):
        with Vertical(id="dialog-container"):
            yield Label(self.row.description)
            yield HorizontalGroup(
                Button("Confirm", id="confirm-close", variant="success"),
                Button("Cancel", id="cancel-close", variant="error"),
                id="bottom-buttons",
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "close" in event.button.id:
            self.dismiss()  # Closes the popup and returns to the app
