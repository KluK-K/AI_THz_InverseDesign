from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .config import RouteBConfig
from .fabrication import connected_loading_masks
from .geometry import project_mask, row_sets
from .metrics import LowPassMetrics, db20, evaluate_lowpass_metrics


@dataclass(frozen=True)
class ABCDModelParams:
    eps_eff_main: float = 5.45
    eps_eff_stub: float = 5.05
    z_high_ohm: float = 201.0
    z_min_ohm: float = 52.0
    z_stub_base_ohm: float = 145.0
    z_stub_min_ohm: float = 42.0
    main_loss_np_per_m_at_1thz: float = 85.0
    stub_loss_np_per_m_at_1thz: float = 38.0
    stub_pair_scale: float = 0.012
    floating_cap_fF_per_cell: float = 0.0007
    pad_loading_power: float = 0.55
    end_cap_um: float = 0.5
    max_tan_abs: float = 12.0


@dataclass(frozen=True)
class ABCDResponse:
    freq_thz: np.ndarray
    s11: np.ndarray
    s21: np.ndarray
    metrics: LowPassMetrics
    profile: dict[str, np.ndarray]

    @property
    def s11_db(self) -> np.ndarray:
        return db20(self.s11)

    @property
    def s21_db(self) -> np.ndarray:
        return db20(self.s21)


def default_frequency_grid() -> np.ndarray:
    return np.linspace(0.05, 2.0, 241)


def extract_loading_profile(mask: np.ndarray, cfg: RouteBConfig) -> dict[str, np.ndarray]:
    mask = project_mask(mask, cfg)
    rows = row_sets(cfg)
    upper = mask[rows["upper_load"], :]

    depth_cells = np.zeros(cfg.nx, dtype=float)
    near_rail_cells = np.zeros(cfg.nx, dtype=float)
    total_cells = upper.sum(axis=0).astype(float)
    connected = connected_loading_masks(mask, cfg)
    upper_connected = connected["upper_connected"]
    upper_floating = connected["upper_floating"]
    connected_cells = upper_connected.sum(axis=0).astype(float)
    floating_cells = upper_floating.sum(axis=0).astype(float)

    for col in range(cfg.nx):
        occupied = np.flatnonzero(upper_connected[:, col] > 0)
        if occupied.size == 0:
            continue
        depth_cells[col] = cfg.load_rows - occupied[0]
        near_rail_cells[col] = cfg.load_rows - occupied[-1]

    depth_um = depth_cells * cfg.grid_um
    total_loading_um = total_cells * cfg.grid_um
    near_rail_um = near_rail_cells * cfg.grid_um

    return {
        "stub_depth_um": depth_um,
        "total_loading_um": total_loading_um,
        "connected_loading_um": connected_cells * cfg.grid_um,
        "floating_loading_um": floating_cells * cfg.grid_um,
        "near_rail_um": near_rail_um,
        "fill_per_column": connected_cells / max(1, cfg.load_rows),
        "floating_cells_per_column": floating_cells,
    }


def _transmission_line_abcd(gamma_l: complex, z0: float) -> tuple[complex, complex, complex, complex]:
    ch = np.cosh(gamma_l)
    sh = np.sinh(gamma_l)
    return ch, z0 * sh, sh / z0, ch


def _matmul2(
    left: tuple[complex, complex, complex, complex],
    right: tuple[complex, complex, complex, complex],
) -> tuple[complex, complex, complex, complex]:
    a1, b1, c1, d1 = left
    a2, b2, c2, d2 = right
    return (
        a1 * a2 + b1 * c2,
        a1 * b2 + b1 * d2,
        c1 * a2 + d1 * c2,
        c1 * b2 + d1 * d2,
    )


def _shunt_abcd(y: complex) -> tuple[complex, complex, complex, complex]:
    return 1.0 + 0.0j, 0.0 + 0.0j, y, 1.0 + 0.0j


def _abcd_to_s(
    abcd: tuple[complex, complex, complex, complex],
    z_ref: float,
) -> tuple[complex, complex]:
    a, b, c, d = abcd
    den = a + b / z_ref + c * z_ref + d
    s11 = (a + b / z_ref - c * z_ref - d) / den
    s21 = 2.0 / den
    return s11, s21


def evaluate_abcd(
    mask: np.ndarray,
    cfg: RouteBConfig,
    freq_thz: np.ndarray | None = None,
    params: ABCDModelParams | None = None,
) -> ABCDResponse:
    if freq_thz is None:
        freq_thz = default_frequency_grid()
    if params is None:
        params = ABCDModelParams()

    mask = project_mask(mask, cfg)
    freq_thz = np.asarray(freq_thz, dtype=float)
    profile = extract_loading_profile(mask, cfg)

    dx_m = cfg.grid_um * 1e-6
    c0 = 299_792_458.0
    z_ref = params.z_high_ohm
    s11 = np.zeros(freq_thz.size, dtype=complex)
    s21 = np.zeros(freq_thz.size, dtype=complex)

    stub_depth_um = profile["stub_depth_um"]
    fill = profile["fill_per_column"]
    near_rail_um = profile["near_rail_um"]
    floating_cells = profile["floating_cells_per_column"]

    loading_factor = np.clip((near_rail_um / max(cfg.load_depth_each_side_um, cfg.grid_um)) ** params.pad_loading_power, 0.0, 1.0)
    z_main_cols = params.z_high_ohm - (params.z_high_ohm - params.z_min_ohm) * loading_factor

    for fi, f_thz in enumerate(freq_thz):
        f_hz = f_thz * 1e12
        omega = 2.0 * np.pi * f_hz
        beta_main = omega * np.sqrt(params.eps_eff_main) / c0
        beta_stub = omega * np.sqrt(params.eps_eff_stub) / c0
        alpha_main = params.main_loss_np_per_m_at_1thz * np.sqrt(max(f_thz, 1e-6))
        alpha_stub = params.stub_loss_np_per_m_at_1thz * np.sqrt(max(f_thz, 1e-6))

        total = (1.0 + 0.0j, 0.0 + 0.0j, 0.0 + 0.0j, 1.0 + 0.0j)

        for col in range(cfg.nx):
            z_main = float(z_main_cols[col])
            gamma_l = (alpha_main + 1j * beta_main) * dx_m
            total = _matmul2(total, _transmission_line_abcd(gamma_l, z_main))

            depth_um = float(stub_depth_um[col])
            if depth_um <= 0.0:
                floating_c_f = float(floating_cells[col]) * params.floating_cap_fF_per_cell * 1e-15
                if floating_c_f > 0.0:
                    total = _matmul2(total, _shunt_abcd(1j * omega * floating_c_f))
                continue

            width_factor = max(1.0, float(fill[col] * cfg.load_rows))
            z_stub = max(params.z_stub_min_ohm, params.z_stub_base_ohm / (width_factor ** 0.35))
            l_eff_m = (depth_um + params.end_cap_um) * 1e-6
            tan_arg = np.tan((beta_stub - 1j * alpha_stub) * l_eff_m)
            tan_arg = complex(
                np.clip(tan_arg.real, -params.max_tan_abs, params.max_tan_abs),
                np.clip(tan_arg.imag, -params.max_tan_abs, params.max_tan_abs),
            )
            y_stub = params.stub_pair_scale * 1j * tan_arg / z_stub
            floating_c_f = float(floating_cells[col]) * params.floating_cap_fF_per_cell * 1e-15
            if floating_c_f > 0.0:
                y_stub += 1j * omega * floating_c_f
            total = _matmul2(total, _shunt_abcd(y_stub))

        s11[fi], s21[fi] = _abcd_to_s(total, z_ref)

    metrics = evaluate_lowpass_metrics(freq_thz, s11, s21, cfg)
    return ABCDResponse(freq_thz=freq_thz, s11=s11, s21=s21, metrics=metrics, profile=profile)
