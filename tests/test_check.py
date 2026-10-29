from matplotlib.figure import Figure

from cvdkit import check, distinguishable, separation, style_cycler

ORANGE, AQUA = "#eb6834", "#1baf7a"


def test_pair_with_large_delta_e_but_same_lightness_and_hue_is_not_distinct():
    # This orange and aqua keep a CIEDE2000 distance near 17 under deuteranopia, which a
    # distance-only test passes, but both become a mid olive that differs only in saturation.
    sep = separation(ORANGE, AQUA, "deutan")
    assert sep.de > 15
    assert sep.dl < 5 and sep.dhue < 10
    assert not sep.ok("line")
    assert sep.ok("area")
    assert not distinguishable(ORANGE, AQUA)
    assert distinguishable(ORANGE, AQUA, kinds=())


def test_blue_and_orange_are_distinct():
    assert distinguishable("#0072b2", "#e69f00")


def _fig():
    fig = Figure()
    return fig, fig.add_subplot()


def test_check_flags_lines_told_apart_by_colour_only():
    fig, ax = _fig()
    ax.plot([0, 1], [0, 1], "o-", color=ORANGE, label="a")
    ax.plot([0, 1], [1, 0], "o-", color=AQUA, label="b")
    ax.plot([0, 1], [0.5, 0.5], "o-", color="#0072b2", label="c")
    (hit,) = check(fig)
    assert (hit.a, hit.b, hit.view) == ("a", "b", "deutan")
    assert (hit.color_a, hit.color_b) == (ORANGE, AQUA)


def test_check_accepts_a_second_channel():
    fig, ax = _fig()
    ax.plot([0, 1], [0, 1], "o-", color=ORANGE)
    ax.plot([0, 1], [1, 0], "s-", color=AQUA)
    ax.plot([0, 1], [1, 1], "s", linestyle=(0, (5, 2)), color=AQUA)
    assert check(fig) == []


def test_check_tells_custom_dash_patterns_apart():
    fig, ax = _fig()
    ax.set_prop_cycle(style_cycler([ORANGE, AQUA], markers=False))
    ax.plot([0, 1], [0, 1])
    ax.plot([0, 1], [1, 0])
    assert check(fig) == []


def test_check_scatter_and_bars():
    fig, ax = _fig()
    ax.scatter([0, 1], [0, 1], color=ORANGE, label="s1")
    ax.scatter([0, 1], [1, 0], color=AQUA, label="s2")
    assert [(h.a, h.b) for h in check(fig)] == [("s1", "s2")]

    fig, ax = _fig()
    ax.bar([0], [1], color="#d62728", label="r")
    ax.bar([1], [1], color="#2ca02c", label="g")
    assert [(h.a, h.b) for h in check(fig)] == [("r", "g")]

    fig, ax = _fig()
    ax.bar([0], [1], color="#d62728", hatch="//")
    ax.bar([1], [1], color="#2ca02c")
    assert check(fig) == []


def test_check_only_compares_within_one_axes():
    fig = Figure()
    a1, a2 = fig.subplots(1, 2)
    a1.plot([0, 1], color=ORANGE)
    a2.plot([0, 1], color=AQUA)
    assert check(fig) == []


def test_check_uses_edge_colour_for_two_open_markers():
    fig, ax = _fig()
    ax.plot([0, 1], [0, 1], "D", color="black", mfc="none", ls="none", label="dark")
    ax.plot([0, 1], [1, 0], "D", color="0.55", mfc="none", ls="none", label="light")
    # Both marker faces are transparent; the drawn edges are distinguishable.
    assert check(fig, kinds=()) == []


def test_check_treats_open_vs_filled_as_a_second_channel():
    fig, ax = _fig()
    ax.plot([0, 1], [0, 1], "D", color="black", ls="none", label="filled")
    ax.plot([0, 1], [1, 0], "D", color="black", mfc="none", ls="none", label="open")
    # Fill state, like dash or marker shape, can distinguish equal colours.
    assert check(fig, kinds=()) == []


def test_check_reports_actual_edge_colours_when_open_markers_collide():
    fig, ax = _fig()
    ax.plot([0, 1], [0, 1], "D", color="black", mfc="none", ls="none", label="a")
    ax.plot([0, 1], [1, 0], "D", color="0.05", mfc="none", ls="none", label="b")
    (hit,) = check(fig, kinds=())
    assert hit.view == "normal"
    assert (hit.color_a, hit.color_b) == ("#000000", "#0d0d0d")


def test_check_ignores_invisible_marker_with_no_face_or_edge():
    fig, ax = _fig()
    ax.plot([0, 1], [0, 1], "D", color="black", mfc="none", mec="none", ls="none")
    ax.plot([0, 1], [1, 0], "D", color="black", mfc="none", mec="none", ls="none")
    assert check(fig, kinds=()) == []
