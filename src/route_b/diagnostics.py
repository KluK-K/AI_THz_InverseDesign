from __future__ import annotations

import numpy as np

from .config import RouteBConfig
from .metrics import band_mask, db10_power


def energy_loss_estimate(s11: np.ndarray, s21: np.ndarray) -> np.ndarray:
    reflected = np.abs(s11) ** 2
    transmitted = np.abs(s21) ** 2
    return np.maximum(0.0, 1.0 - reflected - transmitted)


def mechanism_diagnostics(freq_thz: np.ndarray, s11: np.ndarray, s21: np.ndarray, cfg: RouteBConfig) -> dict[str, float]:
    freq_thz = np.asarray(freq_thz, dtype=float)
    loss = energy_loss_estimate(s11, s21)
    reflected = np.abs(s11) ** 2
    transmitted = np.abs(s21) ** 2

    pass_sel = band_mask(freq_thz, cfg.passband_thz)
    stop_sel = band_mask(freq_thz, cfg.stopband_thz)
    cutoff_sel = band_mask(freq_thz, (cfg.cutoff_thz - 0.05, cfg.cutoff_thz + 0.05))

    def mean_or_zero(values: np.ndarray, selector: np.ndarray) -> float:
        return float(np.mean(values[selector])) if np.any(selector) else 0.0

    return {
        "pass_reflected_power_avg": mean_or_zero(reflected, pass_sel),
        "pass_transmitted_power_avg": mean_or_zero(transmitted, pass_sel),
        "pass_loss_power_avg": mean_or_zero(loss, pass_sel),
        "cutoff_reflected_power_avg": mean_or_zero(reflected, cutoff_sel),
        "cutoff_transmitted_power_avg": mean_or_zero(transmitted, cutoff_sel),
        "cutoff_loss_power_avg": mean_or_zero(loss, cutoff_sel),
        "stop_reflected_power_avg": mean_or_zero(reflected, stop_sel),
        "stop_transmitted_power_avg": mean_or_zero(transmitted, stop_sel),
        "stop_loss_power_avg": mean_or_zero(loss, stop_sel),
        "stop_loss_db_avg": mean_or_zero(db10_power(loss), stop_sel),
    }

