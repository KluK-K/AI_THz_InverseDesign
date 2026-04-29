from __future__ import annotations

import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from route_b.config import load_config
from route_b.fabrication import check_fabrication
from route_b.fast_abcd import evaluate_abcd
from route_b.grammar import make_hybrid_stub_island_design, render_grammar_design


def main() -> None:
    cfg = load_config(ROOT / "configs" / "default_route_b.json")
    out_dir = ROOT / "results" / "hybrid_island_sweep"
    out_dir.mkdir(parents=True, exist_ok=True)

    freq = np.linspace(0.05, 2.0, 121)
    rows = []
    best = None
    best_mask = None
    idx = 0

    for stride in [2, 3, 4]:
        for length_um in [1.0, 2.0, 3.0]:
            for height_um in [0.5, 1.0]:
                for y_factor in [0.62, 0.72, 0.82]:
                    idx += 1
                    design = make_hybrid_stub_island_design(
                        cfg,
                        island_stride=stride,
                        island_length_um=length_um,
                        island_height_um=height_um,
                        y_factor=y_factor,
                    )
                    mask = render_grammar_design(cfg, design)
                    fab = check_fabrication(mask, cfg, allow_floating_islands=True)
                    response = evaluate_abcd(mask, cfg, freq_thz=freq)
                    m = response.metrics
                    row = {
                        "candidate": f"HYB_{idx:04d}",
                        "stride": stride,
                        "length_um": length_um,
                        "height_um": height_um,
                        "y_factor": y_factor,
                        "island_count": len(design.islands),
                        "fabrication_valid": fab.is_valid,
                        **m.to_dict(),
                    }
                    rows.append(row)

                    cutoff_ok = 0.76 <= m.f3db_thz <= 0.84
                    pass_ok = m.pass_avg_s21_db > -0.8 and m.pass_ripple_db < 1.5
                    if fab.is_valid and cutoff_ok and pass_ok and (best is None or m.score > best["score"]):
                        best = row
                        best_mask = mask

    csv_path = out_dir / "hybrid_island_sweep_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    if best is not None and best_mask is not None:
        np.savetxt(out_dir / "best_hybrid_island_mask.csv", best_mask, fmt="%d", delimiter=",")
        (out_dir / "best_hybrid_island_summary.json").write_text(json.dumps(best, indent=2), encoding="utf-8")

    print("Hybrid island sweep complete.")
    print(f"  candidates: {len(rows)}")
    if best is None:
        print("  best:       no candidate passed cutoff/passband gates")
    else:
        print(f"  best:       {best['candidate']}")
        print(f"  f3dB:       {best['f3db_thz']:.4f} THz")
        print(f"  pass S21:   {best['pass_avg_s21_db']:.3f} dB")
        print(f"  ripple:     {best['pass_ripple_db']:.3f} dB")
        print(f"  stop avg:   {best['stop_avg_s21_db']:.3f} dB")
        print(f"  score:      {best['score']:.4f}")
    print(f"  wrote:      {csv_path}")


if __name__ == "__main__":
    main()

