from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from .config import RouteBConfig
from .geometry import build_baseline_mask, project_mask, seed_chirped_stub_mask


@dataclass(frozen=True)
class StubSpec:
    center_um: float
    depth_um: float
    width_um: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class IslandSpec:
    center_um: float
    y_from_rail_um: float
    length_um: float
    height_um: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class GrammarDesign:
    name: str
    stubs: tuple[StubSpec, ...]
    islands: tuple[IslandSpec, ...] = ()
    taper_um: float = 18.0
    allow_floating_islands: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "name": self.name,
            "taper_um": self.taper_um,
            "allow_floating_islands": self.allow_floating_islands,
            "stubs": [s.to_dict() for s in self.stubs],
            "islands": [i.to_dict() for i in self.islands],
        }


def _to_col(x_um: float, cfg: RouteBConfig) -> int:
    return int(np.clip(round(x_um / cfg.grid_um), 0, cfg.nx - 1))


def _cells(value_um: float, cfg: RouteBConfig) -> int:
    return max(1, int(round(value_um / cfg.grid_um)))


def render_grammar_design(cfg: RouteBConfig, design: GrammarDesign) -> np.ndarray:
    mask = build_baseline_mask(cfg)

    for stub in design.stubs:
        cx = _to_col(stub.center_um, cfg)
        half_w = max(0, _cells(stub.width_um, cfg) // 2)
        depth = int(np.clip(_cells(stub.depth_um, cfg), 1, cfg.load_rows - 1))
        x0 = max(0, cx - half_w)
        x1 = min(cfg.nx, cx + half_w + 1)
        y0 = cfg.load_rows - depth
        y1 = cfg.load_rows
        mask[y0:y1, x0:x1] = 1

    for island in design.islands:
        cx = _to_col(island.center_um, cfg)
        half_l = max(0, _cells(island.length_um, cfg) // 2)
        h = _cells(island.height_um, cfg)
        gap_from_rail = max(1, _cells(island.y_from_rail_um, cfg))
        y1 = max(0, cfg.load_rows - gap_from_rail)
        y0 = max(0, y1 - h)
        x0 = max(0, cx - half_l)
        x1 = min(cfg.nx, cx + half_l + 1)
        if y1 > y0:
            mask[y0:y1, x0:x1] = 1

    return project_mask(mask, cfg)


def chirped_stub_specs(
    cfg: RouteBConfig,
    n_stubs: int = 11,
    depth_scale: float = 1.04,
    width_scale: float = 0.75,
    seed_offset: int = 1,
) -> tuple[StubSpec, ...]:
    rng = np.random.default_rng(cfg.random_seed + n_stubs + 997 * seed_offset)
    margin_cols = max(4, round(0.08 * cfg.nx))
    centers = np.linspace(margin_cols, cfg.nx - margin_cols - 1, n_stubs)
    quarter_wave_um = 299.792458 / (4.0 * 1.05 * np.sqrt(5.05))
    base_len_cells = int(round(quarter_wave_um / cfg.grid_um))

    stubs: list[StubSpec] = []
    for idx, center in enumerate(centers):
        cx = int(round(center + rng.normal(0, 2.0)))
        width_cells = max(1, int(round(float(rng.integers(1, 7)) * width_scale)))
        chirp = 0.82 + 0.36 * idx / max(1, n_stubs - 1)
        depth_cells = int(np.clip(round(base_len_cells * chirp * depth_scale), 4, cfg.load_rows - 1))
        stubs.append(
            StubSpec(
                center_um=(cx + 0.5) * cfg.grid_um,
                depth_um=depth_cells * cfg.grid_um,
                width_um=width_cells * cfg.grid_um,
            )
        )
    return tuple(stubs)


def make_hybrid_stub_island_design(
    cfg: RouteBConfig,
    island_stride: int = 2,
    island_length_um: float = 2.0,
    island_height_um: float = 0.5,
    y_factor: float = 0.70,
) -> GrammarDesign:
    stubs = chirped_stub_specs(cfg, n_stubs=11, depth_scale=1.04, width_scale=0.75, seed_offset=1)
    islands: list[IslandSpec] = []
    for idx, (left, right) in enumerate(zip(stubs[:-1], stubs[1:])):
        if island_stride > 1 and idx % island_stride != 0:
            continue
        center = 0.5 * (left.center_um + right.center_um)
        if center < 35.0 or center > cfg.design_length_um - 35.0:
            continue
        local_depth = 0.5 * (left.depth_um + right.depth_um)
        y_from_rail = min(max(local_depth * y_factor, 10.0), cfg.load_depth_each_side_um - 8.0)
        islands.append(
            IslandSpec(
                center_um=center,
                y_from_rail_um=y_from_rail,
                length_um=island_length_um,
                height_um=island_height_um,
            )
        )
    return GrammarDesign(name="hybrid_chirped_stub_island_v0", stubs=stubs, islands=tuple(islands))


def make_traditional_stepped_impedance_design(cfg: RouteBConfig) -> GrammarDesign:
    """Hand-synthesized stepped-impedance/Bessel-like CPS low-pass baseline.

    This is intentionally not AI optimized. It keeps the 3/3/3 CPS rails fixed
    and adds broad outer low-impedance pad sections, approximating the classic
    high-Z / low-Z stepped-impedance synthesis idea on the same fabrication grid.
    """
    centers_um = [55.0, 105.0, 150.0, 195.0, 245.0]
    lengths_um = [21.0, 16.0, 12.5, 16.0, 21.0]
    depths_um = [9.0, 14.0, 18.5, 14.0, 9.0]
    stubs = tuple(
        StubSpec(center_um=c, width_um=w, depth_um=d)
        for c, w, d in zip(centers_um, lengths_um, depths_um)
    )
    return GrammarDesign(
        name="traditional_stepped_impedance_bessel_like_cps",
        stubs=stubs,
        islands=(),
        taper_um=28.0,
        allow_floating_islands=False,
    )
