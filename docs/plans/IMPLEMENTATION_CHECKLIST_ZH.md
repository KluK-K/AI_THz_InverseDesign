# Implementation Checklist

## Already present

- [x] VSCode project folder.
- [x] Default Route B JSON config.
- [x] Basic binary mask geometry generation.
- [x] Gap/rail/mirror projection.
- [x] Stage-1 smoke test.
- [x] Initial literature map.
- [x] Detailed Chinese research plan.

## Next coding tasks

- [x] `src/route_b/metrics.py`
- [x] `src/route_b/fast_abcd.py`
- [x] `scripts/evaluate_mask_abcd.py`
- [x] `src/route_b/fabrication.py`
- [x] `src/route_b/analog.py`
- [ ] `src/route_b/ga.py`
- [ ] `src/route_b/bpso.py`
- [ ] `src/route_b/dbs.py`
- [x] `scripts/run_seed_sweep.py`
- [x] `src/route_b/grammar.py`
- [x] `scripts/run_benchmark_table.py`
- [x] `scripts/run_hybrid_island_sweep.py`
- [x] `scripts/prepare_comsol_validation_queue.py`
- [ ] `scripts/run_ga_search.py`
- [ ] `scripts/run_bpso_search.py`
- [ ] `scripts/run_dbs_polish.py`
- [ ] `comsol_bridge/mask_to_comsol_geometry.m`
- [ ] `comsol_bridge/build_route_b_model.m`

## Next research tasks

- [ ] Define B0/B1/B2 baselines.
- [x] Decide first exact frequency grid.
- [ ] Decide sapphire effective permittivity model.
- [ ] Define COMSOL port geometry.
- [ ] Decide air box and boundary/PML thickness.
- [ ] Run first baseline COMSOL sweep.
- [x] Prepare first COMSOL validation queue.
- [ ] Compare fast ABCD vs COMSOL baseline.
- [ ] Correct fast model coefficients.
- [ ] Run GA quick search.
- [x] Run seed-family pre-GA sweep.
- [ ] Run BPSO quick search.
- [ ] DBS polish top-5.
- [ ] COMSOL validate top-3.

## Go / no-go checks

Before claiming a candidate is good:

- [ ] It has f3dB near 0.8 THz in fast model.
- [ ] It beats straight CPS baseline.
- [ ] It beats traditional analog baseline.
- [ ] It remains legal after fabrication checks.
- [ ] It has no isolated Au islands unless intentionally attached.
- [ ] It has acceptable S11 in passband.
- [ ] It has COMSOL S21/S11 validation.
- [ ] It has field plots explaining the low-pass mechanism.
