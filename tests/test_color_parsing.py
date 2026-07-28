from hyprland_settings_tui.colors import Color, parse_color, parse_gradient


def test_color_parsing():
    equivalent_pairs = [
        ("#fafc21", "0xfffafc21"),
        ("#bae", "#bbaaee"),
        (0xDEADBEEF, "0xDEADBEEF"),
        ("rgb(179,255,26)", "rgba(179,255,26,1.0)"),
        ("rgba(b3ff1aee)", "rgba(179,255,26,0.933)"),
        ("#fc770345", "rgba(252, 119, 3, 0.27  )"),
    ]

    for a, b in equivalent_pairs:
        c1 = parse_color(a)
        c2 = parse_color(b)

        assert c1 == c2

    # Ensure parse_color returns valid Color objects
    assert parse_color("#fc770345") == Color(r=252, g=119, b=3, a=69)


def test_gradient_parsing():
    g1 = parse_gradient("#fafc21 rgba(179,255,26,1.0) 17deg ")
    assert g1.main_color == parse_color("#fafc21")
    assert g1.second_color == parse_color("rgba(179,255,26,1.0)")
    assert g1.angle_deg == 17

    g2 = parse_gradient("rgba(179,255,26,1.0) 0deg")
    assert g2.second_color is None
    assert g2.angle_deg == 0
    assert str(g2) == str(parse_color("rgba(179,255,26,1.0)"))

    g3 = parse_gradient("#bae")
    assert g3.main_color == parse_color("0xffbbaaee")
    assert g3.second_color is None
