from __future__ import annotations

from collections import deque
from dataclasses import dataclass, asdict

import numpy as np

from .config import RouteBConfig
from .geometry import row_sets


@dataclass(frozen=True)
class FabricationReport:
    is_valid: bool
    gap_violations: int
    upper_rail_missing_cells: int
    lower_rail_missing_cells: int
    mirror_mismatch_cells: int
    disconnected_upper_loading_cells: int
    disconnected_lower_loading_cells: int
    floating_islands_allowed: bool
    min_feature_um: float
    notes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _reachable_from_seed(region: np.ndarray, seed_rows: list[int]) -> np.ndarray:
    reachable = np.zeros_like(region, dtype=bool)
    q: deque[tuple[int, int]] = deque()
    ny, nx = region.shape

    for row in seed_rows:
        if row < 0 or row >= ny:
            continue
        cols = np.flatnonzero(region[row, :])
        for col in cols:
            reachable[row, col] = True
            q.append((row, int(col)))

    while q:
        r, c = q.popleft()
        for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if rr < 0 or rr >= ny or cc < 0 or cc >= nx:
                continue
            if region[rr, cc] and not reachable[rr, cc]:
                reachable[rr, cc] = True
                q.append((rr, cc))
    return reachable


def connected_loading_masks(mask: np.ndarray, cfg: RouteBConfig) -> dict[str, np.ndarray]:
    if mask.shape != (cfg.ny, cfg.nx):
        raise ValueError(f"mask shape {mask.shape} does not match {(cfg.ny, cfg.nx)}")

    rows = row_sets(cfg)
    binary = mask > 0

    upper_load = binary[rows["upper_load"], :]
    upper_region = binary[: rows["upper_rail"].stop, :]
    upper_reachable = _reachable_from_seed(upper_region, [rows["upper_rail"].start])
    upper_connected = np.logical_and(upper_load, upper_reachable[: cfg.load_rows, :])
    upper_floating = np.logical_and(upper_load, ~upper_connected)

    lower_region = binary[rows["lower_rail"].start :, :]
    lower_reachable = _reachable_from_seed(lower_region, [0])
    lower_load_local = lower_region[cfg.rail_rows :, :]
    lower_connected = np.logical_and(lower_load_local, lower_reachable[cfg.rail_rows :, :])
    lower_floating = np.logical_and(lower_load_local, ~lower_connected)

    return {
        "upper_connected": upper_connected,
        "upper_floating": upper_floating,
        "lower_connected": lower_connected,
        "lower_floating": lower_floating,
    }


def check_fabrication(mask: np.ndarray, cfg: RouteBConfig, allow_floating_islands: bool = False) -> FabricationReport:
    if mask.shape != (cfg.ny, cfg.nx):
        raise ValueError(f"mask shape {mask.shape} does not match {(cfg.ny, cfg.nx)}")

    rows = row_sets(cfg)
    binary = mask > 0
    notes: list[str] = []

    gap_violations = int(binary[rows["gap"], :].sum())
    upper_rail_missing = int((~binary[rows["upper_rail"], :]).sum())
    lower_rail_missing = int((~binary[rows["lower_rail"], :]).sum())

    upper_load = binary[rows["upper_load"], :]
    lower_load = binary[rows["lower_load"], :]
    if cfg.mirror_top_bottom:
        mirror_mismatch = int(np.logical_xor(lower_load, np.flipud(upper_load)).sum())
    else:
        mirror_mismatch = 0

    connectivity = connected_loading_masks(mask, cfg)
    disconnected_upper = int(connectivity["upper_floating"].sum())
    disconnected_lower = int(connectivity["lower_floating"].sum())

    if gap_violations:
        notes.append("center gap contains metal")
    if upper_rail_missing or lower_rail_missing:
        notes.append("one or both CPS rails are not continuous")
    if mirror_mismatch:
        notes.append("top-bottom mirror symmetry is broken")
    if (disconnected_upper or disconnected_lower) and allow_floating_islands:
        notes.append("floating capacitive islands are present and explicitly allowed")
    elif disconnected_upper or disconnected_lower:
        notes.append("some loading metal is disconnected from the CPS rails")
    if not notes:
        notes.append("all stage-2 fabrication checks passed")

    valid = not (
        gap_violations
        or upper_rail_missing
        or lower_rail_missing
        or mirror_mismatch
        or ((disconnected_upper or disconnected_lower) and not allow_floating_islands)
    )

    return FabricationReport(
        is_valid=bool(valid),
        gap_violations=gap_violations,
        upper_rail_missing_cells=upper_rail_missing,
        lower_rail_missing_cells=lower_rail_missing,
        mirror_mismatch_cells=mirror_mismatch,
        disconnected_upper_loading_cells=disconnected_upper,
        disconnected_lower_loading_cells=disconnected_lower,
        floating_islands_allowed=allow_floating_islands,
        min_feature_um=cfg.min_feature_um,
        notes=tuple(notes),
    )
