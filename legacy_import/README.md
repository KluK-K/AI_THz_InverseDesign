# Legacy Import Plan

This project has moved to:

```text
/Users/lukuan/Desktop/ Quantum Engineering/AI_THZ/routeB_binary_ai_lpf
```

If older scripts still exist under:

```text
/Users/lukuan/COMSOL_MAT
```

do not keep editing them in-place for the main research. Instead:

1. Copy only the scripts we need into `legacy_import/`.
2. Record the original path and date.
3. Refactor them into `src/route_b/` or `comsol_bridge/`.
4. Make all new outputs go into this project `results/` folder.

Likely useful legacy scripts:

```text
play/real3/thz_cps_monolithic_strong_stub_lpf_0p5um.m
play/real/thz_cps_pngf_like_dbs_demo.m
testing/paper_design/build_bessel_cps.m
THz_CPS_N5_0p8THz_estimate.m
```

