from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from route_b.config import load_config
from route_b.geometry import row_sets


def greedy_rectangles(binary: np.ndarray) -> list[tuple[int, int, int, int]]:
    """Return rectangles as inclusive-exclusive row/column spans."""
    work = binary.astype(bool).copy()
    ny, nx = work.shape
    rects: list[tuple[int, int, int, int]] = []

    for r in range(ny):
        for c in range(nx):
            if not work[r, c]:
                continue

            c1 = c
            while c1 < nx and work[r, c1]:
                c1 += 1

            r1 = r + 1
            while r1 < ny and np.all(work[r1, c:c1]):
                r1 += 1

            work[r:r1, c:c1] = False
            rects.append((r, r1, c, c1))

    return rects


def rect_to_um(rect: tuple[int, int, int, int], cfg, layer: str) -> dict[str, float | str]:
    r0, r1, c0, c1 = rect
    grid = cfg.grid_um
    total_y_um = cfg.ny * grid
    y_top = total_y_um / 2.0

    x0 = cfg.left_feed_length_um + c0 * grid
    x1 = cfg.left_feed_length_um + c1 * grid
    y0 = y_top - r1 * grid
    y1 = y_top - r0 * grid
    return {
        "layer": layer,
        "x_um": float(x0),
        "y_um": float(y0),
        "w_um": float(x1 - x0),
        "h_um": float(y1 - y0),
    }


def load_mask(path: Path) -> np.ndarray:
    return np.loadtxt(path, delimiter=",", dtype=np.uint8)


def export_one(mask_path: Path, out_dir: Path, cfg) -> dict[str, object]:
    mask = load_mask(mask_path)
    if mask.shape != (cfg.ny, cfg.nx):
        raise ValueError(f"{mask_path} has shape {mask.shape}, expected {(cfg.ny, cfg.nx)}")

    rows = row_sets(cfg)
    design_rects = [rect_to_um(rect, cfg, "design") for rect in greedy_rectangles(mask > 0)]

    # Feed rails are kept separate and identical for all candidates.
    y_top = cfg.ny * cfg.grid_um / 2.0
    upper_rail_y0 = y_top - rows["upper_rail"].stop * cfg.grid_um
    lower_rail_y0 = y_top - rows["lower_rail"].stop * cfg.grid_um
    rail_h = cfg.au_width_um
    total_len = cfg.left_feed_length_um + cfg.design_length_um + cfg.right_feed_length_um
    feed_rects = [
        {"layer": "feed", "x_um": 0.0, "y_um": float(upper_rail_y0), "w_um": float(cfg.left_feed_length_um), "h_um": rail_h},
        {"layer": "feed", "x_um": 0.0, "y_um": float(lower_rail_y0), "w_um": float(cfg.left_feed_length_um), "h_um": rail_h},
        {
            "layer": "feed",
            "x_um": float(cfg.left_feed_length_um + cfg.design_length_um),
            "y_um": float(upper_rail_y0),
            "w_um": float(cfg.right_feed_length_um),
            "h_um": rail_h,
        },
        {
            "layer": "feed",
            "x_um": float(cfg.left_feed_length_um + cfg.design_length_um),
            "y_um": float(lower_rail_y0),
            "w_um": float(cfg.right_feed_length_um),
            "h_um": rail_h,
        },
    ]

    candidate = mask_path.stem
    rect_path = out_dir / f"{candidate}_rectangles.csv"
    with rect_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["layer", "x_um", "y_um", "w_um", "h_um"])
        writer.writeheader()
        writer.writerows(feed_rects + design_rects)

    meta = {
        "candidate": candidate,
        "mask_csv": str(mask_path),
        "rectangles_csv": str(rect_path),
        "feed_rectangles": len(feed_rects),
        "design_rectangles": len(design_rects),
        "total_rectangles": len(feed_rects) + len(design_rects),
        "geometry_um": {
            "total_length": total_len,
            "total_width": cfg.ny * cfg.grid_um,
            "au_thickness": cfg.au_thickness_um,
            "grid": cfg.grid_um,
            "design_x0": cfg.left_feed_length_um,
            "design_x1": cfg.left_feed_length_um + cfg.design_length_um,
        },
    }
    meta_path = out_dir / f"{candidate}_rectangles_meta.json"
    meta_path.write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return meta


def main() -> None:
    parser = argparse.ArgumentParser(description="Export mask rectangles for locked COMSOL template.")
    parser.add_argument("--config", default=str(ROOT / "configs" / "default_route_b.json"))
    parser.add_argument("--queue-dir", default=str(ROOT / "results" / "comsol_validation_queue"))
    parser.add_argument("--out-dir", default=str(ROOT / "results" / "comsol_rectangles"))
    parser.add_argument("masks", nargs="*", help="Optional explicit mask CSV files. Defaults to validation queue B*.csv.")
    args = parser.parse_args()

    cfg = load_config(args.config)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.masks:
        masks = [Path(p) for p in args.masks]
    else:
        masks = sorted(Path(args.queue_dir).glob("B*.csv"))

    metas = [export_one(path, out_dir, cfg) for path in masks]
    manifest_path = out_dir / "rectangles_manifest.json"
    manifest_path.write_text(json.dumps({"entries": metas}, indent=2), encoding="utf-8")

    print("COMSOL rectangle export complete.")
    for meta in metas:
        print(f"  {meta['candidate']}: {meta['total_rectangles']} rectangles")
    print(f"  wrote: {manifest_path}")


if __name__ == "__main__":
    main()

