from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from .config import RouteBConfig


EPS = 1e-15


@dataclass(frozen=True)
class LowPassMetrics:
    f3db_thz: float
    pass_avg_s21_db: float
    pass_min_s21_db: float
    pass_ripple_db: float
    pass_avg_s11_db: float
    edge_avg_s21_db: float
    stop_avg_s21_db: float
    stop_max_s21_db: float
    stop_coverage_below_10_db: float
    stop_coverage_below_20_db: float
    recovery_peak_db: float
    passband_notch_penalty_db: float
    monotonic_violation_db: float
    score: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


def db20(x: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.maximum(np.abs(x), EPS))


def db10_power(x: np.ndarray) -> np.ndarray:
    return 10.0 * np.log10(np.maximum(np.asarray(x, dtype=float), EPS))


def band_mask(freq_thz: np.ndarray, band: tuple[float, float]) -> np.ndarray:
    return (freq_thz >= band[0]) & (freq_thz <= band[1])


def find_f3db(freq_thz: np.ndarray, s21_db: np.ndarray, target_db: float = -3.0) -> float:
    below = np.flatnonzero(s21_db <= target_db)
    if below.size == 0:
        return float(freq_thz[-1])
    idx = int(below[0])
    if idx == 0:
        return float(freq_thz[0])

    f0, f1 = float(freq_thz[idx - 1]), float(freq_thz[idx])
    y0, y1 = float(s21_db[idx - 1]), float(s21_db[idx])
    if abs(y1 - y0) < 1e-12:
        return f1
    frac = (target_db - y0) / (y1 - y0)
    return f0 + frac * (f1 - f0)


def evaluate_lowpass_metrics(
    freq_thz: np.ndarray,
    s11: np.ndarray,
    s21: np.ndarray,
    cfg: RouteBConfig,
) -> LowPassMetrics:
    freq_thz = np.asarray(freq_thz, dtype=float)
    s11_db = db20(s11)
    s21_db = db20(s21)

    pass_sel = band_mask(freq_thz, cfg.passband_thz)
    stop_sel = band_mask(freq_thz, cfg.stopband_thz)
    edge_sel = band_mask(freq_thz, (cfg.cutoff_thz, min(cfg.stopband_thz[0], cfg.cutoff_thz + 0.25)))

    if not np.any(pass_sel) or not np.any(stop_sel):
        raise ValueError("frequency grid must include passband and stopband samples")

    pass_vals = s21_db[pass_sel]
    stop_vals = s21_db[stop_sel]
    edge_vals = s21_db[edge_sel] if np.any(edge_sel) else s21_db[stop_sel]
    pass_s11_vals = s11_db[pass_sel]

    f3db = find_f3db(freq_thz, s21_db)
    pass_avg = float(np.mean(pass_vals))
    pass_min = float(np.min(pass_vals))
    pass_ripple = float(np.max(pass_vals) - np.min(pass_vals))
    pass_s11_avg = float(np.mean(pass_s11_vals))
    edge_avg = float(np.mean(edge_vals))
    stop_avg = float(np.mean(stop_vals))
    stop_max = float(np.max(stop_vals))
    stop_coverage_10 = float(np.mean(stop_vals <= -10.0))
    stop_coverage_20 = float(np.mean(stop_vals <= -20.0))
    recovery_peak = stop_max

    post_cutoff = freq_thz >= cfg.cutoff_thz
    if np.sum(post_cutoff) > 2:
        post_vals = s21_db[post_cutoff]
        local_recoveries = np.diff(post_vals)
        monotonic_violation = float(np.sum(np.maximum(local_recoveries, 0.0)))
    else:
        monotonic_violation = 0.0
    passband_notch_penalty = max(0.0, -3.0 - pass_min)

    cutoff_error = abs(f3db - cfg.cutoff_thz)
    cutoff_reward = -cutoff_error / 0.04
    pass_reward = pass_avg
    pass_floor_penalty = max(0.0, -1.0 - pass_min) * 1.5
    ripple_penalty = max(0.0, pass_ripple - 0.8) * 1.2
    stop_reward = min(0.0, stop_avg + 24.0) * 0.12 - max(0.0, stop_max + 12.0) * 0.10
    edge_reward = min(0.0, edge_avg + 8.0) * 0.10
    reflection_penalty = max(0.0, pass_s11_avg + 10.0) * 0.10
    coverage_reward = 1.2 * stop_coverage_20 + 0.4 * stop_coverage_10
    recovery_penalty = max(0.0, recovery_peak + 10.0) * 0.20

    score = (
        1.8 * cutoff_reward
        + 1.5 * pass_reward
        + 1.2 * stop_reward
        + 0.8 * edge_reward
        + coverage_reward
        - pass_floor_penalty
        - ripple_penalty
        - reflection_penalty
        - recovery_penalty
        - 1.0 * passband_notch_penalty
        - 0.4 * monotonic_violation
    )

    return LowPassMetrics(
        f3db_thz=float(f3db),
        pass_avg_s21_db=pass_avg,
        pass_min_s21_db=pass_min,
        pass_ripple_db=pass_ripple,
        pass_avg_s11_db=pass_s11_avg,
        edge_avg_s21_db=edge_avg,
        stop_avg_s21_db=stop_avg,
        stop_max_s21_db=stop_max,
        stop_coverage_below_10_db=stop_coverage_10,
        stop_coverage_below_20_db=stop_coverage_20,
        recovery_peak_db=recovery_peak,
        passband_notch_penalty_db=passband_notch_penalty,
        monotonic_violation_db=monotonic_violation,
        score=float(score),
    )
