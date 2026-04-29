from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from route_b import load_config, summarize_mask
from route_b.geometry import seed_chirped_stub_mask
from route_b.objectives import proxy_metrics


def main() -> None:
    cfg = load_config(ROOT / "configs" / "default_route_b.json")
    mask = seed_chirped_stub_mask(cfg, n_stubs=7)
    summary = summarize_mask(mask, cfg)
    metrics = proxy_metrics(mask, cfg)

    out_dir = ROOT / "results"
    out_dir.mkdir(exist_ok=True)
    np.savetxt(out_dir / "stage1_smoke_mask.csv", mask, fmt="%d", delimiter=",")
    (out_dir / "stage1_smoke_summary.json").write_text(
        json.dumps({"summary": summary, "proxy_metrics": metrics}, indent=2),
        encoding="utf-8",
    )

    print("Route B stage-1 smoke test complete.")
    print(f"Mask: {mask.shape[0]} rows x {mask.shape[1]} cols")
    print(f"Proxy score: {metrics['proxy_score']:.4f}")
    print(f"Estimated added Au area: {summary['estimated_added_area_um2']:.2f} um^2")
    print(f"Wrote: {out_dir / 'stage1_smoke_mask.csv'}")


if __name__ == "__main__":
    main()

