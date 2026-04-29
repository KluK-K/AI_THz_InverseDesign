from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from .config import RouteBConfig
from .fast_abcd import extract_loading_profile


@dataclass(frozen=True)
class StubEquivalent:
    index: int
    center_um: float
    width_um: float
    depth_um: float
    estimated_quarter_wave_thz: float
    role: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def extract_stub_equivalents(mask: np.ndarray, cfg: RouteBConfig, eps_eff_stub: float = 5.05) -> list[StubEquivalent]:
    profile = extract_loading_profile(mask, cfg)
    depths = profile["stub_depth_um"]
    active = depths > 0
    stubs: list[StubEquivalent] = []
    c_um_per_ps = 299.792458

    idx = 0
    col = 0
    while col < cfg.nx:
        if not active[col]:
            col += 1
            continue
        start = col
        while col + 1 < cfg.nx and active[col + 1]:
            col += 1
        end = col

        local_depth = float(np.max(depths[start : end + 1]))
        width_um = (end - start + 1) * cfg.grid_um
        center_um = (0.5 * (start + end) + 0.5) * cfg.grid_um
        l_eff_um = max(local_depth + 0.5, cfg.grid_um)
        fq_thz = c_um_per_ps / (4.0 * l_eff_um * np.sqrt(eps_eff_stub))

        if fq_thz < cfg.cutoff_thz:
            role = "deep slow-wave / below-target resonance risk"
        elif fq_thz < cfg.cutoff_thz * 1.35:
            role = "target-edge cutoff stub"
        else:
            role = "high-frequency suppression / matching stub"

        idx += 1
        stubs.append(
            StubEquivalent(
                index=idx,
                center_um=float(center_um),
                width_um=float(width_um),
                depth_um=local_depth,
                estimated_quarter_wave_thz=float(fq_thz),
                role=role,
            )
        )
        col += 1

    return stubs


def analog_summary(mask: np.ndarray, cfg: RouteBConfig) -> dict[str, object]:
    stubs = extract_stub_equivalents(mask, cfg)
    if stubs:
        fq = np.array([s.estimated_quarter_wave_thz for s in stubs], dtype=float)
        depths = np.array([s.depth_um for s in stubs], dtype=float)
    else:
        fq = np.array([], dtype=float)
        depths = np.array([], dtype=float)

    return {
        "model": "main CPS line with cascaded weakly coupled open-stub shunt resonators",
        "meaning": "This is an analog interpretation of the binary mask, not a replacement for full-wave validation.",
        "stub_count": len(stubs),
        "stub_depth_um_min": float(depths.min()) if depths.size else 0.0,
        "stub_depth_um_max": float(depths.max()) if depths.size else 0.0,
        "quarter_wave_thz_min": float(fq.min()) if fq.size else 0.0,
        "quarter_wave_thz_max": float(fq.max()) if fq.size else 0.0,
        "stubs": [s.to_dict() for s in stubs],
    }

