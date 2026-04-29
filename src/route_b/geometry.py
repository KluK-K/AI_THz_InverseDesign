from __future__ import annotations

import numpy as np

from .config import RouteBConfig


def row_sets(cfg: RouteBConfig) -> dict[str, slice]:
    upper_load = slice(0, cfg.load_rows)
    upper_rail = slice(cfg.load_rows, cfg.load_rows + cfg.rail_rows)
    gap_start = upper_rail.stop
    gap = slice(gap_start, gap_start + cfg.gap_rows)
    lower_rail = slice(gap.stop, gap.stop + cfg.rail_rows)
    lower_load = slice(lower_rail.stop, cfg.ny)
    return {
        "upper_load": upper_load,
        "upper_rail": upper_rail,
        "gap": gap,
        "lower_rail": lower_rail,
        "lower_load": lower_load,
    }


def build_baseline_mask(cfg: RouteBConfig) -> np.ndarray:
    mask = np.zeros((cfg.ny, cfg.nx), dtype=np.uint8)
    rows = row_sets(cfg)
    mask[rows["upper_rail"], :] = 1
    mask[rows["lower_rail"], :] = 1
    return project_mask(mask, cfg)


def build_allowed_flip_mask(cfg: RouteBConfig) -> np.ndarray:
    allowed = np.zeros((cfg.ny, cfg.nx), dtype=bool)
    rows = row_sets(cfg)
    allowed[rows["upper_load"], :] = True
    if not cfg.mirror_top_bottom:
        allowed[rows["lower_load"], :] = True
    return allowed


def project_mask(mask: np.ndarray, cfg: RouteBConfig) -> np.ndarray:
    if mask.shape != (cfg.ny, cfg.nx):
        raise ValueError(f"mask shape {mask.shape} does not match {(cfg.ny, cfg.nx)}")

    out = (mask > 0).astype(np.uint8)
    rows = row_sets(cfg)

    out[rows["upper_rail"], :] = 1
    out[rows["lower_rail"], :] = 1
    out[rows["gap"], :] = 0

    if cfg.mirror_top_bottom:
        upper = out[rows["upper_load"], :]
        out[rows["lower_load"], :] = np.flipud(upper)

    return out


def seed_chirped_stub_mask(
    cfg: RouteBConfig,
    n_stubs: int = 7,
    depth_scale: float = 1.0,
    width_scale: float = 1.0,
    seed_offset: int = 0,
) -> np.ndarray:
    mask = build_baseline_mask(cfg)
    rows = row_sets(cfg)
    upper = rows["upper_load"]
    rng = np.random.default_rng(cfg.random_seed + n_stubs + 997 * seed_offset)

    margin_cols = max(4, round(0.08 * cfg.nx))
    centers = np.linspace(margin_cols, cfg.nx - margin_cols - 1, n_stubs)
    quarter_wave_um = 299.792458 / (4.0 * 1.05 * np.sqrt(5.05))
    base_len_cells = int(round(quarter_wave_um / cfg.grid_um))

    for idx, center in enumerate(centers):
        cx = int(round(center + rng.normal(0, 2.0)))
        width = max(1, int(round(float(rng.integers(1, 7)) * width_scale)))
        chirp = 0.82 + 0.36 * idx / max(1, n_stubs - 1)
        depth = int(np.clip(round(base_len_cells * chirp * depth_scale), 4, cfg.load_rows - 1))
        x0 = max(0, cx - width // 2)
        x1 = min(cfg.nx, cx + width // 2 + 1)
        y0 = cfg.load_rows - depth
        y1 = cfg.load_rows
        mask[y0:y1, x0:x1] = 1

        if depth > 12 and width <= 3:
            branch_y = max(0, y0 + depth // 2)
            branch_len = int(rng.integers(2, 9))
            mask[branch_y : branch_y + 1, max(0, x0 - branch_len) : x0] = 1
            mask[branch_y : branch_y + 1, x1 : min(cfg.nx, x1 + branch_len)] = 1

    return project_mask(mask, cfg)


def summarize_mask(mask: np.ndarray, cfg: RouteBConfig) -> dict[str, float | int]:
    rows = row_sets(cfg)
    added_upper = int(mask[rows["upper_load"], :].sum())
    rail_cells = int(mask[rows["upper_rail"], :].sum() + mask[rows["lower_rail"], :].sum())
    return {
        "nx": cfg.nx,
        "ny": cfg.ny,
        "grid_um": cfg.grid_um,
        "added_upper_cells": added_upper,
        "rail_cells": rail_cells,
        "total_metal_cells": int(mask.sum()),
        "estimated_added_area_um2": added_upper * 2 * cfg.grid_um * cfg.grid_um,
    }
