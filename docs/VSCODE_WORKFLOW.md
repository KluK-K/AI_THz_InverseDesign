# VSCode Workflow

## Recommended workspace

Open this folder directly:

```bash
code /Users/lukuan/COMSOL_MAT/routeB_binary_ai_lpf
```

## First setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/run_stage1_smoke.py
```

## Daily research loop

1. Edit `configs/default_route_b.json`.
2. Run `python scripts/run_stage1_smoke.py`.
3. Inspect generated `results/stage1_smoke_mask.csv` and `results/stage1_smoke_summary.json`.
4. When the fast model is connected, run a larger GA/BPSO/DBS search.
5. Export top candidates to `comsol_bridge/`.
6. Validate in COMSOL and copy S-parameter summaries back to `results/`.

## Coding standard

- Python owns orchestration, data handling, and future ML.
- MATLAB owns existing fast electromagnetic prototypes until they are cleanly ported.
- COMSOL LiveLink owns final 3D validation.
- Every generated result should be reproducible from config + seed.

