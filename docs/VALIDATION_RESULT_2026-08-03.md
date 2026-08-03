# Validation result - 3 August 2026

Executed in a clean container environment with Python 3.13.5, NumPy 2.3.5 and GCC 14.2.0.

## Python

- Tests: **10 passed**
- Coverage: **78% overall**
- Spectrometer demo: 8 accumulated frames; injected 512 Hz tone recovered at 512 Hz using NumPy
- Single-dish demo:
  - finite cube fraction: 1.0
  - recovered peak frequency: 100.099607843 GHz
  - peak S/N: 153.62
  - median scan baseline RMS: 0.1000 K

## C++

- CMake configure/build: passed
- CTest: **1/1 passed**
- 1024-point radix-2 FFT self-test recovered injected bin 37

The GPU backend was not executed because no CUDA/CuPy environment was available. It remains an optional, explicitly tested-at-runtime path rather than a claimed performance result.

## Local macOS validation — Python 3.9 and GCC 16

A second independent run on Apple Silicon macOS completed with:

- Python 3.9.6 and NumPy 2.0.2
- Ruff: passed
- MyPy: passed for all 8 source files
- Pytest: 10/10 passed
- Coverage: 78%
- Synthetic FFT tone: 512 Hz injected and recovered at 512 Hz
- Single-dish line: recovered at 100.099607843 GHz with peak S/N 153.62
- C++ compiler: Homebrew GCC 16.1.0
- CMake configure/build: passed
- CTest: 1/1 passed in 0.38 s

The Apple Command Line Tools installation also passed a direct
`xcrun clang++` standard-library probe after reinstallation. Version 0.1.3
corrects the repository preflight so AppleClang is invoked with its resolved
macOS SDK context rather than as a bare compiler path.
