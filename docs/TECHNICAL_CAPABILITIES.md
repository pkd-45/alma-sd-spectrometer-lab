# Technical capabilities and evidence

This independent project demonstrates two complementary types of scientific
software. It uses **synthetic data and simulated devices**, not ALMA
observations or production infrastructure.

## Reproducible scientific computing

- Unix/Linux-oriented Python package and command-line interface
- Tests, continuous integration, Slurm example and reproducible products
- Requirements, architecture, validation records and provenance
- Explicit interfaces, lifecycle states, fault handling and telemetry

## Single-dish spectral-line processing

- Synthetic total-power ON/OFF calibration and spectral-line processing
- Process-based scan processing, channel flagging, baseline subtraction
- Spectral regridding, spatial cube gridding and QA products

## FFT-spectrometer modelling and control

- Python reference path and a separate C++17 FFT test implementation
- Simulated acquisition states, commands, telemetry, failures and recovery
- Accumulated FFT power spectra and tone-recovery tests
- Optional CuPy backend, with no claim of measured production GPU acceleration

These tests demonstrate research-software design and validation, **not**
ALMA pipeline compatibility, observatory commissioning or deployed instrument
control. See the project README and validation documents for exact gates and
reference measurements.
