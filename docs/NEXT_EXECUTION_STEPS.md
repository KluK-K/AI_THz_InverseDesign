# Next Execution Steps

## Step 1: Make the existing fast solver callable

Wrap this script as the first authoritative fast evaluator:

```text
/Users/lukuan/COMSOL_MAT/play/real3/thz_cps_monolithic_strong_stub_lpf_0p5um.m
```

Required changes:

- Accept a config file or MATLAB struct instead of only hardcoded defaults.
- Save metrics to a stable JSON or CSV schema.
- Save masks with the same row/column convention as this Route B workspace.
- Add a `quick`, `standard`, and `long` run profile under `configs/`.

## Step 2: Add BPSO before DBS

Current local scripts already contain DBS-like optimization. The next missing piece is BPSO:

- Particle state: compressed upper-load binary mask.
- Projection: always restore rails, empty gap, top-bottom mirror.
- Fitness: call the fast evaluator.
- Output: top-k candidates for DBS polish.

## Step 3: Cross-check with PNGF-like reduced model

Use this script as an independent evaluator:

```text
/Users/lukuan/COMSOL_MAT/play/real/thz_cps_pngf_like_dbs_demo.m
```

Purpose:

- Detect overfitting to the strong-stub ABCD model.
- Keep only candidates that score well in both models.

## Step 4: Export top candidates to COMSOL

Generate COMSOL models for:

- baseline 3/3/3 CPS.
- existing best strong-stub candidate.
- best BPSO + DBS candidate.
- ablation variants.

Validation metrics:

- f3dB.
- average passband S21.
- passband ripple.
- average stopband S21.
- average passband S11.
- field localization and radiation leakage.

## Step 5: Decide publication-level novelty

A candidate becomes serious only if it satisfies all three:

- It beats the traditional Bessel/stepped CPS baseline after COMSOL validation.
- It keeps 0.5 um fabrication constraints with no isolated nonmanufacturable islands.
- It has a clear physical explanation: chirped SSPP slow-wave cutoff plus analog LC equivalent.

