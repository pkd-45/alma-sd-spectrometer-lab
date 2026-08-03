# Mapping to NAOJ ALMA Senior Specialist vacancy

## Common requirements

- Unix/Linux team software: package structure, CI, command line, Slurm and reproducible products.
- English software documentation: requirements, design, validation and README.
- Equivalent IT knowledge: typed interfaces, state machines, error handling, tests, CI and provenance.
- Git: repository-native development and review workflow.

## JD1

- Python proficiency: all pipeline stages and CLI are Python.
- Multicore/cluster Python: process-based scan processing and Slurm recipe.
- Astronomical data processing: synthetic total-power ON/OFF calibration, spectral flags, polynomial baselines, spectral regridding and cube gridding.

## JD2

- Java/C++/Python: production path in Python plus an independent C++17 FFT reference.
- Design/specification documents: `SOFTWARE_REQUIREMENTS_SPECIFICATION.md` and `DESIGN.md`.
- Instrument lifecycle: explicit states, commands, telemetry, injected faults and recovery.
- Fourier/FFT: accumulated power spectrum with deterministic tone-recovery validation.
- GPU: optional CuPy backend and a backend benchmark; no claim of production GPU deployment.

## How to describe this in the application

> To make my transfer to ALMA-specific work inspectable, I built an independent JD1/JD2 demonstrator using synthetic data. It implements a tested total-power processing path and a simulated FFT spectrometer/control boundary, with requirements, design, telemetry, fault recovery, optional GPU execution, Slurm support and scientific QA. It is not ALMA production software and does not use proprietary ALMA code or data.
