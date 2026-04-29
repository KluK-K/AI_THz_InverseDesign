# Topology Optimization Strategy

## Position

Nature Communications 2025 is a useful inspiration, but Route B should not become
a pure topology optimization project yet.

The correct role of topology optimization here is:

```text
physics grammar seed -> binary search -> soft-topology local refinement -> threshold -> COMSOL
```

not:

```text
blank domain -> unconstrained topology optimization -> hope it becomes a CPS filter
```

## Why not pure topology first

The target device is a CPS guided-wave low-pass filter. It has strong transmission-line
physics priors:

- the 3/3/3 CPS rails must remain continuous;
- the center gap must remain open;
- useful low-pass behavior comes from distributed LC / slow-wave loading;
- fabrication is constrained by 0.5 um minimum features.

Pure topology optimization would waste search effort rediscovering these constraints.

## Allowed soft-topology domain

Only the outer loading region may change:

```text
allowed:
  upper outer loading region
  mirrored lower outer loading region

fixed:
  center gap = air
  main Au rails = metal
  input/output ports
```

## Soft-density variable

```text
rho(x, y) in [0, 1]
rho = 0 -> air
rho = 1 -> Au
```

After each update:

1. apply density filter with radius >= 0.5 um;
2. project with a sigmoid or Heaviside continuation;
3. force fixed gap/rail constraints;
4. threshold to binary for fabrication checks.

## Refinement objective

The refinement layer should not invent a whole new topology. It should optimize local
perturbations around a good grammar/BPSO/DBS candidate:

```text
loss =
  cutoff error
  + passband insertion loss
  + passband S11 penalty
  + stopband leakage
  + recovery peak penalty
  + fabrication penalty
```

## Stop condition

Topology refinement is worth keeping only if it improves at least one of:

- stopband average S21;
- recovery peak above cutoff;
- passband S11;
- passband ripple;

without shifting f3dB away from 0.8 THz.

