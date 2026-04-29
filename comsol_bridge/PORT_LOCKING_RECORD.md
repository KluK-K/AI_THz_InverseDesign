# Port Locking Record

## Current Status

```text
Full-wave validation infrastructure exists.
Critical remaining step: lock reproducible differential CPS port definition.
Do not run B0/B1/B2/B3 S-parameter sweeps until B0 port mini-test passes.
```

## Port Strategy

Primary strategy:

```text
differential lumped port / terminal pair
```

Reason:

```text
The device is a 3 um / 3 um / 3 um Au-gap-Au CPS. The desired mode is the
odd/differential voltage across the 3 um gap between the two Au rails.
```

Second-stage cross-check:

```text
waveguide/modal port on the full transverse face
```

This is for refined validation after the lumped differential port ranking test.

## Locked Coordinates

All coordinates are in um.

```text
Input plane:   x = 0
Output plane:  x = 820

Positive rail: y = +1.5 to +4.5
Negative rail: y = -4.5 to -1.5

Au z range:    z = 0 to 0.275
Gap region:    y = -1.5 to +1.5
```

## Named Selections

Coordinate-based box selections are created by:

```text
comsol_bridge/build_locked_template_from_rectangles.m
```

Names:

```text
sel_p1_plus
sel_p1_minus
sel_p2_plus
sel_p2_minus
```

Selection method:

```text
coordinate-based Box selections around Au input/output end faces
no raw boundary IDs
```

## B0 Port Mini-Test

Structure:

```text
B0_straight_cps
```

Frequencies:

```text
0.3 THz
0.8 THz
1.2 THz
```

Required outputs:

```text
S11
S21
loss = 1 - |S11|^2 - |S21|^2
E-field magnitude top view
E-field cross-section through gap
Au surface current distribution
```

## Pass Criteria

```text
0.3 THz: field mainly follows CPS gap region
0.8 THz: no artificial B0 cutoff near target
1.2 THz: B0 still transmits smoothly unless expected material loss dominates
S11: not close to 0 dB across all mini-test frequencies
current: two Au rails show differential/anti-phase behavior
```

## Fail Indicators

```text
strong resonance in straight B0
S11 near 0 dB everywhere
field localized only at input port
field immediately radiates into air/substrate
artificial -3 dB cutoff near 0.8 THz
```

## Next Action

1. Rebuild B0 template with coordinate selections.
2. Open MPH and inspect the four named selections.
3. If selections are correct, encode differential lumped port physics.
4. Run only the mini-test frequencies.
5. Only after mini-test passes, run B0 full sweep.

## Template Version

Template source:

```text
comsol_bridge/build_locked_template_from_rectangles.m
```

Template SHA256 at B0 rebuild:

```text
a3d788ecd69f1d9ad663eeccff5b31c90de69e0261877d751195b26b130229c7
```

Version record:

```text
results/comsol_validation_queue/B0_port_locking_template_version.json
```

B0 rebuilt MPH:

```text
results/comsol_runs/B0_straight_cps/B0_straight_cps_locked_template_geometry.mph
```

Rebuild status:

```text
geometry_mesh_studies_coordinate_port_selections_created_lumped_port_physics_pending
```

## Selection Visual Inspection Result

Fill this section after opening the rebuilt B0 MPH in COMSOL.

| Selection | Expected target | Pass/Fail | Notes |
|---|---|---|---|
| `sel_p1_plus` | input x = 0, +y Au rail end face, y = +1.5 to +4.5 um | pending | |
| `sel_p1_minus` | input x = 0, -y Au rail end face, y = -4.5 to -1.5 um | pending | |
| `sel_p2_plus` | output x = 820, +y Au rail end face, y = +1.5 to +4.5 um | pending | |
| `sel_p2_minus` | output x = 820, -y Au rail end face, y = -4.5 to -1.5 um | pending | |

Notes:

```text
The selection may contain multiple small faces if COMSOL splits the Au end face.
This is acceptable if all selected faces belong to the same rail end face.
It is not acceptable if the selection includes air, substrate, sidewalls, or empty selections.
```

If all pass:

```text
locked_on:
locked_by:
COMSOL_version:
template_sha256:
```
