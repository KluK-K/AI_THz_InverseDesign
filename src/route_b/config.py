from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path


@dataclass(frozen=True)
class RouteBConfig:
    cutoff_thz: float
    passband_thz: tuple[float, float]
    stopband_thz: tuple[float, float]
    grid_um: float
    design_length_um: float
    load_depth_each_side_um: float
    au_width_um: float
    gap_um: float
    au_thickness_um: float
    left_feed_length_um: float
    right_feed_length_um: float
    min_feature_um: float
    mirror_top_bottom: bool
    random_seed: int

    @property
    def nx(self) -> int:
        return round(self.design_length_um / self.grid_um)

    @property
    def load_rows(self) -> int:
        return round(self.load_depth_each_side_um / self.grid_um)

    @property
    def rail_rows(self) -> int:
        return round(self.au_width_um / self.grid_um)

    @property
    def gap_rows(self) -> int:
        return round(self.gap_um / self.grid_um)

    @property
    def ny(self) -> int:
        return 2 * self.load_rows + 2 * self.rail_rows + self.gap_rows


def load_config(path: str | Path) -> RouteBConfig:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    geom = raw["geometry_um"]
    target = raw["target"]
    constraints = raw["constraints"]
    optimizer = raw["optimizer"]
    return RouteBConfig(
        cutoff_thz=float(target["cutoff_thz"]),
        passband_thz=tuple(target["passband_thz"]),
        stopband_thz=tuple(target["stopband_thz"]),
        grid_um=float(geom["grid"]),
        design_length_um=float(geom["design_length"]),
        load_depth_each_side_um=float(geom["load_depth_each_side"]),
        au_width_um=float(geom["au_width"]),
        gap_um=float(geom["gap"]),
        au_thickness_um=float(geom["au_thickness"]),
        left_feed_length_um=float(geom["left_feed_length"]),
        right_feed_length_um=float(geom["right_feed_length"]),
        min_feature_um=float(constraints["minimum_feature_um"]),
        mirror_top_bottom=bool(constraints["mirror_top_bottom"]),
        random_seed=int(optimizer["random_seed"]),
    )
