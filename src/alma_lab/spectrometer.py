from __future__ import annotations

from typing import Any, List, Tuple

import numpy as np

from .models import SpectrometerConfig, SpectrumProduct


def _backend(name: str) -> Tuple[Any, str]:
    if name in {"auto", "cupy"}:
        try:
            import cupy as cp  # type: ignore

            return cp, "cupy"
        except ImportError as exc:
            if name == "cupy":
                raise RuntimeError(
                    "CuPy backend requested but CuPy is not installed"
                ) from exc
    return np, "numpy"


def simulate_adc(
    sample_rate_hz: float,
    duration_s: float,
    tones: List[Tuple[float, float]],
    noise_std: float = 0.25,
    seed: int = 7,
) -> np.ndarray:
    """Generate deterministic real ADC samples with injected sinusoidal tones."""
    if sample_rate_hz <= 0 or duration_s <= 0:
        raise ValueError("sample_rate_hz and duration_s must be positive")
    n_samples = int(round(sample_rate_hz * duration_s))
    time_s = np.arange(n_samples, dtype=np.float64) / sample_rate_hz
    samples = np.zeros(n_samples, dtype=np.float64)
    for frequency_hz, amplitude in tones:
        if not 0 <= frequency_hz <= sample_rate_hz / 2:
            raise ValueError("tone must be inside the real-signal Nyquist band")
        samples += amplitude * np.sin(2.0 * np.pi * frequency_hz * time_s)
    rng = np.random.default_rng(seed)
    samples += rng.normal(0.0, noise_std, size=n_samples)
    return samples


def _window(xp: Any, name: str, size: int) -> Any:
    if name == "hann":
        return xp.hanning(size)
    return xp.ones(size)


def accumulated_power_spectrum(
    samples: np.ndarray, config: SpectrometerConfig
) -> SpectrumProduct:
    """Compute an accumulated one-sided power spectrum on CPU or optional GPU."""
    config.validate()
    xp, backend_name = _backend(config.backend)
    values = xp.asarray(samples, dtype=xp.float64)
    step = max(1, int(config.fft_size * (1.0 - config.overlap_fraction)))
    starts = list(range(0, int(values.size) - config.fft_size + 1, step))
    if len(starts) < config.accumulation:
        raise ValueError(
            f"not enough samples for {config.accumulation} frames of size {config.fft_size}"
        )
    starts = starts[: config.accumulation]
    window = _window(xp, config.window, config.fft_size)
    normalization = xp.sum(window * window)
    powers = []
    for start in starts:
        frame = values[start : start + config.fft_size] * window
        transformed = xp.fft.rfft(frame)
        powers.append((xp.abs(transformed) ** 2) / normalization)
    accumulated = xp.mean(xp.stack(powers, axis=0), axis=0)
    frequencies = xp.fft.rfftfreq(config.fft_size, d=1.0 / config.sample_rate_hz)
    if backend_name == "cupy":
        import cupy as cp  # type: ignore

        accumulated_np = cp.asnumpy(accumulated)
        frequencies_np = cp.asnumpy(frequencies)
    else:
        accumulated_np = np.asarray(accumulated)
        frequencies_np = np.asarray(frequencies)
    return SpectrumProduct(
        frequency_hz=frequencies_np,
        power=accumulated_np,
        n_frames=len(starts),
        backend=backend_name,
        metadata={
            "fft_size": config.fft_size,
            "sample_rate_hz": config.sample_rate_hz,
            "window": config.window,
            "overlap_fraction": config.overlap_fraction,
        },
    )
