from __future__ import annotations

import numpy as np

from .config import RouteBConfig
from .geometry import row_sets


def proxy_metrics(mask: np.ndarray, cfg: RouteBConfig) -> dict[str, float]:
    """Cheap geometry-only proxy before the real EM evaluator is wired in.

    This score is intentionally conservative. It does not claim EM accuracy;
    it only checks whether a mask has Route-B-like ingredients: continuous
    rails, outer slow-wave loading, chirped variation, and moderate metal use.
    """
    rows = row_sets(cfg)
    upper = mask[rows["upper_load"], :].astype(float)
    col_depth = upper.sum(axis=0) * cfg.grid_um
    metal_fill = upper.mean()

    active_depth = col_depth[col_depth > 0]
    if active_depth.size == 0:
        chirp_score = 0.0
        slow_wave_score = 0.0
        active_p90 = 0.0
    else:
        spectrum = np.abs(np.fft.rfft(col_depth - col_depth.mean()))
        low_freq_energy = spectrum[1:8].sum() if spectrum.size > 8 else spectrum.sum()
        total_energy = spectrum[1:].sum() + 1e-9
        chirp_score = float(low_freq_energy / total_energy)
        target_depth_um = 299.792458 / (4.0 * 1.05 * np.sqrt(5.05))
        active_p90 = float(np.percentile(active_depth, 90))
        slow_wave_score = float(np.exp(-abs(active_p90 - target_depth_um) / 20.0))

    excessive_fill_penalty = max(0.0, metal_fill - 0.22) * 4.0
    sparse_penalty = max(0.0, 0.025 - metal_fill) * 8.0
    score = 2.0 * slow_wave_score + chirp_score - excessive_fill_penalty - sparse_penalty

    return {
        "proxy_score": float(score),
        "metal_fill_upper": float(metal_fill),
        "chirp_score": float(chirp_score),
        "slow_wave_score": float(slow_wave_score),
        "p90_active_stub_depth_um": active_p90,
    }
