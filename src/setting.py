from dataclasses import dataclass
import enum
from hyprland_state import HyprlandState
from rich.text import Text

from hyprland_schema import HyprOption


class Status(enum.Enum):
    DEFAULT = Text("default", style="white")
    PENDING = Text("pending", style="yellow")
    CHANGED = Text("changed", style="blue")
    UNKNOWN = Text(" ????? ", style="red")


@dataclass
class Setting:
    opt: HyprOption
    status: Status = Status.DEFAULT
    name: str = ""
    section: str = ""
    value: int | float | str | bool | tuple | None = None
    disk: str | None = None

    @property
    def row(self):
        return [
            self.name,
            self.status.value,
            self.value,
            self.opt.default,
            self.disk,
            self.opt.description,
        ]


def sanitize_string(x: str):
    if x == "[[Auto]]":
        return ""

    x = x.removesuffix(" 0deg")

    if x.startswith("0x"):
        pre, _, post = x.partition(" ")
        num = int(pre, 0)
        x = f"{num} {post}".strip()

    return x


def is_similar(x, y):
    """
    Unfortunately, the formats provided from the hyprland_state API vary wildly and converting Lua <-> Python
    is not exactly one-to-one, hence these hacks
    """
    if (isinstance(x, list) or isinstance(x, tuple)) and (
        isinstance(y, list) or isinstance(y, tuple)
    ):
        if len(x) != len(y):
            return False

        for xx, yy in zip(x, y):
            if not is_similar(xx, yy):
                return False

        return True

    if isinstance(x, str):
        x = sanitize_string(x)

    if isinstance(y, str):
        y = sanitize_string(y)

    if str(x).lower().strip() == str(y).lower().strip():
        return True

    try:
        xx = float(x)
        yy = float(y)
    except (ValueError, TypeError):
        return False

    return abs(xx - yy) < 0.0001


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

    setting.value = value

    disk_value = state.get_disk(full_name)
    setting.disk = disk_value

    if is_similar(setting.disk, setting.value) or setting.disk is None:
        if is_similar(value, opt.default):
            setting.status = Status.DEFAULT
        else:
            setting.status = Status.CHANGED
    else:
        setting.status = Status.PENDING

    return setting
