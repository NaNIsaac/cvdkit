from pathlib import Path

import numpy as np

from cvdkit import delta_e2000, srgb_to_lab

DATA = Path(__file__).with_name("data") / "ciede2000_sharma2005.txt"


def test_ciede2000_matches_sharma_test_data():
    rows = np.loadtxt(DATA)
    assert rows.shape == (34, 7)
    got = delta_e2000(rows[:, 0:3], rows[:, 3:6])
    np.testing.assert_allclose(got, rows[:, 6], atol=1e-4)


def test_ciede2000_is_symmetric_on_test_data():
    rows = np.loadtxt(DATA)
    np.testing.assert_allclose(
        delta_e2000(rows[:, 0:3], rows[:, 3:6]), delta_e2000(rows[:, 3:6], rows[:, 0:3]), atol=1e-4
    )


def test_lab_of_white_black_and_primary():
    np.testing.assert_allclose(srgb_to_lab(np.array([1.0, 1.0, 1.0])), [100, 0, 0], atol=1e-3)
    np.testing.assert_allclose(srgb_to_lab(np.array([0.0, 0.0, 0.0])), [0, 0, 0], atol=1e-6)
    # sRGB red in CIELAB D65, as in Lindbloom's calculator
    np.testing.assert_allclose(
        srgb_to_lab(np.array([1.0, 0.0, 0.0])), [53.24, 80.09, 67.20], atol=0.02
    )
