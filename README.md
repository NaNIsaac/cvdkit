# cvdkit

[English](README.md) | [한국어](README.ko.md)

Colour-vision-deficiency-safe styling for matplotlib: palettes that stay apart under protan, deutan
and tritan simulation, markers, dash patterns and hatches cycled with the colours, and a check that
finds the series in a figure that only colour tells apart.

## Install

cvdkit needs Python 3.12 or newer. Until the first release is on PyPI, install it from a clone of
this repository:

<!-- test unix -->
```sh
uv venv
uv pip install .
```

<!-- test windows -->
```powershell
uv venv
uv pip install .
```

Check that it imports:

<!-- test unix -->
```sh
uv run --no-project python -c "import cvdkit; print(cvdkit.pick(3).colors)"
```

<!-- test windows -->
```powershell
uv run --no-project python -c "import cvdkit; print(cvdkit.pick(3).colors)"
```

## Use

```python
import matplotlib.pyplot as plt
import cvdkit

p = cvdkit.pick(4)  # 4 colours that stay apart for every simulated deficiency
fig, ax = plt.subplots()
ax.set_prop_cycle(p.cycler())  # colour, marker and dash pattern change together
for k in range(4):
    ax.plot(range(10), [k * x for x in range(10)], label=f"k={k}")
ax.legend()

for c in cvdkit.check(fig):  # pairs that only colour separates, and colour fails
    print(c.a, c.b, c.view, c.color_a, c.color_b)

sim = cvdkit.simulate(fig, "deutan")  # RGB array of the figure as seen with deuteranopia
plt.imsave("figure_deutan.png", sim)
```

- `simulate(obj, kind, severity)` takes a figure, an image array or colour specs. `kind` is
  `"protan"`, `"deutan"` or `"tritan"`, and `severity` runs from 0 to 1, where 1 is dichromacy.
- `check(fig)` compares the lines, scatter sets and bar sets inside each Axes. A pair is reported
  when nothing but colour separates them (same marker, dash pattern or hatch) and the colours
  collide under one of the simulations. Colour-mapped images are not checked; look at them through
  `simulate`.
- `distinguishable(a, b)` and `separation(a, b, view)` give the same test for two colours.
- `pick(n, background)` takes the `n` colours of a palette (Okabe-Ito by default) whose closest
  pair is farthest apart under every simulation, and drops colours that would be lost against the
  background. Past what the palette can keep apart, colours repeat and the markers, dashes and
  hatches separate the series.
- `style_cycler(colors)` and `hatch_cycler(colors)` build the cyclers for any colour list.
- `palette(name)` and `colormap(name)` give the data below.

### When two colours count as distinct

Lines and markers must differ in CIELAB lightness by at least 10, or in hue angle by at least
30 degrees with both colours at chroma 15 or more, under normal vision and under each simulation.
Filled areas need a CIEDE2000 difference of at least 10. A difference in saturation alone does not
count for lines: `#eb6834` and `#1baf7a` keep a CIEDE2000 distance of about 17 under deuteranopia,
more than some pairs in the palettes below, yet both become a mid olive at the same lightness and
a thin line cannot show which is which. These thresholds are working values chosen for this
package, not results from a study.

## Data

Categorical palettes, with the smallest pairwise CIEDE2000 under normal vision and each simulation
at severity 1:

| name | colours | normal | protan | deutan | tritan | source | terms |
|---|---|---|---|---|---|---|---|
| `okabe_ito` | 8 | 21.7 | 12.2 | 11.6 | 10.9 | Okabe and Ito; Wong 2011 | free to use with credit |
| `tol_bright` | 7 | 20.5 | 14.2 | 14.8 | 8.6 | Tol | BSD-3-Clause |
| `tol_vibrant` | 7 | 18.3 | 13.7 | 14.4 | 8.6 | Tol | BSD-3-Clause |
| `tol_muted` | 9 | 15.0 | 11.8 | 14.3 | 11.5 | Tol | BSD-3-Clause |
| `tol_high_contrast` | 3 | 38.9 | 26.0 | 25.3 | 21.2 | Tol | BSD-3-Clause |
| `petroff6` | 6 | 17.9 | 10.6 | 14.7 | 18.3 | Petroff 2021 | CC0-1.0 |
| `petroff8` | 8 | 20.0 | 9.0 | 14.5 | 11.7 | Petroff 2021 | CC0-1.0 |
| `petroff10` | 10 | 17.3 | 11.9 | 12.6 | 13.3 | Petroff 2021 | CC0-1.0 |

Colormaps: `colormap("tol_sunset")` and `colormap("tol_BuRd")` are Tol's diverging maps. For
sequential data use matplotlib's `cividis` (Nuñez et al. 2018) or `viridis`; Crameri's scientific
colour maps (Crameri et al. 2020) are in the `cmcrameri` package.

The Tol colours are taken from the `tol_colors` package; its BSD-3-Clause notice is in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## References

- Machado, G. M., Oliveira, M. M. and Fernandes, L. A. F. (2009). A physiologically-based model for
  simulation of color vision deficiency. *IEEE Transactions on Visualization and Computer Graphics*
  15(6), 1291-1298. doi:10.1109/TVCG.2009.113. The simulation matrices are Table 1, from
  https://www.inf.ufrgs.br/~oliveira/pubs_files/CVD_Simulation/CVD_Simulation.html; the paper does
  not state the RGB encoding, and cvdkit applies them to linear-light sRGB.
- Brettel, H., Viénot, F. and Mollon, J. D. (1997). Computerized simulation of color appearance for
  dichromats. *Journal of the Optical Society of America A* 14(10), 2647.
  doi:10.1364/JOSAA.14.002647. Background for dichromat simulation; not implemented here.
- Viénot, F., Brettel, H. and Mollon, J. D. (1999). Digital video colourmaps for checking the
  legibility of displays by dichromats. *Color Research & Application* 24(4), 243-252.
  doi:10.1002/(SICI)1520-6378(199908)24:4<243::AID-COL5>3.0.CO;2-3. Background; not implemented.
- Okabe, M. and Ito, K. (2002, revised 2008). Color Universal Design (CUD): Colorblind Barrier Free.
  https://jfly.uni-koeln.de/color/
- Wong, B. (2011). Points of view: Color blindness. *Nature Methods* 8(6), 441.
  doi:10.1038/nmeth.1618.
- Nuñez, J. R., Anderton, C. R. and Renslow, R. S. (2018). Optimizing colormaps with consideration
  for color vision deficiency to enable accurate interpretation of scientific data. *PLOS ONE*
  13(7), e0199239. doi:10.1371/journal.pone.0199239.
- Crameri, F., Shephard, G. E. and Heron, P. J. (2020). The misuse of colour in science
  communication. *Nature Communications* 11, 5444. doi:10.1038/s41467-020-19160-7.
- Petroff, M. A. (2021). Accessible color sequences for data visualization. arXiv:2107.02270.
  Colour sequences from https://github.com/mpetroff/accessible-color-cycles (CC0-1.0).
- Tol, P. (2021). Colour Schemes. SRON/EPS/TN/09-002, issue 3.2. https://sronpersonalpages.nl/~pault/
- Sharma, G., Wu, W. and Dalal, E. N. (2005). The CIEDE2000 color-difference formula: implementation
  notes, supplementary test data, and mathematical observations. *Color Research & Application*
  30(1), 21-30. doi:10.1002/col.20070. The tests use its 34 published pairs.

## License

MIT. Palette data keeps the terms listed above.
