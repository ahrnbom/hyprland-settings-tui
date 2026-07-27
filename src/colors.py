from dataclasses import dataclass
import re
from typing import Optional


@dataclass(frozen=True)
class Color:
    r: int
    g: int
    b: int
    a: int = 255

    def to_hex(self, include_alpha: bool = True):
        """Outputs standard #rrggbbaa or #rrggbb string."""
        if include_alpha:
            return f"#{self.r:02x}{self.g:02x}{self.b:02x}{self.a:02x}"
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgb_tuple(self):
        return (self.r, self.g, self.b)

    def to_rgba_tuple(self):
        return (self.r, self.g, self.b, self.a)

    def __str__(self):
        return self.to_hex(include_alpha=self.a != 255)


@dataclass(frozen=True)
class Gradient:
    main_color: Color
    second_color: Optional[Color] = None
    angle_deg: int = 0

    def __str__(self) -> str:
        if self.second_color is None:
            return str(self.main_color)

        return (
            str(self.main_color)
            + " "
            + str(self.second_color)
            + f" {self.angle_deg}deg"
        )

    def __eq__(self, other):
        return str(self) == str(other)


def parse_color(val: str | int) -> Color:
    if isinstance(val, int) and val < 0:
        return Color(0, 0, 0)

    # Normalize integers (0xeeb3ff1a) to string hex
    if isinstance(val, int):
        val = f"{val:08x}"

    s = str(val).strip().lower()

    # Match 0xAARRGGBB or just AARRGGBB (8-char hex without #) -> Legacy ARGB
    if m := re.match(r"^(?:0x)?([0-9a-f]{8})$", s):
        hex_str = m.group(1)
        return Color(
            r=int(hex_str[2:4], 16),
            g=int(hex_str[4:6], 16),
            b=int(hex_str[6:8], 16),
            a=int(hex_str[0:2], 16),
        )

    # Match standard #RRGGBBAA or #RRGGBB
    if m := re.match(r"^#([0-9a-f]{6})([0-9a-f]{2})?$", s):
        rgb_part, alpha_part = m.groups()
        return Color(
            r=int(rgb_part[0:2], 16),
            g=int(rgb_part[2:4], 16),
            b=int(rgb_part[4:6], 16),
            a=int(alpha_part, 16) if alpha_part else 255,
        )

    # Match short web hash #RGB
    if m := re.match(r"^#([0-9a-f]{3})$", s):
        h = m.group(1)
        return Color(r=int(h[0] * 2, 16), g=int(h[1] * 2, 16), b=int(h[2] * 2, 16))

    # Match functional hex macros with optional spaces: rgb( b3ff1a )
    if m := re.match(r"^rgba?\(\s*([0-9a-f]{6})([0-9a-f]{2})?\s*\)$", s):
        rgb_part, alpha_part = m.groups()
        return Color(
            r=int(rgb_part[0:2], 16),
            g=int(rgb_part[2:4], 16),
            b=int(rgb_part[4:6], 16),
            a=int(alpha_part, 16) if alpha_part else 255,
        )

    # Match functional decimal macros WITH optional spaces anywhere inside the call
    # \s* allows any amount of spacing around numbers, commas, and parentheses
    if m := re.match(
        r"^rgba?\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*(?:,\s*([\d.]+)\s*)?\)$", s
    ):
        r, g, b, a = m.groups()
        return Color(r=int(r), g=int(g), b=int(b), a=int(a) if a is not None else 255)

    raise ValueError(f"Unknown or malformed color format: {val}")


def parse_gradient(x: str | int) -> Gradient:
    if isinstance(x, str):
        values = [v for v in x.split(" ") if v]
        if len(values) == 1:
            return Gradient(main_color=parse_color(values[0]))

        if len(values) == 2:
            main = parse_color(values[0])
            if "deg" in values[1]:
                return Gradient(main_color=main)

            second = parse_color(values[1])
            return Gradient(main_color=main, second_color=second)

        if len(values) == 3:
            main = parse_color(values[0])
            second = parse_color(values[1])
            deg = int(round(float(values[2].removesuffix("deg"))))
            return Gradient(main_color=main, second_color=second, angle_deg=deg)

        raise ValueError(f"Invalid gradient: {x}")

    main = parse_color(x)
    return Gradient(main_color=main)


if __name__ == "__main__":
    # Verify
    inputs = [
        "#fafc21",  # Web hash
        "#ddd",  # Short hash
        "#fa3d7bff",  # Web rgba hash
        "rgba(b3ff1aee)",  # Hex rgba macro
        "rgba(179,255,26,0.933)",  # Decimal rgba macro (no spaces)
        "rgb(b3ff1a)",  # Hex rgb macro
        "rgb(179,255,26)",  # Decimal rgb macro
        0xEEB3FF1A,  # Legacy ARGB int
        "0xeeb3ff1a",  # Legacy ARGB string
    ]

    for inp in inputs:
        c = parse_color(inp)
        print(
            f"Input: {str(inp):<22} -> Parsed: {c.to_rgba_tuple()} | Hex out: {c.to_hex()}"
        )
