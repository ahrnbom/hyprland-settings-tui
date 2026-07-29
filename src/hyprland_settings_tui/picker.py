from hyprland_schema import HyprOption
from textual.binding import Binding
from textual.containers import Container, HorizontalGroup, VerticalGroup
from textual.widget import Widget
from textual.widgets import Input, Label, RadioSet, Rule, Static

from hyprland_settings_tui.colors import Gradient, parse_color
from hyprland_settings_tui.setting import Setting


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
        self.widget.styles.width = "30%"

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
        self.widget.styles.width = "30%"

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
        self.widget.styles.width = "90%"

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
        self.widget = LimitedFocusRadioSet("true", "false")
        self.widget.styles.width = "30%"

    def get_value(self):
        assert isinstance(self.widget, LimitedFocusRadioSet)
        idx = self.widget.pressed_index
        if idx < 0:
            return None

        return idx == 0


class ChoicePicker(Picker):
    def __init__(self, opt: HyprOption):
        super().__init__()

        assert opt.enum_values is not None
        self.options = opt.enum_values

        self.widget = LimitedFocusRadioSet(*self.options)
        self.widget.styles.width = "50%"

    def get_value(self):
        assert isinstance(self.widget, LimitedFocusRadioSet)
        if self.widget.pressed_index < 0:
            return None
        return self.options[self.widget.pressed_index]


class Vec2Picker(Picker):
    def __init__(self):
        super().__init__()
        self.x = FloatPicker()
        self.y = FloatPicker()
        self.widget = VerticalGroup(self.x.widget, self.y.widget)
        self.widget.styles.width = "30%"

    def get_value(self):
        x = self.x.get_value()
        y = self.y.get_value()

        if x is None or y is None:
            return None

        return (x, y)


def make_spacer():
    spacer = Static()
    spacer.styles.width = "100%"
    spacer.styles.height = "100%"
    return spacer


class CSSGapPicker(Picker):
    def __init__(self):
        super().__init__()

        self.pickers = (IntPicker(), IntPicker(), IntPicker(), IntPicker())
        (self.top, self.right, self.bottom, self.left) = self.pickers

        self.widget = Container(
            make_spacer(),
            self.top.widget,
            make_spacer(),
            self.left.widget,
            make_spacer(),
            self.right.widget,
            make_spacer(),
            self.bottom.widget,
            make_spacer(),
        )
        self.widget.styles.layout = "grid"
        self.widget.styles.grid_size_columns = 3
        self.widget.styles.grid_size_rows = 3
        self.widget.styles.grid_columns = "1fr 1fr 1fr"
        self.widget.styles.grid_rows = "1fr 1fr 1fr"

        for picker in self.pickers:
            picker.widget.styles.width = "100%"

    def get_value(self):
        values = [x.get_value() for x in self.pickers]
        if all(map(lambda x: x is None, values)):
            return None

        values = tuple(map(lambda x: x or 0, values))
        return values


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
        case "choice":
            return ChoicePicker(setting.opt)
        case "vec2":
            return Vec2Picker()
        case "cssgap":
            return CSSGapPicker()
        case "font_weight":
            return StringPicker()
