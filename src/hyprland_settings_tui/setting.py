from dataclasses import dataclass
import enum
from functools import lru_cache
from typing import List, Tuple
from hyprland_state import HyprlandState
from rich.text import Text
from hyprland_schema import HyprOption

from hyprland_settings_tui.colors import Gradient, parse_gradient


class Status(enum.Enum):
    DEFAULT = Text("default", style="bright_yellow")
    PENDING = Text("pending", style="yellow")
    CHANGED = Text("changed", style="blue")
    UNKNOWN = Text("  N/A  ", style="red")


@lru_cache(16)
def type_with_color(type_text: str):
    styles = {
        "int": "yellow",
        "float": "green",
        "string": "blue",
        "color": "magenta",
        "gradient": "bright_magenta",
        "vec2": "bright_yellow",
        "choice": "cyan",
        "cssgap": "red",
        "bool": "white",
    }
    return Text(type_text, style=styles.get(type_text, "white"))


@dataclass
class Setting:
    opt: HyprOption
    status: Status = Status.DEFAULT
    name: str = ""
    section: str = ""
    value: int | float | str | bool | tuple | Gradient | None = None
    disk: str | None = None
    default: int | float | str | bool | tuple | Gradient | None = None

    @property
    def row(self):
        return [
            self.name,
            self.status.value,
            self.value,
            self.default,
            self.disk,
            type_with_color(self.opt.type),
            self.opt.description,
        ]


def sanitize_string(x: str):
    if x == "[[Auto]]":
        return ""
    return x


def as_bool(x):
    if isinstance(x, str):
        if x.lower().strip() == "false":
            return False

    return bool(x)


def as_vec2(x):
    if isinstance(x, str):
        x = tuple(x.split(" "))

    return tuple([float(v) for v in x])


def as_gradient(x):
    return parse_gradient(x)


def as_int(x):
    try:
        return int(x)
    except (ValueError, TypeError):
        return None


def as_float(x):
    try:
        return float(x)
    except (ValueError, TypeError):
        return None


def as_css_gap(x) -> Tuple[int, ...] | None:
    if isinstance(x, str):
        x = [int(v) for v in x.strip().split(" ")]

    if isinstance(x, int):
        x = [x]

    if x is None:
        x = tuple()

    if isinstance(x, list):
        x = tuple(x)

    assert isinstance(x, tuple)

    if len(x) == 4:
        return x

    if len(x) == 3:
        top, lr, bot = [int(v) for v in x]
        return (top, lr, bot, lr)

    if len(x) == 2:
        tb, lr = [int(v) for v in x]
        return (tb, lr, tb, lr)

    if len(x) == 1:
        tblr = int(x[0])
        return (tblr, tblr, tblr, tblr)


def canonical_form(x, opt: HyprOption):
    if x is None:
        return None

    if opt.type == "bool":
        return as_bool(x)
    elif opt.type == "int":
        return as_int(x)
    elif opt.type == "float":
        return as_float(x)
    elif opt.type == "color" or opt.type == "gradient":
        return as_gradient(x)
    elif opt.type == "vec2":
        return as_vec2(x)
    elif opt.type == "cssgap":
        return as_css_gap(x)

    return sanitize_string(x)


def is_similar(x, y):
    if isinstance(x, float) and isinstance(y, float):
        return abs(x - y) < (0.01 * max(abs(x), abs(y)))

    return x == y


def to_setting(opt: HyprOption, state: HyprlandState, section: str):
    setting = Setting(opt)

    name = setting.opt.name
    if len(setting.opt.section) > 1:
        parts = list(setting.opt.section[1:])
        parts.append(name)
        name = ":".join(parts)

    setting.name = name
    setting.section = section

    full_name = section + ":" + name
    value, avail = state.get_live(full_name)
    if not avail:
        setting.status = Status.UNKNOWN
        setting.value = None
        return setting
    setting.value = canonical_form(value, opt)

    disk_value = state.get_disk(full_name)
    setting.disk = canonical_form(disk_value, opt)
    setting.default = canonical_form(opt.default, opt)

    if is_similar(setting.disk, setting.value) or setting.disk is None:
        if is_similar(setting.value, setting.default):
            setting.status = Status.DEFAULT
        else:
            setting.status = Status.CHANGED
    else:
        setting.status = Status.PENDING

    return setting
