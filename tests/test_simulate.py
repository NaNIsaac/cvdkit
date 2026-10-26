import numpy as np
import pytest
from matplotlib.figure import Figure

from cvdkit import machado_matrix, simulate

# Copied by hand from Table 1 of Machado, Oliveira and Fernandes (2009), to check the packaged table
PUBLISHED = {
    ("protan", 1.0): [
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281, 0.099216],
        [-0.003882, -0.048116, 1.051998],
    ],
    ("protan", 0.5): [
        [0.458064, 0.679578, -0.137642],
        [0.092785, 0.846313, 0.060902],
        [-0.007494, -0.016807, 1.024301],
    ],
    ("deutan", 1.0): [
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501, 0.047413],
        [-0.011820, 0.042940, 0.968881],
    ],
    ("deutan", 0.5): [
        [0.547494, 0.607765, -0.155259],
        [0.181692, 0.781742, 0.036566],
        [-0.010410, 0.027275, 0.983136],
    ],
    ("tritan", 1.0): [
        [1.255528, -0.076749, -0.178779],
        [-0.078411, 0.930809, 0.147602],
        [0.004733, 0.691367, 0.303900],
    ],
    ("tritan", 0.5): [
        [1.017277, 0.027029, -0.044306],
        [-0.006113, 0.958479, 0.047634],
        [0.006379, 0.248708, 0.744913],
    ],
}


@pytest.mark.parametrize(("kind", "severity"), PUBLISHED)
def test_matrix_matches_paper(kind, severity):
    np.testing.assert_allclose(machado_matrix(kind, severity), PUBLISHED[kind, severity], atol=1e-6)


@pytest.mark.parametrize("kind", ["protan", "deutan", "tritan"])
def test_zero_severity_is_identity_and_rows_keep_white(kind):
    np.testing.assert_allclose(machado_matrix(kind, 0.0), np.eye(3), atol=1e-6)
    for s in np.linspace(0, 1, 11):
        np.testing.assert_allclose(machado_matrix(kind, s).sum(axis=1), 1.0, atol=2e-5)


def test_interpolates_between_table_rows():
    m8, m9 = machado_matrix("deutan", 0.8), machado_matrix("deutan", 0.9)
    np.testing.assert_allclose(machado_matrix("deutan", 0.873), 0.27 * m8 + 0.73 * m9, atol=1e-12)


def test_rejects_bad_arguments():
    with pytest.raises(ValueError):
        machado_matrix("achromat", 1.0)
    with pytest.raises(ValueError):
        machado_matrix("deutan", 1.5)


def test_grey_is_unchanged_and_red_green_merge():
    np.testing.assert_allclose(simulate("#808080", "deutan"), [128 / 255] * 3, atol=1e-3)
    red, green = simulate(["#d62728", "#2ca02c"], "deutan")
    assert np.abs(red - green).max() < 0.2


def test_image_inputs_keep_shape():
    img8 = np.zeros((4, 5, 4), np.uint8)
    img8[..., 0] = 255
    out = simulate(img8, "protan")
    assert out.shape == (4, 5, 3)
    np.testing.assert_allclose(out, simulate(np.ones((4, 5, 3)) * [1, 0, 0], "protan"))


def test_figure_input():
    fig = Figure(figsize=(2, 1), dpi=50)
    fig.add_subplot().plot([0, 1], [0, 1], color="red")
    out = simulate(fig, "deutan")
    assert out.shape == (50, 100, 3)
    assert 0.0 <= out.min() and out.max() <= 1.0
