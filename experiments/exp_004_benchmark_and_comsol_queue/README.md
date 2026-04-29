# Experiment 004 - Benchmark Table And COMSOL Validation Queue

Date: 2026-04-28

## 1. What was done

Implemented the first benchmark table and prepared the first COMSOL/CST validation queue.

New code:

```text
src/route_b/grammar.py
scripts/run_benchmark_table.py
scripts/run_hybrid_island_sweep.py
scripts/prepare_comsol_validation_queue.py
```

New docs:

```text
docs/TOPOLOGY_OPTIMIZATION_STRATEGY.md
docs/PAPER_POSITIONING.md
docs/ACTIVE_LEARNING_PROTOCOL.md
```

## 2. Why this was done

The project needed to move from:

```text
find one good 0.8 THz candidate
```

to:

```text
build a benchmarked, fabrication-aware inverse-design framework
```

This experiment creates the first benchmark table and selects the first three structures
that should be sent to COMSOL/CST:

```text
B0 straight CPS
B1 traditional stepped/Bessel CPS
B2 7-stub seed
B3 11-stub sweep best
```

## 3. Critical correction from the user feedback

The model was updated to avoid three mistakes:

1. Treating topology optimization as the main engine too early.
2. Searching raw pixels instead of physics grammar parameters.
3. Mistaking a local resonance notch for a true low-pass roll-off.

Added low-pass metrics:

```text
stopband coverage below -10 dB
stopband coverage below -20 dB
recovery peak
passband notch penalty
monotonic violation
```

## 4. Benchmark result

Current benchmark table:

```text
results/benchmark/benchmark_table.md
```

Important interpretation:

- Straight CPS is the truth baseline and should not low-pass near 0.8 THz.
- Traditional stepped/Bessel CPS is the analog synthesis control. It is needed to prove
  inverse design beats ordinary filter synthesis.
- 7-stub seed hits f3dB near 0.8 THz, but stopband is weak.
- 11-stub sweep best improves stopband average, but strict low-pass score exposes
  recovery/monotonicity risk.
- Hybrid stub-island grammar v0 is not better yet; floating islands are not automatically useful.

This means the current best scientific move is COMSOL ranking validation, not deeper
blind optimization.

## 5. Floating island finding

Floating capacitive islands were added as a grammar feature and tested. The first naive
version overloaded the line and pulled cutoff too low. After fixing the grammar encoding
bug, the conservative island variants still did not beat the connected-stub candidate.

Conclusion:

```text
floating islands stay as local topology-refinement freedom,
not the main design family yet.
```

## 6. COMSOL/CST validation queue

Prepared:

```text
results/comsol_validation_queue/manifest.json
results/comsol_validation_queue/B0_straight_cps.csv
results/comsol_validation_queue/B1_traditional_stepped_bessel_cps.csv
results/comsol_validation_queue/B2_7_stub_seed.csv
results/comsol_validation_queue/B3_11_stub_sweep_best.csv
```

Main validation question:

```text
Does COMSOL/CST preserve the fast-model ranking?
```

Required outputs:

```text
S21 dB
S11 dB
f3dB
passband ripple
stopband average
field maps at 0.5, 0.8, 1.2 THz
```

## 7. Next step

Do not train a generator yet.

Next engineering step:

```text
build COMSOL export/run scripts for the three queued masks
```

Next optimization step after COMSOL sanity:

```text
GA/BPSO on grammar parameters:
  n_stubs
  center positions
  depth vector
  width vector
  taper/matching profile
  optional tiny floating island perturbations
```
