"""Colour-vision-deficiency-safe palettes, redundant encodings and simulation checks for matplotlib."""

from .check import Collision, Separation, check, distinguishable, separation
from .color import delta_e2000, srgb_to_lab
from .encode import HATCHES, LINESTYLES, MARKERS, hatch_cycler, style_cycler
from .palettes import PALETTES, Palette, colormap, palette
from .pick import Picked, pick
from .simulate import KINDS, machado_matrix, simulate

__all__ = [
    "HATCHES",
    "KINDS",
    "LINESTYLES",
    "MARKERS",
    "PALETTES",
    "Collision",
    "Palette",
    "Picked",
    "Separation",
    "check",
    "colormap",
    "delta_e2000",
    "distinguishable",
    "hatch_cycler",
    "machado_matrix",
    "palette",
    "pick",
    "separation",
    "simulate",
    "srgb_to_lab",
    "style_cycler",
]
