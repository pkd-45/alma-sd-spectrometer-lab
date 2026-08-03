# Design

```text
Simulated ADC -> SpectrometerController -> FFT accumulator -> spectrum + telemetry
                                           | NumPy CPU
                                           + optional CuPy GPU

Synthetic ON/OFF scans -> calibration -> robust flags -> baseline -> regrid -> spatial cube
                                                                      |
                                                                      + QA + SHA-256 manifest
```

## Component boundaries

- `spectrometer.py`: numerical FFT accumulation and backend selection.
- `control.py`: explicit instrument state, commands, telemetry and fault recovery.
- `single_dish.py`: calibration, flagging, baselines, regridding and gridding.
- `pipeline.py`: deterministic synthetic observations, orchestration, QA and provenance.
- `cpp/`: independent C++17 radix-2 FFT reference used as a cross-language numerical sanity check.

## Failure policy

The controller enters `FAULT` if acquisition fails. The pipeline raises an error rather than publishing a product when recovered line frequency, finite fraction or peak S/N miss their declared gates. Invalid states and data shapes are rejected explicitly.

## Performance path

The baseline implementation uses vectorised NumPy, optional CuPy for FFT accumulation, process-based scan parallelism, and a Slurm launch recipe. The benchmark reports backend, FFT size, accumulation and timing without claiming production-scale ALMA performance.
