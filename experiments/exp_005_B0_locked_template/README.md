# Experiment 005 - B0 Locked Template First Build

Date: 2026-04-28

## 1. What was done

Built the first locked COMSOL template for:

```text
B0_straight_cps
```

Generated rectangle geometry first:

```text
results/comsol_rectangles/B0_straight_cps_rectangles.csv
```

Then used COMSOL LiveLink through MATLAB batch to create:

```text
results/comsol_runs/B0_straight_cps/B0_straight_cps_locked_template_geometry.mph
```

Status of the previously built MPH:

```text
geometry_mesh_study_created_port_selection_pending
```

After the latest route correction, the template script was updated and B0 was rebuilt
to create coordinate-based terminal selections:

```text
sel_p1_plus
sel_p1_minus
sel_p2_plus
sel_p2_minus
```

The rebuilt MPH is ready for visual selection inspection. This rebuild is
geometry/template generation only, not an S-parameter run.

Latest status:

```text
geometry_mesh_studies_coordinate_port_selections_created_lumped_port_physics_pending
```

## 2. Why this was done

The project now needs a full-wave credibility test, not more fast-model optimization.
B0 is the cleanest first target because it has only two continuous CPS rails.

If the locked template cannot correctly simulate B0, then B1/B2/B3 results would not
be trustworthy.

## 3. What succeeded

- COMSOL server launched successfully.
- MATLAB connected to COMSOL LiveLink.
- Rectangle export succeeded.
- B0 geometry, materials, mesh scaffold, EMW physics scaffold, and frequency study were created.
- MPH file was saved.

## 4. Current blocker

The template still needs confirmed differential lumped port physics.

This is intentionally not hand-waved. Port selection must be defined once, checked on B0,
and then reused identically for B1/B2/B3.

Required next task:

```text
rebuild B0_straight_cps_locked_template_geometry.mph with coordinate selections
open B0_straight_cps_locked_template_geometry.mph
inspect sel_p1_plus/minus and sel_p2_plus/minus
encode differential lumped port physics
run only 0.3 / 0.8 / 1.2 THz mini-test
inspect fields and currents before any full sweep
```

## 5. Run commands used

Start COMSOL server:

```bash
/Applications/COMSOL64/Multiphysics/bin/comsol mphserver -port 2037
```

Build B0 from MATLAB:

```bash
/Applications/MATLAB_R2022a.app/bin/matlab -batch "addpath('/Applications/COMSOL64/Multiphysics/mli'); mphstart(2037); cd('/Users/lukuan/Desktop/Quantum Engineering/AI_THZ/routeB_binary_ai_lpf/comsol_bridge'); candidateName='B0_straight_cps'; RUN_SOLVE=false; run('build_locked_template_from_rectangles.m');"
```

## 6. Next

Do not run B1/B2/B3 yet.

Next step is B0 port-selection inspection and B0 mini-test, not B0 full sweep.
