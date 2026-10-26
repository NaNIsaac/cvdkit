"""Colour-vision-deficiency simulation (Machado, Oliveira and Fernandes 2009).

The matrices are Table 1 of the paper, tabulated at severities 0.0 to 1.0 in steps of 0.1;
severity 1.0 is dichromacy. Between table entries the matrix is interpolated linearly, which the
authors describe as a fast and accurate approximation. The paper derives the matrices from linear
cone responses and does not state the encoding of the RGB input, so they are applied to
linear-light sRGB, as colorspacious does.
"""

import io
import json
from functools import cache
from importlib import resources
from typing import Literal

import numpy as np
from matplotlib import image as plt_image
from matplotlib.figure import Figure

from .color import as_rgb, linear_to_srgb, srgb_to_linear

type Kind = Literal["protan", "deutan", "tritan"]
KINDS: tuple[Kind, ...] = ("protan", "deutan", "tritan")


@cache
def _table() -> dict[str, np.ndarray]:
    raw = json.loads(resources.files("cvdkit").joinpath("data/machado2009.json").read_text())
    return {kind: np.array(raw[kind]) for kind in KINDS}


def machado_matrix(kind: Kind, severity: float = 1.0) -> np.ndarray:
    """The 3x3 matrix that maps linear sRGB to its simulation for `kind` at `severity` in [0, 1]."""
    if kind not in KINDS:
        raise ValueError(f"kind must be one of {KINDS}, not {kind!r}")
    if not 0.0 <= severity <= 1.0:
        raise ValueError(f"severity must be in [0, 1], not {severity}")
    table = _table()[kind]
    pos = severity * 10
    lo = min(int(np.floor(pos)), 9)
    w = pos - lo
    return (1 - w) * table[lo] + w * table[lo + 1]


def simulate_rgb(rgb: np.ndarray, kind: Kind, severity: float = 1.0) -> np.ndarray:
    """Simulate sRGB values in [0, 1], shape (..., 3); the result is clipped to the gamut."""
    lin = srgb_to_linear(np.asarray(rgb, float)) @ machado_matrix(kind, severity).T
    return linear_to_srgb(lin)


def figure_to_array(fig: Figure, dpi: float | None = None) -> np.ndarray:
    """Render a figure to an RGB array in [0, 1]."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi or fig.dpi)
    buf.seek(0)
    return plt_image.imread(buf, format="png")[..., :3].astype(float)


def simulate(obj, kind: Kind = "deutan", severity: float = 1.0) -> np.ndarray:
    """Simulate how `obj` looks with a colour-vision deficiency.

    `obj` is a matplotlib Figure, an image array (H, W, 3 or 4; uint8 or float in [0, 1]), or one
    or more matplotlib colour specs. Returns sRGB in [0, 1]; an image keeps its height and width,
    an alpha channel is dropped.
    """
    rgb = figure_to_array(obj) if isinstance(obj, Figure) else as_rgb(obj)
    return simulate_rgb(rgb, kind, severity)
