# Route B Binary AI THz Low-Pass Filter

This folder is the VSCode research workspace for the Route B plan:
binary Au/air inverse design for an on-chip CPS terahertz low-pass filter.

The target physical platform is:

- CPS core: 3 um Au / 3 um gap / 3 um Au.
- Au thickness: 0.275 um.
- Minimum fabrication grid: 0.5 um.
- Substrate: sapphire.
- Desired low-pass cutoff: 0.8 THz.
- Main search space: added Au outside the two continuous CPS rails.

The folder is intentionally split into reproducible stages:

1. `docs/` - research plan, literature map, and design logic.
2. `configs/` - machine-readable design and optimization settings.
3. `src/route_b/` - Python prototype modules for geometry, constraints, and fast scoring.
4. `scripts/` - command-line entry points for smoke tests and future optimization runs.
5. `comsol_bridge/` - future MATLAB/COMSOL export and validation scripts.
6. `results/` - generated masks, spectra, plots, and reports.
7. `external/` - notes about open-source repositories to inspect or vendor only if needed.

Start in VSCode:

```bash
cd /Users/lukuan/COMSOL_MAT/routeB_binary_ai_lpf
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_stage1_smoke.py
```

The current code is a stage-0/stage-1 scaffold. It is not a final EM solver.
Its job is to keep the research path concrete while we progressively replace
simple scoring pieces with the existing MATLAB fast models and COMSOL validation.

