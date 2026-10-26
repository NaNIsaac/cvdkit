"""sRGB, CIELAB and the CIEDE2000 colour difference.

CIEDE2000 follows the implementation notes of Sharma, Wu and Dalal (2005) and is tested against
their published pairs.
"""

from collections.abc import Iterable

import numpy as np
from matplotlib.colors import to_rgb

# IEC 61966-2-1 sRGB primaries with the D65 white, as in Lindbloom's tables
_RGB_TO_XYZ = np.array(
    [
        [0.4124564, 0.3575761, 0.1804375],
        [0.2126729, 0.7151522, 0.0721750],
        [0.0193339, 0.1191920, 0.9503041],
    ]
)
_WHITE_D65 = _RGB_TO_XYZ.sum(axis=1)

type ColorLike = str | tuple[float, ...] | np.ndarray


def as_rgb(colors: ColorLike | Iterable[ColorLike]) -> np.ndarray:
    """Return sRGB in [0, 1] with shape (..., 3) from matplotlib colour specs or an array."""
    if isinstance(colors, str):
        return np.array(to_rgb(colors))
    arr = np.asarray(colors)
    if arr.dtype.kind in "fiu" and arr.ndim >= 1 and arr.shape[-1] in (3, 4):
        integer = arr.dtype.kind in "iu"
        arr = arr[..., :3].astype(float)
        return arr / 255.0 if integer else arr
    return np.array([to_rgb(c) for c in colors])


def to_hex(rgb: np.ndarray) -> str:
    r, g, b = (np.clip(np.asarray(rgb, float), 0, 1) * 255).round().astype(int)
    return f"#{r:02x}{g:02x}{b:02x}"


def srgb_to_linear(rgb: np.ndarray) -> np.ndarray:
    rgb = np.asarray(rgb, float)
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def linear_to_srgb(lin: np.ndarray) -> np.ndarray:
    lin = np.clip(np.asarray(lin, float), 0.0, 1.0)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055)


def srgb_to_lab(rgb: np.ndarray) -> np.ndarray:
    """CIELAB (D65) of sRGB values in [0, 1], shape (..., 3)."""
    xyz = srgb_to_linear(rgb) @ _RGB_TO_XYZ.T / _WHITE_D65
    eps, kappa = 216 / 24389, 24389 / 27
    f = np.where(xyz > eps, np.cbrt(xyz), (kappa * xyz + 16) / 116)
    return np.stack(
        [116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]), 200 * (f[..., 1] - f[..., 2])],
        axis=-1,
    )


def delta_e2000(lab1: np.ndarray, lab2: np.ndarray) -> np.ndarray:
    """CIEDE2000 colour difference with kL = kC = kH = 1, broadcast over leading axes."""
    lab1, lab2 = np.asarray(lab1, float), np.asarray(lab2, float)
    L1, a1, b1 = np.moveaxis(lab1, -1, 0)
    L2, a2, b2 = np.moveaxis(lab2, -1, 0)

    C_bar = (np.hypot(a1, b1) + np.hypot(a2, b2)) / 2
    G = 0.5 * (1 - np.sqrt(C_bar**7 / (C_bar**7 + 25.0**7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = np.hypot(a1p, b1), np.hypot(a2p, b2)
    h1p = np.degrees(np.arctan2(b1, a1p)) % 360
    h2p = np.degrees(np.arctan2(b2, a2p)) % 360

    dLp = L2 - L1
    dCp = C2p - C1p
    zero = C1p * C2p == 0
    dh = h2p - h1p
    dh = np.where(dh > 180, dh - 360, np.where(dh < -180, dh + 360, dh))
    dh = np.where(zero, 0.0, dh)
    dHp = 2 * np.sqrt(C1p * C2p) * np.sin(np.radians(dh / 2))

    Lp_bar = (L1 + L2) / 2
    Cp_bar = (C1p + C2p) / 2
    h_sum = h1p + h2p
    hp_bar = np.where(
        np.abs(h1p - h2p) <= 180,
        h_sum / 2,
        np.where(h_sum < 360, (h_sum + 360) / 2, (h_sum - 360) / 2),
    )
    hp_bar = np.where(zero, h_sum, hp_bar)

    T = (
        1
        - 0.17 * np.cos(np.radians(hp_bar - 30))
        + 0.24 * np.cos(np.radians(2 * hp_bar))
        + 0.32 * np.cos(np.radians(3 * hp_bar + 6))
        - 0.20 * np.cos(np.radians(4 * hp_bar - 63))
    )
    d_theta = 30 * np.exp(-(((hp_bar - 275) / 25) ** 2))
    R_C = 2 * np.sqrt(Cp_bar**7 / (Cp_bar**7 + 25.0**7))
    S_L = 1 + 0.015 * (Lp_bar - 50) ** 2 / np.sqrt(20 + (Lp_bar - 50) ** 2)
    S_C = 1 + 0.045 * Cp_bar
    S_H = 1 + 0.015 * Cp_bar * T
    R_T = -np.sin(np.radians(2 * d_theta)) * R_C

    return np.sqrt(
        (dLp / S_L) ** 2 + (dCp / S_C) ** 2 + (dHp / S_H) ** 2 + R_T * (dCp / S_C) * (dHp / S_H)
    )
