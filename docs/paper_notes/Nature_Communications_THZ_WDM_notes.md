# s41467-025-62557-5.pdf Notes

Source file:

```text
/Users/lukuan/Desktop/ Quantum Engineering/AI_THZ/Past_Paper/s41467-025-62557-5.pdf
```

Title:

```text
On-chip, inverse-designed active wavelength division multiplexer at THz frequencies
```

## Why this paper matters for Route B

This paper is not a CPS low-pass filter paper. Its value is different:

- It proves that inverse-designed topology optimization is publishable and credible for integrated THz devices.
- It shows how to frame a THz inverse-designed component as a platform-level contribution.
- It uses a strongly constrained on-chip waveguide environment, which is conceptually similar to our constrained CPS platform.

## Lessons to borrow

1. Make the platform explicit.

Route B should always state:

```text
Au-on-sapphire CPS
3 um / 3 um / 3 um core
0.275 um Au
0.5 um fabrication grid
on-chip differential THz propagation
```

2. Show topology plus fields.

The final Route B result must include:

```text
geometry mask
fabrication-ready layout
S21/S11 curves
E-field at passband, cutoff, and stopband
current density on Au
```

3. Prove the design is useful compared with baselines.

Baselines:

```text
straight CPS
traditional stepped/Bessel low-pass
manual chirped stub
AI binary optimized structure
```

4. Avoid claiming "AI" as the only novelty.

The actual novelty should be:

```text
constrained binary inverse design for a 0.8 THz on-chip CPS low-pass filter
with mirror-chirped fractal SSPP-like outer loading
and a reproducible fast-to-COMSOL validation loop.
```

