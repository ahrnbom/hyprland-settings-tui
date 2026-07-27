from textual.containers import Vertical
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
        width: 90%;
        height: auto;
        border: thick $primary;
        background: $panel;
        padding: 1 2;
        align: center middle;
    }
    
    #dialog-container Button {
        margin-top: 1;
    }
    """

    def __init__(self, row: TableRow):
        super().__init__()
        self.row = row

    def compose(self):
        with Vertical(id="dialog-container"):
            yield Label(self.row.description)
            yield Button("Confirm", id="confirm-close", variant="success")
            yield Button("Cancel", id="cancel-close", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if "close" in event.button.id:
            self.dismiss()  # Closes the popup and returns to the app
