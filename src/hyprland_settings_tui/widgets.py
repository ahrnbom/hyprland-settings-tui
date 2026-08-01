from textual.binding import Binding
from textual.widgets import RadioSet


class LimitedFocusRadioSet(RadioSet, inherit_bindings=False):
    BINDINGS = [
        Binding(
            "down",
            "next_button",
            "Next option",
            show=False,
        ),
        Binding("enter,space", "toggle_button", "Toggle", show=False),
        Binding(
            "up",
            "previous_button",
            "Previous option",
            show=False,
        ),
    ]
