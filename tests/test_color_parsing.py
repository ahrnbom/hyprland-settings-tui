from hyprland_settings_tui.colors import parse_color

def test_color_parsing():
    equivalent_pairs = [
        ("#fafc21", "0xfffafc21"),
        ("#bae", "#bbaaee"),
        (0xDEADBEEF, "0xDEADBEEF"),
        ("rgb(179,255,26)", "rgba(179,255,26,1.0)")
    ]


    for a, b in equivalent_pairs:
        c1 = parse_color(a)
        c2 = parse_color(b)

        assert c1 == c2