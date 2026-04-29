# Paper Positioning

## Core claim

This project should not be framed as "we found one low-pass filter."

The stronger claim is:

```text
A fabrication-aware, physics-guided inverse-design framework for on-chip THz CPS low-pass filters.
```

## Proposed contribution stack

1. Fixed Au-on-sapphire CPS platform with 0.5 um fabrication rules.
2. Physics grammar for mirror-chirped slow-wave loading.
3. Fast ABCD/qTEM evaluator for search.
4. Binary/grammar global search plus DBS polish.
5. Optional soft-topology refinement in the outer loading region.
6. COMSOL/CST truth-layer validation.
7. Active-learning correction for future target frequencies.

## Current critical finding

Floating capacitive islands are not automatically beneficial. Early tests show that
too much disconnected metal can pull the cutoff too low or harm the low-pass shape.

Therefore the current main structure remains:

```text
mirror-chirped connected outer stubs
```

and floating islands are demoted to:

```text
local refinement feature, only kept if COMSOL/fast metrics prove benefit
```

## Required evidence before claiming novelty

- benchmark against straight CPS;
- benchmark against traditional stepped/Bessel low-pass;
- validate at least baseline, seed, and best candidate in COMSOL/CST;
- show S21 and S11;
- show field maps at pass/cutoff/stop frequencies;
- prove the response is true low-pass, not a single resonance notch;
- report fabrication constraints and connected/floating metal status.

