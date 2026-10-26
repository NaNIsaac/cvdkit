"""Draw docs/swatches.png: every palette as lines with markers and dashes and as hatched bars, in
the original colours, so that a reader with a colour-vision deficiency can judge them directly.

Run: uv run python examples/swatches.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

import cvdkit

OUT = Path(__file__).resolve().parents[1] / "docs" / "swatches.png"


def main() -> None:
    names = list(cvdkit.PALETTES)
    fig, axes = plt.subplots(
        len(names), 2, figsize=(11, 2.0 * len(names)), width_ratios=(3, 2), layout="constrained"
    )
    x = np.linspace(0, 1, 9)
    for row, name in zip(axes, names, strict=True):
        colors = cvdkit.palette(name).colors
        lines, bars = row
        lines.set_prop_cycle(cvdkit.style_cycler(colors))
        for k, c in enumerate(colors):
            lines.plot(x, 0.15 + x * 0.6 + k, lw=2, ms=6, label=c)
        lines.set_title(name, loc="left", fontsize=11, fontweight="bold")
        lines.set_yticks([0.45 + k for k in range(len(colors))], colors, fontsize=8)
        lines.set_xticks([])
        lines.set_ylim(-0.2, len(colors))
        for i, style in enumerate(cvdkit.hatch_cycler(colors)):
            bars.bar(i, 1, edgecolor="black", linewidth=0.6, **style)
        bars.set_xticks(range(len(colors)), [c[1:] for c in colors], rotation=90, fontsize=8)
        bars.set_yticks([])
        bars.set_ylim(0, 1)
        for ax in row:
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
    OUT.parent.mkdir(exist_ok=True)
    fig.savefig(OUT, dpi=110)
    print(OUT)


if __name__ == "__main__":
    main()
