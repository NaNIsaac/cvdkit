from itertools import combinations

import numpy as np
import pytest

from cvdkit import PALETTES, colormap, palette, separation

# Smallest pairwise CIEDE2000 within each palette, under normal vision and each simulation at
# severity 1. Recorded from this implementation; a change here means the palette data or the
# colour maths changed.
MIN_DE = {
    "okabe_ito": {"normal": 21.7, "protan": 12.2, "deutan": 11.6, "tritan": 10.9},
    "tol_bright": {"normal": 20.5, "protan": 14.2, "deutan": 14.8, "tritan": 8.6},
    "tol_vibrant": {"normal": 18.3, "protan": 13.7, "deutan": 14.4, "tritan": 8.6},
    "tol_muted": {"normal": 15.0, "protan": 11.8, "deutan": 14.3, "tritan": 11.5},
    "tol_high_contrast": {"normal": 38.9, "protan": 26.0, "deutan": 25.3, "tritan": 21.2},
    "petroff6": {"normal": 17.9, "protan": 10.6, "deutan": 14.7, "tritan": 18.3},
    "petroff8": {"normal": 20.0, "protan": 9.0, "deutan": 14.5, "tritan": 11.7},
    "petroff10": {"normal": 17.3, "protan": 11.9, "deutan": 12.6, "tritan": 13.3},
}


@pytest.mark.parametrize("name", PALETTES)
def test_min_pairwise_distance(name):
    p = palette(name)
    for view, expected in MIN_DE[name].items():
        got = min(separation(a, b, view).de for a, b in combinations(p.colors, 2))
        assert got == pytest.approx(expected, abs=0.05), view


@pytest.mark.parametrize("name", PALETTES)
def test_every_palette_has_a_source_and_terms(name):
    p = palette(name)
    assert p.source and p.terms
    assert len(set(p.colors)) == len(p) >= 3


def test_unknown_palette():
    with pytest.raises(KeyError, match="okabe_ito"):
        palette("rainbow")


def test_colormaps():
    sunset = colormap("tol_sunset")
    np.testing.assert_allclose(sunset(0.0)[:3], [0x36 / 255, 0x4B / 255, 0x9A / 255], atol=1e-6)
    np.testing.assert_allclose(sunset(1.0)[:3], [0xA5 / 255, 0.0, 0x26 / 255], atol=1e-6)
    assert colormap("cividis").name == "cividis"
