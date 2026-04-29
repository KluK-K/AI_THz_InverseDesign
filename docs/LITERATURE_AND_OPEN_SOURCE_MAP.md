# Literature And Open-Source Map

## Route B directly relevant literature

1. Genetic Algorithm-Based Inverse Design of Guided Wave Planar Terahertz Filters  
   https://arxiv.org/abs/2506.03372  
   Use: validates the GA + fast ABCD + FEM final-validation pattern for CPS THz filters.

2. Demonstration of a terahertz coplanar-strip spoof-surface-plasmon-polariton low-pass filter  
   https://www.nature.com/articles/s41598-023-50599-y  
   Use: supports the physical idea that CPS SSPP structures can create THz low-pass band-edge behavior.

3. Design and Verification of a Terahertz Bandpass Filter using a Spoof Surface Plasmon Polariton Waveguide with Gapped Unit Cells  
   https://arxiv.org/abs/2604.14466  
   Use: shows how SSPP low-pass behavior combines with capacitive gaps. We avoid center gaps for low-pass, but reuse the band-edge intuition.

4. Reverse design of pixel-type terahertz band-pass filters  
   https://pubmed.ncbi.nlm.nih.gov/35209273/  
   Use: supports DBS/BPSO as practical binary THz inverse-design algorithms.

5. On-chip, inverse-designed active wavelength division multiplexer at THz frequencies  
   https://www.nature.com/articles/s41467-025-62557-5  
   Use: higher-level proof that inverse design is now credible for THz on-chip devices. This is more adjoint/topology than Route B, so it is a later-stage reference.

6. Simulated Comparison of On-Chip Terahertz Filters for Sub-Wavelength Dielectric Sensing  
   https://www.mdpi.com/1424-8220/26/1/129  
   Use: useful practical reference for on-chip THz simulation setup and mesh scale around 0.5-0.8 um in high-field regions.

## Open-source tools worth inspecting

1. SPINS-B  
   https://github.com/stanfordnqp/spins-b  
   Role: adjoint/topology optimization architecture reference. Not the first implementation target for Route B.

2. Meep  
   https://github.com/NanoComp/meep  
   Role: open FDTD and adjoint ecosystem. Useful for later independent validation, but COMSOL is more aligned with current local files.

3. Ceviche  
   https://github.com/fancompute/ceviche  
   Role: Python FDFD/FDTD with automatic differentiation. Useful for future 2D surrogate physics experiments.

4. invrs-io / invrs-gym  
   https://invrs-io.github.io/invrs-io/  
   Role: benchmark organization pattern for inverse-design tasks.

5. MATLAB Central Binary PSO examples  
   https://www.mathworks.com/matlabcentral/fileexchange/39844-binary-particle-swarm-optimization  
   Role: simple BPSO implementation pattern. We should reimplement the small algorithm ourselves to avoid dependency and licensing ambiguity.

## What not to do first

- Do not start with a full neural generator before the physics dataset exists.
- Do not optimize unconstrained pixel art that breaks the CPS rails.
- Do not trust a single surrogate model without COMSOL cross-checks.
- Do not claim novelty from "AI" alone. Novelty should be the constrained, mirror-chirped, multi-scale SSPP-like geometry plus the reproducible optimization workflow.

