# Verification and validation

## Automated verification

- Python linting with Ruff.
- Static type checking with MyPy.
- Unit tests for calibration, flagging, FFT tone recovery and state transitions.
- Integration test for cube generation, scientific QA and product checksums.
- CMake/CTest build of the independent C++17 FFT reference.
- GitHub Actions on Python 3.9, 3.11 and 3.13.

## Scientific acceptance gates

The deterministic demo must:

1. produce a cube with at least 99% finite voxels;
2. recover the injected line centre within 2 MHz;
3. recover a peak line signal-to-noise ratio above 10;
4. write checksummed products and a machine-readable QA report.

## Deliberate limitations

This project does not implement CASA MeasurementSets, ASDM ingestion, ALMA calibration heuristics, production telescope interfaces, real-time network transport, hardware drivers or observatory deployment. The code is evidence of transferable software and signal-processing practice, not a claim of prior ALMA operations experience.
