from dataclasses import dataclass
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
    is_changed = False
    value = row.opt.default

    row.row = [name, is_changed, value, default, description]
    return row
