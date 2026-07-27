from typing import List
from hyprland_schema import HyprOption
import msgspec


class TableRow(msgspec.Struct):
    name: str
    is_changed: bool
    value: str | int | float | bool
    default: str | int | float | bool
    description: str

    @classmethod
    def from_opt(cls, opt: HyprOption):
        name = opt.name
        if len(opt.section) > 1:
            parts = list(opt.section[1:])
            parts.append(name)
            name = ":".join(parts)

        description = opt.description
        default = opt.default

        # TODO
        is_changed = False
        value = opt.default

        return cls.from_list([name, is_changed, value, default, description])

    def to_list(self):
        return [self.name, self.is_changed, self.value, self.default, self.description]

    @classmethod
    def from_list(cls, l: List):
        return cls(*l)
