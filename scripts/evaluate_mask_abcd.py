from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from route_b import build_baseline_mask, load_config
from route_b.analog import analog_summary
from route_b.diagnostics import energy_loss_estimate, mechanism_diagnostics
from route_b.fabrication import check_fabrication
from route_b.fast_abcd import default_frequency_grid, evaluate_abcd
from route_b.geometry import seed_chirped_stub_mask, summarize_mask


def load_mask(mask_arg: str, cfg):
    if mask_arg == "baseline":
        return build_baseline_mask(cfg), "baseline"
    if mask_arg == "seed":
        return seed_chirped_stub_mask(cfg, n_stubs=7), "seed"
    path = Path(mask_arg)
    return np.loadtxt(path, delimiter=",", dtype=np.uint8), path.stem


def write_sparams(path: Path, response) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["freq_thz", "s11_real", "s11_imag", "s21_real", "s21_imag", "s11_db", "s21_db", "loss_power_est"])
        loss = energy_loss_estimate(response.s11, response.s21)
        for f_thz, s11, s21, s11_db, s21_db, loss_power in zip(
            response.freq_thz,
            response.s11,
            response.s21,
            response.s11_db,
            response.s21_db,
            loss,
        ):
            writer.writerow([f_thz, s11.real, s11.imag, s21.real, s21.imag, s11_db, s21_db, loss_power])


def write_svg_plot(path: Path, response, label: str, cfg) -> None:
    width, height = 920, 640
    margin_l, margin_r = 74, 22
    top1, h_panel = 58, 220
    top2 = 365
    x0, x1 = margin_l, width - margin_r
    f_min, f_max = float(response.freq_thz[0]), float(response.freq_thz[-1])

    def xmap(f):
        return x0 + (float(f) - f_min) / (f_max - f_min) * (x1 - x0)

    def ymap(y, ymin, ymax, top):
        return top + (ymax - float(y)) / (ymax - ymin) * h_panel

    def polyline(xs, ys, ymin, ymax, top):
        pts = [f"{xmap(x):.2f},{ymap(y, ymin, ymax, top):.2f}" for x, y in zip(xs, ys)]
        return " ".join(pts)

    s21_ymin, s21_ymax = -45.0, 1.0
    s11_ymin, s11_ymax = -45.0, 1.0
    cutoff_x = xmap(cfg.cutoff_thz)
    s21_m3 = ymap(-3.0, s21_ymin, s21_ymax, top1)
    s11_m10 = ymap(-10.0, s11_ymin, s11_ymax, top2)

    s21_pts = polyline(response.freq_thz, np.clip(response.s21_db, s21_ymin, s21_ymax), s21_ymin, s21_ymax, top1)
    s11_pts = polyline(response.freq_thz, np.clip(response.s11_db, s11_ymin, s11_ymax), s11_ymin, s11_ymax, top2)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <text x="{margin_l}" y="30" font-family="Arial" font-size="20" fill="#222">ABCD/qTEM fast response: {label}</text>
  <text x="{margin_l}" y="{top1 - 12}" font-family="Arial" font-size="14" fill="#444">S21 (dB)</text>
  <rect x="{x0}" y="{top1}" width="{x1 - x0}" height="{h_panel}" fill="#fbfbfb" stroke="#cccccc"/>
  <line x1="{cutoff_x:.2f}" y1="{top1}" x2="{cutoff_x:.2f}" y2="{top1 + h_panel}" stroke="#2357a4" stroke-dasharray="5 4"/>
  <line x1="{x0}" y1="{s21_m3:.2f}" x2="{x1}" y2="{s21_m3:.2f}" stroke="#555" stroke-dasharray="5 4"/>
  <polyline points="{s21_pts}" fill="none" stroke="#ba2f3a" stroke-width="2"/>
  <text x="{x1 - 90}" y="{s21_m3 - 6:.2f}" font-family="Arial" font-size="12" fill="#555">-3 dB</text>
  <text x="{cutoff_x + 6:.2f}" y="{top1 + 18}" font-family="Arial" font-size="12" fill="#2357a4">0.8 THz</text>

  <text x="{margin_l}" y="{top2 - 12}" font-family="Arial" font-size="14" fill="#444">S11 (dB)</text>
  <rect x="{x0}" y="{top2}" width="{x1 - x0}" height="{h_panel}" fill="#fbfbfb" stroke="#cccccc"/>
  <line x1="{cutoff_x:.2f}" y1="{top2}" x2="{cutoff_x:.2f}" y2="{top2 + h_panel}" stroke="#2357a4" stroke-dasharray="5 4"/>
  <line x1="{x0}" y1="{s11_m10:.2f}" x2="{x1}" y2="{s11_m10:.2f}" stroke="#555" stroke-dasharray="5 4"/>
  <polyline points="{s11_pts}" fill="none" stroke="#335c67" stroke-width="2"/>
  <text x="{x1 - 98}" y="{s11_m10 - 6:.2f}" font-family="Arial" font-size="12" fill="#555">-10 dB</text>

  <text x="{x0}" y="{height - 25}" font-family="Arial" font-size="13" fill="#444">{f_min:.2f} THz</text>
  <text x="{(x0 + x1) / 2 - 50:.2f}" y="{height - 25}" font-family="Arial" font-size="13" fill="#444">Frequency (THz)</text>
  <text x="{x1 - 58}" y="{height - 25}" font-family="Arial" font-size="13" fill="#444">{f_max:.2f} THz</text>
</svg>
"""
    path.write_text(svg, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a Route B mask with the first ABCD/qTEM fast model.")
    parser.add_argument("mask", nargs="?", default="seed", help="'baseline', 'seed', or path to mask CSV")
    parser.add_argument("--config", default=str(ROOT / "configs" / "default_route_b.json"))
    parser.add_argument("--out-dir", default=str(ROOT / "results" / "abcd_eval"))
    parser.add_argument("--f-min", type=float, default=0.05)
    parser.add_argument("--f-max", type=float, default=2.0)
    parser.add_argument("--n-freq", type=int, default=241)
    args = parser.parse_args()

    cfg = load_config(args.config)
    mask, label = load_mask(args.mask, cfg)
    freq = np.linspace(args.f_min, args.f_max, args.n_freq)
    response = evaluate_abcd(mask, cfg, freq_thz=freq)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_label = label.replace("/", "_").replace(" ", "_")
    sparam_path = out_dir / f"{safe_label}_sparams_abcd.csv"
    metrics_path = out_dir / f"{safe_label}_metrics_abcd.json"
    profile_path = out_dir / f"{safe_label}_profile_abcd.json"
    analog_path = out_dir / f"{safe_label}_analog_equivalent.json"
    fab_path = out_dir / f"{safe_label}_fabrication_report.json"
    plot_path = out_dir / f"{safe_label}_response_abcd.svg"

    write_sparams(sparam_path, response)
    metrics_payload = {
        "label": label,
        "model": "stage2_abcd_qtem_open_stub",
        "meaning": "Fast surrogate for ranking binary CPS low-pass candidates before COMSOL.",
        "metrics": response.metrics.to_dict(),
        "mechanism_diagnostics": mechanism_diagnostics(response.freq_thz, response.s11, response.s21, cfg),
        "geometry_summary": summarize_mask(mask, cfg),
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")
    profile_payload = {
        "stub_depth_um": response.profile["stub_depth_um"].tolist(),
        "total_loading_um": response.profile["total_loading_um"].tolist(),
        "near_rail_um": response.profile["near_rail_um"].tolist(),
    }
    profile_path.write_text(json.dumps(profile_payload), encoding="utf-8")
    analog_path.write_text(json.dumps(analog_summary(mask, cfg), indent=2), encoding="utf-8")
    fab_report = check_fabrication(mask, cfg)
    fab_path.write_text(json.dumps(fab_report.to_dict(), indent=2), encoding="utf-8")
    write_svg_plot(plot_path, response, label, cfg)

    m = response.metrics
    print(f"ABCD evaluation complete: {label}")
    print(f"  f3dB:              {m.f3db_thz:.4f} THz")
    print(f"  pass avg S21:      {m.pass_avg_s21_db:.3f} dB")
    print(f"  pass ripple:       {m.pass_ripple_db:.3f} dB")
    print(f"  pass avg S11:      {m.pass_avg_s11_db:.3f} dB")
    print(f"  stop avg S21:      {m.stop_avg_s21_db:.3f} dB")
    print(f"  score:             {m.score:.4f}")
    print(f"  fabrication valid: {fab_report.is_valid}")
    print(f"  wrote:             {metrics_path}")
    print(f"  wrote:             {sparam_path}")
    print(f"  wrote:             {analog_path}")
    print(f"  wrote:             {fab_path}")
    print(f"  wrote:             {plot_path}")


if __name__ == "__main__":
    main()
