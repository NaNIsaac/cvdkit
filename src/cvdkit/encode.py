"""Redundant encodings, so that colour is never the only channel that tells series apart."""

from cycler import Cycler, cycler

MARKERS: tuple[str, ...] = ("o", "s", "^", "D", "v", "P", "X", "<", ">", "*")
# Dash patterns rather than the four named styles, so that ten series still differ
LINESTYLES: tuple = (
    "-",
    (0, (5, 2)),
    (0, (1, 1.5)),
    (0, (6, 2, 1, 2)),
    (0, (2, 2)),
    (0, (8, 2, 1, 2, 1, 2)),
    (0, (10, 3)),
    (0, (3, 1, 1, 1, 1, 1)),
    (0, (1, 3)),
    (0, (12, 2, 2, 2)),
)
HATCHES: tuple[str, ...] = ("", "//", "\\\\", "xx", "..", "oo", "++", "--", "||", "**")


def _take(seq: tuple, n: int) -> list:
    return [seq[i % len(seq)] for i in range(n)]


def style_cycler(colors, *, markers: bool = True, linestyles: bool = True) -> Cycler:
    """A cycler that changes colour, marker and line style together, one entry per colour."""
    colors = list(colors)
    n = len(colors)
    cyc = cycler(color=colors)
    if markers:
        cyc += cycler(marker=_take(MARKERS, n))
    if linestyles:
        cyc += cycler(linestyle=_take(LINESTYLES, n))
    return cyc


def hatch_cycler(colors) -> Cycler:
    """A cycler for bars and fills that pairs each colour with a hatch pattern.

    The axes property cycle does not carry hatches to `bar` or `fill_between`, so iterate it and
    pass each entry as keyword arguments.
    """
    colors = list(colors)
    return cycler(facecolor=colors) + cycler(hatch=_take(HATCHES, len(colors)))
