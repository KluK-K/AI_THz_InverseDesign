from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from route_b.config import load_config
from route_b.geometry import build_baseline_mask, seed_chirped_stub_mask
from route_b.grammar import make_traditional_stepped_impedance_design, render_grammar_design


def main() -> None:
    cfg = load_config(ROOT / "configs" / "default_route_b.json")
    out_dir = ROOT / "results" / "comsol_validation_queue"
    out_dir.mkdir(parents=True, exist_ok=True)

    entries = []

    designs = [
        ("B0_straight_cps", build_baseline_mask(cfg), "Truth baseline: straight 3/3/3 CPS."),
        (
            "B1_traditional_stepped_bessel_cps",
            render_grammar_design(cfg, make_traditional_stepped_impedance_design(cfg)),
            "Traditional analog baseline: hand-synthesized stepped-impedance/Bessel-like CPS on the same platform.",
        ),
        ("B2_7_stub_seed", seed_chirped_stub_mask(cfg, n_stubs=7), "Initial seed: f3dB near 0.8 THz in ABCD."),
    ]

    sweep_path = ROOT / "results" / "seed_sweep" / "best_seed_sweep_mask.csv"
    if sweep_path.exists():
        designs.append(
            (
                "B3_11_stub_sweep_best",
                np.loadtxt(sweep_path, delimiter=",", dtype=np.uint8),
                "Current best fast-model candidate: stronger stopband than 7-stub seed.",
            )
        )

    for name, mask, rationale in designs:
        mask_path = out_dir / f"{name}.csv"
        np.savetxt(mask_path, mask, fmt="%d", delimiter=",")
        entries.append(
            {
                "name": name,
                "mask_csv": str(mask_path),
                "rationale": rationale,
                "comsol_status": "pending",
                "validation_question": "Does full-wave S21/S11 preserve the fast-model ranking?",
            }
        )

    manifest = {
        "purpose": "First COMSOL/CST ranking check before deeper GA/BPSO/topology optimization.",
        "platform": {
            "core": "3 um Au / 3 um gap / 3 um Au CPS",
            "au_thickness_um": cfg.au_thickness_um,
            "grid_um": cfg.grid_um,
            "substrate": "sapphire",
            "target_cutoff_thz": cfg.cutoff_thz,
        },
        "frequency_sweep_thz": [0.05, 2.0],
        "locked_template_requirement": "All four masks must use identical geometry extents, material properties, ports, boundaries, mesh rules, and frequency sweep.",
        "must_extract": [
            "S21_dB",
            "S11_dB",
            "loss_power = 1 - |S11|^2 - |S21|^2",
            "f3dB",
            "passband_ripple",
            "stopband_average",
            "recovery_peak",
            "E_field_maps_0p4_0p8_1p2THz",
            "Au_current_distribution_0p4_0p8_1p2THz"
        ],
        "entries": entries,
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("COMSOL validation queue prepared.")
    print(f"  entries: {len(entries)}")
    print(f"  wrote:   {manifest_path}")


if __name__ == "__main__":
    main()
