from hyprland_settings_tui.colors import Color, parse_color


def test_color_parsing():
    equivalent_pairs = [
        ("#fafc21", "0xfffafc21"),
        ("#bae", "#bbaaee"),
        (0xDEADBEEF, "0xDEADBEEF"),
        ("rgb(179,255,26)", "rgba(179,255,26,1.0)"),
        ("rgba(b3ff1aee)", "rgba(179,255,26,0.933)"),
        ("#fc770345", "rgba(252, 119, 3, 0.27)"),
    ]

    for a, b in equivalent_pairs:
        c1 = parse_color(a)
        c2 = parse_color(b)

        assert c1 == c2

    # Ensure parse_color returns valid Color objects
    assert parse_color("#fc770345") == Color(r=252, g=119, b=3, a=69)
