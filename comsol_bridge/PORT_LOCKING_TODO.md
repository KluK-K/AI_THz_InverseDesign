# Port Locking TODO

## Goal

Convert the current B0 geometry scaffold into a solved S-parameter template.

Current B0 model:

```text
results/comsol_runs/B0_straight_cps/B0_straight_cps_locked_template_geometry.mph
```

## Required locked port decision

Use differential lumped port / terminal pair first. Define identical differential CPS ports at:

```text
input plane:  x = 0 um
output plane: x = 820 um
```

The port definition must excite the differential mode between the two Au rails:

```text
upper rail: +V
lower rail: -V
```

## Procedure

1. Open the B0 MPH file in COMSOL.
2. Inspect coordinate-based named selections, not raw boundary IDs:

```text
sel_p1_plus
sel_p1_minus
sel_p2_plus
sel_p2_minus
```

3. Confirm they select the Au end faces:

```text
x = 0 / 820 um
y = +1.5 to +4.5 um or -4.5 to -1.5 um
z = 0 to 0.275 um
```

4. Add differential lumped port / terminal-pair physics.
5. Run only the mini-test frequencies first:

```text
0.3 THz, 0.8 THz, 1.2 THz
```

6. Only after B0 mini-test passes, run the full frequency sweep:

```text
0.05 THz to 2.0 THz
```

7. Export:

```text
S11
S21
loss = 1 - abs(S11)^2 - abs(S21)^2
```

8. Save metrics to:

```text
results/comsol_runs/B0_straight_cps/B0_straight_cps_comsol_metrics.json
results/comsol_runs/B0_straight_cps/B0_straight_cps_comsol_sparams.csv
```

## Rule

After port selections are encoded, rerun B0 from script. Then use the exact same script
for B1/B2/B3.
