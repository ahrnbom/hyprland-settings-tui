from dataclasses import dataclass
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

    def __eq__(self, other):
        if not isinstance(other, Color):
            return False

        return (
            self.a == other.a
            and self.r == other.r
            and self.g == other.g
            and self.b == other.b
        )


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


def pairwise(values: str):
    l = len(values)
    for i in range(l // 2):
        yield values[2 * i : 2 * (i + 1)]


def parse_color(val: str | int, can_be_argb=True) -> Color:
    if isinstance(val, int) and val < 0:
        return Color(0, 0, 0)

    # Normalize integers (0xeeb3ff1a) to string hex
    if isinstance(val, int):
        val = f"{val:08x}"

    s = str(val).strip().lower()

    if s.endswith(")"):
        if s.startswith("rgb("):
            ss = s.removeprefix("rgb(").removesuffix(")")
            return parse_color(ss, can_be_argb=False)

        if s.startswith("rgba("):
            ss = s.removeprefix("rgba(").removesuffix(")")
            return parse_color(ss, can_be_argb=False)

    if "," in s:
        values = [x.strip().lower() for x in s.split(",")]
        if len(values) in (3, 4):
            r, g, b = [int(x) for x in values[:3]]
            a = 255
            if len(values) == 4:
                a = int(round(255 * float(values[-1])))
            return Color(r=r, g=g, b=b, a=a)

    # Match 0xAARRGGBB or just AARRGGBB
    ss = s.removeprefix("0x")
    if len(ss) == 8 and can_be_argb:
        a, r, g, b = [int(x, 16) for x in pairwise(ss)]
        return Color(r=r, g=g, b=b, a=a)

    # Match standard #RRGGBBAA or #RRGGBB
    ss = s.removeprefix("#")
    if len(ss) == 6:
        ss += "ff"
    if len(ss) == 8:
        r, g, b, a = [int(x, 16) for x in pairwise(ss)]
        return Color(r=r, g=g, b=b, a=a)

    # Match short web hash #RGB
    ss = s.removeprefix("#")
    if len(ss) == 3:
        r, g, b = [int(x + x, 16) for x in ss]
        return Color(r=r, g=g, b=b)

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
