import pytest

from cvdkit import distinguishable, pick


def test_pick_keeps_colours_apart_for_every_view():
    p = pick(4)
    assert len(set(p.colors)) == 4
    assert p.min_score >= 1.0
    for i, a in enumerate(p.colors):
        for b in p.colors[i + 1 :]:
            assert distinguishable(a, b)


def test_pick_drops_colours_lost_in_the_background():
    assert "#000000" not in pick(5, background="black").colors
    assert "#000000" in pick(8, background="white").colors
    assert "#f0e442" not in pick(7, background="white").colors


def test_pick_more_than_the_palette_repeats_colours_with_new_markers():
    p = pick(12)
    assert len(p.colors) == 12
    assert len(set(p.colors)) < 12
    assert len(set(zip(p.colors, p.markers, strict=True))) == 12
    assert p.min_score == 0.0


def test_cyclers_have_one_entry_per_series():
    p = pick(3)
    entries = list(p.cycler())
    assert len(entries) == 3
    assert set(entries[0]) == {"color", "marker", "linestyle"}
    assert set(next(iter(p.hatch_cycler()))) == {"facecolor", "hatch"}


def test_pick_rejects_zero():
    with pytest.raises(ValueError):
        pick(0)
