# Commands

Run from:

```bash
cd "/Users/lukuan/Desktop/Quantum Engineering/AI_THZ/routeB_binary_ai_lpf"
```

Smoke test:

```bash
python3 scripts/run_stage1_smoke.py
```

Evaluate straight CPS baseline:

```bash
python3 scripts/evaluate_mask_abcd.py baseline
```

Evaluate current chirped-stub seed:

```bash
python3 scripts/evaluate_mask_abcd.py seed
```

Compile check:

```bash
python3 -m compileall -q src scripts
```

Inspect the analog interpretation:

```bash
cat results/abcd_eval/seed_analog_equivalent.json
```

Inspect fabrication constraints:

```bash
cat results/abcd_eval/seed_fabrication_report.json
```
