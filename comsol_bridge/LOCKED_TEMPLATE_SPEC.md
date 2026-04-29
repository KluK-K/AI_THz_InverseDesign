# Locked COMSOL/CST Template Specification

## Fixed platform

```text
Core CPS:      3 um Au / 3 um gap / 3 um Au
Au thickness: 0.275 um
Grid:         0.5 um
Substrate:    sapphire
```

## Geometry inputs

Use masks from:

```text
results/comsol_validation_queue/*.csv
```

Each mask uses rows as transverse y cells and columns as propagation x cells.

## Identical simulation settings

All candidates must use the same:

```text
left/right feed length
substrate block
air box
port planes
boundary conditions
mesh size rules
frequency sweep
solver settings
```

## Post-processing equations

```text
S21_dB = 20*log10(abs(S21))
S11_dB = 20*log10(abs(S11))
loss_power = max(0, 1 - abs(S11)^2 - abs(S21)^2)
```

## Field snapshots

Export at:

```text
0.4 THz
0.8 THz
1.2 THz
```

Required views:

```text
E-field magnitude top view
E-field cross-section through gap
surface current density on Au
```

## Rule

If any template parameter changes after the first run, rerun B0, B1, B2, and B3.

