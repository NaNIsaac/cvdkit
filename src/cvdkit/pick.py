"""Choose n colours that stay apart under simulation, with markers, dashes and hatches to match."""

from dataclasses import dataclass
from itertools import combinations
from math import comb

from cycler import Cycler

from .check import View, separation
from .color import ColorLike
from .encode import HATCHES, LINESTYLES, MARKERS, _take, hatch_cycler, style_cycler
from .palettes import palette
from .simulate import KINDS

_VIEWS: tuple[View, ...] = ("normal", *KINDS)
_EXHAUSTIVE_LIMIT = 5000
# Twice the pair threshold: Okabe and Ito warn that thin yellow lines are hard to read on white,
# and their yellow is only about 11 lightness units from it
_BACKGROUND_SCORE = 2.0


@dataclass(frozen=True)
class Picked:
    colors: tuple[str, ...]
    markers: tuple[str, ...]
    linestyles: tuple
    hatches: tuple[str, ...]
    min_score: float
    """Smallest pairwise line separation over all views; below 1 some pair needs the marker,
    dash or hatch to be told apart."""

    def cycler(self) -> Cycler:
        return style_cycler(self.colors)

    def hatch_cycler(self) -> Cycler:
        return hatch_cycler(self.colors)


def _score(a: str, b: str) -> float:
    return min(separation(a, b, v).score for v in _VIEWS)


def pick(n: int, background: ColorLike = "white", from_palette: str = "okabe_ito") -> Picked:
    """The `n` colours of a palette whose worst pair is most distinct under every simulation.

    Colours that do not stand out from `background` are dropped first. If more colours are asked
    for than the palette can keep distinct, the colours repeat and the markers, dashes and hatches
    keep the series apart.
    """
    if n < 1:
        raise ValueError("n must be at least 1")
    candidates = [
        c for c in palette(from_palette).colors if _score(c, background) >= _BACKGROUND_SCORE
    ]
    k = min(n, len(candidates))
    pair = {(a, b): _score(a, b) for a, b in combinations(candidates, 2)}

    def worst(subset: tuple[str, ...]) -> float:
        return min((pair[p] for p in combinations(subset, 2)), default=float("inf"))

    if comb(len(candidates), k) <= _EXHAUSTIVE_LIMIT:
        best = max(combinations(candidates, k), key=worst)
    else:
        chosen = [candidates[0]]
        while len(chosen) < k:
            chosen.append(
                max(
                    (c for c in candidates if c not in chosen),
                    key=lambda c: min(pair.get((x, c), pair.get((c, x), 0.0)) for x in chosen),
                )
            )
        best = tuple(chosen)

    colors = tuple(_take(best, n))
    return Picked(
        colors=colors,
        markers=tuple(_take(MARKERS, n)),
        linestyles=tuple(_take(LINESTYLES, n)),
        hatches=tuple(_take(HATCHES, n)),
        min_score=worst(best) if n <= len(best) else 0.0,
    )
