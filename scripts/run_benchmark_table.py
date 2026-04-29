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
from route_b.geometry import build_baseline_mask, seed_chirped_stub_mask
from route_b.diagnostics import mechanism_diagnostics
from route_b.grammar import make_hybrid_stub_island_design, make_traditional_stepped_impedance_design, render_grammar_design


def design_rows(cfg):
    yield "Straight CPS", build_baseline_mask(cfg), False, "B0 baseline with no outer loading"
    b1 = make_traditional_stepped_impedance_design(cfg)
    yield "Traditional stepped/Bessel CPS", render_grammar_design(cfg, b1), False, "B1 hand-synthesized stepped-impedance/Bessel-like analog baseline"
    yield "7-stub seed", seed_chirped_stub_mask(cfg, n_stubs=7), False, "Initial chirped-stub seed"

    sweep_path = ROOT / "results" / "seed_sweep" / "best_seed_sweep_mask.csv"
    if sweep_path.exists():
        yield "11-stub sweep best", np.loadtxt(sweep_path, delimiter=",", dtype=np.uint8), False, "Best seed-family sweep candidate"

    hybrid = make_hybrid_stub_island_design(cfg)
    yield "Hybrid stub-island grammar v0", render_grammar_design(cfg, hybrid), True, "Adds floating capacitive islands between chirped stubs"


def main() -> None:
    cfg = load_config(ROOT / "configs" / "default_route_b.json")
    freq = np.linspace(0.05, 2.0, 241)
    out_dir = ROOT / "results" / "benchmark"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for name, mask, allow_floating, note in design_rows(cfg):
        response = evaluate_abcd(mask, cfg, freq_thz=freq)
        fab = check_fabrication(mask, cfg, allow_floating_islands=allow_floating)
        analog = analog_summary(mask, cfg)
        diag = mechanism_diagnostics(response.freq_thz, response.s11, response.s21, cfg)
        row = {
            "design": name,
            "f3db_thz": response.metrics.f3db_thz,
            "pass_avg_s21_db": response.metrics.pass_avg_s21_db,
            "pass_ripple_db": response.metrics.pass_ripple_db,
            "pass_avg_s11_db": response.metrics.pass_avg_s11_db,
            "stop_avg_s21_db": response.metrics.stop_avg_s21_db,
            "stop_max_s21_db": response.metrics.stop_max_s21_db,
            "stop_coverage_below_10_db": response.metrics.stop_coverage_below_10_db,
            "stop_coverage_below_20_db": response.metrics.stop_coverage_below_20_db,
            "recovery_peak_db": response.metrics.recovery_peak_db,
            "monotonic_violation_db": response.metrics.monotonic_violation_db,
            "stop_reflected_power_avg": diag["stop_reflected_power_avg"],
            "stop_loss_power_avg": diag["stop_loss_power_avg"],
            "score": response.metrics.score,
            "fabrication_valid": fab.is_valid,
            "floating_allowed": allow_floating,
            "stub_count": analog["stub_count"],
            "note": note,
        }
        rows.append(row)
        safe = name.lower().replace(" ", "_").replace("/", "_")
        np.savetxt(out_dir / f"{safe}_mask.csv", mask, fmt="%d", delimiter=",")
        (out_dir / f"{safe}_fabrication.json").write_text(json.dumps(fab.to_dict(), indent=2), encoding="utf-8")
        (out_dir / f"{safe}_analog.json").write_text(json.dumps(analog, indent=2), encoding="utf-8")

    csv_path = out_dir / "benchmark_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md_lines = [
        "# Route B Benchmark Table",
        "",
        "| Design | f3dB THz | Pass S21 dB | Ripple dB | Pass S11 dB | Stop avg dB | Stop max dB | Stop refl P | Stop loss P | Coverage < -10 | Coverage < -20 | Score | Fab |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        md_lines.append(
            "| {design} | {f3db_thz:.4f} | {pass_avg_s21_db:.3f} | {pass_ripple_db:.3f} | "
            "{pass_avg_s11_db:.3f} | {stop_avg_s21_db:.3f} | {stop_max_s21_db:.3f} | "
            "{stop_reflected_power_avg:.2f} | {stop_loss_power_avg:.2f} | "
            "{stop_coverage_below_10_db:.2f} | {stop_coverage_below_20_db:.2f} | {score:.2f} | {fabrication_valid} |".format(**row)
        )
    md_path = out_dir / "benchmark_table.md"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print("Benchmark table complete.")
    print(f"  designs: {len(rows)}")
    print(f"  wrote:   {csv_path}")
    print(f"  wrote:   {md_path}")


if __name__ == "__main__":
    main()
