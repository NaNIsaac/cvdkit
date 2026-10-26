from pathlib import Path

import matplotlib
import numpy as np
from matplotlib import image as plt_image
from matplotlib.figure import Figure

import cvdkit

BASELINE = Path(__file__).with_name("baseline") / "lines_deutan.png"


def _figure() -> Figure:
    # No text, so the render does not depend on the fonts installed
    fig = Figure(figsize=(3, 2), dpi=60)
    ax = fig.add_axes((0, 0, 1, 1))
    ax.set_axis_off()
    ax.set_prop_cycle(cvdkit.pick(4).cycler())
    x = np.linspace(0, 1, 8)
    for k in range(4):
        ax.plot(x, x * (k + 1) / 4, lw=2, ms=5)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    return fig


def test_simulated_figure_matches_baseline():
    got = cvdkit.simulate(_figure(), "deutan")
    want = plt_image.imread(BASELINE)[..., :3]
    assert got.shape == want.shape
    # Agg antialiasing can move single edge pixels between matplotlib builds
    assert np.abs(got - want).mean() < 2e-3, matplotlib.__version__


def test_styled_figure_passes_check():
    assert cvdkit.check(_figure()) == []
