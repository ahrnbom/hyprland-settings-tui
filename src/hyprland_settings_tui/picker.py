from textual.widget import Widget
from textual.widgets import Input

from hyprland_settings_tui.setting import Setting


class Picker:
    """
    Represents a wrapper around some widgets which allows input of arbitrary data
    """

    widget: Widget

    def get_value(self):
        raise NotImplementedError()


class IntPicker(Picker):
    def __init__(self):
        super().__init__()
        self.widget = Input(type="integer")

    def get_value(self):
        assert isinstance(self.widget, Input)
        try:
            return int(self.widget.value)
        except (ValueError, TypeError):
            return None


class FloatPicker(Picker):
    def __init__(self):
        super().__init__()
        self.widget = Input(type="number")

    def get_value(self):
        assert isinstance(self.widget, Input)
        try:
            return float(self.widget.value)
        except (ValueError, TypeError):
            return None


def make_picker(setting: Setting):
    if setting.opt.type == "int":
        return IntPicker()

    if setting.opt.type == "float":
        return FloatPicker()
