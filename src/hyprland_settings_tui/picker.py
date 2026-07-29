from textual.containers import HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Input, Label, RadioButton, RadioSet, Rule, Static

from hyprland_settings_tui.colors import Gradient, parse_color
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


class StringPicker(Picker):
    def __init__(self):
        super().__init__()
        self.widget = Input(type="text")

    def get_value(self):
        assert isinstance(self.widget, Input)
        val = self.widget.value
        if not val.strip():
            return None
        return val


class ColorPicker(Picker):
    def __init__(self):
        super().__init__()
        self.input = Input(type="text")
        self.input.styles.width = "45%"
        self.color_preview = Static(" color preview")
        self.color_preview.styles.border = ("tall", "white")
        self.color_preview.styles.width = "45%"
        self.widget = HorizontalGroup(self.input, self.color_preview)

        self.input.watch(self.input, "value", self._update_preview)

    def _update_preview(self):
        try:
            color = self.get_value()
        except ValueError:
            color = None

        if color is not None:
            tcol = color.to_textual()
            self.color_preview.styles.background = tcol

            if tcol.brightness > 0.5:
                self.color_preview.styles.color = "black"
                self.color_preview.styles.border = ("tall", "black")
            else:
                self.color_preview.styles.color = "white"
                self.color_preview.styles.border = ("tall", "white")

    def get_value(self):
        if self.input.value:
            return parse_color(self.input.value)


class GradientPicker(Picker):
    def __init__(self):
        super().__init__()

        self.main_color_picker = ColorPicker()
        self.second_color_picker = ColorPicker()
        self.angle_picker = IntPicker()

        self.widget = VerticalGroup(
            Label("main color"),
            self.main_color_picker.widget,
            Rule(),
            Label("secondary color (leave blank for solid)"),
            self.second_color_picker.widget,
            Rule(),
            Label("gradient angle (degrees)"),
            self.angle_picker.widget,
        )

    def get_value(self):
        main_color = self.main_color_picker.get_value()
        if main_color is None:
            return None

        second = self.second_color_picker.get_value()
        angle = self.angle_picker.get_value() or 0

        return Gradient(main_color=main_color, second_color=second, angle_deg=angle)


class BoolPicker(Picker):
    def __init__(self):
        super().__init__()
        self.widget = RadioSet("true", "false")
        

    def get_value(self):
        assert isinstance(self.widget, RadioSet)
        idx = self.widget.pressed_index
        if idx < 0:
            return None

        return idx == 0


def make_picker(setting: Setting):
    match setting.opt.type:
        case "int":
            return IntPicker()
        case "float":
            return FloatPicker()
        case "string":
            return StringPicker()
        case "color":
            return ColorPicker()
        case "gradient":
            return GradientPicker()
        case "bool":
            return BoolPicker()
