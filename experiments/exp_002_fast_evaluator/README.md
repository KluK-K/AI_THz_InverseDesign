# Experiment 002 - Stage-2 ABCD/qTEM Fast Evaluator

Date: 2026-04-28

## 1. What was done

Implemented the first physically motivated fast evaluator for Route B:

```text
src/route_b/metrics.py
src/route_b/fast_abcd.py
src/route_b/fabrication.py
src/route_b/analog.py
scripts/evaluate_mask_abcd.py
```

The evaluator turns a legal binary Au/air mask into approximate S-parameters:

```text
mask -> loading profile -> cascaded ABCD matrix -> S11/S21 -> low-pass metrics
```

It also writes stable experiment artifacts:

```text
results/abcd_eval/*_metrics_abcd.json
results/abcd_eval/*_sparams_abcd.csv
results/abcd_eval/*_response_abcd.svg
results/abcd_eval/*_analog_equivalent.json
results/abcd_eval/*_fabrication_report.json
```

## 2. Why this was done

The Route B research path needs a fast scoring function before GA/BPSO/DBS can run.
COMSOL is too slow to evaluate thousands of candidate masks. Guided-AI used the same
logic: fast ABCD evaluation for search, FEM only for final validation.

This first evaluator is intentionally a surrogate, not a final electromagnetic truth.
Its purpose is to rank candidate geometries and provide direction for optimization.

## 3. Physical meaning

The model interprets the geometry as:

- the fixed 3/3/3 CPS rails are the main differential transmission line;
- each x-column is a short transmission-line unit cell;
- outer Au loading lowers local impedance and adds slow-wave loading;
- vertical outer stubs are modeled as weakly coupled open-stub shunt admittances;
- chirped stub depths create a distributed cutoff instead of one narrow resonance.

This corresponds to the proposed analog equivalent:

```text
main CPS line + cascade of shunt capacitances/open-stub resonators
```

## 4. Calibration trace

The first uncaliabrated version used a strong `stub_pair_scale = 1.15`. That caused
the seed structure to appear blocked from nearly DC:

```text
seed f3dB ~ 0.058 THz
passband S21 ~ -108 dB
```

This was physically too aggressive because each 0.5 um pixel column was being treated
as a strongly coupled port. A parameter sweep showed that a weak-coupling scale around
0.008-0.018 gives a more realistic first-stage surrogate.

Current default:

```text
stub_pair_scale = 0.012
end_cap_um      = 0.5
max_tan_abs     = 12
```

The meaning of this calibration is important: outer loading couples to the CPS rail
through a narrow 0.5 um-scale contact, so its low-frequency effect should be weak;
near its quarter-wave condition it should become much stronger.

## 5. Current results

Baseline straight CPS:

```text
f3dB:          2.0000 THz, sweep upper bound
pass avg S21: -0.134 dB
pass ripple:  0.121 dB
pass avg S11: -298.393 dB
stop avg S21: -0.265 dB
score:        -55.6138
```

Seed chirped-stub binary mask:

```text
f3dB:          0.7982 THz
pass avg S21: -0.220 dB
pass ripple:  0.352 dB
pass avg S11: -21.088 dB
stop avg S21: -6.587 dB
score:        -4.0687
fabrication:  valid
```

Analog extraction for the seed:

```text
stub count:                 7
stub depth range:           26-38 um
quarter-wave estimate:      0.866-1.259 THz
main physical role:         target-edge cutoff stubs plus high-frequency suppression
```

## 6. Interpretation

The baseline result is correct as a sanity check: a straight short CPS section should
not naturally become a 0.8 THz low-pass filter in this simplified model.

The seed result is useful but not final:

- Good: f3dB is almost exactly at the 0.8 THz target.
- Good: passband loss and S11 are acceptable in the surrogate.
- Not enough: stopband suppression is only about -6.6 dB average.
- Useful physical trace: extracted stubs are chirped from high-frequency suppression
  toward target-edge cutoff, which supports the planned SSPP-like slow-wave narrative.

Therefore the current geometry is a target-cutoff seed, not a final filter.

## 7. Next step

Implement optimization around this evaluator:

1. Add `src/route_b/fabrication.py` to reject impossible masks.
2. Add `src/route_b/analog.py` to extract equivalent LC/stub parameters.
3. Add `src/route_b/ga.py` using Guided-AI settings.
4. Add `src/route_b/bpso.py` for binary global search.
5. Add `src/route_b/dbs.py` for local polish.
6. Use COMSOL only after the fast evaluator finds candidates with both:

```text
f3dB near 0.8 THz
stop avg S21 significantly below the current -6.6 dB seed
```
