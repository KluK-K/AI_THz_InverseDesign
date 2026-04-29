# Locked Full-Wave Validation Protocol

## Purpose

This is not just a COMSOL/CST run. It is a credibility test for the fast evaluator.

The key question is:

```text
Does the fast ABCD/qTEM model preserve design ranking under full-wave Maxwell simulation?
```

If ranking is not preserved, do not continue GA/BPSO/topology optimization until the
fast evaluator is corrected.

## Candidate queue

First locked validation queue:

```text
B0_straight_cps
B1_traditional_stepped_bessel_cps
B2_7_stub_seed
B3_11_stub_sweep_best
```

The queue lives at:

```text
results/comsol_validation_queue/manifest.json
```

## Locked settings

All four structures must use identical:

```text
substrate material and size
Au conductivity and thickness
air box height
boundary/PML settings
port type
port location
feed lengths
mesh rules
frequency sweep
solver tolerances
post-processing equations
```

Do not hand tune mesh or ports per structure. If a setting must change, rerun all four
structures with the new setting.

## Port-locking gate

Before any full sweep, B0 must pass a port-locking mini-test.

Port strategy:

```text
differential lumped port / terminal pair
```

Mini-test frequencies:

```text
0.3 THz, 0.8 THz, 1.2 THz
```

Pass criteria:

```text
field follows the CPS gap region
current on the two rails is differential / anti-phase
B0 has no artificial cutoff near 0.8 THz
S11 is not near 0 dB across all frequencies
```

Only after this gate passes should B0 full sweep be run.

## Required outputs

For every candidate:

```text
S21(f)
S11(f)
loss(f) = 1 - |S11|^2 - |S21|^2
f3dB
passband ripple
stopband average
recovery peak
E-field maps at 0.4, 0.8, 1.2 THz
Au current distribution at 0.4, 0.8, 1.2 THz
```

## Mechanism diagnosis

Possible mechanisms:

1. Distributed slow-wave cutoff.
2. Localized resonant notch.
3. Port mismatch.
4. Radiation/substrate leakage.

Interpretation:

```text
Good filter:
  stopband S21 low
  passband S11 low
  stopband energy mostly reflected or stored near stubs
  no severe radiation leakage
  no high-frequency recovery peak

Port mismatch:
  passband or cutoff S11 high
  fields concentrated near ports rather than loading region

Lossy scatterer:
  loss = 1 - |S11|^2 - |S21|^2 high
  fields leak into substrate/air

Notch-like response:
  narrow S21 dip near 0.8 THz
  high-frequency recovery above -10 dB
```

## Decision tree

### Case 1: B3 beats B2, B1, and B0 in COMSOL

Proceed:

```text
grammar GA/BPSO search
DBS polish
restricted topology refinement
```

### Case 2: B3 has cutoff but S11 is high

Interpretation:

```text
mostly reflection-type low-pass with poor matching
```

Fix:

```text
add input/output taper
reduce first/last stub depth
increase chirp smoothness
raise S11 penalty
```

### Case 3: B3 has a notch but high-frequency recovery

Interpretation:

```text
not a true low-pass yet
```

Fix:

```text
increase distributed loading
spread stub lengths
add recovery peak penalty
avoid single dominant resonant length
```

### Case 4: B3 fails in COMSOL

Stop optimization and repair the surrogate:

```text
refit effective epsilon
refit open-stub admittance
add radiation/leakage penalty
add port discontinuity correction
validate against B0-B3 again
```

## Pass/fail criterion for the fast evaluator

The fast evaluator passes the first credibility test only if:

```text
full-wave ranking is qualitatively consistent with fast ranking
and the mechanism diagnosis does not contradict the fast-model explanation.
```

The fast evaluator does not need perfect absolute S-parameter values.
