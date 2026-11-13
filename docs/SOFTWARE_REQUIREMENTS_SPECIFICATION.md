# Software Requirements Specification

## Scope

This is an independent demonstrator, not ALMA production software. It models two bounded responsibilities: synthetic total-power data processing and a simulated FFT spectrometer/control boundary.

## Functional requirements

| ID | Requirement | Verification |
|---|---|---|
| FR-01 | The spectrometer shall transform real ADC frames into an accumulated one-sided power spectrum. | Inject a tone and recover its frequency within one channel. |
| FR-02 | The controller shall enforce OFF, READY, ARMED, ACQUIRING and FAULT states. | State-transition unit tests. |
| FR-03 | Every controller command shall emit structured telemetry. | JSONL telemetry test and demo output. |
| FR-04 | Single-dish processing shall calibrate ON/OFF spectra. | Analytic calibration unit test. |
| FR-05 | Processing shall detect impulsive spectral interference. | Injected-channel unit test. |
| FR-06 | Processing shall fit and subtract a polynomial baseline outside a line mask. | Baseline RMS acceptance test. |
| FR-07 | Processed scans shall be spectrally regridded and spatially gridded into a cube. | End-to-end cube shape and recovered-line tests. |
| FR-08 | Products shall include QA metrics and SHA-256 provenance. | Manifest integration test. |
| FR-09 | The Python processing path shall support more than one worker. | ProcessPool implementation and Slurm recipe. |
| FR-10 | The FFT path shall support NumPy and an optional CuPy GPU backend. | CPU CI; explicit runtime error or GPU execution when requested. |

## Non-functional requirements

- Python 3.9+ and Linux portability.
- Deterministic synthetic data under a fixed seed.
- No dependency on proprietary data, CASA internals or ALMA operational code.
- Small reviewable modules, typed public interfaces and automated tests.
- Fail closed on invalid states, invalid dimensions and failed scientific QA.
