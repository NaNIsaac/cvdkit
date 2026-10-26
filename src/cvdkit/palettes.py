"""Categorical palettes and colormaps designed to stay readable with colour-vision deficiency.

Each palette records where its colours come from and under what terms; see the README for the
full references.
"""

from dataclasses import dataclass

from matplotlib import colormaps
from matplotlib.colors import Colormap, LinearSegmentedColormap


@dataclass(frozen=True)
class Palette:
    name: str
    colors: tuple[str, ...]
    source: str
    terms: str

    def __len__(self) -> int:
        return len(self.colors)

    def __iter__(self):
        return iter(self.colors)


_TOL = "Tol, Colour Schemes, SRON/EPS/TN/09-002 issue 3.2 (2021), via the tol_colors package"
_TOL_TERMS = "BSD-3-Clause, Copyright (c) 2019 Paul Tol, Clement Haeck"

PALETTES: dict[str, Palette] = {
    p.name: p
    for p in (
        Palette(
            "okabe_ito",
            (
                "#000000",
                "#e69f00",
                "#56b4e9",
                "#009e73",
                "#f0e442",
                "#0072b2",
                "#d55e00",
                "#cc79a7",
            ),
            "Okabe and Ito, Color Universal Design (2002, revised 2008); Wong, Nat. Methods 8, 441 (2011)",
            "free to use with credit to Okabe and Ito",
        ),
        Palette(
            "tol_bright",
            ("#4477aa", "#ee6677", "#228833", "#ccbb44", "#66ccee", "#aa3377", "#bbbbbb"),
            _TOL,
            _TOL_TERMS,
        ),
        Palette(
            "tol_vibrant",
            ("#ee7733", "#0077bb", "#33bbee", "#ee3377", "#cc3311", "#009988", "#bbbbbb"),
            _TOL,
            _TOL_TERMS,
        ),
        Palette(
            "tol_muted",
            (
                "#cc6677",
                "#332288",
                "#ddcc77",
                "#117733",
                "#88ccee",
                "#882255",
                "#44aa99",
                "#999933",
                "#aa4499",
            ),
            _TOL,
            _TOL_TERMS,
        ),
        Palette("tol_high_contrast", ("#004488", "#ddaa33", "#bb5566"), _TOL, _TOL_TERMS),
        Palette(
            "petroff6",
            ("#5790fc", "#f89c20", "#e42536", "#964a8b", "#9c9ca1", "#7a21dd"),
            "Petroff, arXiv:2107.02270 (2021)",
            "CC0-1.0",
        ),
        Palette(
            "petroff8",
            (
                "#1845fb",
                "#ff5e02",
                "#c91f16",
                "#c849a9",
                "#adad7d",
                "#86c8dd",
                "#578dff",
                "#656364",
            ),
            "Petroff, arXiv:2107.02270 (2021)",
            "CC0-1.0",
        ),
        Palette(
            "petroff10",
            (
                "#3f90da",
                "#ffa90e",
                "#bd1f01",
                "#94a4a2",
                "#832db6",
                "#a96b59",
                "#e76300",
                "#b9ac70",
                "#717581",
                "#92dadd",
            ),
            "Petroff, arXiv:2107.02270 (2021)",
            "CC0-1.0",
        ),
    )
}

_TOL_MAPS = {
    "tol_sunset": (
        "#364b9a",
        "#4a7bb7",
        "#6ea6cd",
        "#98cae1",
        "#c2e4ef",
        "#eaeccc",
        "#feda8b",
        "#fdb366",
        "#f67e4b",
        "#dd3d2d",
        "#a50026",
    ),
    "tol_BuRd": (
        "#2166ac",
        "#4393c3",
        "#92c5de",
        "#d1e5f0",
        "#f7f7f7",
        "#fddbc7",
        "#f4a582",
        "#d6604d",
        "#b2182b",
    ),
}
_TOL_BAD = {"tol_sunset": "#ffffff", "tol_BuRd": "#ffee99"}


def palette(name: str = "okabe_ito") -> Palette:
    try:
        return PALETTES[name]
    except KeyError:
        raise KeyError(f"unknown palette {name!r}; known: {', '.join(PALETTES)}") from None


def colormap(name: str) -> Colormap:
    """A CVD-safe colormap: the diverging Tol maps `tol_sunset` and `tol_BuRd`, or a matplotlib
    name. For sequential data matplotlib's `cividis` (Nunez, Anderton and Renslow 2018) or
    `viridis` already serve."""
    if name in _TOL_MAPS:
        cmap = LinearSegmentedColormap.from_list(name, _TOL_MAPS[name])
        return cmap.with_extremes(bad=_TOL_BAD[name])
    return colormaps[name]
