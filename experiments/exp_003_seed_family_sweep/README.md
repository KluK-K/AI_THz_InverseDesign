# Experiment 003 - Chirped Stub Seed-Family Sweep

Date: 2026-04-28

## 1. What was done

Implemented and ran a small parameter sweep before building the full GA/BPSO optimizer.

New code:

```text
scripts/run_seed_sweep.py
src/route_b/geometry.py  # seed_chirped_stub_mask now accepts depth/width/seed variants
```

Sweep dimensions:

```text
n_stubs:       5, 7, 9, 11
depth_scale:   0.88, 0.96, 1.04, 1.12
width_scale:   0.75, 1.00, 1.25
seed_offset:   0, 1
total:         96 candidates
```

## 2. Why this was done

Before running a more expensive GA/BPSO search, we need to know whether the
design variables have the expected physical direction. This sweep tests whether
changing stub count, depth, and width can improve the low-pass objective.

This is a research sanity check:

- If all seed variants performed randomly, the evaluator/objective would be suspect.
- If a physically plausible trend appears, those ranges can seed GA/BPSO.

## 3. Result

Best quick-sweep candidate:

```text
candidate:       SWEEP_0086
n_stubs:         11
depth_scale:     1.04
width_scale:     0.75
f3dB quick:      0.7969 THz
pass avg S21:    -0.315 dB
stop avg S21:    -12.578 dB
score quick:     -2.7533
```

Full 241-frequency-point re-evaluation:

```text
f3dB:            0.7861 THz
pass avg S21:    -0.318 dB
pass ripple:     0.867 dB
pass avg S11:    -17.834 dB
stop avg S21:    -12.684 dB
fabrication:     valid
```

Generated files:

```text
results/seed_sweep/seed_sweep_results.csv
results/seed_sweep/best_seed_sweep_mask.csv
results/seed_sweep/best_seed_sweep_summary.json
results/abcd_eval/best_seed_sweep_mask_metrics_abcd.json
results/abcd_eval/best_seed_sweep_mask_sparams_abcd.csv
results/abcd_eval/best_seed_sweep_mask_response_abcd.svg
```

## 4. Meaning

Compared with the initial 7-stub seed:

```text
initial seed stop avg S21:      -6.587 dB
best sweep stop avg S21:        -12.684 dB
```

The sweep roughly doubles stopband rejection while keeping cutoff close to 0.8 THz.

The trend is physically meaningful:

- 11 stubs provide more distributed slow-wave loading than 7.
- Slightly deeper stubs move the edge response toward the 0.8 THz target.
- Narrower stubs reduce passband overloading and keep S11 acceptable.

This supports the proposed "mirror-chirped multi-stub / SSPP-like" direction.

## 5. Next step

Use the sweep result to define GA/BPSO priors:

```text
n_stubs prior:       9-13
depth_scale prior:   0.98-1.10
width_scale prior:   0.60-1.00
```

Then implement:

```text
src/route_b/ga.py
src/route_b/bpso.py
src/route_b/dbs.py
```

The immediate objective for the optimizer is:

```text
keep f3dB in 0.78-0.82 THz
push stop avg S21 from -12.7 dB toward -20 dB and then -24 dB
keep pass avg S21 better than -0.8 dB
keep pass avg S11 below -10 dB
```

