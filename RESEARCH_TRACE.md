# Research Trace

## 2026-04-28 - Path migration and stage-2 fast model

Current project path:

```text
/Users/lukuan/Desktop/Quantum Engineering/AI_THZ/routeB_binary_ai_lpf
```

What changed:

- Confirmed the new no-leading-space path.
- Re-ran the stage-1 smoke mask generator.
- Added `metrics.py` for low-pass S-parameter scoring.
- Added `fast_abcd.py` for first-stage ABCD/qTEM evaluation.
- Added `evaluate_mask_abcd.py` for command-line evaluation.
- Added SVG response output so plots do not depend on matplotlib.
- Added fabrication and analog extraction reports.

Why it matters:

- This turns the research plan into a repeatable scoring loop.
- It creates the fast feedback needed before GA/BPSO/DBS can be useful.
- It keeps every candidate tied to physics, fabrication, and analog interpretation.

Key result:

```text
baseline f3dB:      2.0000 THz sweep bound
initial seed f3dB:  0.7982 THz
initial seed stop:  -6.587 dB
```

Next:

- Use optimization to deepen the stopband while preserving 0.8 THz cutoff.

## 2026-04-28 - Seed-family sweep

What changed:

- Added `scripts/run_seed_sweep.py`.
- Extended seed geometry generation with `depth_scale`, `width_scale`, and `seed_offset`.
- Ran 96 candidates.

Why it matters:

- Before full GA/BPSO, this checks whether the selected geometric degrees of freedom are meaningful.
- It gives optimizer priors instead of starting from blind randomness.

Key result:

```text
best sweep candidate: SWEEP_0086
n_stubs:              11
depth_scale:          1.04
width_scale:          0.75
f3dB full:            0.7861 THz
stop avg S21 full:    -12.684 dB
fabrication:          valid
```

Next:

- Implement GA/BPSO using priors around 9-13 stubs, depth scale 0.98-1.10, width scale 0.60-1.00.

## 2026-04-28 - Critical route correction and COMSOL queue

What changed:

- Added stricter true-low-pass metrics: recovery peak, stopband coverage, passband notch penalty.
- Added grammar-based design encoding with `StubSpec`, `IslandSpec`, and `GrammarDesign`.
- Updated the evaluator to distinguish connected open stubs from floating capacitive islands.
- Tested hybrid stub-island grammar variants.
- Prepared the first COMSOL/CST validation queue.
- Added B1 traditional stepped/Bessel CPS as the analog baseline control.
- Added mechanism diagnostics: S11/S21/loss power and locked field/current map requirements.

Why it matters:

- The project is now framed as a physics-guided inverse-design platform, not a one-off filter search.
- Floating islands are treated critically: they are allowed as a controlled refinement feature, but not assumed beneficial.
- The next scientific check is full-wave ranking consistency, not more fast-model optimization.

Key result:

```text
results/benchmark/benchmark_table.md
results/comsol_validation_queue/manifest.json
docs/FULL_WAVE_VALIDATION_PROTOCOL.md
comsol_bridge/LOCKED_TEMPLATE_SPEC.md
```

Next:

- Build mask-to-COMSOL geometry export for the three queued masks.
- Use COMSOL/CST to decide whether the fast evaluator is trustworthy enough for GA/BPSO.

## 2026-04-28 - B0 locked template first build

What changed:

- Added rectangle export for COMSOL geometry.
- Exported B0/B1/B2/B3 rectangle CSVs.
- Added locked COMSOL LiveLink template script.
- Successfully launched COMSOL server and MATLAB LiveLink.
- Built and saved B0 locked template geometry/mesh/study scaffold.

Key files:

```text
scripts/export_rectangles_for_comsol.py
comsol_bridge/build_locked_template_from_rectangles.m
comsol_bridge/run_B0_first_locked_template.m
results/comsol_runs/B0_straight_cps/B0_straight_cps_locked_template_geometry.mph
```

Current status:

```text
geometry_mesh_study_created_port_selection_pending
```

Next:

- Lock input/output differential CPS port boundary selections on B0.
- Rerun B0 and extract S11/S21/loss.
- Only after B0 is solved, run B1/B3/B2 with the same locked template.

## 2026-04-28 - Port locking correction

What changed:

- Stopped before B0 S-parameter solving.
- Chose differential lumped port / terminal pair as the first validation strategy.
- Added coordinate-based terminal selections to the COMSOL template script:

```text
sel_p1_plus
sel_p1_minus
sel_p2_plus
sel_p2_minus
```

- Added a B0 mini-test manifest for 0.3, 0.8, and 1.2 THz.
- Added explicit pass/fail criteria for field confinement and differential current.

Why it matters:

- Raw COMSOL boundary IDs are not stable across B0/B1/B2/B3.
- A wrong port could create fake reflection, fake attenuation, or fake cutoff.
- The full-wave truth layer is only meaningful after the port definition is locked.

Key files:

```text
comsol_bridge/PORT_LOCKING_RECORD.md
results/comsol_validation_queue/B0_PORT_MINITEST_MANIFEST.json
comsol_bridge/build_locked_template_from_rectangles.m
```

Next:

- Rebuild B0 template so the coordinate selections are present.
- Inspect selections in COMSOL.
- Encode differential lumped port physics.
- Run only the B0 three-frequency mini-test.

## 2026-04-28 - B0 rebuilt with coordinate port selections

What changed:

- Rebuilt B0 MPH with updated coordinate-based terminal selections.
- Confirmed status file now lists:

```text
sel_p1_plus
sel_p1_minus
sel_p2_plus
sel_p2_minus
```

- Generated template SHA256/version record.
- Added visual inspection table to `PORT_LOCKING_RECORD.md`.

Current status:

```text
geometry_mesh_studies_coordinate_port_selections_created_lumped_port_physics_pending
```

Next:

- Open the rebuilt B0 MPH in COMSOL.
- Visually inspect the four selections.
- Do not define lumped port physics until selections pass.
