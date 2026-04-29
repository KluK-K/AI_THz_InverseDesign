from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_fast_rows() -> dict[str, dict[str, str]]:
    path = ROOT / "results" / "benchmark" / "benchmark_table.csv"
    rows = {}
    if not path.exists():
        return rows
    with path.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            rows[row["design"]] = row
    return rows


def main() -> None:
    fast = load_fast_rows()
    mapping = {
        "Straight CPS": "B0_straight_cps",
        "Traditional stepped/Bessel CPS": "B1_traditional_stepped_bessel_cps",
        "7-stub seed": "B2_7_stub_seed",
        "11-stub sweep best": "B3_11_stub_sweep_best",
    }
    out_dir = ROOT / "results" / "full_wave_comparison"
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for design, candidate in mapping.items():
        f = fast.get(design, {})
        comsol_metrics_path = ROOT / "results" / "comsol_runs" / candidate / f"{candidate}_comsol_metrics.json"
        if comsol_metrics_path.exists():
            c = json.loads(comsol_metrics_path.read_text(encoding="utf-8"))
        else:
            c = {}
        rows.append(
            {
                "Design": candidate,
                "Fast f3dB": f.get("f3db_thz", ""),
                "COMSOL f3dB": c.get("f3db_thz", "pending"),
                "Fast stop avg": f.get("stop_avg_s21_db", ""),
                "COMSOL stop avg": c.get("stop_avg_s21_db", "pending"),
                "Passband S11": c.get("pass_avg_s11_db", "pending"),
                "Recovery": c.get("recovery_peak_db", "pending"),
                "Mechanism diagnosis": c.get("mechanism_diagnosis", "pending"),
            }
        )

    csv_path = out_dir / "fast_vs_full_wave_table.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    md = [
        "# Fast vs Full-Wave Validation Table",
        "",
        "| Design | Fast f3dB | COMSOL f3dB | Fast stop avg | COMSOL stop avg | Passband S11 | Recovery | Mechanism diagnosis |",
        "|---|---:|---:|---:|---:|---:|---:|---|",
    ]
    for row in rows:
        md.append(
            "| {Design} | {Fast f3dB} | {COMSOL f3dB} | {Fast stop avg} | {COMSOL stop avg} | {Passband S11} | {Recovery} | {Mechanism diagnosis} |".format(
                **row
            )
        )
    md_path = out_dir / "fast_vs_full_wave_table.md"
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote {md_path}")


if __name__ == "__main__":
    main()

