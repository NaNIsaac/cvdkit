"""Decide whether two colours stay apart under simulation, and find the artists that collide.

A colour difference alone is not enough. Two colours can keep a CIEDE2000 distance above 15
under deuteranopia while sharing lightness and hue, so that only saturation tells them apart;
that does not survive a thin line or a small marker. Lines and markers therefore have to differ
in lightness or in hue. Filled areas are judged by CIEDE2000 alone. The thresholds are working
values chosen for this package, not taken from a study.
"""

from dataclasses import dataclass
from itertools import combinations
from typing import Literal

import numpy as np
from matplotlib.collections import PathCollection
from matplotlib.container import BarContainer
from matplotlib.figure import Figure
from matplotlib.lines import Line2D

from .color import ColorLike, as_rgb, delta_e2000, srgb_to_lab, to_hex
from .simulate import KINDS, Kind, simulate_rgb

MIN_DL = 10.0
MIN_DHUE = 30.0
MIN_CHROMA = 15.0
MIN_DE_AREA = 10.0

type View = Literal["normal", "protan", "deutan", "tritan"]
type Mark = Literal["line", "area"]


@dataclass(frozen=True)
class Separation:
    view: View
    de: float
    dl: float
    dhue: float
    chroma: float

    def ok(self, mark: Mark = "line") -> bool:
        if mark == "area":
            return self.de >= MIN_DE_AREA
        return self.dl >= MIN_DL or (self.dhue >= MIN_DHUE and self.chroma >= MIN_CHROMA)

    @property
    def score(self) -> float:
        """At least 1 when a line or marker pair is distinct; larger is more distinct."""
        return max(self.dl / MIN_DL, min(self.dhue / MIN_DHUE, self.chroma / MIN_CHROMA))


def separation(
    a: ColorLike, b: ColorLike, view: View = "deutan", severity: float = 1.0
) -> Separation:
    rgb = np.stack([as_rgb(a), as_rgb(b)])
    if view != "normal":
        rgb = simulate_rgb(rgb, view, severity)
    lab = srgb_to_lab(rgb)
    chroma = np.hypot(lab[:, 1], lab[:, 2])
    hue = np.degrees(np.arctan2(lab[:, 2], lab[:, 1]))
    return Separation(
        view=view,
        de=float(delta_e2000(lab[0], lab[1])),
        dl=float(abs(lab[0, 0] - lab[1, 0])),
        dhue=float(abs((hue[0] - hue[1] + 180) % 360 - 180)),
        chroma=float(chroma.min()),
    )


def distinguishable(
    a: ColorLike,
    b: ColorLike,
    mark: Mark = "line",
    kinds: tuple[Kind, ...] = KINDS,
    severity: float = 1.0,
) -> bool:
    """True when `a` and `b` stay apart for normal vision and every simulated deficiency."""
    views: tuple[View, ...] = ("normal", *kinds)
    return all(separation(a, b, v, severity).ok(mark) for v in views)


@dataclass(frozen=True)
class Collision:
    """Two artists in one Axes that only colour separates, and colour fails under `view`."""

    axes: int
    a: str
    b: str
    color_a: str
    color_b: str
    view: View
    separation: Separation


@dataclass(frozen=True)
class _Item:
    label: str
    color: np.ndarray
    channels: tuple
    mark: Mark


def _line_item(i: int, line: Line2D) -> _Item | None:
    if not line.get_visible():
        return None
    has_line = line.get_linestyle() not in ("None", "", " ") and line.get_linewidth() > 0
    marker = line.get_marker()
    has_marker = marker not in ("None", None, "", " ", "none")
    if not (has_line or has_marker):
        return None
    color = line.get_color() if has_line else line.get_markerfacecolor()
    # get_linestyle() reports every custom dash tuple as "--", so compare the pattern itself
    _, seq = getattr(line, "_unscaled_dash_pattern", (0, None))
    dashes = tuple(np.round(seq, 2)) if has_line and seq else ()
    channels = (
        "line",
        has_line and (line.get_linestyle(), dashes),
        has_marker and str(marker),
    )
    return _Item(line.get_label() or f"line {i}", as_rgb(color), channels, "line")


def _scatter_item(i: int, coll: PathCollection) -> _Item | None:
    fc = coll.get_facecolors()
    if not coll.get_visible() or len(fc) == 0 or len(fc) > 1 and not np.allclose(fc, fc[0]):
        return None
    paths = coll.get_paths()
    shape = tuple(np.round(paths[0].vertices, 2).ravel()) if paths else ()
    return _Item(coll.get_label() or f"scatter {i}", as_rgb(fc[0]), ("marker", shape), "line")


def _bar_item(i: int, bars: BarContainer) -> _Item | None:
    if not bars.patches:
        return None
    p = bars.patches[0]
    return _Item(
        bars.get_label() or f"bars {i}",
        as_rgb(p.get_facecolor()),
        ("area", p.get_hatch() or ""),
        "area",
    )


def _items(ax) -> list[_Item]:
    out: list[_Item | None] = []
    out += [_line_item(i, ln) for i, ln in enumerate(ax.lines)]
    out += [
        _scatter_item(i, c) for i, c in enumerate(ax.collections) if isinstance(c, PathCollection)
    ]
    out += [_bar_item(i, c) for i, c in enumerate(ax.containers) if isinstance(c, BarContainer)]
    return [it for it in out if it is not None]


def check(fig: Figure, kinds: tuple[Kind, ...] = KINDS, severity: float = 1.0) -> list[Collision]:
    """Pairs of lines, scatter sets or bar sets in the same Axes that share every channel except
    colour, and whose colours are not distinguishable under one of the simulations.

    Colour-mapped images and scatter points coloured by value are skipped; check those by eye
    with `simulate`.
    """
    found = []
    for k, ax in enumerate(fig.axes):
        for a, b in combinations(_items(ax), 2):
            if a.channels != b.channels:
                continue
            for view in ("normal", *kinds):
                sep = separation(a.color, b.color, view, severity)
                if not sep.ok(a.mark):
                    found.append(
                        Collision(k, a.label, b.label, to_hex(a.color), to_hex(b.color), view, sep)
                    )
                    break
    return found
