from dataclasses import dataclass
import enum
from random import choice
from typing import List
from rich.text import Text


from hyprland_schema import HyprOption


class Status(enum.Enum):
    DEFAULT = Text("default", style="white")
    PENDING = Text("pending", style="magenta")
    CHANGED = Text("changed", style="blue")


@dataclass
class RowData:
    opt: HyprOption
    status: Status
    name: str
    row: List


def to_row(opt: HyprOption):
    row = RowData(opt, Status.DEFAULT, "", [])

    name = row.opt.name
    if len(row.opt.section) > 1:
        parts = list(row.opt.section[1:])
        parts.append(name)
        name = ":".join(parts)

    row.name = name

    description = row.opt.description
    default = row.opt.default

    # TODO
    row.status = choice([Status.CHANGED, Status.DEFAULT, Status.PENDING])
    value = row.opt.default

    row.row = [name, row.status.value, value, default, description]
    return row
