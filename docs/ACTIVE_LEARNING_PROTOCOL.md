# Active Learning Protocol

## Goal

Use COMSOL/CST full-wave results to correct the fast ABCD/qTEM model.

## Dataset levels

```text
Level 0: geometry only
Level 1: fast ABCD/qTEM evaluation
Level 2: reduced-coupling cross-check
Level 3: COMSOL/CST validation
```

## Per-candidate record

```text
mask.csv
grammar.json
fast_sparams.csv
fast_metrics.json
fabrication_report.json
analog_equivalent.json
comsol_sparams.csv
comsol_metrics.json
field_notes.md
```

## First active-learning question

Before training any generator, answer:

```text
Does fast-model ranking match COMSOL ranking for:
  straight CPS
  7-stub seed
  11-stub sweep best
```

If no, update the fast evaluator before optimizing further.

## Correction target

Train a small correction model:

```text
delta_metrics = COMSOL_metrics - fast_metrics
```

Features:

```text
stub count
stub depth statistics
chirp slope
metal fill
connected loading area
floating island area
quarter-wave frequency range
```

