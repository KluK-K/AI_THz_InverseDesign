from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from route_b.analog import analog_summary
from route_b.config import load_config
from route_b.fabrication import check_fabrication
from route_b.fast_abcd import evaluate_abcd
from route_b.geometry import seed_chirped_stub_mask, summarize_mask


def main() -> None:
    cfg = load_config(ROOT / "configs" / "default_route_b.json")
    out_dir = ROOT / "results" / "seed_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)

    freq = np.linspace(0.05, 2.0, 121)
    n_options = [5, 7, 9, 11]
    depth_scales = [0.88, 0.96, 1.04, 1.12]
    width_scales = [0.75, 1.00, 1.25]
    seed_offsets = [0, 1]

    rows = []
    best = None
    best_payload = None
    candidate_idx = 0

    for n_stubs in n_options:
        for depth_scale in depth_scales:
            for width_scale in width_scales:
                for seed_offset in seed_offsets:
                    candidate_idx += 1
                    mask = seed_chirped_stub_mask(
                        cfg,
                        n_stubs=n_stubs,
                        depth_scale=depth_scale,
                        width_scale=width_scale,
                        seed_offset=seed_offset,
                    )
                    fab = check_fabrication(mask, cfg)
                    response = evaluate_abcd(mask, cfg, freq_thz=freq)
                    metrics = response.metrics
                    row = {
                        "candidate": f"SWEEP_{candidate_idx:04d}",
                        "n_stubs": n_stubs,
                        "depth_scale": depth_scale,
                        "width_scale": width_scale,
                        "seed_offset": seed_offset,
                        "fabrication_valid": fab.is_valid,
                        **metrics.to_dict(),
                    }
                    rows.append(row)
                    if fab.is_valid and (best is None or metrics.score > best.metrics.score):
                        best = response
                        best_payload = {
                            "row": row,
                            "mask": mask,
                            "fabrication": fab.to_dict(),
                            "analog": analog_summary(mask, cfg),
                            "geometry": summarize_mask(mask, cfg),
                        }

    csv_path = out_dir / "seed_sweep_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    if best_payload is None:
        raise RuntimeError("seed sweep produced no valid candidates")

    np.savetxt(out_dir / "best_seed_sweep_mask.csv", best_payload["mask"], fmt="%d", delimiter=",")
    payload_for_json = {k: v for k, v in best_payload.items() if k != "mask"}
    (out_dir / "best_seed_sweep_summary.json").write_text(
        json.dumps(payload_for_json, indent=2),
        encoding="utf-8",
    )

    row = best_payload["row"]
    print("Seed-family sweep complete.")
    print(f"  candidates:        {len(rows)}")
    print(f"  best:              {row['candidate']}")
    print(f"  n_stubs:           {row['n_stubs']}")
    print(f"  depth_scale:       {row['depth_scale']}")
    print(f"  width_scale:       {row['width_scale']}")
    print(f"  f3dB:              {row['f3db_thz']:.4f} THz")
    print(f"  pass avg S21:      {row['pass_avg_s21_db']:.3f} dB")
    print(f"  stop avg S21:      {row['stop_avg_s21_db']:.3f} dB")
    print(f"  score:             {row['score']:.4f}")
    print(f"  wrote:             {csv_path}")


if __name__ == "__main__":
    main()

