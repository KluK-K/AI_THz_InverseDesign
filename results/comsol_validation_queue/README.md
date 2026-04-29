# COMSOL Validation Queue

This queue is a locked full-wave credibility test for the Route B fast evaluator.

Candidates:

```text
B0_straight_cps
B1_traditional_stepped_bessel_cps
B2_7_stub_seed
B3_11_stub_sweep_best
```

Main question:

```text
Does full-wave simulation preserve the fast-model ranking and mechanism?
```

Required outputs:

```text
S21
S11
loss = 1 - |S11|^2 - |S21|^2
E-field maps at 0.4 / 0.8 / 1.2 THz
Au current distribution at 0.4 / 0.8 / 1.2 THz
```

Do not manually tune the COMSOL/CST template per candidate.

