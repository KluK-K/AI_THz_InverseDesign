# Guided_AI_inversedesign.pdf Method Notes

Source file:

```text
/Users/lukuan/Desktop/ Quantum Engineering/AI_THZ/Guided_AI_inversedesign.pdf
```

Title:

```text
Genetic Algorithm-Based Inverse Design of Guided Wave Planar Terahertz Filters
```

## Key points to reuse

- The design is represented as a binary matrix of Au and air pixels.
- Structural connectivity is enforced because the CPS platform must keep a continuous conductive pathway.
- A genetic algorithm explores the discrete design space.
- Candidate responses are evaluated with an ABCD transmission-matrix method.
- FEM/HFSS is used only for final validation because full-wave simulation is too expensive for every candidate.
- The fitness is RMSE between simulated and target S-parameters, including S21/S11 magnitude and phase.

## Parameters reported by the paper

```text
Population size: 200
Elite count: 30, about 15%
Tournament size: 4
Crossover: two-point column crossover
Mutation: 10% selected individuals
Pixel size in paper: 4 um x 10 um
Design example: 300 um x 2000 um, 200 columns along propagation
W range in paper: 10-90 um
S range in paper: 5-90 um
Surrogate: ABCD matrix method
Validation: FEM/HFSS
```

## How Route B differs

```text
Paper:   band-stop filters centered at 0.6, 0.8, 1.0 THz
Route B: low-pass filter with 0.8 THz cutoff

Paper:   W/S CPS profile search
Route B: fixed 3/3/3 CPS rails plus outer-only binary loading

Paper:   4 um x 10 um pixels
Route B: 0.5 um fabrication grid

Paper:   GA
Route B: GA initialization + BPSO global search + DBS local polish
```

## Direct implementation notes

1. Reuse their GA population logic:

```text
population = 200
elite = top 30
tournament size = 4
two-point crossover over columns
mutation = bit flip with geometry projection
```

2. Replace their band-stop target with low-pass target:

```text
S21 passband 0.08-0.70 THz: near 0 dB
S21 cutoff near 0.8 THz: -3 dB
S21 stopband 1.0-1.9 THz: below -24 dB
S11 passband: below -10 dB
```

3. Keep phase as secondary:

```text
Early optimization: magnitude only or 90% magnitude / 10% phase
Late optimization: add group delay and phase smoothness
```

4. Use ABCD as the first fast evaluator, but cross-check with a second reduced model before COMSOL.

