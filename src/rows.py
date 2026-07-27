from dataclasses import dataclass
from random import choice
from typing import List

from hyprland_schema import HyprOption


@dataclass
class RowData:
    opt: HyprOption
    is_changed: bool
    name: str
    row: List


def to_row(opt: HyprOption):
    row = RowData(opt, False, "", [])

    name = row.opt.name
    if len(row.opt.section) > 1:
        parts = list(row.opt.section[1:])
        parts.append(name)
        name = ":".join(parts)

    row.name = name

    description = row.opt.description
    default = row.opt.default

    # TODO
    row.is_changed = choice([True, False])
    value = row.opt.default

    row.row = [name, row.is_changed, value, default, description]
    return row
